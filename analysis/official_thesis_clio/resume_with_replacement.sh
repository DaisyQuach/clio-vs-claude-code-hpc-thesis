#!/usr/bin/env bash
# Run one replacement packet (already prepared with prepare_clio_trial.sh --suffix R), score it, then resume the counted
# batch at the next trial. E1/E2 only. Usage: resume_with_replacement.sh e1|e2 N R NEXT   (e.g. e1 3 R e1:4)
set -uo pipefail
exp=$1 n=$2 sfx=$3 next=$4
A=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/automation; RO=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only
LOGF=$RO/batch_logs/clio_replacement_${exp}_$(printf %02d $n)${sfx}_$(date -u +%Y%m%dT%H%M%SZ).log
say(){ echo "[$(date -u +%FT%TZ)] $*" | tee -a "$LOGF"; }
CLI=$HOME/.local/share/claude/versions/2.1.295
for i in $(seq 1 24); do
  out=$(cd $RO/batch_logs && timeout 600 srun --account=hochhalter-np --partition=hochhalter-np --qos=hochhalter-np -n1 --mem=2G --time=00:05:00 --job-name=fable-check "$CLI" --print --model claude-fable-5-1 "Reply with the word OK only." 2>&1)
  echo "$out" | grep -qw OK && { say "fable check: OK"; break; }; say "fable check failed ($i/24); retry in 15 min"; sleep 900
  [[ $i == 24 ]] && { say "STOP: Fable unavailable"; exit 1; }
done
case $exp in e1) d=E1_uninterrupted_example8;; e2) d=E2_interrupted_recovery_example16;; *) echo "e1|e2 only"; exit 2;; esac
td=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/$d/clio/trial_$(printf %02d $n)$sfx
say "$exp trial $(basename $td) (replacement): start"
"$A/clio/run_${exp}_clio.sh" --trial "$n" --suffix "$sfx" --execute-counted >> "$LOGF" 2>&1; rc=$?
st=$(grep -E '^status:' "$td/manifest.yaml"); say "runner rc=$rc, manifest $st"
[[ $rc == 0 && "$st" == *completed_unscored* ]] || { say "STOP: replacement did not complete cleanly"; exit 1; }
"$A/score_researcher_only.sh" --trial-dir "$td" --figures >> "$LOGF" 2>&1; say "scored rc=$?"
say "resuming counted batch --from $next"; exec "$A/clio/run_counted_thesis_clio.sh" --from "$next"
