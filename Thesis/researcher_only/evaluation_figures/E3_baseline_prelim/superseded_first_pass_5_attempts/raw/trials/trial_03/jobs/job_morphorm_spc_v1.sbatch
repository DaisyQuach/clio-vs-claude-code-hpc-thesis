#!/bin/bash
#SBATCH --job-name=e3_spc_v1_oc50
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_03/logs/slurm-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_03/logs/slurm-%j.err
# E3-baseline-trial_03 -- E3-SPC-v1 Symmetry-Plane Cantilever, one uninterrupted 50-iteration OC optimization.
# Reads only the trial workspace (work/run) and the approved software interface. Resources: frozen compute_resources.md.
set -u
TRIAL_ROOT=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_03
RUN_DIR=$TRIAL_ROOT/work/run
echo "UTC job start: $(date -u +%FT%TZ)  host: $(hostname -s)  SLURM_JOB_ID=$SLURM_JOB_ID  E3_TRIAL_ID=${E3_TRIAL_ID:-E3-baseline-trial_03}"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh || { echo "loader failed"; exit 2; }
echo "--- module list"; module list 2>&1
echo "--- executables"; which PlatoMain analyze_MPMD mpiexec
cd "$RUN_DIR" || exit 3
echo "--- run directory: $PWD"; ls -l
echo "--- sha256 of inputs"; sha256sum input_deck.i mesh.exo interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "--- mpirun.source"; cat mpirun.source
export OMP_NUM_THREADS=1
echo "UTC morphorm start: $(date -u +%FT%TZ)"
bash mpirun.source > morphorm_run.log 2>&1
rc=$?
echo "UTC morphorm end: $(date -u +%FT%TZ)  exit=$rc"
echo "--- run directory after run"; ls -l; ls -l analyze_id_2_output* 2>/dev/null | tail -5
echo "--- optimizer diagnostics tail"; tail -n 5 morphorm_oc_optimizer_diagnostics.txt 2>/dev/null
echo "UTC job end: $(date -u +%FT%TZ)"
exit $rc
