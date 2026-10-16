#!/bin/bash
#SBATCH --job-name=ex16_stage2_E2-example16-baseline-03
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_03/logs/stage2_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_03/logs/stage2_%j.err
# FROZEN-EX16-v1 Stage 2 (continuation: max_iterations 40, initial design = iteration-20 'control' field of restart_input.exo = copy of the Stage-1 checkpoint).
# Trial E2-example16-baseline-03. Run directory: work/stage2 (deck translated there by XMLGenerator on the agent host).
set -u
RUNDIR="/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_03/work/stage2"
echo "=== STAGE 2 JOB ${SLURM_JOB_ID} on $(hostname)"
echo "JOB START UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "=== module list"
module list 2>&1
echo "=== executables"
which PlatoMain analyze_MPMD mpiexec XMLGenerator
cd "${RUNDIR}" || { echo "cannot cd to ${RUNDIR}"; exit 2; }
echo "=== run directory: $(pwd)"
echo "=== sha256 of inputs used by this job"
sha256sum input_deck.i mesh.exo restart_input.exo interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "=== mpirun.source"
cat mpirun.source
# single-rank performers: one processor per service (number_processors 1), so one thread per process
export OMP_NUM_THREADS=1
export OMP_PROC_BIND=false
echo "OMP_NUM_THREADS=${OMP_NUM_THREADS}"
echo "MORPHORM START UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
bash mpirun.source > morphorm_stage2.log 2>&1
RC=$?
echo "MORPHORM END UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "MORPHORM EXIT CODE: ${RC}"
echo "=== run directory listing"
ls -la
echo "=== optimizer diagnostics (tail)"
tail -n 30 morphorm_oc_optimizer_diagnostics.txt 2>/dev/null || echo "(no diagnostics file)"
echo "JOB END UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit ${RC}
