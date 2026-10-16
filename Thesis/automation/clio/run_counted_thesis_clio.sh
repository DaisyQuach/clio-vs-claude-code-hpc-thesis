#!/usr/bin/env bash
# Counted CLIO arm, all three experiments, one trial at a time (researcher decision 2026-10-13: blueprint factorio-flat 0.5.0,
# see blueprints/factorio-flat-0.5.0.PROVENANCE.md; run these first on Fable). Order: E1 trials 1-5, E2 trials 1-5,
# E3 trials 1-5, each scored right after it ends with the same scorer as its baseline:
#   E1/E2: run_e1_clio.sh / run_e2_clio.sh --execute-counted, then ../score_researcher_only.sh --figures (unchanged)
#   E3:    run_clio_e3_trial_v2.sh --execute-counted inside a fresh agent-host allocation (baseline contract), then
#          score_e3_clio.sh (the E3 baseline's recorded scoring procedure)
# Before every trial a one-line Fable call in a 5-minute allocation checks that the provider accepts calls (provider usage
# limits aborted baseline E1-04/04R and E2-02/04); it retries every 15 min for up to 6 h, then stops.
# Stops at the first trial that does not complete cleanly: replacements (--suffix R) are a researcher decision.
# Usage: run_counted_thesis_clio.sh [--from e1:1|e2:1|e3:1]     (never edit this file while it runs)
source "$(dirname "${BASH_SOURCE[0]}")/lib/clio_common.sh"
from="e1:1"; [[ "${1:-}" == --from ]] && from=${2:?}
LOGF="$RESEARCHER_ONLY/batch_logs/clio_counted_$(date -u +%Y%m%dT%H%M%SZ).log"; mkdir -p "$(dirname "$LOGF")"
say(){ echo "[$(utc_now)] $*" | tee -a "$LOGF"; }
E3D="$RUNS_DIR/E3_disparate_storage_example8"; CLI="$(clio_cli_bin)"
fable_ok() {
  local i out
  for i in $(seq 1 24); do
    out=$(cd "$RESEARCHER_ONLY/batch_logs" && timeout 600 srun --account=hochhalter-np --partition=hochhalter-np --qos=hochhalter-np -n1 \
          --mem=2G --time=00:05:00 --job-name=fable-check "$CLI" --print --model claude-fable-5-1 "Reply with the word OK only." 2>&1)
    if echo "$out" | grep -qw OK; then say "fable check: OK"; return 0; fi
    say "fable check failed ($i/24): $(echo "$out" | tr '\n' ' ' | cut -c1-200); retry in 15 min"; sleep 900
  done
  return 1
}
started=0
for exp in e1 e2 e3; do for n in 1 2 3 4 5; do
  [[ $started == 1 || "$exp:$n" == "$from" ]] || continue; started=1
  nn=$(printf %02d $n)
  fable_ok || { say "STOP: Fable unavailable for 6 h before $exp trial $nn"; exit 1; }
  case $exp in
    e1) td="$RUNS_DIR/E1_uninterrupted_example8/clio/trial_$nn"; say "E1 trial $nn: start"
        "$CLIO_AUTOMATION_DIR/run_e1_clio.sh" --trial "$n" --execute-counted >> "$LOGF" 2>&1; rc=$?;;
    e2) td="$RUNS_DIR/E2_interrupted_recovery_example16/clio/trial_$nn"; say "E2 trial $nn: start"
        "$CLIO_AUTOMATION_DIR/run_e2_clio.sh" --trial "$n" --execute-counted >> "$LOGF" 2>&1; rc=$?;;
    e3) td="$E3D/clio/trial_$nn"; say "E3 trial $nn: start"
        sbatch --wait --account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00 \
          --job-name="e3-clio-trial_$nn" --output="$RESEARCHER_ONLY/batch_logs/e3_clio_trial_${nn}_%j.out" \
          --wrap "$E3D/automation/clio/run_clio_e3_trial_v2.sh --trial-dir $td --execute-counted" >> "$LOGF" 2>&1; rc=$?;;
  esac
  st=$(grep -E '^(status|e3dc_status):' "$td/manifest.yaml" | tail -1)
  say "$exp trial $nn: runner rc=$rc, manifest $st"
  if [[ $exp == e3 ]]; then
    [[ $rc == 0 && "$st" == *awaiting_scoring* ]] || { say "STOP: E3 trial $nn did not complete cleanly"; exit 1; }
    "$CLIO_AUTOMATION_DIR/score_e3_clio.sh" --trial-dir "$td" >> "$LOGF" 2>&1; say "E3 trial $nn scored rc=$?"
  else
    [[ $rc == 0 && "$st" == *completed_unscored* ]] || { say "STOP: $exp trial $nn did not complete cleanly (decide under the replacement policy)"; exit 1; }
    "$AUTOMATION_DIR/score_researcher_only.sh" --trial-dir "$td" --figures >> "$LOGF" 2>&1; say "$exp trial $nn scored rc=$?"
  fi
done; done
say "all counted CLIO trials done"; touch "$RESEARCHER_ONLY/batch_logs/clio_counted.done"
