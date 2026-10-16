#!/usr/bin/env bash
# Usage: stage_file.sh <source_file> [staged_relative_path]
# Copies one file from a permitted collection into $E3_STAGING_DIR (cp -p; the source is only read),
# verifies SHA-256 of source and copy, and appends a line to staging-manifest/staged_files.tsv.
# Refuses sources outside the permitted collection roots and refuses to overwrite a different staged file.
source "$(dirname "$0")/_common.sh"
[[ $# -ge 1 && $# -le 2 ]] || die "usage: stage_file.sh <source_file> [staged_relative_path]"
[[ -n "$STAGING" && -d "$STAGING" ]] || die "E3_STAGING_DIR is not set or does not exist"
src=$(abspath "$1"); [[ -f "$src" ]] || die "not a regular file: $src"
al=$(alias_of "$src") || die "source is not inside a permitted collection root: $src"
rel=${2:-$al/$(basename "$src")}; [[ "$rel" != /* && "$rel" != *..* ]] || die "staged path must be relative, without '..'"
dst="$STAGING/$rel"; s1=$(sha "$src")
if [[ -e "$dst" ]]; then [[ "$(sha "$dst")" == "$s1" ]] && { echo "already staged (identical): $dst"; exit 0; }; die "different file already staged at $dst"; fi
mkdir -p "$(dirname "$dst")"; cp -p -- "$src" "$dst"; s2=$(sha "$dst")
[[ "$s1" == "$s2" ]] || die "hash mismatch after copy: $src"
append_tsv "$TRIAL_ROOT/staging-manifest/staged_files.tsv" $'utc\tcollection_alias\tsource_path\tstaged_path\tbytes\tsource_sha256\tstaged_sha256' \
  "$(utc)" "$al" "$src" "$dst" "$(stat -c %s "$dst")" "$s1" "$s2"
echo "$dst"
