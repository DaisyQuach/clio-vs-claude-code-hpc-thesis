#!/bin/bash
#SBATCH --job-name=ex16_stage1
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_02R/logs/stage1_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_02R/logs/stage1_%j.err
#SBATCH --chdir=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_02R/work/stage1/run
# Stage-1 Morphorm job -- frozen workflow EX16 (FROZEN-EX16-v1), trial E2-example16-baseline-02R
# Runs the translated (XMLGenerator) configuration in work/stage1/run via the generated mpirun.source.
set -u
echo "TRIAL_ID=E2-example16-baseline-02R  STAGE=1"
echo "JOB_START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "SLURM_JOB_ID=$SLURM_JOB_ID  NODE=$(hostname)  CPUS=$SLURM_CPUS_PER_TASK  MEM=$SLURM_MEM_PER_NODE"
echo "PWD=$(pwd)"
# approved software interface (required before any Morphorm/Cubit executable)
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh || { echo "FAILED to source approved software interface"; exit 97; }
echo "---- module list ----"
module list 2>&1
echo "---- executables ----"
which PlatoMain analyze_MPMD mpiexec
echo "---- input files (sha256) ----"
sha256sum input_deck.i mesh.exo interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "---- mpirun.source ----"
cat mpirun.source
echo "MORPHORM_START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
bash mpirun.source > morphorm_stage1.log 2>&1
rc=$?
echo "MORPHORM_END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "MORPHORM_RC=$rc"
echo "---- run directory after Morphorm ----"
ls -la
ls -la analyze_id_2_output* 2>/dev/null | tail -5
echo "---- tail of morphorm_stage1.log ----"
tail -40 morphorm_stage1.log
echo "---- optimizer diagnostics ----"
cat morphorm_oc_optimizer_diagnostics.txt 2>/dev/null
echo "JOB_END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit $rc
