#!/bin/bash
#SBATCH --job-name=ex8_morphorm_E1-example8-baseline-02
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_02/logs/slurm-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_02/logs/slurm-%j.err
# Frozen workflow EX8 (FROZEN-EX8-v1), trial E1-example8-baseline-02
# 50-iteration OC topology optimization of the half cantilever with a Helmholtz symmetry-plane filter.
set -u
RUN_DIR="/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_02/work/run1"
echo "=== job ${SLURM_JOB_ID} start UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ) on $(hostname) ==="
echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST} SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK} SLURM_MEM_PER_NODE=${SLURM_MEM_PER_NODE:-}"
# Approved software interface (software_contract.md)
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "source approved software rc=$?"
echo "=== module list ==="
module list 2>&1
echo "=== executables ==="
which PlatoMain analyze_MPMD mpiexec XMLGenerator
cd "$RUN_DIR" || { echo "cannot cd to $RUN_DIR"; exit 2; }
echo "=== run directory $PWD ==="
sha256sum input_deck.i mesh.exo interface.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml engine_input_deck.xml engine_operations.xml mpirun.source
echo "=== mpirun.source ==="
cat mpirun.source
export OMP_NUM_THREADS=1
echo "=== morphorm start UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
bash mpirun.source > morphorm_run.log 2>&1
RC=$?
echo "=== morphorm end UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ) rc=$RC ==="
echo "=== run directory listing ==="
ls -la
ls -la analyze_id_2_output* 2>/dev/null | tail -5
echo "=== optimizer diagnostics tail ==="
tail -n 8 morphorm_oc_optimizer_diagnostics.txt 2>/dev/null
echo "=== job end UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
exit $RC
