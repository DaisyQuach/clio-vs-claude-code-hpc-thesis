#!/usr/bin/env bash
# Render a topology figure with ParaView 6.0.1 (CHPC module).  Usage: render_figures.sh <final.exo> <out.png> "<title>" [extra args...]
set -euo pipefail
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module load paraview/6.0.1 >/dev/null 2>&1
exec pvbatch "$(dirname "$(readlink -f "$0")")/render_topology_pv.py" "$@"
