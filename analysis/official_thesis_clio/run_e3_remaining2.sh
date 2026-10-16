#!/usr/bin/env bash
# Finish the counted CLIO E3 arm (2026-10-13): trial_01 aborted before launch -> trial_06; trial_02 excluded (researcher
# edit during the run) -> trial_07. Runs the unchanged counted driver from e3:3 (trials 03-05), then trial_06 and trial_07
# with the driver's exact E3 commands (sbatch + v2 runner, then score_e3_clio.sh). Never edit this file while it runs.
set -uo pipefail
TH=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis; RO=$TH/researcher_only; A=$TH/automation/clio
E3D=$TH/runs/E3_disparate_storage_example8
LOGF=$RO/batch_logs/clio_e3_replacements_06_07_$(date -u +%Y%m%dT%H%M%SZ).log
say(){ echo "[$(date -u +%FT%TZ)] $*" | tee -a "$LOGF"; }
"$A/run_counted_thesis_clio.sh" --from e3:3 || { say "STOP: counted driver stopped before trial_06 (see its clio_counted_*.log)"; exit 1; }
CLI=$HOME/.local/share/claude/versions/2.1.295
for nn in 06 07; do
  for i in $(seq 1 24); do
    out=$(cd $RO/batch_logs && timeout 600 srun --account=hochhalter-np --partition=hochhalter-np --qos=hochhalter-np -n1 --mem=2G --time=00:05:00 --job-name=fable-check "$CLI" --print --model claude-fable-5-1 "Reply with the word OK only." 2>&1)
    echo "$out" | grep -qw OK && { say "fable check: OK"; break; }; say "fable check failed ($i/24); retry in 15 min"; sleep 900
    [[ $i == 24 ]] && { say "STOP: Fable unavailable"; exit 1; }
  done
  td="$E3D/clio/trial_$nn"; say "E3 trial $nn: start"
  sbatch --wait --account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00 \
    --job-name="e3-clio-trial_$nn" --output="$RO/batch_logs/e3_clio_trial_${nn}_%j.out" \
    --wrap "$E3D/automation/clio/run_clio_e3_trial_v2.sh --trial-dir $td --execute-counted" >> "$LOGF" 2>&1; rc=$?
  st=$(grep -E '^e3dc_status:' "$td/manifest.yaml" | tail -1); say "e3 trial $nn: runner rc=$rc, manifest $st"
  [[ $rc == 0 && "$st" == *awaiting_scoring* ]] || { say "STOP: E3 trial $nn did not complete cleanly"; exit 1; }
  "$A/score_e3_clio.sh" --trial-dir "$td" >> "$LOGF" 2>&1; say "E3 trial $nn scored rc=$?"
done
say "all counted CLIO E3 trials done"; touch "$RO/batch_logs/clio_e3_all.done"
