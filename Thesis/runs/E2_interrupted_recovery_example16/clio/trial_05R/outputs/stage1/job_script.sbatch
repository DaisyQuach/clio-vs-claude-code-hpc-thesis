#!/bin/bash
#SBATCH --job-name=ex16_stage1
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_05R/logs/stage1_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_05R/logs/stage1_%j.err
# Frozen workflow EX16 (FROZEN-EX16-v1), Stage 1: OC, max_iterations 20, fresh start from uniform density 0.15
set -u
RUN_DIR=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_05R/work/stage1/run
echo "STAGE1 job ${SLURM_JOB_ID} start_utc=$(date -u +%FT%TZ) host=$(hostname)"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "--- module list ---"
module list 2>&1
echo "--- which ---"
which PlatoMain analyze_MPMD mpiexec
cd "${RUN_DIR}" || { echo "cannot cd to ${RUN_DIR}"; exit 2; }
echo "run_dir=$(pwd)"
sha256sum mesh.exo input_deck.i interface.xml engine_operations.xml engine_input_deck.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "morphorm_start_utc=$(date -u +%FT%TZ)"
bash mpirun.source > morphorm_stage1.log 2>&1
RC=$?
echo "morphorm_end_utc=$(date -u +%FT%TZ) morphorm_exit=${RC}"
ls -la
echo "STAGE1 job ${SLURM_JOB_ID} end_utc=$(date -u +%FT%TZ)"
exit ${RC}
