#!/usr/bin/env bash
# Verify (read-only) the E3 source collections against their manifests, the candidate archive's write protection,
# and optionally the original source files against setup/source_inventory.sha256 (researcher-side only; never inside a trial).
# Usage: verify_readonly_sources.sh [--with-originals]
source "$(dirname "${BASH_SOURCE[0]}")/lib/e3_common.sh"
orig=0; [[ "${1:-}" == --with-originals ]] && orig=1
rc=0; verify_collections || rc=1
w=$(find "$E3_ARCHIVE_ROOT" -perm /222 -print 2>/dev/null | wc -l); echo "candidate archive entries with any write bit: $w"; [[ $w -eq 0 ]] || rc=1
if [[ $orig == 1 ]]; then
  if sha256sum -c --quiet "$E3_ROOT/setup/source_inventory.sha256" >/dev/null 2>&1; then echo "original sources: PASS ($(wc -l < "$E3_ROOT/setup/source_inventory.sha256") files)"; else echo "original sources: FAIL"; rc=1; fi
fi
exit $rc
