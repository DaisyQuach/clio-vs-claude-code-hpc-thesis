#!/bin/bash
#SBATCH --job-name=ex16_s2probe_ri20
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_02R/logs/stage2_probe_ri20_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_02R/logs/stage2_probe_ri20_%j.err
#SBATCH --chdir=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_02R/work/stage2/probe_runs/ri20
# Stage-2 RESTART PROBE (restart_iteration 20, max_iterations 1) -- frozen workflow EX16, trial E2-example16-baseline-02R
# Purpose: determine which saved state of the Stage-1 checkpoint the engine reads for restart_iteration 20
# (first evaluated compliance must equal the Stage-1 iteration-20 value 2.360040e+05). NOT a deliverable run.
set -u
echo "TRIAL_ID=E2-example16-baseline-02R  STAGE=2-probe  RESTART_ITERATION=20"
echo "JOB_START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "SLURM_JOB_ID=$SLURM_JOB_ID  NODE=$(hostname)  CPUS=$SLURM_CPUS_PER_TASK  MEM=$SLURM_MEM_PER_NODE"
echo "PWD=$(pwd)"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh || { echo "FAILED to source approved software interface"; exit 97; }
echo "---- module list ----"
module list 2>&1
echo "---- input files (sha256) ----"
sha256sum input_deck.i mesh.exo restart_input.exo interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "MORPHORM_START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
bash mpirun.source > morphorm_probe.log 2>&1
rc=$?
echo "MORPHORM_END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "MORPHORM_RC=$rc"
echo "---- optimizer diagnostics ----"
cat morphorm_oc_optimizer_diagnostics.txt 2>/dev/null
echo "---- tail of morphorm_probe.log ----"
tail -30 morphorm_probe.log
echo "JOB_END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit $rc
