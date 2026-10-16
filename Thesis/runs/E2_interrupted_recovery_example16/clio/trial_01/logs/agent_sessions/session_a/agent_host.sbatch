#!/bin/bash -l
#SBATCH --job-name=clio_E2-example16-clio-01_session_a
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/session_evidence/E2-example16-clio-01/session_a/agent_host_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/session_evidence/E2-example16-clio-01/session_a/agent_host_%j.err
# Agent-host job (the baseline's frozen contract). Runs exactly one CLIO deployment and one CLIO session.
echo "agent_host_job=$SLURM_JOB_ID node=$(hostname -s) start_utc=$(date -u +%FT%TZ)"
export THESIS_CLIO_RUNTIME_ROOT="/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/.agent_runtime"
exec "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/automation/clio/launch_clio_session.sh" --trial-dir "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_01" --run-id "E2-example16-clio-01" --session-label "session_a" --prompt-file "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/session_evidence/E2-example16-clio-01/session_a/prompt.md" --execute-counted --local --evidence-dir "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/session_evidence/E2-example16-clio-01/session_a" 
