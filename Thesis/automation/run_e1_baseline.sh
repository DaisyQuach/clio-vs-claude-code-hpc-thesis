#!/usr/bin/env bash
# Run ONE E1 (frozen Example 8) baseline trial headlessly, or dry-run it.
# Usage: run_e1_baseline.sh --trial N (--dry-run | --execute-counted) [--local]
#   --dry-run          preflight + packet verification + launch plan; no model call, no Slurm, no manifest change
#   --execute-counted  required guard for a counted run (manifest planned -> running -> completed_unscored|failed|ambiguous)
#   --local            run the agent in the current allocation instead of an sbatch agent-host job
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
SEL=e1-example8; n=""; mode=""; via=""; sfx=""
while [[ $# -gt 0 ]]; do case "$1" in --trial) n=${2:?}; shift 2;; --suffix) sfx=${2:?}; shift 2;; --dry-run) mode=dry; shift;; --execute-counted) mode=counted; shift;; --local) via=--local; shift;; -h|--help) sed -n '2,7p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -n "$n" && -n "$mode" ]] || die "need --trial N and --dry-run or --execute-counted" 2
td=$(trial_dir_of "$SEL" "$n" "${sfx:-}"); rid=$(run_id_of "$SEL" "$n" "${sfx:-}"); m="$td/manifest.yaml"
[[ -f "$m" ]] || die "planned packet missing: $td (run prepare_trial.sh)" 4
log "== $rid ($mode) =="
"$AUTOMATION_DIR/preflight.sh" --experiment "$SEL" $([[ $mode == dry ]] && echo --dry-run) || { [[ $mode == dry ]] && warn "preflight BLOCKED: a counted run would be refused; continuing the dry run for the plan only" || die "preflight blocked the counted run" 3; }
"$AUTOMATION_DIR/verify_trial_packet.sh" --trial-dir "$td" --planned || die "packet is not a clean planned packet" 4
[[ "$(manifest_get "$m" status)" == planned ]] || die "manifest status is '$(manifest_get "$m" status)', not planned" 4
prompt="$td/agent_inputs/task_prompt.md"
if [[ $mode == dry ]]; then
  "$AUTOMATION_DIR/launch_headless_claude.sh" --trial-dir "$td" --run-id "$rid" --session-label session_main --prompt-file "$prompt" --dry-run $via
  "$AUTOMATION_DIR/collect_baseline_evidence.sh" --trial-dir "$td" --dry-run; "$AUTOMATION_DIR/score_researcher_only.sh" --trial-dir "$td" --dry-run
  log "DRY RUN complete for $rid: no model call, no Slurm submission, manifest unchanged (status=$(manifest_get "$m" status))"; exit 0
fi
[[ -x "$CLAUDE_BIN_PINNED" && "$(claude_version_of "$CLAUDE_BIN_PINNED")" == "$CLAUDE_PIN_VERSION" ]] || die "pinned Claude Code $CLAUDE_PIN_VERSION missing; counted run refused" 3
[[ ! -d "$SESSION_EVIDENCE_ROOT/$rid/session_main" ]] || die "session evidence for $rid already exists (refusing)" 4
manifest_set "$m" status running; manifest_set "$m" started_utc "$(utc_now)"
"$AUTOMATION_DIR/launch_headless_claude.sh" --trial-dir "$td" --run-id "$rid" --session-label session_main --prompt-file "$prompt" --execute-counted ${via:---via-slurm}; lrc=$?
"$AUTOMATION_DIR/collect_baseline_evidence.sh" --trial-dir "$td" || warn "evidence collection reported a problem"
"$AUTOMATION_DIR/verify_trial_packet.sh" --trial-dir "$td" --completed --json "$td/logs/packet_verification.json"; vrc=$?
case "$vrc" in 0) st=completed_unscored;; 5) st=ambiguous;; *) st=failed;; esac; [[ $lrc -eq 0 ]] || st=failed
manifest_set "$m" status "$st"; manifest_set "$m" packet_verification "logs/packet_verification.json"
log "$rid finished: status=$st (launch rc=$lrc, verification rc=$vrc). Scientific scoring is a separate researcher-only step."
[[ "$st" == completed_unscored ]] || exit 1
