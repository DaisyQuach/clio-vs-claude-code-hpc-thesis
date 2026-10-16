#!/bin/bash
#SBATCH --job-name=ex16_stage2
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_03/logs/stage2_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_03/logs/stage2_%j.err

# EX16 Stage 2 (continuation, max_iterations 40, restart from Stage-1 iteration-20 control field) - Morphorm OC topology optimization
set -u
TRIAL_ROOT=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_03
RUN_DIR="$TRIAL_ROOT/work/stage2"

echo "START_UTC $(date -u -Is)"
echo "JOB_ID ${SLURM_JOB_ID:-unknown} NODE $(hostname)"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "=== module list ==="
module list 2>&1
echo "=== which ==="
which PlatoMain analyze_MPMD mpiexec XMLGenerator 2>&1

cd "$RUN_DIR" || { echo "cannot cd to $RUN_DIR"; exit 2; }
echo "RUN_DIR $RUN_DIR"
sha256sum input_deck.i mesh.exo restart_input.exo interface.xml engine_operations.xml engine_input_deck.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "=== mpirun.source ==="
cat mpirun.source
echo "=== launch $(date -u -Is) ==="
bash mpirun.source > morphorm_stage2.log 2>&1
RC=$?
echo "MORPHORM_EXIT $RC"
echo "=== run dir listing ==="
ls -la
echo "END_UTC $(date -u -Is)"
exit $RC
