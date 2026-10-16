#!/bin/bash
#SBATCH --job-name=ex8_morphorm
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_03/logs/morphorm_ex8_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_03/logs/morphorm_ex8_%j.err
# FROZEN-EX8-v1 50-iteration Morphorm OC run; run directory work/run2
set -o pipefail
echo "JOB_START_UTC $(date -u +%FT%TZ) jobid=$SLURM_JOB_ID node=$SLURMD_NODENAME"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "=== module list"
module list 2>&1
echo "=== which"
which PlatoMain analyze_MPMD mpiexec
cd /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_03/work/run2 || exit 2
echo "=== run dir $PWD"
ls -la
echo "MORPHORM_START_UTC $(date -u +%FT%TZ)"
bash mpirun.source 2>&1 | tee morphorm_run.log
RC=${PIPESTATUS[0]}
echo "MORPHORM_END_UTC $(date -u +%FT%TZ) rc=$RC"
ls -la
echo "JOB_END_UTC $(date -u +%FT%TZ)"
exit $RC
