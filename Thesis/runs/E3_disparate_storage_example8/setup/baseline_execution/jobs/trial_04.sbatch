#!/bin/bash -l
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --export=NONE
#SBATCH --signal=B:USR1@300
#SBATCH --job-name=e3-baseline-trial_04
#SBATCH --chdir=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/.agent_runtime/baseline/E3-baseline-trial_04/execution
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/.agent_runtime/baseline/E3-baseline-trial_04/execution/slurm-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/.agent_runtime/baseline/E3-baseline-trial_04/execution/slurm-%j.err
# E3 baseline COUNTED trial 04 (freeze E3-BASELINE-FREEZE-v1). Frozen agent-host contract; self-contained.
exec bash /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/setup/baseline_execution/jobs/e3_baseline_counted_trial.sh --trial 04 --freeze-sha256 e13d2fd6846a2a8814a821c17808575a500073b7e17e434ec4b4d300a868ec35
