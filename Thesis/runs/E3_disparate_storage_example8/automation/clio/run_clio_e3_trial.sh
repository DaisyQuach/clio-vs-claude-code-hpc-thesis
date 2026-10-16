#!/usr/bin/env bash
# Run ONE E3 CLIO trial through the dedicated E3 CLIO server started for it (start_e3_clio_server.sh).
# Usage: run_clio_e3_trial.sh --trial-dir <E3>/clio/trial_NN (--dry-run | --execute-counted) [--config FILE]
#          [--test-prompt FILE]        (test mode only: E3_ROOT_OVERRIDE; replaces the frozen prompt for a pilot)
# Must run on the allocated compute node of THIS trial's allocation (the server binds 127.0.0.1), e.g. from a login node:
#   srun --jobid=<alloc job id> --overlap --ntasks=1 <this script> --trial-dir ... --execute-counted
# Parity with the baseline: same config/pins (automation/baseline/baseline_e3_config.env), same frozen packet
# (prepare_baseline_trial.sh --system clio), same prompt file (byte-identical to task/task_prompt.md at the pin), same
# node-local staging, same 6600 s session limit, same records/audit/verification. Fixed approval_mode=bypass at session
# creation; the runner never answers permission or user prompts (no permission is added or broadened mid-trial).
# Stops with exit 3 and logs/ACTION_REQUIRED_<code>.md (nothing dispatched) if a precondition fails.
source "$(dirname "${BASH_SOURCE[0]}")/../lib/e3_common.sh"
B="$E3_AUTOMATION/baseline"; C="$E3_AUTOMATION/clio"
td=""; mode=""; cfg="$B/baseline_e3_config.env"; tprompt=""
while [[ $# -gt 0 ]]; do case "$1" in
  --trial-dir) td=${2:?}; shift 2;; --dry-run) mode=dry; shift;; --execute-counted) mode=counted; shift;;
  --config) cfg=${2:?}; shift 2;; --test-prompt) tprompt=${2:?}; shift 2;; -h|--help) sed -n '2,13p' "$0"; exit 0;;
  *) die "unknown argument: $1" 2;; esac; done
[[ -n "$td" && -n "$mode" ]] || die "need --trial-dir and --dry-run|--execute-counted" 2
td=$(e3_guard_trial_dir clio "$td") || exit $?; tid=$(trial_id_of clio "$td")
dry=0; [[ $mode == dry ]] && dry=1; export E3_DRY_RUN=$dry
# shellcheck disable=SC1090
source "$cfg"
: "${E3_ACCESS_MODEL:?}" "${E3_CLAUDE_MODEL:?}" "${E3_CONTROL_REPO_URL:?}" "${E3_CONTROL_COMMIT:?}" "${E3_GLOBUS_MODE:?}" "${E3_SESSION_TIMEOUT_SECONDS:?}"
[[ "$E3_ACCESS_MODEL" == procedural_researcher_only ]] || die "E3_ACCESS_MODEL must be procedural_researcher_only" 2
prompt="$B/baseline_e3_prompt.md"
if [[ -n "$tprompt" ]]; then [[ $E3_TEST_MODE == 1 ]] || die "--test-prompt is allowed only in test mode (E3_ROOT_OVERRIDE)" 2; prompt=$tprompt; fi
[[ $E3_TEST_MODE == 1 ]] && warn "TEST MODE (E3_ROOT_OVERRIDE=$E3_ROOT): scratch tree, not a counted trial"
checks=(); ck() { checks+=("$1 $2 $3"); log "check $1: $2 — $3"; }
ar() { action_required "$td" "$@"; }

# 1. allocation, node-local root, dedicated instance
home="$E3_RUNTIME_DIR/clio/$tid"; inst="$home/instance.json"
if nlr=$(e3_node_local_root); then ck allocation PASS "job $SLURM_JOB_ID, node-local root \$TMPDIR on $(hostname -s)"
elif [[ $dry == 1 ]]; then ck allocation INFO "not inside the trial allocation (required for --execute-counted)"
else ar slurm_allocation "Run inside this trial's allocation on its compute node (srun --jobid=<id> --overlap ...)."; fi
if [[ -f "$inst" ]]; then
  port=$(jq -r .port "$inst"); ihost=$(jq -r .host "$inst"); ijob=$(jq -r .slurm_job_id "$inst"); isd=$(jq -r .staging_dir "$inst")
  [[ "$ihost" == "$(hostname -s)" && "$ijob" == "${SLURM_JOB_ID:-}" ]] && ck instance PASS "dedicated instance for $tid on $ihost:$port (job $ijob)" \
    || { [[ $dry == 1 ]] && ck instance INFO "instance is on $ihost job $ijob (this host $(hostname -s))" || ar clio_instance_mismatch "instance.json says $ihost job $ijob; this is $(hostname -s) job ${SLURM_JOB_ID:-none}."; }
else
  [[ $dry == 1 ]] && ck instance ACTION "no dedicated instance yet ($inst); start it with start_e3_clio_server.sh" \
    || ar clio_instance_missing "No dedicated E3 CLIO instance for $tid ($inst). Start it per setup/CLIO_RUNBOOK.md §2."
fi
api() { curl --noproxy '*' -sS -m "${3:-30}" -H 'content-type: application/json' -H 'x-gact-version: 0.2' "${@:4}" -X "$1" "http://127.0.0.1:$port$2"; }
if [[ -n "${port:-}" && ( $dry == 0 || "$ihost" == "$(hostname -s)" ) ]]; then
  hc=$(curl --noproxy '*' -s -m 5 -o /dev/null -w '%{http_code}' "http://127.0.0.1:$port/v1/health"); [[ "$hc" == 200 ]] && ck clio_health PASS "200" || ar clio_unreachable "GET /v1/health on 127.0.0.1:$port returned '$hc'."
  [[ "$(jq -c '.mcp_servers' "$inst")" == "[]" && "$(sed -n 's/^mcp_servers: *//p' "$home/config/mcp.yaml")" == "{}" ]] && ck clio_no_mcp PASS "no MCP servers (no web search)" || ar clio_mcp_present "The dedicated instance must have no MCP servers."
  grep -q "^  model: $E3_CLAUDE_MODEL\$" "$home/config/config.yaml" && ck clio_model PASS "$E3_CLAUDE_MODEL" || ar clio_model_mismatch "config.yaml model is not $E3_CLAUDE_MODEL."
  nws=$(api GET /v1/workspaces 15 | jq '[.workspaces[]? // .[]?] | length' 2>/dev/null); nss=$(api GET /v1/sessions 15 | jq '[.sessions[]? // .[]?] | length' 2>/dev/null)
  [[ "$nss" == 0 ]] && ck clio_fresh PASS "0 sessions, ${nws:-?} workspace(s) on the instance" || ar clio_not_fresh "The instance already has ${nss:-?} session(s); a trial needs a fresh instance."
fi
# 2. GitHub, Globus, sources, workspace (identical to the baseline checks)
export GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=20 -o StrictHostKeyChecking=yes"
[[ "$E3_CONTROL_COMMIT" =~ ^[0-9a-f]{40}$ ]] || ar control_commit_unset "E3_CONTROL_COMMIT is not a 40-hex commit."
timeout 60 git ls-remote --quiet "$E3_CONTROL_REPO_URL" >/dev/null 2>&1 && ck control_repo PASS "readable noninteractively" || ar control_repo_unreadable "git ls-remote failed noninteractively."
[[ "$E3_GLOBUS_MODE" == globus ]] || ar globus_mandatory "Globus is mandatory for E3."
gcli="$E3_ROOT/${E3_GLOBUS_CLI_REL:-automation/environment/tools/globus-cli-3.43.0/bin/globus}"
gsrc=${E3_GLOBUS_COLLECTION_ID:?}; [[ $E3_TEST_MODE == 1 && -n "${E3_TEST_GLOBUS_SOURCE_ID:-}" ]] && gsrc=$E3_TEST_GLOBUS_SOURCE_ID
[[ -x "$gcli" ]] && timeout 60 "$gcli" whoami </dev/null >/dev/null 2>&1 && timeout 120 "$gcli" ls "$gsrc:${E3_TEST_GLOBUS_SOURCE_PREFIX:-}/" </dev/null >/dev/null 2>&1 \
  && ck globus PASS "collection $gsrc listable noninteractively" || ar globus_interactive_auth "Pinned Globus CLI cannot list $gsrc noninteractively."
"$E3_AUTOMATION/verify_readonly_sources.sh" >/dev/null 2>&1 && ck sources PASS "collections verify; archive write-protected" || ar sources_failed_verification "Read-only collections fail verification."
"$E3_AUTOMATION/init_trial_workspace.sh" --system clio --trial-dir "$td" --dry-run >/dev/null 2>&1 && ck workspace PASS "fresh" || die "trial workspace not fresh: $td (never reuse; record a new attempt)" 4
psha=$(sha256_of "$prompt"); sd_plan="${nlr:-<TMPDIR>}/e3/clio/$tid"
[[ -z "${isd:-}" || "$isd" == "$sd_plan" ]] || ar staging_mismatch "instance staging dir $isd differs from $sd_plan."
plan() { jq -n --arg tid "$tid" --arg td "$td" --arg mode "$mode" --argjson test "$E3_TEST_MODE" --arg model "$E3_CLAUDE_MODEL" --arg psha "$psha" \
  --arg url "$E3_CONTROL_REPO_URL" --arg commit "$E3_CONTROL_COMMIT" --arg gsrc "$gsrc" --arg gdst "$E3_GLOBUS_DEST_ID" --arg sd "$sd_plan" \
  --arg port "${port:-}" --arg am "$E3_ACCESS_MODEL" --argjson timeout "$E3_SESSION_TIMEOUT_SECONDS" --arg inst "$inst" \
  --argjson checks "$(printf '%s\n' "${checks[@]}" | jq -R . | jq -s .)" \
  '{trial_id:$tid, system:"clio", trial_dir:$td, mode:$mode, test_mode:($test==1), model:$model, prompt_sha256:$psha, control_repo_url:$url,
    control_commit:$commit, globus_source_collection:$gsrc, globus_destination_collection:$gdst, staging_dir:$sd, api:("http://127.0.0.1:"+$port),
    session_settings:{mode:"edit", approval_mode:"bypass", delivery:"start"}, permission_answers:"never", access_model:$am, sandbox_used:false,
    timeout_seconds:$timeout, instance_record:$inst, checks:$checks}' | redact_home; }
if [[ $dry == 1 ]]; then plan; log "DRY RUN complete: no files written, no session created, no model call"; exit 0; fi

# ======================= counted execution =======================
[[ "$(manifest_get "$td/manifest.yaml" e3dc_status)" == planned ]] || die "manifest status is not planned; refusing" 4
[[ -e "$sd_plan" ]] && die "staging directory already exists: $sd_plan (refusing reuse)" 4
clone=$("$B/prepare_baseline_trial.sh" --system clio --trial-dir "$td" --clone-root "$nlr/e3/_control" --staging-dir "$sd_plan" --config "$cfg" | tail -1) || exit $?
sd=$("$E3_AUTOMATION/init_node_local_staging.sh" --system clio --trial-dir "$td") || exit $?; [[ "$sd" == "$sd_plan" ]] || die "staging dir differs from plan" 1
"$E3_AUTOMATION/record_source_versions.sh" --trial-dir "$td" --control-dir "$clone" >/dev/null || die "source/version verification failed" 1
sess="$td/logs/session"; mkdir -p "$sess"; marker="$td/provenance/.trial_start_marker"; : > "$marker"
plan > "$sess/launch_plan.json"; cp -p "$prompt" "$sess/prompt.md"; echo "$psha  prompt.md" > "$sess/prompt.sha256"
redact_home < "$inst" > "$sess/clio_instance.json"; api GET /v1/capabilities 30 > "$sess/capabilities.json" 2>/dev/null || true
cp -p "$home/config/config.yaml" "$sess/clio_config.yaml"; cp -p "$home/config/mcp.yaml" "$sess/clio_mcp.yaml"
ws=$(api POST /v1/workspaces 30 -d "$(jq -n --arg n "$tid" --arg r "$td" '{name:$n, root_path:$r, metadata:{e3_trial_id:$n}}')") || die "workspace creation failed" 1
echo "$ws" > "$sess/workspace_created.json"; wid=$(jq -r '.id // .workspace_id' <<< "$ws")
sreq=$(jq -n --arg w "$wid" --arg t "$tid" --arg m "$E3_CLAUDE_MODEL" '{workspace_id:$w, title:$t, model:{provider_id:"claude_code", model_id:$m}, mode:"edit", approval_mode:"bypass", metadata:{e3_trial_id:$t}}')
echo "$sreq" > "$sess/session_request.json"
so=$(api POST /v1/sessions 30 -d "$sreq") || die "session creation failed" 1; echo "$so" > "$sess/session_created.json"
sid=$(jq -r '.id // .session_id' <<< "$so"); [[ "$sid" == sess_* ]] || die "unexpected session id '$sid'" 1
manifest_set "$td/manifest.yaml" e3dc_status running; manifest_set "$td/manifest.yaml" e3dc_session_id "$sid"
manifest_set "$td/manifest.yaml" e3dc_staging_dir "\"$(redact_home <<< "$sd")\""; manifest_set "$td/manifest.yaml" e3dc_model "$E3_CLAUDE_MODEL"
manifest_set "$td/manifest.yaml" e3dc_prompt_sha256 "$psha"; manifest_set "$td/manifest.yaml" e3dc_slurm_job_id "$SLURM_JOB_ID"
manifest_set "$td/manifest.yaml" e3dc_agent_executable "\"clio-agent $(jq -r .clio_agent_version "$inst")\""
( curl --noproxy '*' -sS -N -H 'x-gact-version: 0.2' "http://127.0.0.1:$port/v1/sessions/$sid/events" > "$sess/events.sse" 2> "$sess/events.stderr" ) & evpid=$!
start=$(utc_now); manifest_set "$td/manifest.yaml" e3dc_started_utc "$start"; t0=$(date +%s)
mreq=$(jq -n --rawfile p "$prompt" --arg id "$(cat /proc/sys/kernel/random/uuid)" '{parts:[{type:"text", text:$p}], client_message_id:$id, idempotency_key:$id, delivery:"start"}')
mo=$(api POST "/v1/sessions/$sid/messages" 60 -d "$mreq") || { kill $evpid 2>/dev/null; die "message dispatch failed" 1; }
echo "$mo" > "$sess/message_dispatched.json"; log "dispatched prompt to $sid ($tid)"
# wait: never answer permissions or questions; stop at idle/error/cancelled/waiting_*, or at the session limit
st=""; seen_run=0; tout=false; endreason=""
while :; do
  sleep 15; st=$(api GET "/v1/sessions/$sid" 30 | jq -r '.status // empty' 2>/dev/null)
  [[ "$st" == running ]] && seen_run=1
  case "$st" in error|cancelled) endreason=$st; break;; waiting_permission|waiting_user) endreason="stopped_$st"; break;;
    idle) [[ $seen_run == 1 || $(( $(date +%s) - t0 )) -gt 120 ]] && { endreason=finished_idle; break; };; esac
  if (( $(date +%s) - t0 >= E3_SESSION_TIMEOUT_SECONDS )); then tout=true; endreason=timeout; api POST "/v1/sessions/$sid/cancel" 30 -d '{}' > "$sess/cancel.json" 2>&1 || true; sleep 20; break; fi
done
end=$(utc_now); sleep 5; kill $evpid 2>/dev/null; wait $evpid 2>/dev/null
[[ $endreason == stopped_waiting_* ]] && { api POST "/v1/sessions/$sid/cancel" 30 -d '{}' > "$sess/cancel.json" 2>&1 || true; }
# retain the complete session record
api GET "/v1/sessions/$sid" 30 > "$sess/session_final.json" || true
api GET "/v1/sessions/$sid/export" 120 > "$sess/export.json" || true
api GET "/v1/sessions/$sid/messages?limit=100000&include_system=true" 120 > "$sess/messages.json" || true
api GET "/v1/sessions/$sid/trace" 120 > "$sess/trace.json" || true
api GET "/v1/sessions/$sid/interactions" 60 > "$sess/interactions.json" || true
api GET /v1/permissions 30 > "$sess/permissions_at_end.json" || true
mkdir -p "$sess/clio_server_files"
find "$home" -type f \( -name "$sid.json" -o -name "$sid*.jsonl" \) ! -path '*/config/*' -exec cp -p {} "$sess/clio_server_files/" \; 2>/dev/null
cp -p "$home/clio-server.log" "$sess/clio_server_files/clio-server.log" 2>/dev/null || true
# tool inputs in the baseline's format for the shared audit: {id,name,input}
jq -c '[.messages[]? // .[]?] | .[] | (.parts // [])[] | select(.type=="tool_call") | {id:(.call_id // .id), name:(.tool_name // .name), input:(.input // {})}' "$sess/messages.json" > "$sess/tool_inputs.jsonl" 2>/dev/null || : > "$sess/tool_inputs.jsonl"
nuser=$(jq '[.messages[]? // .[]?] | map(select(.role=="user")) | length' "$sess/messages.json" 2>/dev/null)
rc=0; [[ $endreason == finished_idle ]] || rc=1
jq -n --arg tid "$tid" --arg sid "$sid" --arg wid "$wid" --arg model "$E3_CLAUDE_MODEL" --arg psha "$psha" --arg commit "$E3_CONTROL_COMMIT" \
  --arg start "$start" --arg endt "$end" --arg reason "$endreason" --argjson tout "$tout" --arg host "$(hostname -s)" --arg job "$SLURM_JOB_ID" \
  --arg sd "$sd" --arg nuser "${nuser:-unknown}" --slurpfile inst "$sess/clio_instance.json" \
  '{trial_id:$tid, system:"clio", session_id:$sid, workspace_id:$wid, model:$model, prompt_sha256:$psha, control_commit:$commit,
    start_utc:$start, end_utc:$endt, end_reason:$reason, timeout_hit:$tout, host:$host, slurm_job_id:$job, staging_dir:$sd,
    user_messages_in_session:$nuser, approval_mode:"bypass", permissions_answered_by_runner:0,
    clio_agent_version:$inst[0].clio_agent_version, claude_agent_sdk_version:$inst[0].claude_agent_sdk_version,
    desktop_client_version:"record manually (setup/CLIO_RUNBOOK.md §4)"}' | redact_home > "$sess/session_record.json"
record_command "$td" "$rc" clio-session "$sid" "<prompt.md>"
# post-session records and verification (shared with the baseline)
"$E3_AUTOMATION/record_staging_snapshot.sh" --trial-dir "$td" --staging "$sd" || true
"$E3_AUTOMATION/record_output_provenance.sh" --trial-dir "$td" >/dev/null || true
if "$E3_AUTOMATION/verify_readonly_sources.sh" > "$td/provenance/sources_after_trial.txt" 2>&1; then su=true; else su=false; fi
"$E3_AUTOMATION/audit_boundary.sh" --system clio --trial-dir "$td" --since "$marker" --staging "$sd" >/dev/null; arc=$?
av=$(sed -n 's/^verdict: //p' "$td/provenance/boundary_audit.txt")
"$C/collect_clio_metrics.sh" --trial-dir "$td" >/dev/null || warn "metrics collection failed"
manifest_set "$td/manifest.yaml" e3dc_finished_utc "$end"; manifest_set "$td/manifest.yaml" e3dc_exit_status "$rc"
manifest_set "$td/manifest.yaml" e3dc_boundary_audit "${av:-unknown}"; manifest_set "$td/manifest.yaml" e3dc_sources_unchanged "$su"
manifest_set "$td/manifest.yaml" e3dc_status "$([[ $E3_TEST_MODE == 1 ]] && echo test_completed || echo awaiting_scoring)"
"$B/verify_baseline_trial.sh" --system clio --trial-dir "$td" --completed > "$td/provenance/verification.txt" 2>&1 || true
log "CLIO session $sid ended: $endreason (user messages in session: ${nuser:-?}) audit=${av:-unknown} sources_unchanged=$su"
[[ $su == true && $arc -eq 0 ]] || exit 1
exit $rc
