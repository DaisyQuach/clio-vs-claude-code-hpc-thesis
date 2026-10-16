#!/usr/bin/env bash
# CLIO-specific checks that run IN ADDITION to the baseline verifier (../verify_trial_packet.sh --completed, used unchanged).
# Usage: verify_clio_supplement.sh --trial-dir D [--json OUT]        Exit 0 verified | 1 failed | 5 ambiguous
# Per session: one user message (plus permitted nudges); effective model / approval / effort / blueprint+version equal the
# configuration; Claude Code CLI version equals the pin; clio-agent equals the pin; own fresh deployment; boundary audit over
# the CLIO API exports (the baseline verifier already audits stream.jsonl and transcript_*.jsonl); usage telemetry present.
source "$(dirname "${BASH_SOURCE[0]}")/lib/clio_common.sh"
td=""; json_out=""
while [[ $# -gt 0 ]]; do case "$1" in --trial-dir) td=${2:?}; shift 2;; --json) json_out=${2:?}; shift 2;; -h|--help) sed -n '2,6p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -d "$td" ]] || die "trial dir not found" 2; td=$(cd "$td" && pwd -P)
fails=0; amb=0; lines=()
ck() { lines+=("$1|$2|$3"); printf '%-9s %-40s %s\n' "$1" "$2" "$3"; [[ $1 == FAIL ]] && fails=$((fails+1)); [[ $1 == AMBIGUOUS ]] && amb=$((amb+1)); return 0; }
recs=$(find "$td/logs/agent_sessions" -name session_record.json 2>/dev/null | sort)
[[ -n "$recs" ]] || ck FAIL session_records "no session records under logs/agent_sessions"
deps=$(for r in $recs; do jq -r .config_dir "$r"; done | sort -u | wc -l); n=$(echo "$recs" | grep -c .)
[[ "$deps" -eq "$n" ]] && ck PASS fresh_deployment_per_session "$n session(s), $deps distinct deployment dirs" || ck FAIL fresh_deployment_per_session "deployments shared"
pat="researcher_only|Morphorm_ground_truth|examplesmanual|/Morphorm/docs|/Morphorm/morphormtests|ThesisExperiments/runs|experiments_groundTruth|Morphorm_Full_Examples_Tests|\.agent_runtime"
for r in $recs; do sd=$(dirname "$r"); l=$(jq -r .session_label "$r"); dep=$(jq -r .config_dir "$r")
  e=$(jq -c '.effective_session_settings // {}' "$r")
  [[ "$(jq -r .model_id <<<"$e")" == "$CLAUDE_MODEL" && "$(jq -r .provider_id <<<"$e")" == claude_code ]] && ck PASS "model_$l" "claude_code/$CLAUDE_MODEL" || ck FAIL "model_$l" "$e"
  [[ "$(jq -r .approval_mode <<<"$e")" == "$CLIO_APPROVAL_MODE" ]] && ck PASS "approval_$l" "$CLIO_APPROVAL_MODE" || ck FAIL "approval_$l" "$(jq -r .approval_mode <<<"$e")"
  [[ "$(jq -r .effort <<<"$e")" == "$CLIO_EFFORT" ]] && ck PASS "effort_$l" "$CLIO_EFFORT" || ck FAIL "effort_$l" "$(jq -r .effort <<<"$e")"
  bpg="$(jq -r .blueprint_id <<<"$e")@$(jq -r .blueprint_version <<<"$e")"
  [[ "$bpg" == "$CLIO_BLUEPRINT_ID@$CLIO_BLUEPRINT_VERSION" || ( "$CLIO_BLUEPRINT_ID" == none && "$bpg" == none@* ) ]] && ck PASS "blueprint_$l" "$bpg" || ck FAIL "blueprint_$l" "$bpg != $CLIO_BLUEPRINT_ID@$CLIO_BLUEPRINT_VERSION"
  v=$(jq -r .executable_version "$r"); [[ "$v" == "$CLIO_CLAUDE_CLI_PIN" ]] && ck PASS "claude_cli_$l" "$v" || ck FAIL "claude_cli_$l" "Claude Code CLI '$v' != pin $CLIO_CLAUDE_CLI_PIN"
  v=$(jq -r .clio_agent_version "$r"); [[ "$v" == "$CLIO_AGENT_VERSION_PIN" ]] && ck PASS "clio_agent_$l" "$v" || ck FAIL "clio_agent_$l" "clio-agent $v != pin $CLIO_AGENT_VERSION_PIN"
  nu=$(jq -r .user_messages_in_session "$r"); nn=$(jq '[.messages[]? | select(.kind=="nudge")] | length' "$sd/clio/runner_state.json" 2>/dev/null || echo 0)
  [[ "$nu" == $((1 + nn)) && $nn -le $CLIO_MAX_NUDGES ]] && ck PASS "user_messages_$l" "$nu (prompt + $nn nudge(s); limit $CLIO_MAX_NUDGES)" || ck FAIL "user_messages_$l" "user messages $nu, nudges $nn (limit $CLIO_MAX_NUDGES)"
  er=$(jq -r .end_reason "$r"); [[ "$er" == finished_idle ]] && ck PASS "end_$l" "$er" || ck AMBIGUOUS "end_$l" "$er (researcher review)"
  [[ -s "$sd/clio/usage_summary.json" && -s "$sd/result.json" ]] && ck PASS "usage_$l" "$(jq -c '{api_calls, cost:(.totals.cost_usd*100|round/100), resends:.full_resend_calls, reset_reasons:.stream_audit.reset_reasons}' "$sd/clio/usage_summary.json")" || ck AMBIGUOUS "usage_$l" "usage telemetry missing"
  viol=""; for f in "$sd"/clio/{messages,export_transcript,export_full,trace,interactions}.json; do [[ -f "$f" ]] || continue
    sed -e "s#${dep//#/\\#}##g" "$f" | grep -qsE "$pat" && viol="$viol $(basename "$f")"; done
  [[ -z "$viol" ]] && ck PASS "boundary_audit_clio_$l" "no restricted paths in the CLIO exports" || ck FAIL "boundary_audit_clio_$l" "restricted material referenced in:$viol"
done
res=$([[ $fails -eq 0 && $amb -eq 0 ]] && echo verified || { [[ $fails -gt 0 ]] && echo failed || echo ambiguous; })
printf '\nCLIO supplement verification: %s  fails=%d ambiguous=%d\n' "$res" "$fails" "$amb"
if [[ -n "$json_out" ]]; then printf '%s\n' "${lines[@]}" | jq -R 'split("|") | {result:.[0], name:.[1], detail:(.[2:]|join("|"))}' | jq -s --arg r "$res" --arg u "$(utc_now)" '{utc:$u, result:$r, checks:.}' > "$json_out"; fi
[[ $fails -eq 0 ]] || exit 1; [[ $amb -eq 0 ]] || exit 5; exit 0
