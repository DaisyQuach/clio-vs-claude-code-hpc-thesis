#!/usr/bin/env bash
# Five-trial CLIO batch for ONE experiment (counterpart of ../run_all_planned_baselines.sh). Trials run one after another,
# each in its own agent-host job(s); stops at the first failed/ambiguous trial.
# Usage: run_all_planned_clio.sh --experiment e1-example8|e2-example16 (--dry-run | --execute-counted)
source "$(dirname "${BASH_SOURCE[0]}")/lib/clio_common.sh"
exp=""; mode=""
while [[ $# -gt 0 ]]; do case "$1" in --experiment) exp=${2:?}; shift 2;; --dry-run) mode=--dry-run; shift;; --execute-counted) mode=--execute-counted; shift;; -h|--help) sed -n '2,5p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -n "$mode" ]] || die "need --dry-run or --execute-counted" 2
case "$exp" in e1-example8) r="$CLIO_AUTOMATION_DIR/run_e1_clio.sh";; e2-example16) r="$CLIO_AUTOMATION_DIR/run_e2_clio.sh";; *) die "explicit --experiment required" 2;; esac
for n in 1 2 3 4 5; do "$r" --trial "$n" $mode || die "trial $n did not complete cleanly; batch stopped (inspect, decide under the replacement policy)" 1; done
log "batch $exp $mode: 5 trials done"
