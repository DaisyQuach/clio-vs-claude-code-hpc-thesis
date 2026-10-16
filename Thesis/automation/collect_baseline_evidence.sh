#!/usr/bin/env bash
# Copy session evidence into the packet, gather scheduler accounting, hash everything, update the manifest.
# Usage: collect_baseline_evidence.sh --trial-dir D [--dry-run]
# Never overwrites an existing evidence file (fail closed).
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
td=""; dry=0
while [[ $# -gt 0 ]]; do case "$1" in --trial-dir) td=${2:?}; shift 2;; --dry-run) dry=1; shift;; -h|--help) sed -n '2,5p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -d "$td" ]] || die "trial dir not found" 2; td=$(cd "$td" && pwd -P); m="$td/manifest.yaml"; rid=$(manifest_get "$m" run_id); sel=$(manifest_get "$m" experiment_selector)
ev="$SESSION_EVIDENCE_ROOT/$rid"; dst="$td/logs/agent_sessions"
if [[ $dry -eq 1 ]]; then log "DRY RUN: would copy $ev/<label>/ (launch records, stream, transcript, sacct) into $dst/, write logs/slurm_sacct.psv, logs/evidence_SHA256SUMS.txt and update manifest fields of $rid; nothing written"; exit 0; fi
[[ -d "$ev" ]] || die "no session evidence for $rid under $ev" 1
[[ ! -e "$dst" ]] || die "$dst already exists (refusing to overwrite evidence)" 4
[[ ! -e "$td/logs/slurm_sacct.psv" && ! -e "$td/logs/evidence_SHA256SUMS.txt" ]] || die "evidence files already present in $td/logs (refusing)" 4
mkdir -p "$dst"
for s in "$ev"/*/; do l=$(basename "$s"); [[ "$l" == dryrun_* ]] && continue; [[ -f "$s/session_record.json" ]] || { warn "skipping $s (no session record)"; continue; }
  mkdir -p "$dst/$l"; for f in session_record.json launch_plan.json launch_command.txt launch_env.txt prompt.md prompt.sha256 session_id.txt start_utc.txt end_utc.txt exit_code.txt stream.jsonl stderr.log result.json agent_host_job_id.txt agent_host_sacct.psv agent_host_environment.txt agent_host_environment.txt.sha256 auth_status_isolated_config.json submissions.log agent_host.sbatch evidence_SHA256SUMS.txt; do [[ -e "$s/$f" ]] && cp -p "$s/$f" "$dst/$l/"; done
  for f in "$s"/transcript_*.jsonl "$s"/agent_host_*.out "$s"/agent_host_*.err; do [[ -e "$f" ]] && cp -p "$f" "$dst/$l/"; done
  log "copied session evidence: $l"
done
ls "$dst"/*/session_record.json >/dev/null 2>&1 || die "no session records were copied for $rid (nothing under $ev except dry runs); fail closed" 1
sids=$(for r in "$dst"/*/session_record.json; do jq -r .session_id "$r"; done | paste -sd, -); hosts=$(for r in "$dst"/*/session_record.json; do jq -r '.agent_host_job_id // empty' "$r"; done | grep . | paste -sd, - || true)
wf=$(grep -ohE '[0-9]{6,}' "$td/jobs/job_ids.txt" 2>/dev/null | sort -u | paste -sd, - || true)
all=$(printf '%s,%s' "$wf" "$hosts" | tr ',' '\n' | grep -E '^[0-9]+$' | sort -u | paste -sd, -)
if [[ -n "$all" ]]; then sacct -j "$all" --parsable2 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,Timelimit,AllocCPUS,ReqMem,MaxRSS,TotalCPU,NodeList,WorkDir > "$td/logs/slurm_sacct.psv" 2>/dev/null || true; fi
[[ -s "$td/logs/slurm_sacct.psv" ]] || echo "no job ids available at collection time ($(utc_now))" > "$td/logs/slurm_sacct.psv"
(cd "$td" && find outputs jobs work logs -type f ! -name evidence_SHA256SUMS.txt -print0 | sort -z | xargs -0 sha256sum > logs/evidence_SHA256SUMS.txt)
start=$(for r in "$dst"/*/session_record.json; do jq -r .start_utc "$r"; done | sort | head -1); end=$(for r in "$dst"/*/session_record.json; do jq -r .end_utc "$r"; done | sort | tail -1)
manifest_set "$m" agent_session_ids "\"$sids\""; manifest_set "$m" agent_host_job_ids "\"${hosts:-}\""; manifest_set "$m" workflow_job_ids "\"${wf:-}\""
manifest_set "$m" evidence_sha256_manifest "logs/evidence_SHA256SUMS.txt"; manifest_set "$m" started_utc "$start"; manifest_set "$m" finished_utc "$end"
log "evidence collected for $rid: sessions=$sids workflow_jobs=${wf:-none} agent_host_jobs=${hosts:-none}"
