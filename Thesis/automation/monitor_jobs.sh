#!/usr/bin/env bash
# Show scheduler state for a trial's jobs (agent-host jobs from session evidence + workflow jobs from jobs/job_ids.txt),
# or for explicit job ids.  Usage: monitor_jobs.sh (--trial-dir D | --job-ids 1,2,3) [--watch SECONDS]
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
td=""; ids=""; watch=0
while [[ $# -gt 0 ]]; do case "$1" in --trial-dir) td=${2:?}; shift 2;; --job-ids) ids=${2:?}; shift 2;; --watch) watch=${2:?}; shift 2;; -h|--help) sed -n '2,3p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
collect_ids() { local all="$ids"
  if [[ -n "$td" ]]; then local rid; rid=$(manifest_get "$td/manifest.yaml" run_id)
    all="$all,$(grep -ohE '[0-9]{6,}' "$td/jobs/job_ids.txt" 2>/dev/null | paste -sd, -)"
    all="$all,$(cat "$SESSION_EVIDENCE_ROOT/$rid"/*/agent_host_job_id.txt 2>/dev/null | paste -sd, -)"
    all="$all,$(cat "$td"/logs/agent_sessions/*/agent_host_job_id.txt 2>/dev/null | paste -sd, -)"; fi
  printf '%s' "$all" | tr ',' '\n' | grep -E '^[0-9]+$' | sort -u | paste -sd, -; }
show() { local j; j=$(collect_ids); echo "=== $(utc_now) jobs: ${j:-none}"
  [[ -n "$td" ]] && echo "trial: $(manifest_get "$td/manifest.yaml" run_id) status=$(manifest_get "$td/manifest.yaml" status)"
  [[ -n "$j" ]] || return 0
  squeue -j "$j" -o "%.10i %.40j %.9T %.10M %.12l %.4C %.8m %R" 2>/dev/null || true
  sacct -j "$j" -X --format=JobID,JobName%40,State,ExitCode,Elapsed,Start,End,NodeList -P 2>/dev/null || true; }
if [[ $watch -gt 0 ]]; then while true; do show; j=$(collect_ids); [[ -n "$j" ]] && squeue -h -j "$j" 2>/dev/null | grep -q . || break; sleep "$watch"; done; else show; fi
