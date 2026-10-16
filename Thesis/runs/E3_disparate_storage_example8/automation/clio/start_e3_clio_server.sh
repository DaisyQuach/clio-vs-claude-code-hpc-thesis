#!/usr/bin/env bash
# Start the DEDICATED E3 CLIO server for ONE CLIO trial (researcher runs this manually, inside the fresh per-trial
# allocation, in a shell on the allocated compute node; setup/CLIO_RUNBOOK.md §2).
# Usage: start_e3_clio_server.sh --trial-dir <E3>/clio/trial_NN --port P [--clio-prefix DIR] [--dry-run]
#   Creates a fresh, isolated CLIO home $E3/.agent_runtime/clio/<trial_id>/ (refuses an existing one):
#     - same installed CLIO (default prefix: Daisy/clioSessions/CLIOruntime, used read-only), its own port;
#     - config.yaml: provider claude_code, model = pinned E3 model; mcp.yaml: NO servers (no web search);
#     - no prior workspaces, sessions, memory or traces; core-daemon state isolated (CLIO_RUNTIME_STATE_DIR);
#   exports E3_TRIAL_ID / E3_TRIAL_ROOT / E3_STAGING_DIR / E3_SYSTEM (inherited by CLIO's shell tool, as the baseline
#   prompt states), then runs "<prefix>/bin/clio start" and writes instance.json for the runner.
# Never touches the researcher's normal CLIO install state. Writes nothing in the trial directory.
source "$(dirname "${BASH_SOURCE[0]}")/../lib/e3_common.sh"
td=""; port=""; prefix=/uufs/chpc.utah.edu/common/home/chet/Daisy/clioSessions/CLIOruntime; dry=0
cfg="$E3_AUTOMATION/baseline/baseline_e3_config.env"
while [[ $# -gt 0 ]]; do case "$1" in --trial-dir) td=${2:?}; shift 2;; --port) port=${2:?}; shift 2;;
  --clio-prefix) prefix=${2:?}; shift 2;; --dry-run) dry=1; shift;; -h|--help) sed -n '2,13p' "$0"; exit 0;;
  *) die "unknown argument: $1" 2;; esac; done
td=$(e3_guard_trial_dir clio "$td") || exit $?; tid=$(trial_id_of clio "$td")
[[ "$port" =~ ^[0-9]{4,5}$ ]] || die "--port must be a TCP port number" 2
# shellcheck disable=SC1090
source "$cfg"; : "${E3_CLAUDE_MODEL:?}"
nlr=$(e3_node_local_root) || die "run this inside the per-trial allocation on the compute node (needs SLURM_JOB_ID and per-job \$TMPDIR)" 3
[[ -x "$prefix/bin/clio" && -x "$prefix/clio-agent/.venv/bin/clio-agent" ]] || die "CLIO install not found at $prefix" 3
curl --noproxy '*' -s -m 2 -o /dev/null "http://127.0.0.1:$port/v1/health" && die "port $port already answers on this node; choose another" 4
home="$E3_RUNTIME_DIR/clio/$tid"; [[ -e "$home" ]] && die "CLIO home already exists for $tid: $home (one fresh instance per trial; never reused)" 4
sd="$nlr/e3/clio/$tid"
ver=$("$prefix/clio-agent/.venv/bin/python" -c 'import importlib.metadata as m; print(m.version("clio-agent"))' 2>/dev/null)
sdk=$("$prefix/clio-agent/.venv/bin/python" -c 'import importlib.metadata as m; print(m.version("claude-agent-sdk"))' 2>/dev/null)
if [[ $dry == 1 ]]; then
  log "DRY RUN: would create $home, start clio-agent $ver (claude-agent-sdk $sdk) on 127.0.0.1:$port, host $(hostname -s), job $SLURM_JOB_ID"
  log "DRY RUN: E3_TRIAL_ID=$tid E3_TRIAL_ROOT=$td E3_STAGING_DIR=$sd"; exit 0; fi
mkdir -p "$home"/{config,runtime_state}; chmod 700 "$E3_RUNTIME_DIR" "$E3_RUNTIME_DIR/clio" "$home" 2>/dev/null || true
cat > "$home/config/config.yaml" <<YAML
# E3 dedicated CLIO instance for $tid (written by start_e3_clio_server.sh). No credentials here.
lm:
  provider: claude_code
  model: $E3_CLAUDE_MODEL
  api_base: claude-code://sdk
  claude_code_transport: sdk
YAML
printf 'mcp_servers: {}\n' > "$home/config/mcp.yaml"
export CLIO_AGENT_HOME="$home" CLIO_AGENT_CONFIG_DIR="$home/config" CLIO_RUNTIME_STATE_DIR="$home/runtime_state"
export CLIO_PREFIX="$prefix" CLIO_PORT="$port" CLIO_NO_UPDATE_CHECK=1 CLIO_LOG="$home/clio-server.log"
unset CLIO_USER_DIR CLIO_SESSIONS_PATH CLIO_GACT_BEARER_TOKEN CLIO_AUTH_TOKEN CLIO_ALLOWED_ROOTS
export DISABLE_AUTOUPDATER=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export E3_TRIAL_ID="$tid" E3_TRIAL_ROOT="$td" E3_STAGING_DIR="$sd" E3_SYSTEM=clio
start=$(utc_now)
"$prefix/bin/clio" start > "$home/clio-start.out" 2>&1 || { cat "$home/clio-start.out" >&2; die "clio start failed" 1; }
for _ in $(seq 1 60); do curl --noproxy '*' -s -m 2 -o /dev/null -w '%{http_code}' "http://127.0.0.1:$port/v1/health" | grep -q -E '^(200|503)$' && break; sleep 2; done
caps=$(curl --noproxy '*' -s -m 10 "http://127.0.0.1:$port/v1/capabilities" || echo '{}')
jq -n --arg tid "$tid" --arg td "$td" --arg sd "$sd" --arg home "$home" --arg prefix "$prefix" --arg port "$port" --arg host "$(hostname -s)" \
  --arg job "$SLURM_JOB_ID" --arg start "$start" --arg ver "$ver" --arg sdk "$sdk" --arg model "$E3_CLAUDE_MODEL" --argjson caps "$caps" \
  '{trial_id:$tid, trial_dir:$td, staging_dir:$sd, clio_home:$home, clio_prefix:$prefix, port:($port|tonumber), bind:"127.0.0.1",
    host:$host, slurm_job_id:$job, started_utc:$start, clio_agent_version:$ver, claude_agent_sdk_version:$sdk, configured_model:$model,
    mcp_servers:[], capabilities:$caps}' | redact_home > "$home/instance.json"
log "E3 CLIO server for $tid on $(hostname -s) 127.0.0.1:$port (clio-agent $ver); instance record: $home/instance.json"
log "Desktop (optional, observe/control only; never send messages or approvals during a trial): ssh -L $port:127.0.0.1:$port <you>@$(hostname -s) via a CHPC login node"
