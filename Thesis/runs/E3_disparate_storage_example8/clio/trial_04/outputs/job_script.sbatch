#!/bin/bash
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --job-name=E3-clio-trial_04-spc
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_04/logs/morphorm_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_04/logs/morphorm_%j.err
# E3-clio-trial_04: Symmetry-Plane Cantilever (E3-SPC-v1), 50-iteration OC optimization.
# Reads only the trial workspace and the approved software interface.
set -u
RUN=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_04/work/run
echo "utc_start $(date -u +%FT%TZ) host $(hostname) slurm_job_id $SLURM_JOB_ID run_dir $RUN"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh
echo "--- module list ---"; module list 2>&1; echo "--- end module list ---"
echo "which: $(which PlatoMain) $(which analyze_MPMD) $(which mpiexec)"
cd "$RUN" || exit 2
sha256sum input_deck.i mesh.exo interface.xml analyze_2_input_deck.xml analyze_helmholtz_input_deck.xml engine_input_deck.xml engine_operations.xml analyze_2_operations.xml analyze_helmholtz_operations.xml mpirun.source
echo "utc_morphorm_start $(date -u +%FT%TZ)"
bash mpirun.source > morphorm_run.log 2>&1
rc=$?
echo "utc_morphorm_end $(date -u +%FT%TZ) mpirun_exit=$rc"
ls -la
exit $rc
