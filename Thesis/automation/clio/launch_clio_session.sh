#!/usr/bin/env bash
# Run ONE CLIO session on a completely fresh, dedicated CLIO deployment: the CLIO counterpart of ../launch_headless_claude.sh.
# Usage: launch_clio_session.sh --trial-dir D --run-id ID --session-label LABEL --prompt-file P
#          (--dry-run | --execute-counted | --validate-deployment) [--via-slurm | --local] [--evidence-dir E] [--extra-env F]
#   --dry-run              write the launch plan only: no deployment, no model call, no sbatch
#   --execute-counted      real session (refused while clio_trial_config.env has TBD placeholders or pins do not verify)
#   --validate-deployment  start the deployment, create a workspace+session, read every setting back, stop. NO message is
#                          sent (no model call). Writes only to --evidence-dir and THESIS_CLIO_RUNTIME_ROOT (both required)
#   --via-slurm            wrap in an sbatch job with the baseline's frozen agent-host contract and wait (default for counted)
#   --local                run in the current allocation (used inside the sbatch wrapper)
#   --extra-env F          KEY=VALUE lines exported into the deployment (inherited by CLIO's shell tool); used by E3 for
#                          E3_TRIAL_ID / E3_TRIAL_ROOT / E3_STAGING_DIR / E3_SYSTEM, exactly as the E3 baseline exports them
# Fresh-session guarantees (mirroring the baseline's): new CLIO_AGENT_HOME per session (no workspaces, sessions, memory or
# traces), isolated CLAUDE_CONFIG_DIR per session (credentials copy, removed at the end), one new CLIO session, one prompt,
# never resumed. The deployment lives in $THESIS_ROOT/.agent_runtime/<run_id>/<label>/ (the baseline's per-session location).
source "$(dirname "${BASH_SOURCE[0]}")/lib/clio_common.sh"
td=""; rid=""; label=""; pf=""; mode=""; via=slurm; ev=""; xenv=""
while [[ $# -gt 0 ]]; do case "$1" in
  --trial-dir) td=${2:?}; shift 2;; --run-id) rid=${2:?}; shift 2;; --session-label) label=${2:?}; shift 2;; --prompt-file) pf=${2:?}; shift 2;;
  --dry-run) mode=dry; shift;; --execute-counted) mode=counted; shift;; --validate-deployment) mode=validate; shift;;
  --via-slurm) via=slurm; shift;; --local) via=local; shift;; --evidence-dir) ev=${2:?}; shift 2;; --extra-env) xenv=$(readlink -f "${2:?}"); shift 2;;
  -h|--help) sed -n '2,17p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -n "$td" && -n "$rid" && -n "$label" && -n "$mode" ]] || die "missing required arguments (see --help)" 2
[[ $mode == validate || -f "$pf" ]] || die "prompt file not found: $pf" 2
td=$(cd "$td" && pwd -P) || die "trial dir not found" 2
[[ "$label" =~ ^[a-z0-9_]+$ ]] || die "session label must be [a-z0-9_]+" 2
require_cmd jq curl python3 timeout
if [[ $mode == validate ]]; then
  [[ -n "$ev" && -n "${THESIS_CLIO_RUNTIME_ROOT:-}" ]] || die "--validate-deployment needs --evidence-dir and THESIS_CLIO_RUNTIME_ROOT outside the trial records" 2
  case "$ev" in "$RESEARCHER_ONLY"*|"$RUNS_DIR"*) die "validation evidence must not go into researcher_only/ or runs/" 2;; esac
fi
# --- pins (fail closed for counted runs) -----------------------------------------------------------------------------
ph=$(clio_placeholders | paste -sd' ' -)
cli=$(clio_cli_bin); cliver=$(claude_version_of "$cli" 2>/dev/null)
inst=$(clio_installed_version)
if [[ $mode == counted ]]; then
  [[ -z "$ph" ]] || die "clio_trial_config.env still has placeholders: $ph (counted run refused)" 3
  [[ "$inst" == "$CLIO_AGENT_VERSION_PIN" ]] || die "installed clio-agent $inst != pin $CLIO_AGENT_VERSION_PIN" 3
fi
[[ "$cliver" == "$CLIO_CLAUDE_CLI_PIN" ]] || { [[ $mode == dry ]] && warn "pinned Claude Code CLI $CLIO_CLAUDE_CLI_PIN not verified at $cli" || die "pinned Claude Code CLI $CLIO_CLAUDE_CLI_PIN not available at $cli" 3; }
bp_id=$CLIO_BLUEPRINT_ID; bp_ver=$CLIO_BLUEPRINT_VERSION
[[ $mode == counted || "$bp_id" != TBD* ]] || bp_id=${THESIS_CLIO_VALIDATE_BLUEPRINT:-factorio-flat}   # dry/validate: render with the pilot blueprint
# --- evidence and deployment locations --------------------------------------------------------------------------------
if [[ -z "$ev" ]]; then if [[ $mode == dry ]]; then ev="$SESSION_EVIDENCE_ROOT/$rid/dryrun_$(date -u +%Y%m%dT%H%M%SZ)/$label"; else ev="$SESSION_EVIDENCE_ROOT/$rid/$label"; fi; fi
[[ $mode == counted && -e "$ev/session_record.json" ]] && die "session evidence already exists: $ev (refusing to overwrite)" 4
mkdir -p "$ev"; chmod 700 "$ev" 2>/dev/null || true
dep="$CLIO_RUNTIME_ROOT/$rid/$label"; home="$dep/clio_home"; cfg="$dep/claude_config"; shim="$dep/bin"
[[ "$(readlink -f "$pf" 2>/dev/null)" == "$(readlink -f "$ev/prompt.md" 2>/dev/null)" || $mode == validate ]] || cp -p "$pf" "$ev/prompt.md"
psha=""; [[ $mode == validate ]] || { psha=$(sha256_of "$pf"); echo "$psha  $(basename "$pf")" > "$ev/prompt.sha256"; }
runner=(python3 -u "$CLIO_LIB/clio_session_runner.py" --port '<port>' --trial-dir "$td" --evidence-dir "$ev" --run-id "$rid" --label "$label"
        --model "$CLAUDE_MODEL" --approval "$CLIO_APPROVAL_MODE" --effort "$CLIO_EFFORT" --blueprint-id "$bp_id" --blueprint-version "$bp_ver"
        --timeout-s "$AGENT_SESSION_TIMEOUT_SECONDS" --max-nudges "$CLIO_MAX_NUDGES" --poll-s "$CLIO_POLL_SECONDS")
[[ $mode == validate ]] && runner+=(--validate-only) || runner+=(--prompt-file "$ev/prompt.md")
{ echo "# exact runner command (argv, shell-quoted); <port> is chosen free on the node at start; cwd=$td"; printf '%q ' "${runner[@]}"; echo; } > "$ev/launch_command.txt"
cat > "$ev/launch_env.txt" <<EOF
CLIO_PREFIX=$CLIO_PREFIX
CLIO_AGENT_HOME=$home
CLIO_BIN_DIR=$CLIO_PREFIX/bin
CLIO_ALLOWED_ROOTS=$td:$home:\$TMPDIR
CLIO_NO_UPDATE_CHECK=1
CLIO_STREAM_AUDIT_LOG=$home/state/stream_audit.jsonl
CLIO_CLAUDE_CODE_STREAM_IDLE_TTL_S=$CLIO_CLAUDE_CODE_STREAM_IDLE_TTL_S
CLIO_MCP_CALL_TIMEOUT_S=$CLIO_MCP_CALL_TIMEOUT_S
CLIO_GACT_TURN_TIMEOUT_S=$CLIO_GACT_TURN_TIMEOUT_S
core_isolation=$CLIO_CORE_ISOLATION   (private: CLIO_RUNTIME_STATE_DIR=$dep/core_state, CLIO_CORE_PORT=<free 19400-19499>)
PATH=$shim:<inherited>   (claude -> $cli, version $CLIO_CLAUDE_CLI_PIN)
DISABLE_AUTOUPDATER=1
CLAUDE_CODE_DISABLE_AUTO_MEMORY=1
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
CLAUDE_CONFIG_DIR=$cfg
THESIS_TRIAL_ID=$rid
THESIS_SESSION_LABEL=$label
cwd=$td
timeout_seconds=$AGENT_SESSION_TIMEOUT_SECONDS
mcp_policy=$CLIO_MCP_POLICY
inherited CLAUDE* and CLIO* variables: scrubbed
extra_env_file=${xenv:-none}
EOF
[[ -n "$xenv" ]] && { grep -E '^[A-Z][A-Z0-9_]*=' "$xenv" >> "$ev/launch_env.txt"; }
plan() { jq -n --arg rid "$rid" --arg lbl "$label" --arg td "$td" --arg mode "$mode" --arg via "$via" --arg ev "$ev" --arg dep "$dep" \
   --arg psha "$psha" --arg inst "$inst" --arg cli "$cli" --arg cliver "$cliver" --arg model "$CLAUDE_MODEL" --arg bp "$bp_id" --arg bpv "$bp_ver" \
   --arg ph "$ph" --arg utc "$(utc_now)" --argjson cfgj "$(clio_config_json)" --argjson cmd "$(printf '%s\n' "${runner[@]}" | jq -R . | jq -s .)" \
   '{run_id:$rid, session_label:$lbl, system:"clio", trial_dir:$td, mode:$mode, via:$via, evidence_dir:$ev, deployment_dir:$dep,
     prompt_sha256:$psha, clio_agent_installed:$inst, claude_cli:$cli, claude_cli_version:$cliver, model:$model,
     blueprint:{id:$bp, version:$bpv}, placeholders_unresolved:($ph|split(" ")|map(select(length>0))), planned_utc:$utc,
     clio_config:$cfgj, runner_argv:$cmd,
     fresh_session_guarantees:["new CLIO deployment state (CLIO_AGENT_HOME) per session","isolated CLAUDE_CONFIG_DIR per session",
       "one new CLIO workspace + session","prompt file sent verbatim as the only user message","no resume, no session reuse"]}'; }
if [[ $mode == dry ]]; then plan > "$ev/launch_plan.json"; log "DRY RUN: no deployment, no model call, no sbatch. Plan: $ev/launch_plan.json"; cat "$ev/launch_command.txt"; exit 0; fi

# ====================== deployment (counted or validation) ======================
if [[ "$via" == slurm ]]; then
  plan > "$ev/launch_plan.json"; sb="$ev/agent_host.sbatch"
  flag=--execute-counted; [[ $mode == validate ]] && flag=--validate-deployment
  cat > "$sb" <<EOF
#!/bin/bash -l
#SBATCH --job-name=clio_${rid}_${label}
#SBATCH --account=$SLURM_ACCOUNT
#SBATCH --partition=$SLURM_PARTITION
#SBATCH --nodes=$SLURM_NODES
#SBATCH --ntasks=$SLURM_NTASKS
#SBATCH --cpus-per-task=$SLURM_CPUS
#SBATCH --mem=$SLURM_MEM
#SBATCH --time=$SLURM_TIME
#SBATCH --output=$ev/agent_host_%j.out
#SBATCH --error=$ev/agent_host_%j.err
# Agent-host job (the baseline's frozen contract). Runs exactly one CLIO deployment and one CLIO session.
echo "agent_host_job=\$SLURM_JOB_ID node=\$(hostname -s) start_utc=\$(date -u +%FT%TZ)"
export THESIS_CLIO_RUNTIME_ROOT="$CLIO_RUNTIME_ROOT"
exec "$CLIO_AUTOMATION_DIR/launch_clio_session.sh" --trial-dir "$td" --run-id "$rid" --session-label "$label" --prompt-file "$ev/prompt.md" $flag --local --evidence-dir "$ev" ${xenv:+--extra-env "$xenv"}
EOF
  [[ $mode == validate ]] && sed -i 's#--prompt-file "[^"]*" ##' "$sb"
  log "submitting agent-host job for $rid/$label (sbatch --wait)"; echo "$(utc_now) sbatch --wait --parsable $sb" >> "$ev/submissions.log"
  jid=$(sbatch --wait --parsable "$sb"); src=$?; echo "$jid" > "$ev/agent_host_job_id.txt"; echo "$(utc_now) sbatch returned rc=$src job=$jid" >> "$ev/submissions.log"
  sacct -j "$jid" --parsable2 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,TotalCPU,NodeList > "$ev/agent_host_sacct.psv" 2>/dev/null || true
  [[ -f "$ev/session_record.json" ]] || die "agent-host job $jid ended without a session record (see $ev/agent_host_$jid.err)" 1
  jq -r '"session \(.session_id) rc=\(.exit_code) end=\(.end_reason) timeout_hit=\(.timeout_hit) cli=\(.executable_version)"' "$ev/session_record.json"
  exit "$(jq -r '.exit_code' "$ev/session_record.json")"
fi
# ---- local execution (inside the agent-host job, or an existing allocation with --local) ----
[[ -n "${SLURM_JOB_ID:-}" ]] || die "--local must run inside a Slurm allocation (never on a login node)" 3
[[ -e "$dep" ]] && die "deployment state already exists: $dep (one fresh deployment per session; never reused)" 4
mkdir -p "$home"/{config,data,state,cache} "$cfg" "$shim"; chmod 700 "$CLIO_RUNTIME_ROOT" "$dep" "$cfg" 2>/dev/null || true
# CLIO config: the installed user config (provider claude_code, model, installed blueprints) minus workspaces, paths rewritten
rsync -a --exclude workspaces.json --exclude '.clio-registry-staging' "$CLIO_PREFIX/user/config/" "$home/config/"
grep -rl "$CLIO_PREFIX/user/config" "$home/config" --include=*.json | xargs -r sed -i "s#$CLIO_PREFIX/user/config#$home/config#g"
[[ $CLIO_MCP_POLICY == none ]] && printf 'mcp_servers: {}\n' > "$home/config/mcp.yaml"
if [[ -n "$CLIO_BLUEPRINT_SOURCE_DIR" ]]; then
  [[ -d "$CLIO_BLUEPRINT_SOURCE_DIR" ]] || die "CLIO_BLUEPRINT_SOURCE_DIR not found" 3
  rsync -a "$CLIO_BLUEPRINT_SOURCE_DIR/" "$home/config/agent-blueprints/$bp_id/"
fi
mkdir -p "$ev/clio"
(cd "$home/config" && find . -type f ! -path './storage-auth/*' -print0 | sort -z | xargs -0 sha256sum) > "$ev/clio/deployment_config.sha256"
ln -s "$cli" "$shim/claude"
# isolated Claude config for the provider's CLI (same construction as the baseline's prepare_config_dir)
[[ -f "$HOME/.claude/.credentials.json" ]] || die "no $HOME/.claude/.credentials.json" 3
install -m 600 "$HOME/.claude/.credentials.json" "$cfg/.credentials.json"
python3 - "$HOME/.claude.json" "$cfg/.claude.json" <<'PY'
import json,sys
src,dst=sys.argv[1],sys.argv[2]
try: d=json.load(open(src))
except Exception: d={}
out={"hasCompletedOnboarding": True, "autoUpdates": False, "bypassPermissionsModeAccepted": True}
if "oauthAccount" in d: out["oauthAccount"]=d["oauthAccount"]
json.dump(out, open(dst,"w"), indent=2)
PY
printf '{"model": "%s"}\n' "$CLAUDE_MODEL" > "$cfg/settings.json"
"$COMMON_DIR/scripts/capture_environment.sh" --output "$ev/agent_host_environment.txt" >/dev/null 2>&1 || true
cfgfile=$CLIO_CONFIG_FILE
scrub_claude_env; for v in $(env | sed -n 's/^\(CLIO_[A-Z0-9_]*\)=.*/\1/p'); do unset "$v"; done
# shellcheck disable=SC1090
source "$cfgfile"   # re-read the pinned values after the scrub (an inherited exported CLIO_* must not override them)
# A clio-core daemon binds its port AND port+1 (found in the 2026-10-12 pilots), so both must be free; even ports only.
free_port() { local p; for _ in $(seq 1 50); do p=$(($1 + 2 * (RANDOM % 50))); (exec 3<>/dev/tcp/127.0.0.1/$p) 2>/dev/null && continue; (exec 3<>/dev/tcp/127.0.0.1/$((p + 1))) 2>/dev/null && continue; echo $p; return 0; done; return 1; }
port=$(free_port 17900) || die "no free port in 17900-17999 on $(hostname -s)" 3
if [[ "$CLIO_CORE_ISOLATION" == private ]]; then   # own clio-core daemon: no shared context store with other CLIO deployments on the node
  cport=$(free_port 19400) || die "no free core port in 19400-19499" 3
  export CLIO_RUNTIME_STATE_DIR="$dep/core_state" CLIO_CORE_PORT="$cport"
fi
export CLIO_PREFIX CLIO_AGENT_HOME="$home" CLIO_BIN_DIR="$CLIO_PREFIX/bin" CLIO_PORT="$port" CLIO_ALLOWED_ROOTS="$td:$home:${TMPDIR:-/tmp}"
export CLIO_NO_UPDATE_CHECK=1 CLIO_CLAUDE_CODE_STREAM_IDLE_TTL_S CLIO_MCP_CALL_TIMEOUT_S CLIO_GACT_TURN_TIMEOUT_S
[[ "$CLIO_STREAM_AUDIT" == 1 ]] && export CLIO_STREAM_AUDIT_LOG="$home/state/stream_audit.jsonl"
export PATH="$shim:$PATH" CLAUDE_CONFIG_DIR="$cfg" THESIS_TRIAL_ID="$rid" THESIS_SESSION_LABEL="$label"
if [[ -n "$xenv" ]]; then set -a; source "$xenv"; set +a; cp -p "$xenv" "$ev/clio/extra_env.txt"; fi
"$cli" auth status --json > "$ev/auth_status_isolated_config.json" 2>/dev/null || true
(cd "$td" && "$CLIO_PREFIX/clio-agent/.venv/bin/python" -I -c 'import json; from clio_agent.providers.claude_code_runtime import claude_code_runtime_info as f; print(json.dumps(f()))') > "$ev/clio/claude_cli_selection.json" 2>/dev/null || true
[[ "$(jq -r .cli_version "$ev/clio/claude_cli_selection.json" 2>/dev/null)" == "$CLIO_CLAUDE_CLI_PIN" ]] || { [[ $mode == counted ]] && die "CLIO would not drive the pinned Claude Code CLI (see clio/claude_cli_selection.json)" 3; warn "CLI selection differs from the pin"; }
start=$(utc_now); echo "$start" > "$ev/start_utc.txt"; log "starting CLIO deployment for $rid/$label on $(hostname -s):$port"
(cd "$td" && "$CLIO_PREFIX/bin/clio" start) > "$ev/clio/clio_start.log" 2>&1 || warn "clio start returned non-zero (see clio/clio_start.log)"
ok=0; for _ in $(seq 1 48); do sleep 5; curl --noproxy '*' -s -m 5 "http://127.0.0.1:$port/v1/health" | grep -q '"healthy":true' && { ok=1; break; }; done
runner[4]=$port
rc=3; endr=deployment_unhealthy
if [[ $ok == 1 ]]; then
  (cd "$td" && timeout -k 60 $((AGENT_SESSION_TIMEOUT_SECONDS + 600)) "${runner[@]}") > "$ev/stderr.log" 2>&1; rc=$?
  endr=$(jq -r '.end_reason // "unknown"' "$ev/clio/runner_state.json" 2>/dev/null)
else
  curl --noproxy '*' -s -m 5 "http://127.0.0.1:$port/v1/health" > "$ev/clio/health_unhealthy.json" 2>/dev/null
fi
end=$(utc_now); echo "$end" > "$ev/end_utc.txt"; echo "$rc" > "$ev/exit_code.txt"
"$CLIO_PREFIX/bin/clio" stop >> "$ev/clio/clio_start.log" 2>&1 || true
if [[ "$CLIO_CORE_ISOLATION" == private ]]; then   # the private core daemon must not outlive the session
  sleep 5; pf=$(ls "$dep"/core_state/*.pid 2>/dev/null | head -1)
  [[ -n "$pf" ]] && kill "$(cat "$pf")" 2>/dev/null && echo "$(utc_now) stopped private clio-core daemon $(cat "$pf")" >> "$ev/clio/clio_start.log"
  cp -p "$dep"/core_state/*.log "$ev/clio/" 2>/dev/null || true
fi
cp -p "$home"/state/*.log "$ev/clio/" 2>/dev/null || true
python3 "$CLIO_LIB/clio_usage.py" "$ev" "$cfg" "$home" > "$ev/clio/usage_collect.log" 2>&1 || warn "usage collection failed (clio/usage_collect.log)"
rm -f "$cfg/.credentials.json"   # the copied credential is removed as soon as the session ends
sid=$(jq -r '.session_id // empty' "$ev/clio/runner_state.json" 2>/dev/null); echo "$sid" > "$ev/session_id.txt"
clivers=$(jq -r '.claude_cli_versions_seen // {} | keys | join(",")' "$ev/clio/usage_summary.json" 2>/dev/null)
[[ $mode == validate && -z "$clivers" ]] && clivers="(no model call)"
tout=false; [[ "$endr" == timeout ]] && tout=true
trp=$(ls "$ev"/transcript_*.jsonl 2>/dev/null | head -1)
jq -n --arg rid "$rid" --arg lbl "$label" --arg sid "$sid" --arg td "$td" --arg bin "$CLIO_PREFIX/bin/clio" --arg ver "$clivers" \
  --arg inst "$inst" --arg sdk "$(clio_sdk_version)" --arg model "$CLAUDE_MODEL" --arg psha "$psha" --arg start "$start" --arg endt "$end" \
  --argjson rc "$rc" --argjson tout "$tout" --arg endr "$endr" --arg tr "$trp" --arg st "$ev/stream.jsonl" --arg dep "$dep" \
  --arg host "$(hostname -s)" --arg job "${SLURM_JOB_ID:-}" --arg port "$port" --arg mode "$mode" --arg core "$CLIO_CORE_ISOLATION:${CLIO_CORE_PORT:-9413}" \
  --argjson eff "$(jq '.effective // null' "$ev/clio/runner_state.json" 2>/dev/null || echo null)" \
  --argjson nu "$(jq '.user_messages_in_session // null' "$ev/clio/runner_state.json" 2>/dev/null || echo null)" \
  '{run_id:$rid, session_label:$lbl, session_id:$sid, system:"clio", trial_dir:$td, executable:$bin, executable_version:$ver,
    executable_version_note:"Claude Code CLI version(s) seen in the SDK transcripts of the CLI CLIO drove",
    clio_agent_version:$inst, claude_agent_sdk_version:$sdk, model:$model, prompt_sha256:$psha, start_utc:$start, end_utc:$endt,
    exit_code:$rc, end_reason:$endr, timeout_hit:$tout, transcript_path:$tr, stream_path:$st, config_dir:$dep, host:$host,
    agent_host_job_id:$job, clio_port:($port|tonumber), clio_core:$core, mode:$mode, effective_session_settings:$eff, user_messages_in_session:$nu,
    resume_used:false, continue_used:false, fork_used:false}' > "$ev/session_record.json"
(cd "$ev" && find . -type f ! -name evidence_SHA256SUMS.txt -print0 | sort -z | xargs -0 sha256sum > evidence_SHA256SUMS.txt)
log "CLIO session ${sid:-none} ended rc=$rc end_reason=$endr cli=$clivers"
exit "$rc"
