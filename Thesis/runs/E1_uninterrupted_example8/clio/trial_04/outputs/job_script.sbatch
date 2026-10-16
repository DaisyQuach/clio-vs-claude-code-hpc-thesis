#!/bin/bash
#SBATCH --job-name=ex8_morphorm
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_04/logs/morphorm_ex8_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_04/logs/morphorm_ex8_%j.err
# Frozen workflow EX8 (FROZEN-EX8-v1): 50-iteration Morphorm OC topology optimization
set -u
echo "JOB $SLURM_JOB_ID start $(date -u +%FT%TZ) node $(hostname)"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "=== module list ==="
module list 2>&1
echo "=== which PlatoMain analyze_MPMD mpiexec ==="
which PlatoMain analyze_MPMD mpiexec
cd /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_04/work/run2 || exit 2
echo "RUN_DIR $PWD"
sha256sum input_deck.i mesh.exo interface.xml mpirun.source *_input_deck.xml *_operations.xml
echo "MORPHORM_START $(date -u +%FT%TZ)"
bash mpirun.source > morphorm_run.log 2>&1
RC=$?
echo "MORPHORM_END $(date -u +%FT%TZ) exit $RC"
ls -la
exit $RC
