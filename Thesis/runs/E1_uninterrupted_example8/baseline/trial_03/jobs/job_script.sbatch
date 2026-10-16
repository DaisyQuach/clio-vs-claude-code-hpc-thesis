#!/bin/bash
#SBATCH --job-name=ex8_E1-example8-baseline-03
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --chdir=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_03/work/run2
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_03/logs/slurm-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_03/logs/slurm-%j.err

# FROZEN-EX8-v1 / trial E1-example8-baseline-03: 50-iteration Morphorm topology optimization (attempt run2)
echo "JOB_START_UTC $(date -u +%FT%TZ)"
echo "SLURM_JOB_ID=$SLURM_JOB_ID  NODE=$(hostname)  CPUS=$SLURM_CPUS_PER_TASK  MEM=$SLURM_MEM_PER_NODE  WORKDIR=$(pwd)"

# approved software interface (required before any Morphorm executable)
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "--- module list"
module list 2>&1
echo "--- executables"
which PlatoMain analyze_MPMD mpiexec XMLGenerator
echo "--- generated configuration checksums"
sha256sum input_deck.i mesh.exo interface.xml *_input_deck.xml *_operations.xml mpirun.source

echo "MORPHORM_START_UTC $(date -u +%FT%TZ)"
bash mpirun.source > morphorm_run.log 2>&1
RC=$?
echo "MORPHORM_END_UTC $(date -u +%FT%TZ)  exit=$RC"
echo "--- run directory after completion"
ls -la
ls -la analyze_id_2_output 2>/dev/null | tail -5
echo "JOB_END_UTC $(date -u +%FT%TZ)"
exit $RC
