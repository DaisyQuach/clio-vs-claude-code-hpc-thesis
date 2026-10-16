#!/bin/bash -l
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --export=NONE
#SBATCH --job-name=e3-baseline-postprocess-r1
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/setup/baseline_execution/postprocess_r1/out/postprocess-r1-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/setup/baseline_execution/postprocess_r1/out/postprocess-r1-%j.err
# E3 baseline researcher-side postprocessing r1 (non-agent): all six attempts (trial_06 = 02R). Submitted afterany on the 02R job.
# Runs no Claude, CLIO, Morphorm or Cubit. Reads trials read-only; writes only Thesis/researcher_only/evaluation_figures/E3_baseline_prelim[_<UTC>]/
# and its own Slurm logs. Ground-truth/reference material is read researcher-side only and never written to agent-visible storage.
set -u -o pipefail
E3=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8
PP=$E3/setup/baseline_execution/postprocess_r1
OUT=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/evaluation_figures/E3_baseline_prelim   # with E1/E2 results (researcher request 2026-10-10)
PY=$HOME/miniconda3/bin/python3; PV=/uufs/chpc.utah.edu/sys/installdir/paraview/6.0.1-py312/bin/pvbatch
utc() { date -u +%FT%TZ; }
[[ -e "$OUT" ]] && OUT=${OUT}_$(date -u +%Y%m%dT%H%M%SZ)   # never overwrite an earlier postprocessing output
mkdir -p "$OUT/analysis" "$OUT/renders"; chmod 700 "$OUT"
echo "postprocess start $(utc) host $(hostname -s) job $SLURM_JOB_ID out=$OUT"
cp -p "$PP"/{collect_raw.sh,build_dataset.py,make_figures.py,render_topology.py,e3_baseline_postprocess.sbatch} "$OUT/analysis/"
rc=0
bash "$PP/collect_raw.sh" "$OUT" "$E3/setup/baseline_execution/submission_manifest_all_attempts.tsv" || { echo "collect_raw rc=$?"; rc=1; }
"$PY" -I "$PP/build_dataset.py" --e3-root "$E3" --raw "$OUT/raw" --out "$OUT" || { echo "build_dataset failed"; rc=1; }
ref=$(ls /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/ground_truth/example_8/reference_case/run_symmetry_honored_variant/analyze_id_2_output_scenario_id_1/iteration50.exo 2>/dev/null)
[[ -n "$ref" ]] && "$PV" "$PP/render_topology.py" "$ref" "$OUT/renders/E3_reference.png" 2>&1 | tail -1
for n in 01 02 03 04 05 06; do
  st=$(jq -r '.terminal_state // empty' "$E3/baseline/trial_$n/TRIAL_STATUS.json" 2>/dev/null)
  f="$E3/baseline/trial_$n/outputs/final_analyze_output.exo"
  if [[ "$st" == valid && -f "$f" ]]; then "$PV" "$PP/render_topology.py" "$f" "$OUT/renders/E3_$n.png" 2>&1 | tail -1
  else echo "trial_$n: no render (terminal_state='${st:-none}', final_analyze_output.exo $( [[ -f $f ]] && echo present || echo absent))"; fi
done
"$PY" "$PP/make_figures.py" --out "$OUT" || { echo "make_figures failed"; rc=1; }
(cd "$OUT" && find . -type f ! -name SHA256SUMS.txt -print0 | sort -z | xargs -0 sha256sum) > "$OUT/SHA256SUMS.txt"
echo "postprocess end $(utc) rc=$rc"
exit $rc
