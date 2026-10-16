#!/usr/bin/env bash
# Run ONE E1 (frozen Example 8) CLIO trial headlessly, or dry-run it. CLIO counterpart of ../run_e1_baseline.sh.
# Usage: run_e1_clio.sh --trial N [--suffix R] (--dry-run | --execute-counted) [--local]
#   --dry-run          preflight + packet verification + launch plan; no deployment, no model call, no Slurm, no manifest change
#   --execute-counted  counted run (manifest planned -> running -> completed_unscored|failed|ambiguous)
#   --local            run in the current allocation instead of an sbatch agent-host job
# Same order as the baseline: preflight -> planned-packet verification -> launch -> collect -> completed verification
# (baseline verifier, unchanged) + CLIO supplement -> manifest status. Scoring stays a separate researcher-only step
# (../score_researcher_only.sh, unchanged).
source "$(dirname "${BASH_SOURCE[0]}")/lib/clio_common.sh"
SEL=e1-example8; n=""; mode=""; via=""; sfx=""
while [[ $# -gt 0 ]]; do case "$1" in --trial) n=${2:?}; shift 2;; --suffix) sfx=${2:?}; shift 2;; --dry-run) mode=dry; shift;; --execute-counted) mode=counted; shift;; --local) via=--local; shift;; -h|--help) sed -n '2,9p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -n "$n" && -n "$mode" ]] || die "need --trial N and --dry-run or --execute-counted" 2
td=$(clio_trial_dir_of "$SEL" "$n" "${sfx:-}"); rid=$(clio_run_id_of "$SEL" "$n" "${sfx:-}"); m="$td/manifest.yaml"
[[ -f "$m" ]] || die "planned packet missing: $td (run prepare_clio_trial.sh)" 4
log "== $rid ($mode) =="
"$CLIO_AUTOMATION_DIR/preflight_clio.sh" --experiment "$SEL" $([[ $mode == dry ]] && echo --dry-run) || { [[ $mode == dry ]] && warn "preflight BLOCKED: a counted run would be refused; continuing the dry run for the plan only" || die "preflight blocked the counted run" 3; }
"$AUTOMATION_DIR/verify_trial_packet.sh" --trial-dir "$td" --planned || die "packet is not a clean planned packet" 4
[[ "$(manifest_get "$m" status)" == planned ]] || die "manifest status is '$(manifest_get "$m" status)', not planned" 4
prompt="$td/agent_inputs/task_prompt.md"
if [[ $mode == dry ]]; then
  "$CLIO_AUTOMATION_DIR/launch_clio_session.sh" --trial-dir "$td" --run-id "$rid" --session-label session_main --prompt-file "$prompt" --dry-run $via
  "$CLIO_AUTOMATION_DIR/collect_clio_evidence.sh" --trial-dir "$td" --dry-run; "$AUTOMATION_DIR/score_researcher_only.sh" --trial-dir "$td" --dry-run
  log "DRY RUN complete for $rid: no deployment, no model call, no Slurm submission, manifest unchanged (status=$(manifest_get "$m" status))"; exit 0
fi
[[ ! -d "$SESSION_EVIDENCE_ROOT/$rid/session_main" ]] || die "session evidence for $rid already exists (refusing)" 4
manifest_set "$m" status running; manifest_set "$m" started_utc "$(utc_now)"
"$CLIO_AUTOMATION_DIR/launch_clio_session.sh" --trial-dir "$td" --run-id "$rid" --session-label session_main --prompt-file "$prompt" --execute-counted ${via:---via-slurm}; lrc=$?
"$CLIO_AUTOMATION_DIR/collect_clio_evidence.sh" --trial-dir "$td" || warn "evidence collection reported a problem"
"$AUTOMATION_DIR/verify_trial_packet.sh" --trial-dir "$td" --completed --json "$td/logs/packet_verification.json"; vrc=$?
"$CLIO_AUTOMATION_DIR/verify_clio_supplement.sh" --trial-dir "$td" --json "$td/logs/clio_supplement_verification.json"; src=$?
manifest_set "$m" clio_supplement_verification "logs/clio_supplement_verification.json"
case "$vrc" in 0) st=completed_unscored;; 5) st=ambiguous;; *) st=failed;; esac; [[ $lrc -eq 0 ]] || st=failed
[[ $st == completed_unscored && $src -ne 0 ]] && st=ambiguous
manifest_set "$m" status "$st"; manifest_set "$m" packet_verification "logs/packet_verification.json"
log "$rid finished: status=$st (launch rc=$lrc, verification rc=$vrc, CLIO supplement rc=$src). Scientific scoring is a separate researcher-only step."
[[ "$st" == completed_unscored ]] || exit 1
