#!/usr/bin/env bash
# Verify an E3 baseline trial workspace (read-only).
# Usage: verify_baseline_trial.sh --trial-dir <E3>/baseline/trial_NN (--planned | --completed) [--json OUT]
#   --planned    structure present; workspace fresh; no deck/journal/mesh/job script/result anywhere in the E3 trial dirs
#   --completed  required deliverables and distributed-context records present; hashes consistent; audit and sources recorded
# Exit 0 if every check passes, 1 otherwise.
source "$(dirname "${BASH_SOURCE[0]}")/../lib/e3_common.sh"
td=""; mode=""; jo=""
while [[ $# -gt 0 ]]; do case "$1" in --trial-dir) td=${2:?}; shift 2;; --planned) mode=planned; shift;; --completed) mode=completed; shift;;
  --json) jo=${2:?}; shift 2;; -h|--help) sed -n '2,7p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -n "$td" && -n "$mode" ]] || die "need --trial-dir and --planned|--completed" 2
td=$(e3_guard_trial_dir baseline "$td") || exit $?; fails=0; out=()
ck() { out+=("$1 $2: $3"); [[ $1 == PASS || $1 == INFO ]] || fails=$((fails+1)); }
for d in "${TRIAL_DIRS[@]}"; do [[ -d "$td/$d" ]] && ck PASS "dir_$d" present || ck FAIL "dir_$d" missing; done
[[ -f "$td/manifest.yaml" ]] && grep -q '^e3dc_trial_id:' "$td/manifest.yaml" && ck PASS manifest "E3 fields present" || ck FAIL manifest "manifest.yaml missing or lacks E3 fields"
[[ -d "$td/agent_inputs" ]] && ck INFO legacy_agent_inputs "pre-E3 agent_inputs/ present (researcher decision pending or recorded)"
if [[ $mode == planned ]]; then
  st=$(manifest_get "$td/manifest.yaml" e3dc_status); [[ $st == planned ]] && ck PASS status planned || ck FAIL status "$st"
  for d in "${WRITABLE_TRIAL_DIRS[@]}" agent-inputs; do dir_is_fresh "$td/$d" && ck PASS "fresh_$d" "only .gitkeep/README" || ck FAIL "fresh_$d" "not empty"; done
  n=$(find "$td" -path "$td/agent_inputs" -prune -o -type f \( -name '*.exo' -o -name '*.i' -o -name '*.jou' -o -name '*.sbatch' -o -name '*.e' \) -print | wc -l)
  [[ $n -eq 0 ]] && ck PASS no_solution_files "no deck/journal/mesh/job script" || ck FAIL no_solution_files "$n scientific files present"
else
  for f in outputs/mesh.jou outputs/mesh.exo outputs/input_deck.i outputs/job_script.sbatch outputs/morphorm_oc_optimizer_diagnostics.txt \
           outputs/engine_output.exo outputs/final_analyze_output.exo outputs/SHA256SUMS.txt jobs/job_ids.txt work/run_summary.md \
           provenance/sources_searched.tsv provenance/artifact_selections.md staging-manifest/staged_files.tsv provenance/node_local_placement.txt \
           provenance/control_and_source_versions.txt logs/session/stream.jsonl logs/session/session_record.json provenance/boundary_audit.txt; do
    [[ -s "$td/$f" ]] && ck PASS "exists:$f" ok || ck FAIL "exists:$f" missing; done
  ls "$td"/outputs/mesh_verification.* >/dev/null 2>&1 && ck PASS mesh_verification present || ck FAIL mesh_verification missing
  [[ -d "$td/outputs/generated_config" && -d "$td/outputs/run_logs" ]] && ck PASS output_dirs "generated_config/ run_logs/" || ck FAIL output_dirs "generated_config/ or run_logs/ missing"
  [[ -f "$td/outputs/SHA256SUMS.txt" ]] && (cd "$td/outputs" && sha256sum -c --quiet SHA256SUMS.txt >/dev/null 2>&1) && ck PASS outputs_sha256 verifies || ck FAIL outputs_sha256 "does not verify"
  if [[ -s "$td/staging-manifest/staged_files.tsv" ]]; then
    bad=$(awk -F'\t' 'NR>1 && $6!=$7' "$td/staging-manifest/staged_files.tsv" | wc -l); [[ $bad -eq 0 ]] && ck PASS staged_hashes "source==staged for all rows" || ck FAIL staged_hashes "$bad mismatching rows"
    ext=$(awk -F'\t' 'NR>1{print $2}' "$td/staging-manifest/staged_files.tsv" | grep -v -x -e e3-private-source -e e3-chpc-candidate-archive -e e3-control | wc -l)
    [[ $ext -eq 0 ]] && ck PASS staged_sources "all staged from catalogued collections" || ck FAIL staged_sources "$ext rows from other sources"
    np=$(awk -F'\t' 'NR>1 && $2=="e3-private-source" && $3 !~ /^globus:/' "$td/staging-manifest/staged_files.tsv" | wc -l)
    [[ $np -eq 0 ]] && ck PASS private_source_via_globus "every private-source row staged by Globus" || ck FAIL private_source_via_globus "$np private-source rows not staged by Globus"
  fi
  v=$(sed -n 's/^verdict: //p' "$td/provenance/boundary_audit.txt" 2>/dev/null); [[ $v == PASS ]] && ck PASS boundary_audit PASS || ck FAIL boundary_audit "${v:-missing}"
  grep -q 'FAIL' "$td/provenance/sources_after_trial.txt" 2>/dev/null && ck FAIL sources_unchanged FAIL || ck PASS sources_unchanged "no FAIL recorded"
  ls "$td"/logs/ACTION_REQUIRED_*.md >/dev/null 2>&1 && ck FAIL action_required "ACTION_REQUIRED file present" || ck PASS action_required none
fi
printf '%s\n' "${out[@]}"; echo "verdict: $([[ $fails -eq 0 ]] && echo PASS || echo "FAIL ($fails)")"
[[ -n "$jo" ]] && printf '%s\n' "${out[@]}" | jq -R 'split(" ") | {status:.[0], check:(.[1]|rtrimstr(":")), detail:(.[2:]|join(" "))}' | jq -s --argjson f "$fails" '{failures:$f, checks:.}' > "$jo"
[[ $fails -eq 0 ]]
