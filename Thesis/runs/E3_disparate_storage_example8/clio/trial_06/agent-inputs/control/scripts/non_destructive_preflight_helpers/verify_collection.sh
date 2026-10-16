#!/usr/bin/env bash
# Usage: verify_collection.sh <collection_root>
# Read-only check of a collection against its MANIFEST.sha256; appends the result to provenance/control_and_source_versions.txt.
source "$(dirname "$0")/_common.sh"
[[ $# -eq 1 ]] || die "usage: verify_collection.sh <collection_root>"
root=$(abspath "$1"); al=$(alias_of "$root") || die "not a permitted collection root: $root"
[[ -f "$root/MANIFEST.sha256" ]] || die "no MANIFEST.sha256 in $root"
if (cd "$root" && sha256sum -c --quiet MANIFEST.sha256 >/dev/null 2>&1); then r=PASS; else r=FAIL; fi
mkdir -p "$TRIAL_ROOT/provenance"
echo "$(utc) collection=$al root=$root manifest_sha256=$(sha "$root/MANIFEST.sha256") verification=$r" | tee -a "$TRIAL_ROOT/provenance/control_and_source_versions.txt"
[[ $r == PASS ]]
