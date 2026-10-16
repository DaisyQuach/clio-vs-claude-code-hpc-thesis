#!/bin/bash
#SBATCH --job-name=ex16_stage2
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_01/logs/stage2_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_01/logs/stage2_%j.err
# FROZEN-EX16-v1 Stage 2 continuation (max_iterations 40, restart from Stage-1 iteration-20 control field) -- trial E2-example16-clio-01
set -u
echo "JOB_START_UTC $(date -u +%FT%TZ) jobid=${SLURM_JOB_ID} node=$(hostname)"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "=== module list ==="
module list 2>&1
echo "=================="
cd /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_01/work/stage2/run || exit 2
export OMP_NUM_THREADS=1
echo "RUN_DIR $PWD"
echo "RESTART_INPUT_SHA256 $(sha256sum restart_input.exo)"
echo "MORPHORM_START_UTC $(date -u +%FT%TZ)"
bash mpirun.source > morphorm_stage2.log 2>&1
rc=$?
echo "MORPHORM_END_UTC $(date -u +%FT%TZ) rc=$rc"
echo "JOB_END_UTC $(date -u +%FT%TZ)"
exit $rc
