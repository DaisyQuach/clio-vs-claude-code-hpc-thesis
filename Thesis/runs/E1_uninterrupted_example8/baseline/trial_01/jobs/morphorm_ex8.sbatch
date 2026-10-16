#!/bin/bash
#SBATCH --job-name=ex8_morphorm
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_01/logs/slurm-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_01/logs/slurm-%j.err
# FROZEN-EX8-v1 optimization job, trial E1-example8-baseline-01
set -o pipefail
RUNDIR=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_01/work/run2
echo "JOB_START_UTC $(date -u +%Y-%m-%dT%H:%M:%SZ) jobid=$SLURM_JOB_ID node=$(hostname) cpus=$SLURM_CPUS_PER_TASK mem=$SLURM_MEM_PER_NODE"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "--- module list ---"; module list 2>&1; echo "-------------------"
echo "which: $(which PlatoMain) $(which analyze_MPMD) $(which mpiexec)"
cd "$RUNDIR" || { echo "cannot cd to $RUNDIR"; exit 2; }
echo "sha256 of inputs used:"; sha256sum input_deck.i mesh.exo interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "MORPHORM_START_UTC $(date -u +%Y-%m-%dT%H:%M:%SZ)"
bash mpirun.source 2>&1 | tee morphorm_run.log
RC=${PIPESTATUS[0]}
echo "MORPHORM_END_UTC $(date -u +%Y-%m-%dT%H:%M:%SZ) mpirun_rc=$RC"
ls -la "$RUNDIR"; ls -la "$RUNDIR"/analyze_id_2_output* 2>/dev/null | tail -5
echo "JOB_END_UTC $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit $RC
