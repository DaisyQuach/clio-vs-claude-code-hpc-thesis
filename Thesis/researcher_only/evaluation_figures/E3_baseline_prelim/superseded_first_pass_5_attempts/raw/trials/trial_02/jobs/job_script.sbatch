#!/bin/bash
#SBATCH --job-name=e3-spc-v1-trial02-oc50
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_02/logs/slurm-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_02/logs/slurm-%j.err
# E3-SPC-v1 Symmetry-Plane Cantilever, trial E3-baseline-trial_02: one uninterrupted 50-iteration OC optimization.
# Reads only the trial workspace (work/run) and the approved software interface.
set -u
TRIAL_ROOT=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_02
RUN_DIR=$TRIAL_ROOT/work/run
echo "UTC job start: $(date -u +%FT%TZ)"
echo "SLURM_JOB_ID=$SLURM_JOB_ID host=$(hostname -s) cpus=$SLURM_CPUS_PER_TASK"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh || { echo "loader failed"; exit 2; }
echo "--- module list ---"; module list 2>&1; echo "-------------------"
echo "PlatoMain=$(command -v PlatoMain)"; echo "analyze_MPMD=$(command -v analyze_MPMD)"; echo "mpiexec=$(command -v mpiexec)"
cd "$RUN_DIR" || exit 3
echo "run dir: $PWD"; sha256sum input_deck.i mesh.exo interface.xml analyze_2_input_deck.xml analyze_helmholtz_input_deck.xml engine_input_deck.xml engine_operations.xml analyze_2_operations.xml analyze_helmholtz_operations.xml mpirun.source
echo "UTC morphorm start: $(date -u +%FT%TZ)"
bash mpirun.source > morphorm_run.log 2>&1
RC=$?
echo "UTC morphorm end: $(date -u +%FT%TZ) exit=$RC"
echo "--- run directory listing ---"; ls -la; ls -la analyze_id_2_output* 2>/dev/null | tail -5
echo "--- tail of morphorm_run.log ---"; tail -n 40 morphorm_run.log
echo "--- tail of optimizer diagnostics ---"; tail -n 8 morphorm_oc_optimizer_diagnostics.txt 2>/dev/null
echo "UTC job end: $(date -u +%FT%TZ)"
exit $RC
