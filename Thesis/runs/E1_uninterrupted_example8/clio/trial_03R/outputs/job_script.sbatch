#!/bin/bash
#SBATCH --job-name=ex8_halfcant_oc50
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_03R/logs/morphorm_ex8_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_03R/logs/morphorm_ex8_%j.err
# FROZEN-EX8-v1 (trial $THESIS_TRIAL_ID): 50-iteration OC topology optimization, half cantilever, Helmholtz symmetry-plane filter
set -u
echo "JOB_START_UTC $(date -u +%FT%TZ) jobid=$SLURM_JOB_ID node=$SLURMD_NODENAME trial=E1-example8-clio-03R"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
echo "=== module list ==="
module list 2>&1
echo "=== which ==="
which PlatoMain analyze_MPMD mpiexec XMLGenerator
RUNDIR=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/clio/trial_03R/work/run/attempt2
cd "$RUNDIR" || { echo "cannot cd to $RUNDIR"; exit 2; }
echo "RUNDIR=$RUNDIR"
sha256sum input_deck.i mesh.exo interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "MORPHORM_START_UTC $(date -u +%FT%TZ)"
bash mpirun.source > morphorm_run.log 2>&1
rc=$?
echo "MORPHORM_END_UTC $(date -u +%FT%TZ) exit=$rc"
ls -la
exit $rc
