#!/usr/bin/env bash
# Researcher-only scientific scoring of one completed baseline trial against its reference package.
# Usage: score_researcher_only.sh --trial-dir D [--dry-run] [--figures]
# Writes researcher_only/scores/<run_id>/score.{json,md}; figures only under researcher_only/evaluation_figures/.
# References, tolerances and measured values never enter the packet; only the decision word is written to the manifest.
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
td=""; dry=0; figs=0
while [[ $# -gt 0 ]]; do case "$1" in --trial-dir) td=${2:?}; shift 2;; --dry-run) dry=1; shift;; --figures) figs=1; shift;; -h|--help) sed -n '2,5p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -d "$td" ]] || die "trial dir not found" 2; td=$(cd "$td" && pwd -P); m="$td/manifest.yaml"; rid=$(manifest_get "$m" run_id); sel=$(manifest_get "$m" experiment_selector)
case "$sel" in e1-example8) ref="$RESEARCHER_ONLY/ground_truth/example_8";; e2-example16) ref="$RESEARCHER_ONLY/ground_truth/example_16";; *) die "no scorer for $sel" 2;; esac
spec="$ref/reference_case/acceptance_spec.json"; [[ -f "$spec" ]] || die "acceptance spec missing: $spec" 3
out="$RESEARCHER_ONLY/scores/$rid"; PY3=/uufs/chpc.utah.edu/common/home/chet/Daisy/ThesisExperiments/common/approved_runtime/morphorm/python/bin/python3
if [[ $dry -eq 1 ]]; then log "DRY RUN: would score $rid ($sel) with $spec -> $out/score.json; no files written"; "$PY3" -I "$RESEARCHER_ONLY/ground_truth/tools/score_trial.py" --help >/dev/null && log "scorer loads"; exit 0; fi
[[ ! -e "$out/score.json" ]] || die "score already exists: $out/score.json (refusing to overwrite; move it aside to re-score)" 4
mkdir -p "$out"; chmod 700 "$RESEARCHER_ONLY/scores" "$out" 2>/dev/null || true
"$PY3" -I "$RESEARCHER_ONLY/ground_truth/tools/score_trial.py" --trial-dir "$td" --spec "$spec" --out-dir "$out" $([[ $figs -eq 1 ]] && echo --figures-dir "$RESEARCHER_ONLY/evaluation_figures") | tee "$out/score_stdout.txt"
dec=$(jq -r .decision "$out/score.json")
manifest_set "$m" scoring_decision "$dec"; manifest_set "$m" scoring_scored_utc "$(utc_now)"; manifest_set "$m" scoring_record "researcher_only/scores/$rid/score.json"
log "scored $rid: $dec (record: $out/score.json)"
