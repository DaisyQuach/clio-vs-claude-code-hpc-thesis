#!/bin/bash -l
#SBATCH --job-name=agent_E1-example8-baseline-02_session_main
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/session_evidence/E1-example8-baseline-02/session_main/agent_host_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/session_evidence/E1-example8-baseline-02/session_main/agent_host_%j.err
# Agent-host job (frozen contract).  Runs exactly one headless Claude Code session.
echo "agent_host_job=$SLURM_JOB_ID node=$(hostname -s) start_utc=$(date -u +%FT%TZ)"
exec "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/automation/launch_headless_claude.sh" --trial-dir "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_02" --run-id "E1-example8-baseline-02" --session-label "session_main" --prompt-file "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/session_evidence/E1-example8-baseline-02/session_main/prompt.md" --execute-counted --local --evidence-dir "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/session_evidence/E1-example8-baseline-02/session_main"
