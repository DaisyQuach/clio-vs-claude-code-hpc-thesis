#!/bin/bash
#SBATCH --job-name=ex16_stage2
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_05/logs/stage2_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_05/logs/stage2_%j.err
# FROZEN-EX16-v1 -- Stage 2 (continuation: max_iterations 40, restart from the Stage-1 checkpoint copy restart_input.exo,
# field control) ; trial E2-example16-baseline-05
set -u
echo "STAGE2_JOB_START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "SLURM_JOB_ID=$SLURM_JOB_ID NODE=$(hostname) CPUS=$SLURM_CPUS_PER_TASK MEM=$SLURM_MEM_PER_NODE"
# approved software interface (required before any Morphorm executable)
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "=== module list"; module list 2>&1
echo "=== executables"; which PlatoMain analyze_MPMD mpiexec XMLGenerator
RUN_DIR=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_05/work/stage2/run
cd "$RUN_DIR" || { echo "cannot cd to $RUN_DIR"; exit 2; }
echo "=== run dir: $RUN_DIR"; ls -la
echo "=== sha256 of inputs"; sha256sum input_deck.i mesh.exo restart_input.exo interface.xml *_input_deck.xml *_operations.xml mpirun.source
echo "=== restart settings in engine_operations.xml"; grep -A6 "<Function>InitializeField" engine_operations.xml
echo "=== mpirun.source"; cat mpirun.source
export OMP_NUM_THREADS=1
echo "MORPHORM_START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
bash mpirun.source > morphorm_stage2.log 2>&1
RC=$?
echo "MORPHORM_END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "MORPHORM_EXIT_CODE=$RC"
echo "=== run dir after"; ls -la; ls -la analyze_id_2_output_scenario_id_1 2>/dev/null | tail -5
echo "=== optimizer diagnostics"; cat morphorm_oc_optimizer_diagnostics.txt 2>/dev/null
echo "=== tail of morphorm log"; tail -40 morphorm_stage2.log
echo "STAGE2_JOB_END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit $RC
