#!/bin/bash
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --job-name=e3clio02_spc
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_02/logs/morphorm_run02_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_02/logs/morphorm_run02_%j.err
# E3-clio-trial_02: Symmetry-Plane Cantilever (E3-SPC-v1), 50 OC iterations, run directory work/run02
set -u
RUN=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_02/work/run02
cd "$RUN" || exit 2
echo "utc_start $(date -u +%FT%TZ) host $(hostname) slurm_job_id ${SLURM_JOB_ID:-none} cwd $PWD"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh
echo "--- module list ---"; module list 2>&1; echo "-------------------"
echo "which PlatoMain analyze_MPMD mpiexec: $(which PlatoMain) $(which analyze_MPMD) $(which mpiexec)"
sha256sum input_deck.i mesh.exo interface.xml analyze_2_input_deck.xml analyze_helmholtz_input_deck.xml engine_input_deck.xml mpirun.source
echo "utc_mpirun_start $(date -u +%FT%TZ)"
bash mpirun.source > morphorm_run.log 2>&1
rc=$?
echo "utc_mpirun_end $(date -u +%FT%TZ) mpirun_rc=$rc"
ls -la
exit $rc
