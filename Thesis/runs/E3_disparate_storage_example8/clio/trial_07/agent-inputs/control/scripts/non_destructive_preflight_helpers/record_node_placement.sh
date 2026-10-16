#!/usr/bin/env bash
# Usage: record_node_placement.sh   -- writes provenance/node_local_placement.txt (host, staging dir, free space)
source "$(dirname "$0")/_common.sh"
[[ -n "$STAGING" && -d "$STAGING" ]] || die "E3_STAGING_DIR is not set or does not exist"
out="$TRIAL_ROOT/provenance/node_local_placement.txt"; mkdir -p "$(dirname "$out")"
{ echo "utc: $(utc)"; echo "host: $(hostname -s)"; echo "slurm_job_id: ${SLURM_JOB_ID:-none}"; echo "staging_dir: $STAGING"
  echo "filesystem:"; df -P "$STAGING" | sed 's/^/  /'; } >> "$out"
cat "$out"
