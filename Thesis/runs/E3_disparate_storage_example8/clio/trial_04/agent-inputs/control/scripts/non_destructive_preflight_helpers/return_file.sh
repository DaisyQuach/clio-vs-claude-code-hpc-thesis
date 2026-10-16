#!/usr/bin/env bash
# Usage: return_file.sh <staged_file> <destination relative to the trial root>
# Copies a staged file into the trial workspace (never into agent-inputs/), verifies SHA-256 and records it in
# staging-manifest/returned_files.tsv. Refuses to overwrite an existing destination.
source "$(dirname "$0")/_common.sh"
[[ $# -eq 2 ]] || die "usage: return_file.sh <staged_file> <destination_relative_to_trial_root>"
src=$(abspath "$1"); [[ -f "$src" ]] || die "not a file: $src"
[[ -n "$STAGING" ]] && under "$src" "$(abspath "$STAGING")" || die "source must be inside \$E3_STAGING_DIR"
dst=$(abspath "$TRIAL_ROOT/$2"); under "$dst" "$(abspath "$TRIAL_ROOT")" || die "destination outside the trial root"
case "${dst#"$(abspath "$TRIAL_ROOT")"/}" in agent-inputs*|manifest.yaml) die "destination is read-only trial input";; esac
[[ -e "$dst" ]] && die "destination exists: $dst"
mkdir -p "$(dirname "$dst")"; cp -p -- "$src" "$dst"; s=$(sha "$dst"); [[ "$s" == "$(sha "$src")" ]] || die "hash mismatch"
append_tsv "$TRIAL_ROOT/staging-manifest/returned_files.tsv" $'utc\tstaged_path\tdestination_path\tbytes\tsha256' "$(utc)" "$src" "$dst" "$(stat -c %s "$dst")" "$s"
echo "$dst"
