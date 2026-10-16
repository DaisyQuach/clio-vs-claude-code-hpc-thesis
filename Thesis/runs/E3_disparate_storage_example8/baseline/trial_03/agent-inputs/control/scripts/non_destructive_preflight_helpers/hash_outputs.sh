#!/usr/bin/env bash
# Usage: hash_outputs.sh   -- (re)writes outputs/SHA256SUMS.txt covering every file under outputs/ except itself
source "$(dirname "$0")/_common.sh"
cd "$TRIAL_ROOT/outputs" || die "no outputs/ directory"
find . -type f ! -name SHA256SUMS.txt -print0 | sort -z | xargs -0 -r sha256sum > SHA256SUMS.txt
wc -l < SHA256SUMS.txt
