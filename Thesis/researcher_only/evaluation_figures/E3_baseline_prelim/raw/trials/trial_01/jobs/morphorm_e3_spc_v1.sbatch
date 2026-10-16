#!/usr/bin/env bash
#SBATCH --job-name=e3-spc-v1-trial01
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_01/logs/slurm-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_01/logs/slurm-%j.err
# E3-SPC-v1 Symmetry-Plane Cantilever, trial E3-baseline-trial_01: one uninterrupted 50-iteration OC optimization.
# Reads only the trial workspace and the approved software interface (protocol/access_rules.md, staging_rules.md rule 8).
set -u
TRIAL_ROOT=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_01
RUN_DIR="$TRIAL_ROOT/work/run"
echo "utc_job_start: $(date -u +%FT%TZ)"
echo "slurm_job_id: ${SLURM_JOB_ID:-}  node: $(hostname -s)  cpus: ${SLURM_CPUS_PER_TASK:-}  mem: ${SLURM_MEM_PER_NODE:-}"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh || { echo "loader failed"; exit 2; }
echo "---- module list"; module list 2>&1
echo "---- executables"; for c in PlatoMain analyze_MPMD mpiexec XMLGenerator; do printf '%-13s %s\n' "$c" "$(command -v $c)"; done
cd "$RUN_DIR" || { echo "missing run dir"; exit 3; }
echo "---- run directory: $PWD"; sha256sum input_deck.i mesh.exo interface.xml analyze_2_input_deck.xml analyze_helmholtz_input_deck.xml engine_operations.xml engine_input_deck.xml analyze_2_operations.xml analyze_helmholtz_operations.xml mpirun.source
echo "---- mpirun.source"; cat mpirun.source
echo "utc_morphorm_start: $(date -u +%FT%TZ)"
bash mpirun.source > morphorm_run.log 2>&1
rc=$?
echo "utc_morphorm_end: $(date -u +%FT%TZ)"
echo "morphorm_exit_code: $rc"
echo "---- optimizer diagnostics tail"; tail -n 8 morphorm_oc_optimizer_diagnostics.txt 2>/dev/null
echo "---- run directory listing"; ls -la; ls analyze_id_2_output* 2>/dev/null | tail -n 5
echo "utc_job_end: $(date -u +%FT%TZ)"
exit $rc
