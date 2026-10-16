#!/bin/bash
#SBATCH --job-name=ex16_stage1
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_04/logs/stage1_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_04/logs/stage1_%j.err
# FROZEN-EX16-v1 Stage 1 (max_iterations 20, fresh start) -- trial E2-example16-baseline-04
set -u
RUNDIR="/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_04/work/stage1/run"
echo "JOB START UTC $(date -u +%FT%TZ)  SLURM_JOB_ID=${SLURM_JOB_ID}  host=$(hostname)  cpus=${SLURM_CPUS_PER_TASK:-?}  mem=${SLURM_MEM_PER_NODE:-?}"
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh || { echo "ERROR: failed to source approved software interface"; exit 2; }
echo "----- module list"
module list 2>&1
echo "----- executables"
for c in PlatoMain analyze_MPMD mpiexec; do printf "%-14s %s\n" "$c" "$(command -v $c)"; done
cd "$RUNDIR" || { echo "ERROR: run dir missing"; exit 3; }
echo "----- run directory $PWD"
sha256sum input_deck.i mesh.exo interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source
echo "----- mpirun.source"
cat mpirun.source
echo "MORPHORM START UTC $(date -u +%FT%TZ)"
bash mpirun.source 2>&1 | tee morphorm_stage1.log
rc=${PIPESTATUS[0]}
echo "MORPHORM END UTC $(date -u +%FT%TZ)  mpirun.source rc=$rc"
echo "----- run directory listing"
ls -la
ls -la analyze_id_2_output* 2>/dev/null || true
echo "----- optimizer diagnostics (tail)"
tail -n 30 morphorm_oc_optimizer_diagnostics.txt 2>/dev/null || echo "no diagnostics file"
echo "JOB END UTC $(date -u +%FT%TZ) rc=$rc"
exit $rc
