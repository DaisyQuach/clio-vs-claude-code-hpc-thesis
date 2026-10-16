#!/usr/bin/env bash
# Record every file in a node-local staging directory (path, bytes, SHA-256) and the totals; read-only on the staging dir.
# Usage: record_staging_snapshot.sh --trial-dir D --staging S
source "$(dirname "${BASH_SOURCE[0]}")/lib/e3_common.sh"
td=""; sd=""
while [[ $# -gt 0 ]]; do case "$1" in --trial-dir) td=${2:?}; shift 2;; --staging) sd=${2:?}; shift 2;;
  -h|--help) sed -n '2,3p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -d "$td/staging-manifest" ]] || die "no staging-manifest/ in $td" 2
out="$td/staging-manifest/node_local_final_listing.tsv"
if [[ ! -d "$sd" ]]; then echo "staging directory not present: $sd" > "$out"; warn "staging dir missing"; exit 0; fi
{ printf 'relative_path\tbytes\tsha256\n'
  (cd "$sd" && find . -type f -printf '%P\n' | sort | while IFS= read -r f; do printf '%s\t%s\t%s\n' "$f" "$(stat -c %s "$f")" "$(sha256_of "$f")"; done); } > "$out"
n=$(( $(wc -l < "$out") - 1 )); b=$(awk -F'\t' 'NR>1{s+=$2} END{print s+0}' "$out")
printf 'utc: %s\nhost: %s\nstaging_dir: %s\nfiles: %s\nbytes: %s\n' "$(utc_now)" "$(hostname -s)" "$sd" "$n" "$b" > "$td/staging-manifest/node_local_final_summary.txt"
log "staging snapshot: $n files, $b bytes"
