#!/bin/bash
#SBATCH --job-name=ex16_stage1
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_04/logs/stage1_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_04/logs/stage1_%j.err
# FROZEN-EX16-v1 Stage 1 (max_iterations 20, write_restart_file true)
set -u
TRIAL_ROOT=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_04
RUN_DIR=$TRIAL_ROOT/work/stage1/run
echo "JOB_ID=$SLURM_JOB_ID NODE=$(hostname) START_UTC=$(date -u +%FT%TZ)"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "=== module list ==="
module list 2>&1
echo "=== which ==="
which PlatoMain analyze_MPMD mpiexec XMLGenerator
cd "$RUN_DIR" || exit 2
echo "RUN_DIR=$PWD"
sha256sum input_deck.i mesh.exo interface.xml engine_operations.xml engine_input_deck.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "=== bash mpirun.source START_UTC=$(date -u +%FT%TZ) ==="
bash mpirun.source > morphorm_stage1.log 2>&1
RC=$?
echo "=== mpirun.source exit code $RC END_UTC=$(date -u +%FT%TZ) ==="
ls -la
exit $RC
