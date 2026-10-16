#!/bin/bash
#SBATCH --job-name=orchestrate_E2-05_resume
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=04:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/batch_logs/resume_e2_trial05_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/batch_logs/resume_e2_trial05_%j.err
# Researcher-side recovery (orchestrator only; runs no agent itself). The original chain runner died with its Claude Code
# session while E2-05 Session A (agent-host job 16168659) kept running in Slurm. This waits for Session A to end, records the
# agent-host job id the dead runner would have written, sets the designed pause state, then resumes through the existing
# run_e2_baseline.sh --session-b-only path (which re-runs the Stage-1 interlock), and scores the trial.
set -uo pipefail
T=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis; A=$T/automation; E=$T/researcher_only/session_evidence/E2-example16-baseline-05/session_a
P=$T/runs/E2_interrupted_recovery_example16/baseline/trial_05; SUM=$(ls -t $T/researcher_only/batch_logs/e2_04R_05_chain_*_summary.txt | head -1)
cd $A; source lib/common.sh; unset THESIS_CLAUDE_BIN_OVERRIDE THESIS_SESSION_EVIDENCE_ROOT
echo "$(utc_now) waiting for Session A agent-host job 16168659"
while squeue -h -j 16168659 2>/dev/null | grep -q .; do sleep 60; done
sleep 30
[[ -f $E/session_record.json ]] || { echo "$(utc_now) no Session A record; stopping" | tee -a $SUM; exit 1; }
echo 16168659 > $E/agent_host_job_id.txt
sacct -j 16168659 --parsable2 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,TotalCPU,NodeList > $E/agent_host_sacct.psv 2>/dev/null || true
echo "$(utc_now) recovery: original runner lost with its Claude Code session; agent_host_job_id.txt and agent_host_sacct.psv written by resume job ${SLURM_JOB_ID}" >> $E/submissions.log
rc=$(jq -r .exit_code $E/session_record.json); echo "$(utc_now) Session A rc=$rc"
manifest_set $P/manifest.yaml status paused_after_session_a
./run_e2_baseline.sh --trial 5 --execute-counted --session-b-only; brc=$?
st=$(manifest_get $P/manifest.yaml status)
[[ "$st" == completed_unscored ]] && ./score_researcher_only.sh --trial-dir $P --figures
manifest_set $P/manifest.yaml curation_notes "\"orchestrating runner died with its Claude Code session during Session A; Session A ran to completion in Slurm; resumed through --session-b-only by researcher recovery job ${SLURM_JOB_ID} (researcher_only/batch_logs/resume_e2_trial05_after_runner_loss.sh)\""
echo "$(utc_now) trial 05: status=$st decision=$(manifest_get $P/manifest.yaml scoring_decision) (resumed after runner loss; rc=$brc)" >> $SUM
echo "$(utc_now) chain finished" >> $SUM
