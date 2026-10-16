#!/usr/bin/env bash
# Print the frozen-configuration hash of a directory: sha256 of the sorted list of
# "<sha256>  <relative path>" lines over every regular file (manifest files excluded).
# Usage: hash_frozen_config.sh <dir>   (prints the hash; with --list also prints the lines)
set -euo pipefail
d=${1:?dir}; list=${2:-}
cd "$d"
lines=$(find . -type f ! -name 'FROZEN_CONFIG_SHA256.txt' ! -name 'FROZEN_CONFIG_FILES.sha256' ! -name 'E3_PLANNED_NOT_EXECUTABLE.md' -print0 | sort -z | xargs -0 sha256sum | sed 's#  \./#  #')
[[ "$list" == "--list" ]] && printf '%s\n' "$lines"
printf '%s\n' "$lines" | sha256sum | cut -c1-64
