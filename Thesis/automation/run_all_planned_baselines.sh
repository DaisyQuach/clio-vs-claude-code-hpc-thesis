#!/usr/bin/env bash
# Five-trial batch mode for ONE experiment.  Never runs both experiments; requires the explicit selector and
# --execute-counted (or --dry-run).  Stops immediately after the first failed or ambiguous trial.
# Usage: run_all_planned_baselines.sh --experiment e1-example8|e2-example16 (--dry-run | --execute-counted) [--local]
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
sel=""; mode=""; via=""
while [[ $# -gt 0 ]]; do case "$1" in --experiment) sel=${2:?}; shift 2;; --dry-run) mode=dry; shift;; --execute-counted) mode=counted; shift;; --local) via=--local; shift;; -h|--help) sed -n '2,5p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -n "$sel" ]] || die "an explicit --experiment selector is required (e1-example8 or e2-example16); this script never runs both" 2
executable_experiment "$sel" || die "no executable automation for '$sel' (E3 is planned only)" 2
[[ -n "$mode" ]] || die "--execute-counted is required for a counted batch (or --dry-run)" 2
case "$sel" in e1-example8) runner="$AUTOMATION_DIR/run_e1_baseline.sh";; e2-example16) runner="$AUTOMATION_DIR/run_e2_baseline.sh";; esac
ran=0
for n in 1 2 3 4 5; do td=$(trial_dir_of "$sel" "$n"); [[ -f "$td/manifest.yaml" ]] || { warn "trial_$(printf '%02d' $n) has no packet; skipping"; continue; }
  st=$(manifest_get "$td/manifest.yaml" status); [[ "$st" == planned ]] || { log "trial_$(printf '%02d' $n) status=$st; not planned, skipping"; continue; }
  log "---- $sel trial $n ($mode) ----"
  if "$runner" --trial "$n" $([[ $mode == dry ]] && echo --dry-run || echo --execute-counted) $via; then ran=$((ran+1)); else rc=$?; die "batch stopped: trial $n ended with rc=$rc (failed/ambiguous/blocked). Inspect before continuing." "$rc"; fi
done
log "batch finished: $ran trial(s) processed in $mode mode"
