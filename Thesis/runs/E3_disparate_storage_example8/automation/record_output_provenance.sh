#!/usr/bin/env bash
# Hash every file a trial produced (outputs, work, jobs, logs, provenance, staging-manifest) and check outputs/SHA256SUMS.txt.
# Usage: record_output_provenance.sh --trial-dir D     -> provenance/output_hashes.sha256, provenance/output_check.txt
source "$(dirname "${BASH_SOURCE[0]}")/lib/e3_common.sh"
td=""
while [[ $# -gt 0 ]]; do case "$1" in --trial-dir) td=${2:?}; shift 2;; -h|--help) sed -n '2,3p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -d "$td/provenance" ]] || die "no provenance/ in $td" 2
(cd "$td" && find outputs work jobs logs staging-manifest provenance -type f ! -name output_hashes.sha256 ! -name output_check.txt -print0 2>/dev/null | sort -z | xargs -0 -r sha256sum) > "$td/provenance/output_hashes.sha256"
{ echo "utc: $(utc_now)"
  echo "files_hashed: $(wc -l < "$td/provenance/output_hashes.sha256")"
  if [[ -f "$td/outputs/SHA256SUMS.txt" ]]; then
    if (cd "$td/outputs" && sha256sum -c --quiet SHA256SUMS.txt >/dev/null 2>&1); then echo "outputs_SHA256SUMS: PASS"; else echo "outputs_SHA256SUMS: FAIL"; fi
    echo "outputs_not_in_SHA256SUMS: $(cd "$td/outputs" && find . -type f ! -name SHA256SUMS.txt | sort | while read -r f; do grep -qF "  $f" SHA256SUMS.txt || echo "$f"; done | wc -l)"
  else echo "outputs_SHA256SUMS: MISSING"; fi; } > "$td/provenance/output_check.txt"
cat "$td/provenance/output_check.txt"
