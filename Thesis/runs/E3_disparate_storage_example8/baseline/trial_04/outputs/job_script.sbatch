#!/usr/bin/env bash
#SBATCH --job-name=e3_spc_v1_symcant
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_04/logs/slurm-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_04/logs/slurm-%j.err
# E3-baseline-trial_04 — E3-SPC-v1 Symmetry-Plane Cantilever, 50-iteration OC optimization (Morphorm, approved runtime).
# Reads only the trial workspace and the approved software interface.
set -o pipefail
TRIAL_ROOT=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_04
RUN_DIR="$TRIAL_ROOT/work/run"
echo "utc_job_start: $(date -u +%FT%TZ)"
echo "host: $(hostname) slurm_job_id: $SLURM_JOB_ID nodelist: $SLURM_JOB_NODELIST cpus: $SLURM_CPUS_PER_TASK mem: $SLURM_MEM_PER_NODE"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh || { echo "approved software interface failed to load"; exit 2; }
echo "--- module list"; module list 2>&1
echo "--- executables"; which PlatoMain analyze_MPMD mpiexec
cd "$RUN_DIR" || exit 3
echo "run_dir: $PWD"; echo "--- input hashes"; sha256sum input_deck.i mesh.exo interface.xml *_input_deck.xml *_operations.xml mpirun.source
export OMP_NUM_THREADS=1
echo "utc_morphorm_start: $(date -u +%FT%TZ)"
bash mpirun.source > morphorm_run.log 2>&1
rc=$?
echo "utc_morphorm_end: $(date -u +%FT%TZ) morphorm_exit_code: $rc"
echo "--- run directory listing"; ls -la; ls -la analyze_id_2_output 2>/dev/null | tail -n 5
echo "--- optimizer diagnostics tail"; tail -n 15 morphorm_oc_optimizer_diagnostics.txt 2>/dev/null
echo "--- morphorm_run.log tail"; tail -n 30 morphorm_run.log
echo "utc_job_end: $(date -u +%FT%TZ)"
exit $rc
