#!/usr/bin/env bash
# Run ONE E3 baseline trial: a completely new, fully headless Claude Code process in a fresh trial workspace.
# Usage: run_baseline_e3_trial.sh --trial-dir <E3>/baseline/trial_NN (--dry-run | --execute-counted)
#          [--config FILE] [--accept-legacy-agent-inputs]
#   --dry-run          read-only: run every check that needs no allocation and no model call, print the launch plan; writes nothing
#   --execute-counted  launch the counted trial. Must be run INSIDE a Slurm allocation on the agent-host node
#                      (e.g. the body of an sbatch job with the frozen agent-host contract); this script never calls sbatch.
# Stops with exit 3 and logs/ACTION_REQUIRED_<code>.md (nothing launched) when: not inside an allocation, per-job $TMPDIR
# unusable, pinned Claude Code missing or not authenticated headlessly, control repository unreadable noninteractively,
# Globus not configured/needs interactive login (Globus is mandatory; the former posix_readonly_fallback is refused),
# required headless flags missing, or the read-only sources fail verification.
# Never accesses researcher_only/, completed Example 8 materials, E1/E2 directories or the obsolete ThesisExperiments tree.
# Access model (E3_ACCESS_MODEL=procedural_researcher_only, same as E1/E2): the agent is launched directly (no sandbox);
# researcher-only material is kept out of agent-inputs/, prohibited by the prompt and protocol, and audited afterwards.
# This is procedural, not a technically enforced filesystem boundary; the session and its Slurm jobs run under this account.
source "$(dirname "${BASH_SOURCE[0]}")/../lib/e3_common.sh"
B="$E3_AUTOMATION/baseline"
td=""; mode=""; cfg="$B/baseline_e3_config.env"; legacy=()
while [[ $# -gt 0 ]]; do case "$1" in
  --trial-dir) td=${2:?}; shift 2;; --dry-run) mode=dry; shift;; --execute-counted) mode=counted; shift;; --config) cfg=${2:?}; shift 2;;
  --accept-legacy-agent-inputs) legacy=(--accept-legacy-agent-inputs); shift;;
  -h|--help) sed -n '2,13p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -n "$td" && -n "$mode" ]] || die "need --trial-dir and --dry-run|--execute-counted" 2
td=$(e3_guard_trial_dir baseline "$td") || exit $?; tid=$(trial_id_of baseline "$td")
dry=0; [[ $mode == dry ]] && dry=1; export E3_DRY_RUN=$dry
if [[ ! -f "$cfg" ]]; then
  [[ $dry == 1 ]] || action_required "$td" config_missing "Config $cfg not found. Copy baseline_e3_config.env.example to baseline_e3_config.env and set the pinned commit."
  cfg="$B/baseline_e3_config.env.example"; warn "dry run uses the example config"
fi
# shellcheck disable=SC1090
source "$cfg"
export E3_ALLOW_ACCOUNT_NAME_IN_TMPDIR="${E3_ALLOW_ACCOUNT_NAME_IN_TMPDIR:-0}"
: "${E3_ACCESS_MODEL:?config: E3_ACCESS_MODEL}" "${E3_CLAUDE_PIN_VERSION:?}" "${E3_CLAUDE_BIN_REL:?}" "${E3_CLAUDE_MODEL:?}" "${E3_CONTROL_REPO_URL:?}" "${E3_CONTROL_COMMIT:?}" "${E3_GLOBUS_MODE:?}" "${E3_SESSION_TIMEOUT_SECONDS:?}"
[[ $mode == counted && $E3_TEST_MODE == 1 ]] && warn "TEST MODE (E3_ROOT_OVERRIDE=$E3_ROOT): scratch tree, not a counted trial"
checks=()
ck() { checks+=("$1 $2 $3"); log "check $1: $2 — $3"; }
[[ "$E3_ACCESS_MODEL" == procedural_researcher_only ]] || die "E3_ACCESS_MODEL must be procedural_researcher_only (got '$E3_ACCESS_MODEL')" 2
ck access_model INFO "procedural_researcher_only: prohibited by prompt/protocol and audited; not technically enforced (no sandbox)"

# ---- 1. allocation and node-local storage --------------------------------------------------------
if nlr=$(e3_node_local_root); then ck allocation PASS "job $SLURM_JOB_ID, node-local root \$TMPDIR on $(hostname -s)"
elif [[ $dry == 1 ]]; then ck allocation INFO "not inside an allocation (required for --execute-counted)"
else action_required "$td" slurm_allocation \
"--execute-counted must run inside a Slurm allocation on the agent-host node with the per-job node-local \$TMPDIR (SLURM_JOB_ID='${SLURM_JOB_ID:-}', TMPDIR='${TMPDIR:-}').
A researcher submits the agent-host job; for example a batch script with the frozen contract
  #SBATCH --account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00
whose body is:  $B/run_baseline_e3_trial.sh --trial-dir $td --execute-counted"; fi

# ---- 2. pinned Claude Code executable and headless flags ------------------------------------------
if [[ $E3_TEST_MODE == 1 && -n "${E3_TEST_CLAUDE_BIN:-}" ]]; then bin=$E3_TEST_CLAUDE_BIN; bin_rec="TEST:$E3_TEST_CLAUDE_BIN"
else bin="$HOME/$E3_CLAUDE_BIN_REL"; bin_rec="\$HOME/$E3_CLAUDE_BIN_REL"; fi
ver=$( [[ -x "$bin" ]] && DISABLE_AUTOUPDATER=1 "$bin" --version 2>/dev/null | awk '{print $1}')
if [[ "$ver" == "$E3_CLAUDE_PIN_VERSION" ]]; then ck claude_pinned PASS "$bin_rec = $ver"
else action_required "$td" claude_executable "Pinned Claude Code $E3_CLAUDE_PIN_VERSION not found at $bin_rec (found version '${ver:-none}')."; fi
bin_sha=$(sha256_of "$(readlink -f "$bin")")
help=$(DISABLE_AUTOUPDATER=1 "$bin" --help 2>/dev/null); missing=""
for f in --print --output-format --model --session-id --dangerously-skip-permissions --verbose --disable-slash-commands --no-chrome; do grep -q -- "$f" <<< "$help" || missing+=" $f"; done
[[ -z "$missing" ]] && ck headless_flags PASS "all required flags present in --help" || action_required "$td" claude_flags "flags missing from $bin_rec --help:$missing"

# ---- 3. control repository (noninteractive) ------------------------------------------------------
export GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=20 -o StrictHostKeyChecking=yes"
[[ "$E3_CONTROL_COMMIT" =~ ^[0-9a-f]{40}$ ]] || action_required "$td" control_commit_unset "E3_CONTROL_COMMIT in $cfg is not a 40-hex commit."
if timeout 60 git ls-remote --quiet "$E3_CONTROL_REPO_URL" >/dev/null 2>&1; then ck control_repo PASS "$E3_CONTROL_REPO_URL readable noninteractively"
else action_required "$td" control_repo_unreadable "git ls-remote $E3_CONTROL_REPO_URL failed noninteractively."; fi

# ---- 4. Globus ---------------------------------------------------------------------------------------------
case "$E3_GLOBUS_MODE" in
  globus)
    if [[ -z "${E3_GLOBUS_COLLECTION_ID:-}" ]]; then action_required "$td" globus_not_configured "E3_GLOBUS_MODE=globus but E3_GLOBUS_COLLECTION_ID is empty. See setup/GLOBUS_ACTION_REQUIRED.md, or set E3_GLOBUS_MODE=posix_readonly_fallback as a recorded researcher decision."
    elif gcli="$E3_ROOT/${E3_GLOBUS_CLI_REL:-automation/environment/tools/globus-cli-3.43.0/bin/globus}"; [[ ! -x "$gcli" ]] || \
         ! timeout 60 "$gcli" whoami </dev/null >/dev/null 2>&1 || ! timeout 120 "$gcli" ls "$E3_GLOBUS_COLLECTION_ID:/" </dev/null >/dev/null 2>&1; then
      action_required "$td" globus_interactive_auth "Pinned Globus CLI ($gcli) missing or cannot list collection $E3_GLOBUS_COLLECTION_ID noninteractively (login/consent/MFA needed)."
    else ck globus PASS "collection $E3_GLOBUS_COLLECTION_ID listable noninteractively ($("$gcli" version 2>/dev/null | sed -n 's/^Installed version: *//p'))"; fi;;
  posix_readonly_fallback)   # withdrawn 2026-10-10: Globus is a required distinct storage location for E3 (researcher decision)
    action_required "$td" globus_mandatory "E3_GLOBUS_MODE=posix_readonly_fallback is no longer accepted: Globus is a required distinct read-only storage location for E3, and direct local reading is not an equivalent fallback. Configure the private collection (setup/RESEARCHER_ACTION_REQUIRED.md).";;
  *) die "E3_GLOBUS_MODE must be globus or posix_readonly_fallback" 2;;
esac

# ---- 5. read-only sources ------------------------------------------------------------------------------
if "$E3_AUTOMATION/verify_readonly_sources.sh" >/dev/null 2>&1; then ck sources PASS "collections verify against manifests; archive write-protected"
else action_required "$td" sources_failed_verification "Read-only collections fail verification (automation/verify_readonly_sources.sh). Do not run trials until resolved."; fi

# ---- 6. workspace freshness --------------------------------------------------------------------------
"$E3_AUTOMATION/init_trial_workspace.sh" --system baseline --trial-dir "$td" --dry-run >/dev/null 2>&1 && ck workspace PASS "fresh" || die "trial workspace not fresh: $td" 4
[[ -d "$td/agent_inputs" && ${#legacy[@]} -eq 0 ]] && { [[ $dry == 1 ]] && ck legacy_agent_inputs ACTION "legacy agent_inputs/ present; counted run needs a researcher decision" || action_required "$td" legacy_agent_inputs_present "Legacy agent_inputs/ is present in $td; see prepare_baseline_trial.sh --help."; }

psha=$(sha256_of "$B/baseline_e3_prompt.md"); sid=$(cat /proc/sys/kernel/random/uuid)
cfgdir="$E3_RUNTIME_DIR/baseline/$tid/claude_config"
sd_plan="${nlr:-<TMPDIR>}/e3/baseline/$tid"
cmd=("$bin" --print --verbose --output-format stream-json --model "$E3_CLAUDE_MODEL" --dangerously-skip-permissions
     --session-id "$sid" --disable-slash-commands --no-chrome -- "$(cat "$B/baseline_e3_prompt.md")")
plan() { jq -n --arg tid "$tid" --arg td "$td" --arg bin "$bin_rec" --arg ver "$ver" --arg bsha "$bin_sha" --arg model "$E3_CLAUDE_MODEL" \
  --arg psha "$psha" --arg url "$E3_CONTROL_REPO_URL" --arg commit "$E3_CONTROL_COMMIT" --arg gm "$E3_GLOBUS_MODE" --arg sd "$sd_plan" \
  --arg cfg "$cfgdir" --arg sid "$sid" --arg mode "$mode" --arg am "$E3_ACCESS_MODEL" --argjson timeout "$E3_SESSION_TIMEOUT_SECONDS" --argjson test "$E3_TEST_MODE" \
  --argjson checks "$(printf '%s\n' "${checks[@]}" | jq -R . | jq -s .)" \
  '{trial_id:$tid, trial_dir:$td, mode:$mode, test_mode:($test==1), executable:$bin, executable_version:$ver, executable_sha256:$bsha,
    model:$model, model_settings:"harness defaults (no temperature/token/effort overrides); settings.json model pinned", prompt_sha256:$psha,
    control_repo_url:$url, control_commit:$commit, globus_mode:$gm, access_model:$am, sandbox_used:false, staging_dir:$sd, claude_config_dir:$cfg, session_id:$sid,
    timeout_seconds:$timeout, argv_flags:["--print","--verbose","--output-format","stream-json","--model",$model,"--dangerously-skip-permissions","--session-id",$sid,"--disable-slash-commands","--no-chrome","--","<baseline_e3_prompt.md>"],
    environment:{DISABLE_AUTOUPDATER:"1",CLAUDE_CODE_DISABLE_AUTO_MEMORY:"1",CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC:"1",CLAUDE_CONFIG_DIR:$cfg,E3_TRIAL_ID:$tid,E3_TRIAL_ROOT:$td,E3_STAGING_DIR:$sd,inherited_CLAUDE_vars:"scrubbed"},
    never_used:["--resume","--continue","--fork-session"], checks:$checks}' | redact_home; }
if [[ $dry == 1 ]]; then
  prepare_out=$("$B/prepare_baseline_trial.sh" --trial-dir "$td" --clone-root "/nonexistent-dry-run" --config "$cfg" "${legacy[@]}" --dry-run 2>&1) || true
  printf '%s\n' "$prepare_out" | sed 's/^/  prepare: /'
  plan; log "DRY RUN complete: no files written, no model call, no Slurm submission"; exit 0
fi

# ======================= counted execution (inside the allocation) =======================
[[ "$(manifest_get "$td/manifest.yaml" e3dc_status 2>/dev/null)" =~ ^(planned|)$ ]] || die "manifest status is not planned; refusing" 4
[[ -e "$sd_plan" ]] && die "staging directory already exists: $sd_plan (refusing reuse)" 4
clone=$("$B/prepare_baseline_trial.sh" --trial-dir "$td" --clone-root "$nlr/e3/_control" --staging-dir "$sd_plan" --config "$cfg" "${legacy[@]}" | tail -1) || exit $?
sd=$("$E3_AUTOMATION/init_node_local_staging.sh" --system baseline --trial-dir "$td") || exit $?
[[ "$sd" == "$sd_plan" ]] || die "staging dir differs from plan ($sd vs $sd_plan)" 1
"$E3_AUTOMATION/record_source_versions.sh" --trial-dir "$td" --control-dir "$clone" > /dev/null || die "source/version verification failed" 1
sess="$td/logs/session"; mkdir -p "$sess"
marker="$td/provenance/.trial_start_marker"; : > "$marker"
plan > "$sess/launch_plan.json"
{ echo "# exact headless launch argv (shell-quoted); cwd=$td"; printf '%q ' "${cmd[@]}"; echo; } | redact_home > "$sess/launch_command.txt"
echo "$psha  baseline_e3_prompt.md" > "$sess/prompt.sha256"; cp -p "$B/baseline_e3_prompt.md" "$sess/prompt.md"
# isolated per-session Claude configuration (outside the trial workspace; credential copy removed after the session)
mkdir -p "$cfgdir"; chmod 700 "$E3_RUNTIME_DIR" "$cfgdir"
if [[ $E3_TEST_MODE != 1 ]]; then
  [[ -f "$HOME/.claude/.credentials.json" ]] || action_required "$td" claude_credentials "No Claude Code credentials file in \$HOME/.claude/."
  install -m 600 "$HOME/.claude/.credentials.json" "$cfgdir/.credentials.json"
fi
printf '{"hasCompletedOnboarding": true, "autoUpdates": false, "bypassPermissionsModeAccepted": true}\n' > "$cfgdir/.claude.json"
printf '{"model": "%s"}\n' "$E3_CLAUDE_MODEL" > "$cfgdir/settings.json"
for v in $(env | sed -n 's/^\(CLAUDE[A-Z0-9_]*\)=.*/\1/p'); do unset "$v"; done
export DISABLE_AUTOUPDATER=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export CLAUDE_CONFIG_DIR="$cfgdir" E3_TRIAL_ID="$tid" E3_TRIAL_ROOT="$td" E3_STAGING_DIR="$sd" E3_SYSTEM=baseline
auth=$("$bin" auth status --json 2>/dev/null || true); echo "$auth" | jq '{loggedIn, authMethod}' > "$sess/auth_status.json" 2>/dev/null || echo '{}' > "$sess/auth_status.json"
if [[ "$(jq -r '.loggedIn // false' <<< "$auth" 2>/dev/null)" != true ]]; then
  rm -f -- "$cfgdir/.credentials.json"; action_required "$td" claude_auth "Claude Code is not authenticated headlessly in the isolated config dir (auth status loggedIn != true)."
fi
manifest_set "$td/manifest.yaml" e3dc_status running
manifest_set "$td/manifest.yaml" e3dc_staging_dir "\"$(redact_home <<< "$sd")\""
manifest_set "$td/manifest.yaml" e3dc_agent_executable "\"$bin_rec\""
manifest_set "$td/manifest.yaml" e3dc_agent_version "\"$ver\""
manifest_set "$td/manifest.yaml" e3dc_model "$E3_CLAUDE_MODEL"
manifest_set "$td/manifest.yaml" e3dc_prompt_sha256 "$psha"
manifest_set "$td/manifest.yaml" e3dc_session_id "$sid"
manifest_set "$td/manifest.yaml" e3dc_slurm_job_id "$SLURM_JOB_ID"
start=$(utc_now); manifest_set "$td/manifest.yaml" e3dc_started_utc "$start"
log "launching headless session $sid for $tid"
( cd "$td" && timeout --foreground -k 60 "$E3_SESSION_TIMEOUT_SECONDS" "${cmd[@]}" < /dev/null > "$sess/stream.jsonl" 2> "$sess/stderr.log" ); rc=$?
end=$(utc_now)
record_command "$td" "$rc" claude --print --session-id "$sid" "<baseline_e3_prompt.md>"
rm -f -- "$cfgdir/.credentials.json"
tr=$(find "$cfgdir/projects" -name "$sid.jsonl" -print -quit 2>/dev/null || true)
[[ -n "$tr" ]] && cp -p "$tr" "$sess/transcript_$sid.jsonl" || warn "no transcript found"
jq -c 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | {id, name, input}' "$sess/stream.jsonl" > "$sess/tool_inputs.jsonl" 2>/dev/null || true
grep -E '"type" *: *"result"' "$sess/stream.jsonl" | tail -1 > "$sess/result.json" 2>/dev/null || true
tout=false; [[ $rc -eq 124 || $rc -eq 137 ]] && tout=true
jq -n --arg tid "$tid" --arg sid "$sid" --arg bin "$bin_rec" --arg ver "$ver" --arg bsha "$bin_sha" --arg model "$E3_CLAUDE_MODEL" --arg psha "$psha" \
  --arg commit "$E3_CONTROL_COMMIT" --arg start "$start" --arg endt "$end" --argjson rc "$rc" --argjson tout "$tout" --arg host "$(hostname -s)" \
  --arg job "$SLURM_JOB_ID" --arg sd "$sd" --arg am "$E3_ACCESS_MODEL" '{trial_id:$tid, session_id:$sid, executable:$bin, executable_version:$ver, executable_sha256:$bsha,
  model:$model, prompt_sha256:$psha, control_commit:$commit, start_utc:$start, end_utc:$endt, exit_code:$rc, timeout_hit:$tout, host:$host,
  slurm_job_id:$job, staging_dir:$sd, access_model:$am, sandbox_used:false, resume_used:false, continue_used:false, fork_used:false}' | redact_home > "$sess/session_record.json"

# ---- post-session records and verification (all read-only on sources) ----
"$E3_AUTOMATION/record_staging_snapshot.sh" --trial-dir "$td" --staging "$sd" || true
"$E3_AUTOMATION/record_output_provenance.sh" --trial-dir "$td" >/dev/null || true
if "$E3_AUTOMATION/verify_readonly_sources.sh" > "$td/provenance/sources_after_trial.txt" 2>&1; then su=true; else su=false; fi
"$E3_AUTOMATION/audit_boundary.sh" --system baseline --trial-dir "$td" --since "$marker" --staging "$sd" > /dev/null; arc=$?
av=$(sed -n 's/^verdict: //p' "$td/provenance/boundary_audit.txt")
"$B/collect_baseline_metrics.sh" --trial-dir "$td" > /dev/null || warn "metrics collection failed"
manifest_set "$td/manifest.yaml" e3dc_finished_utc "$end"
manifest_set "$td/manifest.yaml" e3dc_exit_status "$rc"
manifest_set "$td/manifest.yaml" e3dc_boundary_audit "${av:-unknown}"
manifest_set "$td/manifest.yaml" e3dc_sources_unchanged "$su"
manifest_set "$td/manifest.yaml" e3dc_status "$([[ $E3_TEST_MODE == 1 ]] && echo test_completed || echo awaiting_scoring)"
"$B/verify_baseline_trial.sh" --trial-dir "$td" --completed > "$td/provenance/verification.txt" 2>&1 || true
log "session $sid ended rc=$rc timeout=$tout audit=${av:-unknown} sources_unchanged=$su"
[[ $su == true && $arc -eq 0 ]] || exit 1
exit "$rc"
