#!/usr/bin/env bash
# Preflight for the CLIO arm. No model call, no Slurm submission, no manifest change.
# Usage: preflight_clio.sh --experiment e1-example8|e2-example16 [--dry-run] [--json OUT]
# 1. Runs the BASELINE preflight (../preflight.sh) unchanged: pinned Claude Code 2.1.295 (the same CLI CLIO's provider is
#    made to drive), headless flags, auth, scheduler, approved software, frozen-configuration hashes, no CLAUDE.md, clean packets.
# 2. CLIO checks: install and version pin, CLIO_BIN_DIR, decision placeholders, blueprint availability, runtime-tuning values.
# Exit 0 pass | 3 blocked (a counted run must not start).
source "$(dirname "${BASH_SOURCE[0]}")/lib/clio_common.sh"
exp=""; dry=0; json_out=""
while [[ $# -gt 0 ]]; do case "$1" in --experiment) exp=${2:?}; shift 2;; --dry-run) dry=1; shift;; --json) json_out=${2:?}; shift 2;; -h|--help) sed -n '2,8p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ "$exp" == e1-example8 || "$exp" == e2-example16 ]] || die "--experiment e1-example8 | e2-example16" 2
blk=0; lines=()
rec() { lines+=("$1|$2|$3"); printf '%-6s %-34s %s\n' "$2" "$1" "$3"; [[ $2 == FAIL ]] && blk=1; return 0; }
"$AUTOMATION_DIR/preflight.sh" --experiment "$exp" $([[ $dry == 1 ]] && echo --dry-run) >/dev/null 2>&1 && rec baseline_preflight PASS "../preflight.sh --experiment $exp" || rec baseline_preflight FAIL "../preflight.sh blocked (run it directly for details)"
for c in jq curl python3 rsync sbatch sacct squeue; do command -v $c >/dev/null || rec "cmd_$c" FAIL "missing"; done
[[ -x "$CLIO_PREFIX/bin/clio" && -x "$CLIO_PREFIX/bin/clio-kit" ]] && rec clio_install PASS "$CLIO_PREFIX (bin/clio, bin/clio-kit for CLIO_BIN_DIR)" || rec clio_install FAIL "CLIO not installed at $CLIO_PREFIX"
inst=$(clio_installed_version)
if [[ "$CLIO_AGENT_VERSION_PIN" == TBD* ]]; then rec clio_version $([[ $dry == 1 ]] && echo INFO || echo FAIL) "installed clio-agent $inst; pin not decided"
else [[ "$inst" == "$CLIO_AGENT_VERSION_PIN" ]] && rec clio_version PASS "clio-agent $inst" || rec clio_version FAIL "installed $inst != pin $CLIO_AGENT_VERSION_PIN"; fi
rec claude_agent_sdk INFO "$(clio_sdk_version) (bundled CLI $(claude_version_of "$CLIO_PREFIX"/clio-agent/.venv/lib/python3.12/site-packages/claude_agent_sdk/_bundled/claude 2>/dev/null); the deployment puts the pinned CLI first on PATH instead)"
v=$(claude_version_of "$(clio_cli_bin)"); [[ "$v" == "$CLIO_CLAUDE_CLI_PIN" ]] && rec claude_cli_pin PASS "$(clio_cli_bin) = $v (same binary as the baseline)" || rec claude_cli_pin FAIL "pinned CLI $CLIO_CLAUDE_CLI_PIN missing"
[[ -f "$HOME/.claude/.credentials.json" ]] && rec credentials PASS "copied into each session's isolated CLAUDE_CONFIG_DIR at launch" || rec credentials FAIL "no ~/.claude/.credentials.json"
ph=$(clio_placeholders | paste -sd' ' -)
[[ -z "$ph" ]] && rec decisions PASS "no placeholders in clio_trial_config.env" || rec decisions $([[ $dry == 1 ]] && echo INFO || echo FAIL) "placeholders: $ph"
if [[ "$CLIO_BLUEPRINT_ID" == TBD* ]]; then rec blueprint $([[ $dry == 1 ]] && echo INFO || echo FAIL) "blueprint not decided (installed: $(ls "$CLIO_PREFIX/user/config/agent-blueprints" 2>/dev/null | paste -sd, -))"
elif [[ "$CLIO_BLUEPRINT_ID" == none ]]; then rec blueprint PASS "standard agent (no blueprint)"
elif [[ -n "$CLIO_BLUEPRINT_SOURCE_DIR" ]]; then [[ -f "$CLIO_BLUEPRINT_SOURCE_DIR/AGENT.md" || -d "$CLIO_BLUEPRINT_SOURCE_DIR" ]] && rec blueprint PASS "variant from $CLIO_BLUEPRINT_SOURCE_DIR" || rec blueprint FAIL "source dir missing"
else [[ -d "$CLIO_PREFIX/user/config/agent-blueprints/$CLIO_BLUEPRINT_ID" ]] && rec blueprint PASS "installed $CLIO_BLUEPRINT_ID (version verified per session)" || rec blueprint FAIL "$CLIO_BLUEPRINT_ID not installed"; fi
for k in CLIO_CLAUDE_CODE_STREAM_IDLE_TTL_S CLIO_MCP_CALL_TIMEOUT_S CLIO_GACT_TURN_TIMEOUT_S CLIO_MAX_NUDGES; do [[ "${!k}" =~ ^[0-9]+(\.[0-9]+)?$ ]] && rec "$k" PASS "${!k}" || rec "$k" $([[ $dry == 1 ]] && echo INFO || echo FAIL) "${!k}"; done
[[ "${CLIO_GACT_TURN_TIMEOUT_S%.*}" -gt "${CLIO_MCP_CALL_TIMEOUT_S%.*}" ]] 2>/dev/null && rec watchdog_above_tool_timeout PASS "$CLIO_GACT_TURN_TIMEOUT_S > $CLIO_MCP_CALL_TIMEOUT_S" || rec watchdog_above_tool_timeout INFO "turn watchdog not above the tool timeout (E3 pilot failure mode)"
[[ "$CLIO_EFFORT" == default ]] && rec effort_parity PASS "no effort sent (Claude Code CLI default, as the baseline)" || rec effort_parity INFO "effort $CLIO_EFFORT differs from the baseline's CLI default"
[[ "$CLIO_MAX_NUDGES" == 0 ]] && rec prompt_parity PASS "one user message per session (as the baseline)" || rec prompt_parity INFO "$CLIO_MAX_NUDGES nudge(s) allowed: differs from the baseline"
[[ -n "$json_out" ]] && printf '%s\n' "${lines[@]}" | jq -R 'split("|") | {name:.[0], result:.[1], detail:(.[2:]|join("|"))}' | jq -s --arg u "$(utc_now)" --argjson b "$blk" '{utc:$u, blocked:($b==1), checks:.}' > "$json_out"
[[ $blk -eq 0 ]] && { log "CLIO preflight: PASS"; exit 0; } || { log "CLIO preflight: BLOCKED"; exit 3; }
