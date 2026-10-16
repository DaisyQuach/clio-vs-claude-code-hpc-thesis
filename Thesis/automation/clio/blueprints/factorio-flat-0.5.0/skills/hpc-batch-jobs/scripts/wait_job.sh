#!/usr/bin/env bash
# Bounded wait on one Slurm job; prints ONE compact status line, so a wait step costs almost no output.
# Usage: wait_job.sh JOBID [MAX_SECONDS=540] [PROGRESS_FILE] [POLL_SECONDS=30]
#   Waits until the job has left the queue or MAX_SECONDS pass (keep MAX_SECONDS under the tool timeout).
#   Exit 0 = job finished (prints sacct State/ExitCode/Elapsed), 3 = still queued/running at the limit (call again),
#   2 = usage error. With PROGRESS_FILE, the line also shows that file's line count and its last line.
jid=${1:?usage: wait_job.sh JOBID [MAX_SECONDS] [PROGRESS_FILE] [POLL_SECONDS]}
max=${2:-540}; prog=${3:-}; poll=${4:-30}
[[ "$jid" =~ ^[0-9]+$ ]] || { echo "wait_job: bad job id '$jid'" >&2; exit 2; }
end=$((SECONDS + max))
while squeue -h -j "$jid" 2>/dev/null | grep -q . && (( SECONDS < end )); do sleep "$poll"; done
p=""
if [[ -n "$prog" && -f "$prog" ]]; then p=" | $(wc -l < "$prog") lines in $(basename "$prog"); last: $(grep -v '^[[:space:]]*$' "$prog" | tail -n 1 | tr -s ' ' | cut -c1-120)"; fi
if squeue -h -j "$jid" 2>/dev/null | grep -q .; then
  echo "$(date -u +%FT%TZ) job $jid $(squeue -h -j "$jid" -o '%T elapsed=%M node=%N' | head -1)$p"
  exit 3
fi
echo "$(date -u +%FT%TZ) job $jid left queue: $(sacct -X -n -P -j "$jid" -o State,ExitCode,Elapsed,NodeList 2>/dev/null | head -1)$p"
exit 0
