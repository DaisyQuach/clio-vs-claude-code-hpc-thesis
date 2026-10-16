#!/bin/bash
#SBATCH --job-name=ex16_stage1
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_01/logs/stage1_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_01/logs/stage1_%j.err
# FROZEN-EX16-v1 -- Stage 1 (max_iterations 20, fresh start) -- trial E2-example16-baseline-01
set -u
RUN_DIR="/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_01/work/stage1/run"
echo "=== Stage 1 job ${SLURM_JOB_ID} on $(hostname)"
echo "=== UTC job start: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=== approved software interface"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "=== module list"
module list 2>&1
echo "=== executables"
which PlatoMain analyze_MPMD mpiexec XMLGenerator
echo "=== run directory: ${RUN_DIR}"
cd "${RUN_DIR}" || exit 2
echo "=== SHA-256 of inputs used by this job"
sha256sum input_deck.i mesh.exo interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "=== mpirun.source"
cat mpirun.source
echo "=== UTC Morphorm start: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
bash mpirun.source > morphorm_stage1.log 2>&1
RC=$?
echo "=== UTC Morphorm end: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=== mpirun.source exit code: ${RC}"
echo "=== run directory listing"
ls -la
ls -la analyze_id_2_output* 2>/dev/null | tail -n 30
echo "=== optimizer diagnostics"
cat morphorm_oc_optimizer_diagnostics.txt 2>/dev/null
echo "=== UTC job end: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit ${RC}
