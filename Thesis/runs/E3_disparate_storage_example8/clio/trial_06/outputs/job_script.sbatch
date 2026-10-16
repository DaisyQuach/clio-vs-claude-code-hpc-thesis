#!/bin/bash
#SBATCH --job-name=e3-spc-run02
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_06/logs/slurm-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_06/logs/slurm-%j.err
# E3-SPC-v1 Symmetry-Plane Cantilever: one uninterrupted 50-iteration OC optimization (trial E3-clio-trial_06).
# Reads only the trial workspace and the approved software interface.
set -u
RUN_DIR=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_06/work/run02
echo "UTC start: $(date -u +%FT%TZ)  host: $(hostname)  job: ${SLURM_JOB_ID}"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh || { echo 'approved software interface failed to load'; exit 2; }
module list 2>&1
echo "MORPHORM_RUNTIME=${MORPHORM_RUNTIME}"
which PlatoMain analyze_MPMD mpiexec
cd "$RUN_DIR" || exit 3
sha256sum mesh.exo input_deck.i interface.xml analyze_2_input_deck.xml analyze_helmholtz_input_deck.xml engine_input_deck.xml engine_operations.xml analyze_2_operations.xml analyze_helmholtz_operations.xml mpirun.source
echo "UTC morphorm start: $(date -u +%FT%TZ)"
bash mpirun.source > morphorm_run.log 2>&1
rc=$?
echo "UTC morphorm end: $(date -u +%FT%TZ)  rc=$rc"
ls -la "$RUN_DIR"
exit $rc
