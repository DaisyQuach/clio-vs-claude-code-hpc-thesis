#!/usr/bin/env bash
# Verify a trial packet.  --planned: structure of an untouched planned packet.  --completed: artifact
# verification after the agent process(es) ended (deliverables, hashes, scheduler evidence, session
# boundary, researcher-only boundary audit).  Never marks a trial successful by itself.
# Usage: verify_trial_packet.sh --trial-dir D (--planned | --completed) [--json OUT]
# Exit 0 verified | 1 verification failed | 5 ambiguous
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
td=""; mode=""; json_out=""
while [[ $# -gt 0 ]]; do case "$1" in --trial-dir) td=${2:?}; shift 2;; --planned) mode=planned; shift;; --completed) mode=completed; shift;; --json) json_out=${2:?}; shift 2;; -h|--help) sed -n '2,7p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -d "$td" && -n "$mode" ]] || die "need --trial-dir and --planned|--completed" 2
td=$(cd "$td" && pwd -P); m="$td/manifest.yaml"; [[ -f "$m" ]] || die "no manifest.yaml in $td" 1
sel=$(manifest_get "$m" experiment_selector); rid=$(manifest_get "$m" run_id); status=$(manifest_get "$m" status)
fails=0; amb=0; lines=()
ck() { local r=$1 n=$2 d=$3; lines+=("$r|$n|$d"); printf '%-9s %-40s %s\n' "$r" "$n" "$d"; [[ $r == FAIL ]] && fails=$((fails+1)); [[ $r == AMBIGUOUS ]] && amb=$((amb+1)); return 0; }
frozen="$COMMON_DIR/$(experiment_field "$sel" frozen)"
# ---- common checks -------------------------------------------------------------------------
[[ -n "$rid" && -n "$sel" ]] && ck PASS manifest_identity "$rid ($sel)" || ck FAIL manifest_identity "run_id/experiment_selector missing"
want=$(cut -d' ' -f1 "$frozen/FROZEN_CONFIG_SHA256.txt"); have=$("$COMMON_DIR/scripts/hash_frozen_config.sh" "$td/agent_inputs" 2>/dev/null || echo none)
[[ "$have" == "$want" ]] && ck PASS agent_inputs_frozen "agent_inputs hash == frozen $(cat "$frozen/FROZEN_CONFIG_ID.txt")" || ck FAIL agent_inputs_frozen "agent_inputs hash $have != frozen $want"
[[ "$(manifest_get "$m" frozen_configuration_sha256)" == "$want" ]] && ck PASS manifest_frozen_hash "manifest records the frozen hash" || ck FAIL manifest_frozen_hash "manifest frozen hash differs"
if grep -rqs "researcher_only\|Morphorm_ground_truth\|examplesmanual\|ThesisExperiments/runs" "$td/agent_inputs"; then ck FAIL agent_inputs_clean "agent_inputs references restricted material"; else ck PASS agent_inputs_clean "no restricted references in agent_inputs"; fi
case "$sel" in e1-example8|e3-example8) [[ -f "$td/agent_inputs/task_prompt.md" ]] && ck PASS prompts "task_prompt.md present" || ck FAIL prompts "task_prompt.md missing";;
  e2-example16) [[ -f "$td/agent_inputs/session_a_prompt.md" && -f "$td/agent_inputs/recovery_prompt.md" ]] && ck PASS prompts "session_a_prompt.md and recovery_prompt.md present" || ck FAIL prompts "E2 prompts missing"
     if grep -qiE "stage *1|iteration|engine_output|initialguess|restart_iteration|checkpoint file" "$td/agent_inputs/recovery_prompt.md"; then ck FAIL recovery_prompt_neutral "recovery prompt leaks stage labels/filenames/iteration hints"; else ck PASS recovery_prompt_neutral "recovery prompt contains no stage labels, filenames or iteration hints"; fi;;
esac
if [[ "$mode" == planned ]]; then
  [[ "$status" == planned ]] && ck PASS status_planned "status: planned" || ck FAIL status_planned "status is '$status'"
  for d in work jobs logs outputs; do dir_only_gitkeep "$td/$d" && ck PASS "empty_$d" "$d/ contains only .gitkeep" || ck FAIL "empty_$d" "$d/ is not empty"; done
  for k in started_utc finished_utc agent_session_ids workflow_job_ids scoring_decision curation_include_in_analysis; do [[ "$(manifest_get "$m" "$k")" == null ]] && ck PASS "null_$k" "$k: null" || ck FAIL "null_$k" "$k is not null"; done
  [[ -z "$(find "$td" -type f \( -name '*.exo' -o -name '*.i' -o -name '*.jou' -o -name '*.sbatch' \) -print -quit)" ]] && ck PASS no_prior_outputs "no meshes/decks/job scripts in the packet" || ck FAIL no_prior_outputs "scientific files present in a planned packet"
else
  # ---- completed-mode checks ------------------------------------------------------------------
  case "$sel" in
    e1-example8) deliv=(outputs/mesh.jou outputs/mesh.exo outputs/input_deck.i outputs/job_script.sbatch outputs/generated_config/interface.xml outputs/generated_config/analyze_helmholtz_input_deck.xml outputs/generated_config/analyze_2_input_deck.xml outputs/morphorm_oc_optimizer_diagnostics.txt outputs/engine_output.exo outputs/final_analyze_output.exo outputs/SHA256SUMS.txt jobs/job_ids.txt work/run_summary.md);;
    e2-example16) deliv=(outputs/mesh.jou outputs/mesh.exo outputs/stage1/input_deck.i outputs/stage1/job_script.sbatch outputs/stage1/generated_config/interface.xml outputs/stage1/morphorm_oc_optimizer_diagnostics.txt outputs/stage1/engine_output.exo outputs/stage1/final_analyze_output.exo outputs/stage2/input_deck.i outputs/stage2/job_script.sbatch outputs/stage2/generated_config/interface.xml outputs/stage2/generated_config/engine_operations.xml outputs/stage2/restart_input.exo outputs/stage2/morphorm_oc_optimizer_diagnostics.txt outputs/stage2/engine_output.exo outputs/stage2/final_analyze_output.exo outputs/SHA256SUMS.txt jobs/job_ids.txt work/run_summary.md);;
    *) die "completed-mode verification is defined only for e1-example8 and e2-example16" 2;;
  esac
  miss=(); for f in "${deliv[@]}"; do [[ -s "$td/$f" ]] || miss+=("$f"); done
  [[ ${#miss[@]} -eq 0 ]] && ck PASS deliverables "all ${#deliv[@]} locked deliverables present" || ck FAIL deliverables "missing: ${miss[*]}"
  if [[ -s "$td/outputs/SHA256SUMS.txt" ]]; then if (cd "$td/outputs" && sha256sum -c --quiet SHA256SUMS.txt >/dev/null 2>&1); then ck PASS outputs_sha256 "outputs/SHA256SUMS.txt verifies"; else ck FAIL outputs_sha256 "outputs/SHA256SUMS.txt does not verify"; fi; fi
  if [[ -s "$td/jobs/job_ids.txt" ]]; then ids=$(grep -oE '[0-9]{6,}' "$td/jobs/job_ids.txt" | sort -u | tr '\n' ' '); [[ -n "$ids" ]] && ck PASS job_ids "workflow job ids: $ids" || ck FAIL job_ids "jobs/job_ids.txt has no job ids"; fi
  [[ -s "$td/logs/slurm_sacct.psv" ]] && ck PASS sacct_collected "logs/slurm_sacct.psv present" || ck FAIL sacct_collected "no sacct record collected (run collect_baseline_evidence.sh)"
  recs=$(find "$td/logs/agent_sessions" -name session_record.json 2>/dev/null | sort); n=$(printf '%s\n' "$recs" | grep -c . || true)
  case "$sel" in e1-example8) want_n=1;; e2-example16) want_n=2;; esac
  [[ "$n" -eq "$want_n" ]] && ck PASS session_records "$n session record(s) as required" || ck FAIL session_records "found $n session records, need $want_n"
  if [[ "$n" -gt 0 ]]; then
    sids=$(for r in $recs; do jq -r .session_id "$r"; done | sort -u | wc -l); [[ "$sids" -eq "$n" ]] && ck PASS distinct_session_ids "$sids distinct session id(s)" || ck FAIL distinct_session_ids "session ids not distinct"
    if for r in $recs; do jq -e '.resume_used==false and .continue_used==false and .fork_used==false' "$r" >/dev/null; done && ! grep -qsE -- '--resume|--continue|--fork-session|-r |-c ' "$td"/logs/agent_sessions/*/launch_command.txt; then ck PASS no_resume "no resume/continue/fork in any launch"; else ck FAIL no_resume "a launch used resume/continue/fork"; fi
    cfgs=$(for r in $recs; do jq -r .config_dir "$r"; done | sort -u | wc -l); [[ "$cfgs" -eq "$n" ]] && ck PASS isolated_config "each session had its own CLAUDE_CONFIG_DIR" || ck FAIL isolated_config "sessions shared a config dir"
    for r in $recs; do v=$(jq -r .executable_version "$r"); [[ "$v" == "$CLAUDE_PIN_VERSION" ]] && ck PASS "pinned_$(jq -r .session_label "$r")" "executable $v" || ck FAIL "pinned_$(jq -r .session_label "$r")" "executable version $v != $CLAUDE_PIN_VERSION"; done
    for r in $recs; do t=$(jq -r .timeout_hit "$r"); rc=$(jq -r .exit_code "$r"); [[ "$t" == false && "$rc" == 0 ]] && ck PASS "exit_$(jq -r .session_label "$r")" "rc=0, no timeout" || ck AMBIGUOUS "exit_$(jq -r .session_label "$r")" "rc=$rc timeout_hit=$t (process exit alone is not success; researcher review)"; done
    # researcher-only boundary audit over transcripts and streams
    # the session's own CLAUDE_CONFIG_DIR path may legitimately appear (persisted tool outputs); blank it before matching
    pat="researcher_only|Morphorm_ground_truth|examplesmanual|/Morphorm/docs|/Morphorm/morphormtests|ThesisExperiments/runs|experiments_groundTruth|Morphorm_Full_Examples_Tests|\.agent_runtime"
    viol=""
    for r in $recs; do own=$(jq -r .config_dir "$r"); sd=$(dirname "$r")
      for f in "$sd"/transcript_*.jsonl "$sd"/stream.jsonl; do [[ -f "$f" ]] || continue
        if sed -e "s#${own//#/\\#}##g" "$f" | grep -qsE "$pat"; then viol="$viol $f"; fi; done; done
    viol=$(echo "$viol" | sed 's/^ //')
    [[ -z "$viol" ]] && ck PASS boundary_audit "no restricted paths mentioned in session transcripts" || ck FAIL boundary_audit "restricted material referenced in: $viol"
  fi
  if [[ "$sel" == e2-example16 && "$n" -eq 2 ]]; then
    a_end=$(jq -r .end_utc "$td/logs/agent_sessions/session_a/session_record.json" 2>/dev/null || echo ""); b_start=$(jq -r .start_utc "$td/logs/agent_sessions/session_b/session_record.json" 2>/dev/null || echo "")
    [[ -n "$a_end" && -n "$b_start" && "$a_end" < "$b_start" ]] && ck PASS session_order "session A ended $a_end before session B started $b_start" || ck FAIL session_order "session A/B timing not sequential"
    s2=$(stat -c %Y "$td/outputs/stage2/input_deck.i" 2>/dev/null || echo 0); ae=$(date -u -d "$a_end" +%s 2>/dev/null || echo 0)
    [[ $s2 -gt $ae ]] && ck PASS stage2_after_a "stage-2 deck written after session A ended" || ck AMBIGUOUS stage2_after_a "stage-2 deck mtime not after session A end (researcher review)"
  fi
fi
res=$([[ $fails -eq 0 && $amb -eq 0 ]] && echo verified || { [[ $fails -gt 0 ]] && echo failed || echo ambiguous; })
printf '\npacket verification (%s): %s  fails=%d ambiguous=%d\n' "$mode" "$res" "$fails" "$amb"
if [[ -n "$json_out" ]]; then { printf '{"utc":"%s","mode":"%s","run_id":"%s","result":"%s","fails":%d,"ambiguous":%d,"checks":[' "$(utc_now)" "$mode" "$rid" "$res" "$fails" "$amb"; first=1; for l in "${lines[@]}"; do IFS='|' read -r r n d <<<"$l"; [[ $first -eq 1 ]] || printf ','; first=0; printf '{"result":%s,"name":%s,"detail":%s}' "$(jq -Rn --arg s "$r" '$s')" "$(jq -Rn --arg s "$n" '$s')" "$(jq -Rn --arg s "$d" '$s')"; done; printf ']}\n'; } > "$json_out"; fi
[[ $fails -eq 0 ]] || exit 1; [[ $amb -eq 0 ]] || exit 5; exit 0
