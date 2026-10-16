#!/usr/bin/env bash
# Run ONE E2 (frozen Example 16) interrupted-recovery baseline trial: Session A (Stage 1 only) then a
# completely fresh Session B (recovery), both fully headless; or dry-run it.
# Usage: run_e2_baseline.sh --trial N (--dry-run | --execute-counted) [--local] [--pause-after-session-a | --session-b-only]
#   --pause-after-session-a  stop after Session A and its interlock checks (researcher inspects), then resume with --session-b-only
# Fresh-session enforcement: Session B is a new process with a new UUID and its own CLAUDE_CONFIG_DIR; no resume/continue/fork;
# Session A's launch records, stream and transcript live under researcher_only/session_evidence/ until collection, so Session B can
# see only the persistent trial workspace the agent itself wrote.
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
SEL=e2-example16; n=""; mode=""; via=""; pause=0; bonly=0; sfx=""
while [[ $# -gt 0 ]]; do case "$1" in --trial) n=${2:?}; shift 2;; --suffix) sfx=${2:?}; shift 2;; --dry-run) mode=dry; shift;; --execute-counted) mode=counted; shift;; --local) via=--local; shift;; --pause-after-session-a) pause=1; shift;; --session-b-only) bonly=1; shift;; -h|--help) sed -n '2,8p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -n "$n" && -n "$mode" ]] || die "need --trial N and --dry-run or --execute-counted" 2
td=$(trial_dir_of "$SEL" "$n" "${sfx:-}"); rid=$(run_id_of "$SEL" "$n" "${sfx:-}"); m="$td/manifest.yaml"; ev="$SESSION_EVIDENCE_ROOT/$rid"
[[ -f "$m" ]] || die "planned packet missing: $td (run prepare_trial.sh)" 4
log "== $rid ($mode) =="
"$AUTOMATION_DIR/preflight.sh" --experiment "$SEL" $([[ $mode == dry ]] && echo --dry-run) || { [[ $mode == dry ]] && warn "preflight BLOCKED: a counted run would be refused; continuing the dry run for the plan only" || die "preflight blocked the counted run" 3; }
pa="$td/agent_inputs/session_a_prompt.md"; pb="$td/agent_inputs/recovery_prompt.md"
interlock() {  # between sessions: Session A ended, no trial jobs still running, Stage-1 boundary artifacts exist
  local ok=1
  [[ -f "$ev/session_a/session_record.json" ]] || { warn "no Session A record"; ok=0; }
  local ids; ids=$(grep -ohE '[0-9]{6,}' "$td/jobs/job_ids.txt" 2>/dev/null | sort -u | paste -sd, -)
  if [[ -n "$ids" ]] && squeue -h -j "$ids" 2>/dev/null | grep -q .; then warn "trial jobs still running/pending: $(squeue -h -j "$ids" -o '%i:%T' | tr '\n' ' ')"; ok=0; fi
  if squeue -h -u "$USER" -o '%i %Z' 2>/dev/null | grep -q " $td"; then warn "jobs with WorkDir under the trial are still active"; ok=0; fi
  for f in outputs/stage1/engine_output.exo outputs/stage1/morphorm_oc_optimizer_diagnostics.txt work/run_summary.md; do [[ -s "$td/$f" ]] || { warn "Stage-1 boundary artifact missing: $f"; ok=0; }; done
  if [[ -e "$td/outputs/stage2" ]] && [[ -n "$(find "$td/outputs/stage2" -type f -print -quit)" ]]; then warn "Session A produced Stage-2 outputs (boundary violated)"; ok=0; fi
  [[ $ok -eq 1 ]]; }
if [[ $mode == dry ]]; then
  "$AUTOMATION_DIR/verify_trial_packet.sh" --trial-dir "$td" --planned || die "packet is not a clean planned packet" 4
  "$AUTOMATION_DIR/launch_headless_claude.sh" --trial-dir "$td" --run-id "$rid" --session-label session_a --prompt-file "$pa" --dry-run $via
  log "DRY RUN interlock (would check): Session A ended; no trial jobs active; outputs/stage1/{engine_output.exo,morphorm_oc_optimizer_diagnostics.txt} and work/run_summary.md present; no outputs/stage2 content"
  "$AUTOMATION_DIR/launch_headless_claude.sh" --trial-dir "$td" --run-id "$rid" --session-label session_b --prompt-file "$pb" --dry-run $via
  "$AUTOMATION_DIR/collect_baseline_evidence.sh" --trial-dir "$td" --dry-run; "$AUTOMATION_DIR/score_researcher_only.sh" --trial-dir "$td" --dry-run
  log "DRY RUN complete for $rid: two independent launch plans (distinct session ids and config dirs), no model call, no Slurm, manifest unchanged (status=$(manifest_get "$m" status))"; exit 0
fi
[[ -x "$CLAUDE_BIN_PINNED" && "$(claude_version_of "$CLAUDE_BIN_PINNED")" == "$CLAUDE_PIN_VERSION" ]] || die "pinned Claude Code $CLAUDE_PIN_VERSION missing; counted run refused" 3
if [[ $bonly -eq 0 ]]; then
  "$AUTOMATION_DIR/verify_trial_packet.sh" --trial-dir "$td" --planned || die "packet is not a clean planned packet" 4
  [[ "$(manifest_get "$m" status)" == planned ]] || die "manifest status is not planned" 4
  [[ ! -d "$ev/session_a" ]] || die "Session A evidence already exists for $rid (refusing)" 4
  manifest_set "$m" status running_session_a; manifest_set "$m" started_utc "$(utc_now)"
  "$AUTOMATION_DIR/launch_headless_claude.sh" --trial-dir "$td" --run-id "$rid" --session-label session_a --prompt-file "$pa" --execute-counted ${via:---via-slurm}; arc=$?
  log "Session A ended rc=$arc; running interlock"
  if ! interlock; then manifest_set "$m" status failed_stage1_boundary; "$AUTOMATION_DIR/collect_baseline_evidence.sh" --trial-dir "$td" || true; die "$rid: Stage-1 boundary not reached or ambiguous; Session B not launched (trial marked failed_stage1_boundary)" 1; fi
  manifest_set "$m" status paused_after_session_a
  [[ $pause -eq 0 ]] || { log "paused after Session A as requested; resume with: run_e2_baseline.sh --trial $n --execute-counted --session-b-only"; exit 0; }
else
  [[ "$(manifest_get "$m" status)" == paused_after_session_a ]] || die "--session-b-only requires status paused_after_session_a (now '$(manifest_get "$m" status)')" 4
  interlock || die "interlock failed before Session B" 1
fi
[[ ! -d "$ev/session_b" ]] || die "Session B evidence already exists for $rid (refusing)" 4
manifest_set "$m" status running_session_b
"$AUTOMATION_DIR/launch_headless_claude.sh" --trial-dir "$td" --run-id "$rid" --session-label session_b --prompt-file "$pb" --execute-counted ${via:---via-slurm}; brc=$?
"$AUTOMATION_DIR/collect_baseline_evidence.sh" --trial-dir "$td" || warn "evidence collection reported a problem"
"$AUTOMATION_DIR/verify_trial_packet.sh" --trial-dir "$td" --completed --json "$td/logs/packet_verification.json"; vrc=$?
case "$vrc" in 0) st=completed_unscored;; 5) st=ambiguous;; *) st=failed;; esac; [[ $brc -eq 0 ]] || st=failed
manifest_set "$m" status "$st"; manifest_set "$m" packet_verification "logs/packet_verification.json"
log "$rid finished: status=$st (Session B rc=$brc, verification rc=$vrc). Scientific scoring is a separate researcher-only step."
[[ "$st" == completed_unscored ]] || exit 1
