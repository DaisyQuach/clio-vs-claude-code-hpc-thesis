#!/usr/bin/env bash
# E3 baseline counted-trial job body (frozen with E3-BASELINE-FREEZE-v1). Called from trial_NN.sbatch inside its own
# Slurm allocation; self-contained: it does not depend on any interactive or Claude session on the login node.
# r1 (2026-10-10): identical to e3_baseline_counted_trial.sh except it also accepts trial 06 (replacement attempt 02R)
#   and records attempt_label in the start/end records.
# Usage: e3_baseline_counted_trial_r1.sh --trial NN --freeze-sha256 <sha of baseline_freeze.json>
# Steps: concurrency guard -> freeze verification -> immutable trial-start record -> approved runner (--execute-counted:
# prepare at the pin, node-local staging dir, headless Claude Code with the frozen prompt and no other message, records,
# audit, metrics, verification) -> terminal-state classification -> end record. Never reruns, retries or deletes anything.
# Live records: <E3>/.agent_runtime/baseline/<trial_id>/execution/ (researcher-side; excluded from audit section 2;
# forbidden to agents). Terminal state also written to <trial>/TRIAL_STATUS.json after the trial's own audit.
# Exit: 0 valid | 10 failed | 11 invalid | 12 audit_failed | 13 timed_out | 14 cancelled | 20 not started (guard/freeze)
set -u -o pipefail
E3=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8
X=$E3/setup/baseline_execution; FREEZE=$X/freeze/baseline_freeze.json
n=""; fsha=""
while [[ $# -gt 0 ]]; do case "$1" in --trial) n=$2; shift 2;; --freeze-sha256) fsha=$2; shift 2;; *) echo "unknown arg $1" >&2; exit 2;; esac; done
[[ "$n" =~ ^0[1-6]$ && "$fsha" =~ ^[0-9a-f]{64}$ ]] || { echo "usage: --trial 01..06 --freeze-sha256 SHA" >&2; exit 2; }
ATTEMPT=$n; [[ $n == 06 ]] && ATTEMPT=02R   # r1: trial_06 is replacement attempt 02R for trial_02
T=$E3/baseline/trial_$n; TID=E3-baseline-trial_$n; EX=$E3/.agent_runtime/baseline/$TID/execution
utc() { date -u +%FT%TZ; }; red() { sed -e "s#${HOME}#\$HOME#g"; }
log() { echo "[$(utc)] $*"; }
mkdir -p "$EX"
SELF_SHA=$(sha256sum "${BASH_SOURCE[0]}" | cut -c1-64)
got_usr1=0; runner_pid=""; t_start=$(utc)

end_record() { # end_record <state> <reason> <exit code>
  local st=$1 why=$2 code=$3 f
  for f in "$EX/trial_end_record.json" "$T/TRIAL_STATUS.json"; do
    [[ -e "$f" ]] && continue
    jq -n --arg tid "$TID" --arg st "$st" --arg why "$why" --argjson code "$code" --arg job "${SLURM_JOB_ID:-}" --arg host "$(hostname -s)" \
      --arg t0 "$t_start" --arg t1 "$(utc)" --arg rrc "${runner_rc:-}" --arg audit "${audit_v:-}" --arg verif "${verif_v:-}" \
      --arg srec_rc "${sess_rc:-}" --arg tout "${sess_tout:-}" --arg su "${src_un:-}" --arg ar "${ar_codes:-}" --arg wf "${wf_active:-}" \
      --arg fsha "$fsha" --arg wsha "$SELF_SHA" --arg att "$ATTEMPT" \
      '{trial_id:$tid, attempt_label:$att, terminal_state:$st, reason:$why, slurm_exit_code:$code, slurm_job_id:$job, node:$host, job_start_utc:$t0, job_end_utc:$t1,
        runner_exit_code:$rrc, session_exit_code:$srec_rc, session_timeout_hit:$tout, boundary_audit:$audit, completed_verification:$verif,
        sources_unchanged:$su, action_required_codes:$ar, workflow_jobs_still_active_at_end:$wf, freeze_sha256:$fsha, job_body_sha256:$wsha,
        policy:"retained as recorded; never overwritten, retried or replaced; any rerun is a new recorded attempt"}' > "$f" 2>/dev/null || true
  done
  chmod a-w "$EX/trial_end_record.json" 2>/dev/null || true
  log "TERMINAL STATE: $st ($why) exit=$code"
}
on_usr1() { got_usr1=1; log "SIGUSR1: Slurm time limit approaching"; echo "$(utc) time_limit_warning" >> "$EX/signals.log"; }
on_term() {
  echo "$(utc) SIGTERM (usr1_seen=$got_usr1)" >> "$EX/signals.log"
  if [[ $got_usr1 == 1 ]]; then end_record timed_out "Slurm job time limit reached while runner was active" 13; exit 13
  else end_record cancelled "job received SIGTERM before the time-limit warning (scancel or preemption)" 14; exit 14; fi
}
trap on_usr1 USR1; trap on_term TERM INT

log "job ${SLURM_JOB_ID:-?} on $(hostname -s) for $TID"
# ---- 0. guards: no rerun into this trial, freeze unchanged, no concurrent trial or leftover workflow job --------------
if [[ -e "$EX/trial_start_record.json" ]]; then log "start record already exists: refusing (no rerun into the same trial)"; exit 20; fi
not_started() { jq -n --arg tid "$TID" --arg why "$1" --arg job "${SLURM_JOB_ID:-}" --arg t "$(utc)" \
  '{trial_id:$tid, terminal_state:"failed", reason:("not started: " + $why), slurm_job_id:$job, utc:$t, runner_invoked:false}' > "$EX/not_started_record.json"
  log "NOT STARTED: $1"; exit 20; }
[[ "$(sha256sum "$FREEZE" | cut -c1-64)" == "$fsha" ]] || not_started "freeze record hash differs from the submitted freeze hash"
(cd "$E3" && sha256sum -c --quiet "$X/freeze/automation_files.sha256") > "$EX/freeze_check.txt" 2>&1 || not_started "automation differs from the frozen file list"
[[ "$(sha256sum "$E3/automation/baseline/baseline_e3_prompt.md" | cut -c1-64)" == "$(jq -r .prompt.sha256 "$FREEZE")" ]] || not_started "prompt hash differs from freeze"
others=$(squeue -h -u "$(id -un)" -t RUNNING -o '%i %j' | awk -v me="${SLURM_JOB_ID:-x}" '$1!=me && $2 ~ /^e3-baseline-trial_/' )
[[ -z "$others" ]] || not_started "another E3 baseline trial job is running: $others"
for i in $(seq 1 20); do   # bounded wait (<= 20 min) for workflow jobs left by an earlier trial (would contaminate this trial's audit)
  wf=$(squeue -h -u "$(id -un)" -o '%i %Z' | awk -v r="$E3/baseline/" 'index($2, r)==1 {print $1}' | tr '\n' ' ')
  [[ -z "$wf" ]] && break; log "waiting for earlier workflow job(s) under baseline/: $wf"; echo "$(utc) waiting_for $wf" >> "$EX/guard.log"; sleep 60
done
[[ -z "${wf:-}" ]] || not_started "earlier workflow job(s) still active under baseline/ after 20 min: $wf"

# ---- 1. immutable trial-start record --------------------------------------------------------------------------------
CB="$HOME/.local/share/claude/versions/2.1.295"
{ echo "# environment snapshot (non-secret allow-list), $(utc)"
  env | grep -E '^(SLURM_[A-Z_]+|TMPDIR|HOSTNAME|PATH|MODULEPATH|LOADEDMODULES|LMOD_SYSTEM_NAME|SHELL|LANG|LC_ALL)=' | sort
  echo "# module list"; module -t list 2>&1
  echo "# scontrol show job"; scontrol show job "$SLURM_JOB_ID" 2>&1
  echo "# CLAUDE*/ANTHROPIC* variables present (names only)"; env | sed -n 's/^\(CLAUDE[A-Z0-9_]*\|ANTHROPIC[A-Z0-9_]*\)=.*/\1/p'
} 2>&1 | red > "$EX/environment_snapshot.txt"
cp -p "$T/manifest.yaml" "$EX/manifest.pre_run.yaml"
jq -n --arg tid "$TID" --arg t "$(utc)" --arg job "$SLURM_JOB_ID" --arg host "$(hostname -s)" --arg nodes "${SLURM_JOB_NODELIST:-}" \
  --arg cpus "${SLURM_CPUS_PER_TASK:-}" --arg mem "${SLURM_MEM_PER_NODE:-}" --arg part "${SLURM_JOB_PARTITION:-}" --arg acct "${SLURM_JOB_ACCOUNT:-}" \
  --arg tl "$(squeue -h -j "$SLURM_JOB_ID" -o %l)" --arg tmp "${TMPDIR:-}" \
  --arg cver "$(DISABLE_AUTOUPDATER=1 "$CB" --version 2>/dev/null)" --arg csha "$(sha256sum "$(readlink -f "$CB")" | cut -c1-64)" \
  --arg gitv "$(git --version)" --arg jqv "$(jq --version)" --arg pyv "$(python3 --version 2>&1)" \
  --arg gcv "$("$E3/automation/environment/tools/globus-cli-3.43.0/bin/globus" version </dev/null 2>/dev/null | sed -n 's/^Installed version: *//p')" \
  --arg psha "$(sha256sum "$E3/automation/baseline/baseline_e3_prompt.md" | cut -c1-64)" \
  --arg pin "$(jq -r .control_repository.commit "$FREEZE")" --arg gsrc "$(jq -r .globus.source_collection_id "$FREEZE")" \
  --arg gdst "$(jq -r .globus.destination_collection_id "$FREEZE")" --arg sman "$(sha256sum "$E3/globus_source_root/MANIFEST.sha256" | cut -c1-64)" \
  --arg model "$(jq -r .claude.model "$FREEZE")" --arg fsha "$fsha" --arg wsha "$SELF_SHA" --arg att "$ATTEMPT" \
  --arg rsha "$(sha256sum "$E3/automation/baseline/run_baseline_e3_trial.sh" | cut -c1-64)" \
  '{trial_id:$tid, attempt_label:$att, created_utc:$t, slurm_job_id:$job, node:$host, nodelist:$nodes, cpus_per_task:$cpus, mem_per_node_mb:$mem, partition:$part, account:$acct, time_limit:$tl,
    node_local_tmpdir:$tmp, claude_version:$cver, claude_sha256:$csha, model:$model, reasoning_effort:"harness default (no override)", git:$gitv, jq:$jqv, python:$pyv, globus_cli:$gcv,
    prompt_sha256:$psha, control_commit:$pin, globus_source_collection:$gsrc, globus_destination_collection:$gdst, source_manifest_sha256:$sman,
    freeze_sha256:$fsha, job_body_sha256:$wsha, runner_sha256:$rsha, environment_snapshot:"environment_snapshot.txt", researcher_messages_after_prompt:0}' | red > "$EX/trial_start_record.json"
chmod a-w "$EX/trial_start_record.json" "$EX/environment_snapshot.txt" "$EX/manifest.pre_run.yaml"
(cd "$EX" && sha256sum trial_start_record.json environment_snapshot.txt manifest.pre_run.yaml > trial_start_record.sha256 && chmod a-w trial_start_record.sha256)

# ---- 2. approved runner -----------------------------------------------------------------------------------------------
log "starting approved runner"
"$E3/automation/baseline/run_baseline_e3_trial.sh" --trial-dir "$T" --execute-counted > "$EX/runner.log" 2>&1 &
runner_pid=$!
while :; do wait "$runner_pid"; runner_rc=$?; kill -0 "$runner_pid" 2>/dev/null || break; done   # re-wait after USR1
log "runner exited rc=$runner_rc"

# ---- 3. classification (read-only on the trial) -------------------------------------------------------------------------
audit_v=$(sed -n 's/^verdict: //p' "$T/provenance/boundary_audit.txt" 2>/dev/null)
verif_v=$(sed -n 's/^verdict: //p' "$T/provenance/verification.txt" 2>/dev/null)
sess_rc=$(jq -r '.exit_code // empty' "$T/logs/session/session_record.json" 2>/dev/null)
sess_tout=$(jq -r '.timeout_hit // empty' "$T/logs/session/session_record.json" 2>/dev/null)
src_un=$(sed -n 's/^e3dc_sources_unchanged: //p' "$T/manifest.yaml")
ar_codes=$(ls "$T"/logs/ACTION_REQUIRED_*.md 2>/dev/null | sed 's#.*/ACTION_REQUIRED_##; s#\.md$##' | tr '\n' ' ')
wf_active=$(squeue -h -u "$(id -un)" -o '%i %Z' | awk -v r="$T" 'index($2, r)==1 {print $1}' | tr '\n' ' ')
(cd "$T" && find . -type f ! -name TRIAL_STATUS.json -print0 | sort -z | xargs -0 -r sha256sum) > "$EX/trial_artifact_manifest.sha256"
if [[ "$audit_v" == FAIL || "$src_un" == false ]]; then end_record audit_failed "boundary audit FAIL or source collection changed (procedural audit policy: invalidates the trial)" 12; exit 12
elif [[ "$sess_tout" == true || $runner_rc -eq 124 || $runner_rc -eq 137 ]]; then end_record timed_out "agent session hit the frozen ${E3_SESSION_TIMEOUT_SECONDS:-6600}s timeout" 13; exit 13
elif [[ $runner_rc -eq 3 ]]; then end_record failed "runner stopped before launch: ACTION_REQUIRED ${ar_codes:-unknown}" 10; exit 10
elif [[ -z "$sess_rc" ]]; then end_record failed "runner ended (rc=$runner_rc) without a session record" 10; exit 10
elif [[ "$sess_rc" != 0 ]]; then end_record failed "agent session exited with code $sess_rc (e.g. provider/usage limit or harness error)" 10; exit 10
elif [[ "$audit_v" != PASS ]]; then end_record invalid "boundary audit verdict '${audit_v:-missing}' (REVIEW): cannot be counted unless a recorded researcher decision clears it" 11; exit 11
elif [[ "$verif_v" != PASS ]]; then end_record failed "completed-trial verification: ${verif_v:-missing} (deliverables/records incomplete)" 10; exit 10
elif [[ $runner_rc -ne 0 ]]; then end_record failed "runner exit code $runner_rc" 10; exit 10
else end_record valid "session exit 0, audit PASS, sources unchanged, completed verification PASS (awaiting researcher scoring)" 0; exit 0; fi
