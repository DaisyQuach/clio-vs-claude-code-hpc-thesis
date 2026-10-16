#!/bin/bash
#SBATCH --job-name=E3-clio-trial_03-spc
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_03/logs/slurm-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_03/logs/slurm-%j.err
# E3-SPC-v1 Symmetry-Plane Cantilever, 50-iteration OC optimization (trial E3-clio-trial_03).
# Reads only the trial workspace (work/run2) and the approved software interface.
set -u
TRIAL_ROOT=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_03
RUN_DIR=$TRIAL_ROOT/work/run2
echo "UTC start: $(date -u +%FT%TZ)  job=$SLURM_JOB_ID  node=$(hostname -s)"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh
echo "--- module list ---"; module list 2>&1
echo "--- run directory $RUN_DIR ---"; ls -l "$RUN_DIR"
cd "$RUN_DIR" || exit 2
sha256sum input_deck.i mesh.exo interface.xml analyze_2_input_deck.xml analyze_helmholtz_input_deck.xml engine_input_deck.xml mpirun.source
echo "--- bash mpirun.source: $(date -u +%FT%TZ) ---"
bash mpirun.source > morphorm_run.log 2>&1
rc=$?
echo "--- mpirun.source exit=$rc at $(date -u +%FT%TZ) ---"
ls -l
tail -5 morphorm_oc_optimizer_diagnostics.txt 2>/dev/null
echo "UTC end: $(date -u +%FT%TZ)"
exit $rc
