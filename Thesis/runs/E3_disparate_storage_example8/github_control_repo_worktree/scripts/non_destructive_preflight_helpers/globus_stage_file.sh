#!/usr/bin/env bash
# Usage: globus_stage_file.sh <path_in_collection> [staged_relative_path]
# Stages one file from the private source collection by Globus (the only permitted access method for it):
#   1. Globus transfer  <source collection>:/<path>  ->  <destination collection>:<trial root>/staging-inbox/<path>
#      (the destination collection is permitted ONLY for this trial's staging-inbox/);
#   2. waits for the task, verifies the inbox copy against the collection's MANIFEST.sha256 (transferred the same way);
#   3. copies it (cp -p) into $E3_STAGING_DIR and verifies the SHA-256 again.
# Appends staging-manifest/globus_transfers.tsv and staging-manifest/staged_files.tsv. Never writes to a source collection.
# Collection IDs and the pinned CLI are read from agent-inputs/globus_access.txt (written by trial preparation).
source "$(dirname "$0")/_common.sh"
[[ $# -ge 1 && $# -le 2 ]] || die "usage: globus_stage_file.sh <path_in_collection> [staged_relative_path]"
[[ -n "$STAGING" && -d "$STAGING" ]] || die "E3_STAGING_DIR is not set or does not exist"
GA="$TRIAL_ROOT/agent-inputs/globus_access.txt"; [[ -f "$GA" ]] || die "missing $GA"
kv() { sed -n "s/^$1=//p" "$GA" | head -1; }
SRC=$(kv source_collection_id); DST=$(kv destination_collection_id); PFX=$(kv source_root_prefix); CLI=$(kv globus_cli)
AL=$(kv source_alias); [[ -n "$SRC" && -n "$DST" && -x "$CLI" && -n "$AL" ]] || die "incomplete $GA"
rel=${1#/}; [[ -n "$rel" && "$rel" != *..* ]] || die "path must be inside the collection, without '..'"
srel=${2:-$AL/$rel}; [[ "$srel" != /* && "$srel" != *..* ]] || die "staged path must be relative, without '..'"
INBOX="$(abspath "$TRIAL_ROOT")/staging-inbox"; [[ -d "$INBOX" ]] || die "missing $INBOX"
xfer() { # xfer <rel> -> transfers into the inbox unless already there; prints the inbox path
  local r=$1 d="$INBOX/$1" t0 tid st
  [[ -e "$d" ]] && { echo "$d"; return 0; }
  t0=$(utc)
  tid=$("$CLI" transfer "$SRC:$PFX/$r" "$DST:$d" --label "e3-${E3_TRIAL_ID:-trial}" --verify-checksum \
        --jmespath task_id --format unix </dev/null) || die "globus transfer submission failed for $r"
  "$CLI" task wait "$tid" --timeout "${E3_GLOBUS_WAIT_SECONDS:-1800}" </dev/null >/dev/null 2>&1
  st=$("$CLI" task show "$tid" --jmespath status --format unix </dev/null 2>/dev/null)
  # the file is written by the data-transfer node; refresh this client's NFS view of the directory before checking
  [[ "$st" == SUCCEEDED ]] && for _ in $(seq 1 60); do ls -a "$(dirname "$d")" >/dev/null 2>&1; [[ -f "$d" ]] && break; sleep 2; done
  append_tsv "$TRIAL_ROOT/staging-manifest/globus_transfers.tsv" \
    $'utc_submitted\tutc_finished\ttask_id\tsource\tdestination\tstatus\tbytes\tsha256' \
    "$t0" "$(utc)" "$tid" "$SRC:$PFX/$r" "$DST:$d" "$st" "$( [[ -f $d ]] && stat -c %s "$d")" "$( [[ -f $d ]] && sha "$d")"
  [[ "$st" == SUCCEEDED && -f "$d" ]] || die "globus task $tid ended with status '${st:-unknown}'"
  echo "$d"
}
man=$(xfer MANIFEST.sha256) || exit 1
[[ -f "$man" ]] || die "collection manifest not available in the inbox"
exp=$(awk -v f="$rel" '{p=$2; sub(/^\*/,"",p); sub(/^\.\//,"",p)} p==f {print $1; exit}' "$man" </dev/null)
[[ -n "$exp" ]] || die "$rel is not listed in the collection's MANIFEST.sha256"
inb=$(xfer "$rel") || exit 1; s1=$(sha "$inb"); [[ "$s1" == "$exp" ]] || die "inbox copy of $rel does not match MANIFEST.sha256"
dst="$STAGING/$srel"
if [[ -e "$dst" ]]; then [[ "$(sha "$dst")" == "$s1" ]] && { echo "already staged (identical): $dst"; exit 0; }; die "different file already staged at $dst"; fi
mkdir -p "$(dirname "$dst")"; cp -p -- "$inb" "$dst"; s2=$(sha "$dst"); [[ "$s1" == "$s2" ]] || die "hash mismatch after copy: $inb"
append_tsv "$TRIAL_ROOT/staging-manifest/staged_files.tsv" $'utc\tcollection_alias\tsource_path\tstaged_path\tbytes\tsource_sha256\tstaged_sha256' \
  "$(utc)" "$AL" "globus:$SRC:/$rel" "$dst" "$(stat -c %s "$dst")" "$exp" "$s2"
echo "$dst"
