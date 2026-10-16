#!/bin/bash
#SBATCH --job-name=ex8_morphorm
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_05/logs/morphorm_ex8_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_05/logs/morphorm_ex8_%j.err
set -u
echo "JOB_START_UTC=$(date -u +%FT%TZ) JOBID=$SLURM_JOB_ID NODE=$(hostname)"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "=== module list ==="
module list 2>&1
echo "=== end module list ==="
cd /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_05/work/run2 || exit 2
echo "RUN_DIR=$PWD"
sha256sum input_deck.i mesh.exo interface.xml analyze_2_input_deck.xml analyze_helmholtz_input_deck.xml engine_input_deck.xml mpirun.source
echo "MORPHORM_START_UTC=$(date -u +%FT%TZ)"
bash mpirun.source > morphorm_run.log 2>&1
rc=$?
echo "MORPHORM_END_UTC=$(date -u +%FT%TZ) MORPHORM_RC=$rc"
echo "JOB_END_UTC=$(date -u +%FT%TZ)"
exit $rc
