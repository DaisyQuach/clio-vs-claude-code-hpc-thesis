#!/usr/bin/env bash
# Finish the counted CLIO E3 arm after trial_01 was aborted before launch (2026-10-13): run the unchanged counted driver
# from e3:2 (trials 02-05), then the replacement clio/trial_06 with the driver's exact E3 commands (sbatch + v2 runner,
# then score_e3_clio.sh). Never edit this file while it runs.
set -uo pipefail
TH=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis; RO=$TH/researcher_only; A=$TH/automation/clio
E3D=$TH/runs/E3_disparate_storage_example8
LOGF=$RO/batch_logs/clio_e3_replacement_06_$(date -u +%Y%m%dT%H%M%SZ).log
say(){ echo "[$(date -u +%FT%TZ)] $*" | tee -a "$LOGF"; }
"$A/run_counted_thesis_clio.sh" --from e3:2 || { say "STOP: counted driver stopped before trial_06 (see its clio_counted_*.log)"; exit 1; }
CLI=$HOME/.local/share/claude/versions/2.1.295
for i in $(seq 1 24); do
  out=$(cd $RO/batch_logs && timeout 600 srun --account=hochhalter-np --partition=hochhalter-np --qos=hochhalter-np -n1 --mem=2G --time=00:05:00 --job-name=fable-check "$CLI" --print --model claude-fable-5-1 "Reply with the word OK only." 2>&1)
  echo "$out" | grep -qw OK && { say "fable check: OK"; break; }; say "fable check failed ($i/24); retry in 15 min"; sleep 900
  [[ $i == 24 ]] && { say "STOP: Fable unavailable"; exit 1; }
done
td="$E3D/clio/trial_06"; say "E3 trial 06 (replaces aborted trial_01): start"
sbatch --wait --account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00 \
  --job-name="e3-clio-trial_06" --output="$RO/batch_logs/e3_clio_trial_06_%j.out" \
  --wrap "$E3D/automation/clio/run_clio_e3_trial_v2.sh --trial-dir $td --execute-counted" >> "$LOGF" 2>&1; rc=$?
st=$(grep -E '^e3dc_status:' "$td/manifest.yaml" | tail -1); say "e3 trial 06: runner rc=$rc, manifest $st"
[[ $rc == 0 && "$st" == *awaiting_scoring* ]] || { say "STOP: E3 trial 06 did not complete cleanly"; exit 1; }
"$A/score_e3_clio.sh" --trial-dir "$td" >> "$LOGF" 2>&1; say "E3 trial 06 scored rc=$?"
say "all counted CLIO E3 trials done"; touch "$RO/batch_logs/clio_e3_all.done"
