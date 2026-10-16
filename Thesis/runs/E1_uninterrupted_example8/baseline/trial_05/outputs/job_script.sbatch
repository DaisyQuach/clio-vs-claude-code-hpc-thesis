#!/bin/bash
#SBATCH --job-name=ex8_topopt_E1-example8-baseline-05
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_05/logs/ex8_topopt_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_05/logs/ex8_topopt_%j.err
#SBATCH --chdir=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_05/work/run3_accepted
# Frozen workflow EX8 (FROZEN-EX8-v1), trial E1-example8-baseline-05
# 50-iteration OC topology optimization via the approved Morphorm runtime.
set -o pipefail
RUN_DIR=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_05/work/run3_accepted
echo "=== job start UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "SLURM_JOB_ID=$SLURM_JOB_ID  node=$(hostname)  cpus=$SLURM_CPUS_PER_TASK  ntasks=$SLURM_NTASKS"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "approved software interface sourced, rc=$?"
echo "=== module list"
module list 2>&1
echo "=== executables"
which PlatoMain analyze_MPMD mpiexec
cd "$RUN_DIR" || exit 1
echo "=== run dir: $(pwd)"
sha256sum input_deck.i mesh.exo interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "=== morphorm start UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
bash mpirun.source 2>&1 | tee morphorm_run.log
rc=${PIPESTATUS[0]}
echo "=== morphorm end UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)  rc=$rc"
echo "=== run dir listing"
ls -la
ls -la analyze_id_2_output 2>/dev/null | tail -5
echo "=== optimizer diagnostics tail"
tail -5 morphorm_oc_optimizer_diagnostics.txt 2>/dev/null
echo "=== job end UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit $rc
