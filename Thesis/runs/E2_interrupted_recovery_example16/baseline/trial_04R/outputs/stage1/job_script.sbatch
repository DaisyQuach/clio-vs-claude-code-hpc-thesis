#!/bin/bash
#SBATCH --job-name=ex16_stage1
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_04R/logs/stage1_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_04R/logs/stage1_%j.err
# Frozen workflow EX16 (FROZEN-EX16-v1), trial E2-example16-baseline-04R -- Stage 1 (max_iterations 20)
set -u
RUNDIR=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_04R/work/stage1/run
echo "=== Stage 1 job ${SLURM_JOB_ID:-unknown} on $(hostname) ==="
echo "job start (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ)"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh || { echo "FAILED to source approved software interface"; exit 97; }
echo "--- module list ---"
module list 2>&1
echo "--- executables ---"
which PlatoMain analyze_MPMD mpiexec XMLGenerator
cd "$RUNDIR" || { echo "FAILED to cd to $RUNDIR"; exit 98; }
echo "run directory: $(pwd)"
echo "--- sha256 of configuration used by this job ---"
sha256sum input_deck.i mesh.exo interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "--- mpirun.source ---"
cat mpirun.source
export OMP_NUM_THREADS=1
echo "morphorm start (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ)"
bash mpirun.source > morphorm_stage1.log 2>&1
RC=$?
echo "morphorm end (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "mpirun.source exit code: $RC"
echo "--- run directory listing ---"
ls -la
echo "--- tail of optimizer diagnostics ---"
tail -n 30 morphorm_oc_optimizer_diagnostics.txt 2>/dev/null || echo "(no diagnostics file)"
echo "job end (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit $RC
