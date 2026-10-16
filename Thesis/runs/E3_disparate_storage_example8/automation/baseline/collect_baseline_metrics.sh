#!/usr/bin/env bash
# Collect descriptive metrics and an auditable command record for one E3 baseline trial (read-only on the evidence).
# Usage: collect_baseline_metrics.sh --trial-dir <E3>/baseline/trial_NN
# Reads logs/session/stream.jsonl and the trial's staging/provenance records; writes provenance/commands.tsv,
# provenance/tool_calls.tsv and provenance/metrics.json. Tokens/cost/tool counts are descriptive audit metadata, not outcomes.
source "$(dirname "${BASH_SOURCE[0]}")/../lib/e3_common.sh"
td=""
while [[ $# -gt 0 ]]; do case "$1" in --trial-dir) td=${2:?}; shift 2;; -h|--help) sed -n '2,5p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
td=$(e3_guard_trial_dir baseline "$td") || exit $?; s="$td/logs/session/stream.jsonl"; [[ -s "$s" ]] || die "no session stream: $s" 1
P="$td/provenance"
# tool calls joined with their result status (is_error)
jq -rs '
  ( [ .[] | select(.type=="user") | .message.content[]? | select(.type=="tool_result") | {key:.tool_use_id, value:(.is_error // false)} ] | from_entries ) as $err
  | ["tool_use_id","tool","is_error","input_summary"], ( .[] | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use")
  | [.id, .name, ($err[.id] // "no_result" | tostring), ((.input.command // .input.file_path // .input.path // .input.pattern // (.input|tostring)) | tostring | gsub("[\t\n]";" ") | .[0:400])] )
  | @tsv' "$s" | redact_home > "$P/tool_calls.tsv"
awk -F'\t' 'NR==1{print "tool_use_id\tis_error\tcommand"; next} $2=="Bash"{print $1"\t"$3"\t"$4}' "$P/tool_calls.tsv" > "$P/commands.tsv"
cnt() { [[ -s "$1" ]] && echo $(( $(wc -l < "$1") - 1 )) || echo 0; }
bytes() { [[ -s "$1" ]] && awk -F'\t' -v c="$2" 'NR>1{s+=$c} END{print s+0}' "$1" || echo 0; }
res=$(grep -E '"type" *: *"result"' "$s" | tail -1); [[ -n "$res" ]] || res='{}'
jq -n --argjson r "$res" --arg tid "$(trial_id_of baseline "$td")" \
  --argjson tools "$(jq -s '[.[] | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | .name] | group_by(.) | map({key:.[0], value:length}) | from_entries' "$s")" \
  --argjson staged "$(cnt "$td/staging-manifest/staged_files.tsv")" --argjson staged_bytes "$(bytes "$td/staging-manifest/staged_files.tsv" 5)" \
  --argjson returned "$(cnt "$td/staging-manifest/returned_files.tsv")" --argjson returned_bytes "$(bytes "$td/staging-manifest/returned_files.tsv" 4)" \
  --argjson searched "$(cnt "$td/provenance/sources_searched.tsv")" \
  --argjson bash_errors "$(awk -F'\t' 'NR>1 && $2=="true"' "$P/commands.tsv" | wc -l)" \
  --arg selections "$([[ -s $P/artifact_selections.md ]] && echo present || echo missing)" \
  --arg audit "$(sed -n 's/^verdict: //p' "$P/boundary_audit.txt" 2>/dev/null)" \
  '{trial_id:$tid, descriptive_only:true,
    session:{duration_ms:$r.duration_ms, duration_api_ms:$r.duration_api_ms, num_turns:$r.num_turns, is_error:$r.is_error, subtype:$r.subtype,
             total_cost_usd:$r.total_cost_usd, usage:$r.usage},
    tool_calls_by_name:$tools, bash_commands_with_error:$bash_errors,
    staging:{files_staged:$staged, bytes_staged:$staged_bytes, files_returned:$returned, bytes_returned:$returned_bytes},
    discovery:{locations_recorded:$searched, artifact_selection_record:$selections}, boundary_audit:$audit}' > "$P/metrics.json"
cat "$P/metrics.json"
