#!/usr/bin/env bash
# Collect descriptive metrics and an auditable command record for one E3 CLIO trial (read-only on the evidence).
# Usage: collect_clio_metrics.sh --trial-dir <E3>/clio/trial_NN
# Reads logs/session/messages.json (CLIO transcript: tool_call / tool_result parts) and the staging/provenance records;
# writes provenance/tool_calls.tsv, provenance/commands.tsv, provenance/metrics.json in the same shapes as the baseline.
source "$(dirname "${BASH_SOURCE[0]}")/../lib/e3_common.sh"
td=""
while [[ $# -gt 0 ]]; do case "$1" in --trial-dir) td=${2:?}; shift 2;; -h|--help) sed -n '2,5p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
td=$(e3_guard_trial_dir clio "$td") || exit $?; m="$td/logs/session/messages.json"; [[ -s "$m" ]] || die "no CLIO transcript: $m" 1
P="$td/provenance"
jq -r '[.messages[]? // .[]?] as $ms
  | ([ $ms[] | (.parts // [])[] | select(.type=="tool_result") | {key:(.call_id // .tool_call_id // ""), value:(.is_error // false)} ] | from_entries) as $err
  | ["tool_use_id","tool","is_error","input_summary"],
    ( $ms[] | (.parts // [])[] | select(.type=="tool_call")
      | [(.call_id // .id), (.tool_name // .name), ($err[(.call_id // .id)] // "no_result" | tostring),
         ((.input.command // .input.file_path // .input.path // .input.pattern // (.input|tostring)) | tostring | gsub("[\t\n]";" ") | .[0:400])] )
  | @tsv' "$m" | redact_home > "$P/tool_calls.tsv"
awk -F'\t' 'NR==1{print "tool_use_id\tis_error\tcommand"; next} $2 ~ /shell|bash/ {print $1"\t"$3"\t"$4}' "$P/tool_calls.tsv" > "$P/commands.tsv"
cnt() { [[ -s "$1" ]] && echo $(( $(wc -l < "$1") - 1 )) || echo 0; }
bytes() { [[ -s "$1" ]] && awk -F'\t' -v c="$2" 'NR>1{s+=$c} END{print s+0}' "$1" || echo 0; }
sr="$td/logs/session/session_record.json"; [[ -s "$sr" ]] || sr=/dev/null
jq -n --arg tid "$(trial_id_of clio "$td")" \
  --argjson tools "$(jq '[.messages[]? // .[]?] | [.[] | (.parts // [])[] | select(.type=="tool_call") | (.tool_name // .name)] | group_by(.) | map({key:.[0], value:length}) | from_entries' "$m")" \
  --argjson tokens "$(jq '[.messages[]? // .[]?] | [.[] | .tokens // empty] | if length==0 then null else {input:(map(.input // 0)|add), output:(map(.output // 0)|add)} end' "$m" 2>/dev/null || echo null)" \
  --argjson nmsg "$(jq '[.messages[]? // .[]?] | length' "$m")" \
  --argjson session "$(jq -c '{start_utc, end_utc, end_reason, timeout_hit, user_messages_in_session}' "$sr" 2>/dev/null || echo null)" \
  --argjson staged "$(cnt "$td/staging-manifest/staged_files.tsv")" --argjson staged_bytes "$(bytes "$td/staging-manifest/staged_files.tsv" 5)" \
  --argjson returned "$(cnt "$td/staging-manifest/returned_files.tsv")" --argjson returned_bytes "$(bytes "$td/staging-manifest/returned_files.tsv" 4)" \
  --argjson globus "$(cnt "$td/staging-manifest/globus_transfers.tsv")" --argjson searched "$(cnt "$td/provenance/sources_searched.tsv")" \
  --argjson cmd_errors "$(awk -F'\t' 'NR>1 && $2=="true"' "$P/commands.tsv" | wc -l)" \
  --arg selections "$([[ -s $P/artifact_selections.md ]] && echo present || echo missing)" \
  --arg audit "$(sed -n 's/^verdict: //p' "$P/boundary_audit.txt" 2>/dev/null)" \
  '{trial_id:$tid, system:"clio", descriptive_only:true, session:$session, messages:$nmsg, tokens:$tokens,
    tool_calls_by_name:$tools, shell_commands_with_error:$cmd_errors,
    staging:{files_staged:$staged, bytes_staged:$staged_bytes, files_returned:$returned, bytes_returned:$returned_bytes, globus_transfers:$globus},
    discovery:{locations_recorded:$searched, artifact_selection_record:$selections}, boundary_audit:$audit}' > "$P/metrics.json"
cat "$P/metrics.json"
