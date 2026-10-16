#!/usr/bin/env bash
# Approved software interface for the Thesis study.  Source this in agent-host
# shells and in every submitted Slurm script.  It delegates to the frozen,
# read-only approved-runtime loader validated for the pilot study, so the runtime
# identity (modulefile and inventory hashes) is unchanged.
#   Morphorm is always loaded.  Coreform Cubit is loaded when THESIS_CUBIT_MODULE
#   is set before sourcing (the frozen value for this study is cubit-edu/2026.8).
# Safe to source: changes no shell options; returns non-zero on failure.
: "${THESIS_CUBIT_MODULE:=cubit-edu/2026.8}"
export THESIS_CUBIT_MODULE
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh 2>/dev/null || true
source /uufs/chpc.utah.edu/common/home/chet/Daisy/ThesisExperiments/common/scripts/load_approved_software.sh
