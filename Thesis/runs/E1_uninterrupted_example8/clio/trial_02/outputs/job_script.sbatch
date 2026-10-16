#!/bin/bash
#SBATCH --job-name=ex8_clio02
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_02/logs/slurm-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_02/logs/slurm-%j.err
# FROZEN-EX8-v1 accepted run: Morphorm OC topology optimization, 50 iterations
set -u
RUN_DIR=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_02/work/run_legacy
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
cd "$RUN_DIR" || exit 1
echo "job=$SLURM_JOB_ID node=$(hostname) start=$(date -Is) cwd=$PWD"
bash mpirun.source > morphorm_run.log 2>&1
rc=$?
echo "mpirun.source exit=$rc end=$(date -Is)"
exit $rc
