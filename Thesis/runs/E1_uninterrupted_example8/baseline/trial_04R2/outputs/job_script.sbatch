#!/bin/bash
#SBATCH --job-name=ex8_04R2_morphorm
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --chdir=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_04R2/work/run2
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_04R2/logs/morphorm_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_04R2/logs/morphorm_%j.err
# FROZEN-EX8-v1 / trial E1-example8-baseline-04R2 : 50-iteration OC topology optimization
# (half cantilever, Helmholtz symmetry-plane filter). Runs the XMLGenerator output in work/run2.
set -u
echo "JOB_START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "SLURM_JOB_ID=$SLURM_JOB_ID  NODE=$(hostname)  CPUS=$SLURM_CPUS_PER_TASK  MEM=$SLURM_MEM_PER_NODE  PWD=$(pwd)"
echo "THESIS_TRIAL_ID=${THESIS_TRIAL_ID:-E1-example8-baseline-04R2}"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh || { echo "ERROR: approved software interface failed"; exit 97; }
echo "---- module list ----"
module list 2>&1
echo "---- executables ----"
which PlatoMain analyze_MPMD mpiexec XMLGenerator
echo "---- input checksums (SHA-256) ----"
sha256sum input_deck.i mesh.exo interface.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml engine_input_deck.xml engine_operations.xml mpirun.source
echo "---- mpirun.source ----"
cat mpirun.source
echo "MORPHORM_START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
bash mpirun.source 2>&1 | tee morphorm_run.log
rc=${PIPESTATUS[0]}
echo "MORPHORM_END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "MORPHORM_EXIT_CODE=$rc"
echo "---- run directory listing ----"
ls -la . analyze_id_2_output* 2>/dev/null
echo "---- optimizer diagnostics tail ----"
tail -n 6 morphorm_oc_optimizer_diagnostics.txt 2>/dev/null
echo "JOB_END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit $rc
