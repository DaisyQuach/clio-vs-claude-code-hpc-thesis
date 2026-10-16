#!/bin/bash
#SBATCH --job-name=ex8_morphorm_oc50
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_01/logs/slurm-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_01/logs/slurm-%j.err

# Frozen workflow EX8 (FROZEN-EX8-v1): 50-iteration OC topology optimization, Morphorm approved runtime
set -u
RUN_DIR=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_01/work/run2
echo "JOB_START_UTC $(date -u -Is) jobid=${SLURM_JOB_ID} node=$(hostname)"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "=== module list"
module list 2>&1
echo "=== executables"
which PlatoMain analyze_MPMD mpiexec XMLGenerator
cd "$RUN_DIR" || exit 2
echo "=== run dir $RUN_DIR"
ls -la
echo "=== mpirun.source"
cat mpirun.source
echo "MORPHORM_START_UTC $(date -u -Is)"
bash mpirun.source > morphorm_run.log 2>&1
rc=$?
echo "MORPHORM_END_UTC $(date -u -Is) exit=$rc"
echo "=== run dir after run"
ls -la
ls -la analyze_id_2_output* 2>/dev/null | tail -5
echo "JOB_END_UTC $(date -u -Is) exit=$rc"
exit $rc
