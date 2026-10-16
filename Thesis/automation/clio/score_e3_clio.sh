#!/usr/bin/env bash
# Score ONE completed E3 CLIO trial exactly as the E3 baseline was scored (researcher_only/evaluation_figures/
# E3_baseline_prelim/E3_BASELINE_EVALUATION.md, section 2): the unchanged E1 scorer
# (researcher_only/ground_truth/tools/score_trial.py) with the Example 8 acceptance spec, run on a read-only scoring view
# (symlinks + a one-line manifest giving the run ID), with the recorded adapter that maps the trial's own completed-trial
# verification (provenance/verification.txt, "verdict: PASS") to the logs/packet_verification.json the scorer reads.
# Writes researcher_only/scores/E3-clio-NN/ (refuses an existing one) and, as for the baseline, only the decision word and
# status into the trial manifest (pre-scoring copy kept in the score directory). Agent files are never changed.
# Usage: score_e3_clio.sh --trial-dir <E3>/clio/trial_NN
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/clio_common.sh"
td=""
while [[ $# -gt 0 ]]; do case "$1" in --trial-dir) td=$(readlink -f "${2:?}"); shift 2;; -h|--help) sed -n '2,10p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -d "$td" && "$td" == */E3_disparate_storage_example8/clio/trial_* ]] || die "need --trial-dir <E3>/clio/trial_NN" 2
# E3_CLIO_SCORE_ROOT: tests only (write elsewhere, leave the manifest alone)
n=${td##*/trial_}; out="${E3_CLIO_SCORE_ROOT:-$RESEARCHER_ONLY/scores}/E3-clio-$n"; [[ -e "$out" ]] && die "$out exists (scores are never overwritten)" 3
grep -q '^e3dc_status: awaiting_scoring' "$td/manifest.yaml" || \
  warn "manifest status is $(grep '^e3dc_status:' "$td/manifest.yaml") (scoring anyway; the decision records it)"
TOOLS="$RESEARCHER_ONLY/ground_truth/tools"; SPEC="$RESEARCHER_ONLY/ground_truth/example_8/reference_case/acceptance_spec.json"
LOADER="$THESIS_ROOT/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh"
mkdir -p "$out"; V="$out/_score_view"; mkdir -p "$V/logs"
for d in outputs work jobs provenance staging-manifest; do [[ -e "$td/$d" ]] && ln -s "$td/$d" "$V/$d"; done
rid="E3-example8-clio-$n"; printf 'run_id: %s\n' "$rid" > "$V/manifest.yaml"
vf="$td/provenance/verification.txt"; verdict=$(sed -n 's/^verdict: //p' "$vf" 2>/dev/null | tail -1)
res=$([[ "$verdict" == PASS ]] && echo verified || echo failed)
jq -n --arg r "$res" --arg v "${verdict:-missing}" --arg s "clio/trial_$n/provenance/verification.txt" \
      --arg h "$(sha256sum < "$vf" 2>/dev/null | cut -d' ' -f1)" \
  '{result:$r, adapter:"E3 -> E1 scorer field mapping (researcher-side, scoring view only)", e3_completed_verification_verdict:$v, source:$s, source_sha256:$h}' \
  | tee "$out/packet_verification_adapter.json" > "$V/logs/packet_verification.json"
cp -p "$td/manifest.yaml" "$out/manifest.pre_scoring.yaml"
export PYTHONDONTWRITEBYTECODE=1
set +u; source "$LOADER" >/dev/null 2>&1; set -u
python3 "$TOOLS/score_trial.py" --trial-dir "$V" --spec "$SPEC" --out-dir "$out" > "$out/score_stdout.txt" 2>&1; rc=$?
dec=$(jq -r '.decision // empty' "$out/score.json" 2>/dev/null)
jq -n --arg spec "$SPEC" --arg ss "$(sha256sum < "$SPEC" | cut -d' ' -f1)" --arg sc "$TOOLS/score_trial.py" \
      --arg scs "$(sha256sum < "$TOOLS/score_trial.py" | cut -d' ' -f1)" --arg rid "$rid" --arg dec "$dec" --argjson rc $rc --arg utc "$(utc_now)" \
  '{run_id:$rid, scored_utc:$utc, spec:$spec, spec_sha256:$ss, scorer:$sc, scorer_sha256:$scs, rc:$rc, decision:$dec}' > "$out/scoring_run_record.json"
if [[ -n "$dec" && -z "${E3_CLIO_SCORE_ROOT:-}" ]]; then
  sed -i "s/^e3dc_scoring_decision: .*/e3dc_scoring_decision: $dec/; s/^e3dc_status: .*/e3dc_status: scored/" "$td/manifest.yaml"
fi
log "E3 CLIO trial_$n scored: ${dec:-no decision} (rc=$rc) -> $out"
exit $rc
