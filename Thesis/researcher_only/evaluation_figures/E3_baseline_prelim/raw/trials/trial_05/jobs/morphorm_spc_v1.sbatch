#!/usr/bin/env bash
#SBATCH --job-name=e3spc_trial05
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_05/logs/slurm-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_05/logs/slurm-%j.err
# E3-baseline-trial_05 / E3-SPC-v1 Symmetry-Plane Cantilever: one uninterrupted 50-iteration OC optimization.
# Reads only the trial workspace run directory and the approved software interface.
set -u
RUN_DIR="/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_05/work/run"
echo "job_start_utc=$(date -u +%FT%TZ) host=$(hostname -s) SLURM_JOB_ID=${SLURM_JOB_ID:-} trial=${E3_TRIAL_ID:-E3-baseline-trial_05}"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh || { echo "loader failed"; exit 2; }
echo "--- module list"; module list 2>&1
echo "--- executables"; which PlatoMain analyze_MPMD mpiexec
cd "$RUN_DIR" || exit 3
echo "--- run directory: $PWD"; ls -la
echo "--- sha256 of inputs"; sha256sum input_deck.i mesh.exo interface.xml *_input_deck.xml *_operations.xml mpirun.source
echo "morphorm_start_utc=$(date -u +%FT%TZ)"
bash mpirun.source > morphorm_run.log 2>&1
RC=$?
echo "morphorm_end_utc=$(date -u +%FT%TZ) rc=$RC"
echo "--- run directory after"; ls -la; ls analyze_id_2_output 2>/dev/null | tail -3
echo "--- diagnostics tail"; tail -5 morphorm_oc_optimizer_diagnostics.txt 2>/dev/null
echo "job_end_utc=$(date -u +%FT%TZ)"
exit $RC
