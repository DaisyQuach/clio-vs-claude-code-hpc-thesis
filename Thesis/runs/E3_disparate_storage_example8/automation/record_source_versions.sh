#!/usr/bin/env bash
# Record the control-repository commit, catalog checksums and source-collection manifests for a trial.
# Usage: record_source_versions.sh --trial-dir D --control-dir C   (C = the control snapshot/clone used for the trial)
# Writes provenance/source_versions.automation.txt; fails if any verification fails. Read-only on all sources.
source "$(dirname "${BASH_SOURCE[0]}")/lib/e3_common.sh"
td=""; cd_=""
while [[ $# -gt 0 ]]; do case "$1" in --trial-dir) td=${2:?}; shift 2;; --control-dir) cd_=${2:?}; shift 2;;
  -h|--help) sed -n '2,4p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -d "$td/provenance" && -d "$cd_" ]] || die "need --trial-dir with provenance/ and an existing --control-dir" 2
out="$td/provenance/source_versions.automation.txt"; rc=0
{ echo "utc: $(utc_now)"
  if git -C "$cd_" rev-parse HEAD >/dev/null 2>&1; then echo "control_commit: $(git -C "$cd_" rev-parse HEAD)"; else echo "control_commit: $(cat "$cd_/../CONTROL_COMMIT.txt" 2>/dev/null || echo unknown)"; fi
  if (cd "$cd_" && sha256sum -c --quiet catalog/checksums.sha256 >/dev/null 2>&1); then echo "control_checksums: PASS ($(sha256_of "$cd_/catalog/checksums.sha256"))"; else echo "control_checksums: FAIL"; fi
  echo "collections:"; verify_collections | sed 's/^/  /'
  echo "sources_searched_by_automation:"; for a in $(printf '%s\n' "${!E3_COLLECTIONS[@]}" | sort); do echo "  $a ${E3_COLLECTIONS[$a]} (manifest verification only)"; done
} > "$out"
grep -q 'FAIL' "$out" && rc=1
cat "$out"; exit $rc
