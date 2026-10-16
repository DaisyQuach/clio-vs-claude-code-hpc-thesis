#!/usr/bin/env bash
# Capture module/executable/runtime identity for a trial log.  Usage: capture_environment.sh --output PATH
set -euo pipefail
out=""; while [[ $# -gt 0 ]]; do case "$1" in --output) out=${2:?}; shift 2;; *) echo "usage: $0 --output PATH" >&2; exit 2;; esac; done
[[ -n "$out" ]] || { echo "usage: $0 --output PATH" >&2; exit 2; }
mkdir -p "$(dirname "$out")"
exec /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/ground_truth/tools/env_capture.sh "$out"
