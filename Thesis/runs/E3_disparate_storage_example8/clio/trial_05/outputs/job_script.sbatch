#!/bin/bash
#SBATCH --job-name=e3-spc-v1-E3-clio-trial_05
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_05/logs/morphorm_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_05/logs/morphorm_%j.err
# E3-SPC-v1 Symmetry-Plane Cantilever, trial E3-clio-trial_05: 50-iteration OC optimization.
# Reads only the trial workspace run directory and the approved software interface.
set -u
RUN_DIR=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_05/work/run2
echo "utc_start=$(date -u +%FT%TZ) host=$(hostname) job=$SLURM_JOB_ID"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh
echo '--- module list ---'; module list 2>&1; echo '-------------------'
cd "$RUN_DIR" || exit 2
echo "run_dir=$PWD"; ls -la
sha256sum input_deck.i mesh.exo interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "utc_launch=$(date -u +%FT%TZ)"
bash mpirun.source > morphorm_run.log 2>&1
rc=$?
echo "utc_end=$(date -u +%FT%TZ) mpirun_rc=$rc"
ls -la
exit $rc
