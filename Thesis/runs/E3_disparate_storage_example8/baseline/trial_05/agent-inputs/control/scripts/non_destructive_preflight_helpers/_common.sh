#!/usr/bin/env bash
# Shared helpers for E3 trial record keeping. Source only. Never deletes, moves or modifies a source file.
set -o pipefail
TRIAL_ROOT="${E3_TRIAL_ROOT:-$PWD}"
STAGING="${E3_STAGING_DIR:-}"
PERMITTED_ROOTS_FILE="$TRIAL_ROOT/agent-inputs/permitted_roots.txt"   # written by trial preparation: alias<TAB>absolute root
utc() { date -u +%FT%TZ; }
die() { echo "ERROR: $*" >&2; exit 1; }
sha() { sha256sum "$1" | cut -c1-64; }
abspath() { realpath -m -- "$1"; }
under() { [[ "$1" == "$2" || "$1" == "$2"/* ]]; }   # under <path> <root>
# alias_of <abs path> -> prints the collection alias whose root contains the path, or fails
alias_of() {
  [[ -f "$PERMITTED_ROOTS_FILE" ]] || die "missing $PERMITTED_ROOTS_FILE"
  local a r; while IFS=$'\t' read -r a r; do [[ -z "$a" || "$a" == \#* ]] && continue; under "$1" "$r" && { echo "$a"; return 0; }; done < "$PERMITTED_ROOTS_FILE"
  return 1
}
append_tsv() { # append_tsv <file> <header> <fields...>
  local f=$1 h=$2; shift 2; mkdir -p "$(dirname "$f")"
  [[ -s "$f" ]] || printf '%s\n' "$h" > "$f"
  local IFS=$'\t'; printf '%s\n' "$*" >> "$f"
}
