#!/usr/bin/env bash
# Write SHA256SUMS.txt for every regular file under <dir> (excluding the manifest itself).
# Usage: make_sha256_manifest.sh <dir>
set -euo pipefail
d=${1:?dir}; cd "$d"
find . -type f ! -name SHA256SUMS.txt -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
echo "$(wc -l < SHA256SUMS.txt) files hashed into $d/SHA256SUMS.txt"
