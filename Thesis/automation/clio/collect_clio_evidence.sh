#!/usr/bin/env bash
# Collect one CLIO trial's evidence into the packet IN THE SAME WAY AS THE BASELINE, then add the CLIO-only records.
# Usage: collect_clio_evidence.sh --trial-dir D [--dry-run]
# 1. Runs the baseline collector ../collect_baseline_evidence.sh unchanged: logs/agent_sessions/<label>/ (session_record,
#    launch records, prompt, stream.jsonl, result.json, transcript_*.jsonl, sacct, sbatch), logs/slurm_sacct.psv,
#    logs/evidence_SHA256SUMS.txt and the manifest id/timestamp fields.
# 2. Copies each session's clio/ records (configuration freeze, API exports, usage, stream audit, runner logs) into
#    logs/agent_sessions/<label>/clio/ and hashes them in logs/clio_evidence_SHA256SUMS.txt.
# 3. Fills the manifest's clio_* fields. Never overwrites (fail closed).
source "$(dirname "${BASH_SOURCE[0]}")/lib/clio_common.sh"
td=""; dry=0
while [[ $# -gt 0 ]]; do case "$1" in --trial-dir) td=${2:?}; shift 2;; --dry-run) dry=1; shift;; -h|--help) sed -n '2,10p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -d "$td" ]] || die "trial dir not found" 2; td=$(cd "$td" && pwd -P); m="$td/manifest.yaml"; rid=$(manifest_get "$m" run_id)
[[ "$(manifest_get "$m" system)" == clio ]] || die "not a CLIO packet: $td" 2
ev="$SESSION_EVIDENCE_ROOT/$rid"; dst="$td/logs/agent_sessions"
if [[ $dry -eq 1 ]]; then "$AUTOMATION_DIR/collect_baseline_evidence.sh" --trial-dir "$td" --dry-run; log "DRY RUN: would then copy $ev/<label>/clio/ into $dst/<label>/clio/, write logs/clio_evidence_SHA256SUMS.txt and the clio_* manifest fields"; exit 0; fi
[[ ! -e "$td/logs/clio_evidence_SHA256SUMS.txt" ]] || die "CLIO evidence already collected (refusing)" 4
"$AUTOMATION_DIR/collect_baseline_evidence.sh" --trial-dir "$td" || die "baseline collector failed" 1
for s in "$ev"/*/; do l=$(basename "$s"); [[ "$l" == dryrun_* || ! -d "$s/clio" ]] && continue
  [[ -d "$dst/$l" && ! -e "$dst/$l/clio" ]] || { warn "skipping $l"; continue; }
  cp -rp "$s/clio" "$dst/$l/clio"; log "copied CLIO records: $l"; done
(cd "$td" && find logs/agent_sessions -path '*/clio/*' -type f -print0 | sort -z | xargs -0 sha256sum > logs/clio_evidence_SHA256SUMS.txt)
recs=$(ls "$dst"/*/session_record.json); first=$(echo "$recs" | head -1)
cs=$(for r in $recs; do jq -r .session_id "$r"; done | paste -sd, -)
clis=$(for r in $recs; do jq -r .executable_version "$r"; done | sort -u | paste -sd, -)
bp=$(jq -r '.effective_session_settings.blueprint_id // "unknown"' "$first"); bpv=$(jq -r '.effective_session_settings.blueprint_version // "unknown"' "$first")
eff=$(jq -r '.effective_session_settings.effort // "unknown"' "$first"); am=$(jq -r '.effective_session_settings.approval_mode // "unknown"' "$first")
manifest_set "$m" agent_harness_version "\"$(jq -r .clio_agent_version "$first")\""
manifest_set "$m" clio_core_version "\"$CLIO_CORE_VERSION_PIN\""; manifest_set "$m" clio_desktop_version "\"$CLIO_DESKTOP_VERSION\""
manifest_set "$m" clio_claude_cli_version "\"$clis\""; manifest_set "$m" clio_blueprint_id "\"$bp\""; manifest_set "$m" clio_blueprint_version "\"$bpv\""
manifest_set "$m" clio_effort "\"$eff\""; manifest_set "$m" clio_approval_mode "\"$am\""
manifest_set "$m" clio_runtime_tuning "\"idle_ttl=$CLIO_CLAUDE_CODE_STREAM_IDLE_TTL_S mcp_call_timeout=$CLIO_MCP_CALL_TIMEOUT_S turn_timeout=$CLIO_GACT_TURN_TIMEOUT_S\""
manifest_set "$m" clio_session_ids "\"$cs\""; manifest_set "$m" clio_config_sha256 "$(sha256_of "$CLIO_CONFIG_FILE")"
log "CLIO evidence collected for $rid: clio sessions=$cs cli=$clis blueprint=$bp@$bpv"
