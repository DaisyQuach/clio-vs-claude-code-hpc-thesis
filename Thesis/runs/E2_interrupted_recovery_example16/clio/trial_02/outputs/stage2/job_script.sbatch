#!/bin/bash
#SBATCH --job-name=ex16_stage2
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_02/logs/stage2_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_02/logs/stage2_%j.err
# Frozen workflow EX16 -- Stage 2 Morphorm run (continuation from Stage-1 checkpoint restart_input.exo, 40 further iterations)
set -u
RUN_DIR=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_02/work/stage2_run
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh || { echo "software load failed"; exit 2; }
cd "$RUN_DIR" || exit 3
echo "JOB $SLURM_JOB_ID start $(date -Is) host $(hostname)"
module list 2>&1
echo "PATH check: $(which PlatoMain) $(which analyze_MPMD) $(which mpiexec)"
sha256sum mesh.exo restart_input.exo input_deck.i interface.xml engine_operations.xml engine_input_deck.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
bash mpirun.source > morphorm_stage2.log 2>&1
RC=$?
echo "mpirun.source exit code $RC"
echo "JOB $SLURM_JOB_ID end $(date -Is)"
ls -la
exit $RC
