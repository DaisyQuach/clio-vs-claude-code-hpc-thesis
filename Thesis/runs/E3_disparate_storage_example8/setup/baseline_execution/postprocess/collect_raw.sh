#!/usr/bin/env bash
# Researcher-side raw collection after all five E3 baseline trial jobs ended (non-agent; read-only on trials).
# Usage: collect_raw.sh <out dir> <submission_manifest.tsv>
# Preserves raw Slurm accounting exports and copies of trial/execution records BEFORE any summary is built.
set -u -o pipefail
E3=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8
OUT=$1; SM=$2; R=$OUT/raw; mkdir -p "$R/slurm" "$R/execution" "$R/trials"
utc() { date -u +%FT%TZ; }
echo "collect_raw start $(utc) host $(hostname -s) job ${SLURM_JOB_ID:-}"
cp -p "$SM" "$R/submission_manifest.tsv"
ids=$(awk -F'\t' 'NR>1 && $2 ~ /^trial_0[1-5]$/ {print $3}' "$SM" | paste -sd,)
pre=$(awk -F'\t' 'NR>1 && $2=="preflight" {print $3}' "$SM")
# 1. raw accounting (all fields, all steps) for trial jobs and the preflight
sacct -j "$ids" --format=ALL -P > "$R/slurm/sacct_trial_jobs_ALL.psv" 2>&1
sacct -j "$pre" --format=ALL -P > "$R/slurm/sacct_preflight_ALL.psv" 2>&1
F=JobID,JobName,State,ExitCode,DerivedExitCode,Reason,Submit,Eligible,Start,End,Elapsed,ElapsedRaw,TimelimitRaw,TotalCPU,CPUTimeRAW,UserCPU,SystemCPU,MaxRSS,MaxVMSize,AveRSS,AllocCPUS,ReqMem,ReqTRES,AllocTRES,NodeList,Partition,Account,WorkDir
sacct -j "$ids" --format=$F -P > "$R/slurm/sacct_trial_jobs.psv" 2>&1
# 2. workflow jobs submitted by the agents (any job of this account whose WorkDir is inside a baseline trial)
first=$(sacct -j "$ids" -X -n -P --format=Submit | sort | head -1)
sacct -u "$(id -un)" -S "${first:-now-2days}" -E now -X -P --format=$F > "$R/slurm/sacct_account_window_X.psv" 2>&1
awk -F'|' -v r="$E3/baseline/trial_" 'NR==1 || index($NF, r)==1' "$R/slurm/sacct_account_window_X.psv" > "$R/slurm/sacct_workflow_jobs_X.psv"
wf=$(awk -F'|' 'NR>1 {print $1}' "$R/slurm/sacct_workflow_jobs_X.psv" | paste -sd,)
[[ -n "$wf" ]] && sacct -j "$wf" --format=$F -P > "$R/slurm/sacct_workflow_jobs.psv" 2>&1 || echo "no workflow jobs" > "$R/slurm/sacct_workflow_jobs.psv"
squeue -u "$(id -un)" -o '%i|%j|%T|%M|%Z' > "$R/slurm/squeue_at_collection.psv" 2>&1
# 3. execution records and trial records (copies; originals untouched)
for n in 01 02 03 04 05; do
  tid=E3-baseline-trial_$n; T=$E3/baseline/trial_$n; D=$R/trials/trial_$n
  [[ -d "$E3/.agent_runtime/baseline/$tid/execution" ]] && cp -rp "$E3/.agent_runtime/baseline/$tid/execution" "$R/execution/trial_$n"
  mkdir -p "$D"
  (cd "$T" && find . -type f \( -path './manifest.yaml' -o -path './TRIAL_STATUS.json' -o -path './provenance/*' -o -path './staging-manifest/*' \
     -o -path './jobs/*' -o -path './logs/*' ! -path './logs/session/*' -o -path './work/run_summary.md' -o -path './outputs/SHA256SUMS.txt' \
     -o -path './outputs/morphorm_oc_optimizer_diagnostics.txt' -o -path './outputs/*verification*' -o -path './agent-inputs/CONTROL_COMMIT.txt' \
     -o -path './logs/session/launch_plan.json' -o -path './logs/session/session_record.json' -o -path './logs/session/result.json' \
     -o -path './logs/session/auth_status.json' -o -path './logs/session/prompt.sha256' -o -path './logs/session/launch_command.txt' \) \
     ! -name .gitkeep -print0 | xargs -0 -r cp -p --parents -t "$D")
  # large session evidence is referenced by hash, not copied
  (cd "$T" && find logs/session -type f \( -name 'stream.jsonl' -o -name 'transcript_*.jsonl' -o -name 'tool_inputs.jsonl' -o -name 'stderr.log' \) -print0 2>/dev/null | sort -z | xargs -0 -r sha256sum) > "$D/session_evidence_by_reference.sha256"
done
(cd "$R" && find . -type f ! -name SHA256SUMS.txt -print0 | sort -z | xargs -0 sha256sum) > "$R/SHA256SUMS.txt"
echo "collect_raw end $(utc): $(wc -l < "$R/SHA256SUMS.txt") raw files"
