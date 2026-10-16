#!/usr/bin/env bash
# Shared definitions for the CLIO arm automation (E1/E2; E3 reuses the deployment and runner pieces). Source only.
# Sources the BASELINE lib/common.sh read-only, so the model, Slurm contract, session limit, experiment table and manifest
# helpers are literally the baseline's. Nothing here edits a baseline file.
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)/lib/common.sh"
CLIO_AUTOMATION_DIR="$AUTOMATION_DIR/clio"
CLIO_LIB="$CLIO_AUTOMATION_DIR/lib"
CLIO_CONFIG_FILE="${CLIO_CONFIG_FILE:-$CLIO_AUTOMATION_DIR/clio_trial_config.env}"
# shellcheck disable=SC1090
source "$CLIO_CONFIG_FILE"
CLIO_RUNTIME_ROOT="${THESIS_CLIO_RUNTIME_ROOT:-$THESIS_ROOT/.agent_runtime}"   # per-session deployment state; override only for validation

clio_trial_dir_of() { echo "$RUNS_DIR/$(experiment_field "$1" runs)/clio/trial_$(printf '%02d' "$2")${3:-}"; }
clio_run_id_of()    { echo "$(experiment_field "$1" prefix | sed 's/-baseline$/-clio/')-$(printf '%02d' "$2")${3:-}"; }

# Placeholder handling: any decision value beginning with TBD blocks a counted run.
CLIO_DECISION_KEYS=(CLIO_AGENT_VERSION_PIN CLIO_CORE_VERSION_PIN CLIO_DESKTOP_VERSION CLIO_BLUEPRINT_ID CLIO_BLUEPRINT_VERSION
  CLIO_EFFORT CLIO_APPROVAL_MODE CLIO_MAX_NUDGES CLIO_ANSWER_QUESTIONS CLIO_MCP_POLICY CLIO_CLAUDE_CLI_PIN
  CLIO_CLAUDE_CODE_STREAM_IDLE_TTL_S CLIO_MCP_CALL_TIMEOUT_S CLIO_GACT_TURN_TIMEOUT_S CLIO_CORE_ISOLATION)
clio_placeholders() { local k; for k in "${CLIO_DECISION_KEYS[@]}"; do [[ "${!k:-TBD}" == TBD* ]] && echo "$k"; done; }
clio_config_json() { local k; for k in "${CLIO_DECISION_KEYS[@]}" CLIO_PREFIX CLIO_BLUEPRINT_SOURCE_DIR CLIO_POLL_SECONDS CLIO_STREAM_AUDIT; do
    jq -n --arg k "$k" --arg v "${!k:-}" '{($k):$v}'; done | jq -s add; }
clio_installed_version() { "$CLIO_PREFIX/clio-agent/.venv/bin/python" -c 'import importlib.metadata as m; print(m.version("clio-agent"))' 2>/dev/null; }
clio_sdk_version()       { "$CLIO_PREFIX/clio-agent/.venv/bin/python" -c 'import importlib.metadata as m; print(m.version("claude-agent-sdk"))' 2>/dev/null; }
clio_cli_bin()           { echo "$HOME/.local/share/claude/versions/$CLIO_CLAUDE_CLI_PIN"; }
