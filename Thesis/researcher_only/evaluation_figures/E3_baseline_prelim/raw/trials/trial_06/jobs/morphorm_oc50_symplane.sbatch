#!/bin/bash
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --job-name=e3_t06_symplane_oc50
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_06/logs/slurm-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_06/logs/slurm-%j.err
#SBATCH --chdir=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_06/work/run
# E3-baseline-trial_06 / E3-SPC-v1: 50-iteration OC optimization of the symmetry-plane cantilever.
# Reads only this trial's work/run/ (mesh + XMLGenerator output verified before submission) and the approved software interface.
set -u
echo "job_start_utc $(date -u +%FT%TZ) job_id=${SLURM_JOB_ID} host=$(hostname) cwd=$(pwd) trial=E3-baseline-trial_06"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh || { echo "loader failed"; exit 97; }
echo "--- module list"; module list 2>&1
echo "MORPHORM_RUNTIME=${MORPHORM_RUNTIME:-} CUBIT_ROOT=${CUBIT_ROOT:-}"
echo "--- inputs"; sha256sum input_deck.i mesh.exo interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "--- mpirun.source"; cat mpirun.source
echo "morphorm_start_utc $(date -u +%FT%TZ)"
bash mpirun.source > morphorm_run.log 2>&1
rc=$?
echo "morphorm_end_utc $(date -u +%FT%TZ) morphorm_exit=$rc"
echo "--- run directory after run"; ls -la; ls -la analyze_id_2_output 2>/dev/null | tail -5
echo "--- optimizer diagnostics (tail)"; tail -n 5 *diagnostics*.txt 2>/dev/null
echo "job_end_utc $(date -u +%FT%TZ)"
exit $rc
