#!/usr/bin/env bash
# Preflight for the headless Claude baseline.  No model call, no Slurm submission, no manifest change.
# Usage: preflight.sh [--experiment e1-example8|e2-example16] [--dry-run] [--json OUT]
# Exit 0: all blocking checks pass.  Exit 3: blocked (a counted run must not start).
# In --dry-run mode only, THESIS_CLAUDE_BIN_OVERRIDE may point at another Claude Code
# executable so the remaining checks and the dry-run path can be exercised; the pinned-binary
# check is still reported as FAIL and a counted run is still refused.
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
exp=""; dry=0; json_out=""
while [[ $# -gt 0 ]]; do case "$1" in
  --experiment) exp=${2:?}; shift 2;; --dry-run) dry=1; shift;; --json) json_out=${2:?}; shift 2;;
  -h|--help) sed -n '2,8p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -z "$exp" ]] || valid_experiment "$exp" || die "invalid --experiment: $exp (e1-example8 | e2-example16)" 2
declare -A R; blocking_fail=0; notes=()
rec() { # rec <name> <PASS|FAIL|INFO> <detail> [blocking=1]
  R["$1"]="$2|$3"; printf '%-5s %-34s %s\n' "$2" "$1" "$3"; [[ "$2" == FAIL && "${4:-1}" == 1 ]] && blocking_fail=1 || true; }

# 1. pinned executable
bin="$CLAUDE_BIN_PINNED"; pinned_ok=0
if [[ -x "$bin" ]]; then v=$(claude_version_of "$bin"); if [[ "$v" == "$CLAUDE_PIN_VERSION" ]]; then rec pinned_binary PASS "$bin --version = $v"; pinned_ok=1; else rec pinned_binary FAIL "$bin reports '$v', expected $CLAUDE_PIN_VERSION"; fi
else rec pinned_binary FAIL "missing: $bin (installed versions: $(ls "$(dirname "$bin")" 2>/dev/null | tr '\n' ' '))"; fi
check_bin="$bin"
if [[ $pinned_ok -eq 0 && $dry -eq 1 && -n "${THESIS_CLAUDE_BIN_OVERRIDE:-}" && -x "${THESIS_CLAUDE_BIN_OVERRIDE}" ]]; then
  check_bin="$THESIS_CLAUDE_BIN_OVERRIDE"; rec dry_run_binary_override INFO "dry-run only: syntax checks use $check_bin ($(claude_version_of "$check_bin")); counted runs stay refused" 0
fi
# 2. headless syntax verified from --help (never guessed)
if [[ -x "$check_bin" ]]; then
  help=$(DISABLE_AUTOUPDATER=1 "$check_bin" --help 2>&1 || true); missing=()
  for f in "${CLAUDE_REQUIRED_FLAGS[@]}"; do grep -q -- "$f" <<<"$help" || missing+=("$f"); done
  if [[ ${#missing[@]} -eq 0 ]]; then rec help_flags PASS "all required flags present in --help of $(claude_version_of "$check_bin")"; else rec help_flags FAIL "missing in --help: ${missing[*]}"; fi
  present=(); for f in "${CLAUDE_FORBIDDEN_FLAGS[@]}"; do grep -q -- " $f" <<<"$help" && present+=("$f"); done
  rec forbidden_flags_known INFO "resume/continue/fork flags exist (${present[*]}) and are never passed by the launcher" 0
  if grep -q -- "--output-format <format>" <<<"$help" && grep -q 'stream-json' <<<"$help"; then rec output_format PASS "--output-format stream-json documented"; else rec output_format FAIL "stream-json output not documented"; fi
  if DISABLE_AUTOUPDATER=1 "$check_bin" auth status --help 2>&1 | grep -q -- '--json'; then rec auth_status_cmd PASS "'auth status --json' available (no-model auth check)"; else rec auth_status_cmd FAIL "'auth status --json' not available"; fi
else rec help_flags FAIL "no executable to inspect"; fi
# 3. authentication of the researcher's Claude login (no model call)
if [[ -x "$check_bin" ]]; then
  st=$(DISABLE_AUTOUPDATER=1 "$check_bin" auth status --json 2>/dev/null || true)
  if printf '%s' "$st" | grep -qiE '"loggedIn" *: *true|"logged_in" *: *true|"authenticated" *: *true'; then rec auth_logged_in PASS "auth status reports logged in"; else rec auth_logged_in FAIL "auth status did not report a login: ${st:0:200}"; fi
fi
[[ -f "$HOME/.claude/.credentials.json" ]] && rec credentials_file PASS "$HOME/.claude/.credentials.json present (copied into each isolated session config dir)" || rec credentials_file FAIL "no $HOME/.claude/.credentials.json for config isolation"
au=$(python3 -c "import json,sys;d=json.load(open('$HOME/.claude.json'));print(d.get('autoUpdates'))" 2>/dev/null || echo unknown)
rec autoupdates_setting INFO "~/.claude.json autoUpdates=$au; launcher also exports DISABLE_AUTOUPDATER=1" 0
# 4. scheduler
for c in sbatch sacct squeue scontrol sinfo uuidgen jq; do command -v "$c" >/dev/null 2>&1 && rec "cmd_$c" PASS "$(command -v "$c")" || rec "cmd_$c" FAIL "not found"; done
if sinfo -h -p "$SLURM_PARTITION" -o '%P' 2>/dev/null | grep -q "$SLURM_PARTITION"; then rec partition PASS "$SLURM_PARTITION available"; else rec partition FAIL "partition $SLURM_PARTITION not visible"; fi
rec slurm_contract INFO "account=$SLURM_ACCOUNT partition=$SLURM_PARTITION nodes=$SLURM_NODES ntasks=$SLURM_NTASKS cpus=$SLURM_CPUS mem=$SLURM_MEM time=$SLURM_TIME" 0
# 5. approved software
sw=$(bash -lc "source $COMMON_DIR/scripts/load_approved_software.sh >/dev/null 2>&1 && echo OK:\$(command -v XMLGenerator):\$(command -v cubit):\$(sha256sum < \$MORPHORM_RUNTIME/provenance/SHA256SUMS | cut -c1-64)" 2>/dev/null || echo FAIL)
if [[ "$sw" == OK:* ]]; then inv=${sw##*:}; if [[ "$inv" == fa0d97b93a7990271813eccf8768e14465266853a83ef8adab9e6987b4e3e4d2 ]]; then rec approved_software PASS "loader ok; runtime inventory hash matches frozen value"; else rec approved_software FAIL "runtime inventory hash $inv differs from frozen"; fi
else rec approved_software FAIL "load_approved_software.sh failed"; fi
# 6. frozen configuration integrity
for sel in ${exp:-e1-example8 e2-example16}; do fz="$COMMON_DIR/$(experiment_field "$sel" frozen)"; want=$(cut -d' ' -f1 "$fz/FROZEN_CONFIG_SHA256.txt"); have=$("$COMMON_DIR/scripts/hash_frozen_config.sh" "$fz")
  [[ "$want" == "$have" ]] && rec "frozen_$sel" PASS "$(cat "$fz/FROZEN_CONFIG_ID.txt") $have" || rec "frozen_$sel" FAIL "frozen config hash changed: recorded $want, now $have"; done
# 7. no CLAUDE.md leakage into agent context (ancestors of the runs tree)
leak=(); d="$RUNS_DIR"; while [[ "$d" != / ]]; do [[ -e "$d/CLAUDE.md" || -e "$d/.claude/CLAUDE.md" ]] && leak+=("$d"); d=$(dirname "$d"); done
[[ ${#leak[@]} -eq 0 ]] && rec claude_md_ancestors PASS "no CLAUDE.md in ancestors of $RUNS_DIR" || rec claude_md_ancestors FAIL "CLAUDE.md found in: ${leak[*]}"
# 8. researcher-only tree not referenced in agent-visible material
if grep -rqs "researcher_only\|Morphorm_ground_truth\|examplesmanual" "$COMMON_DIR/frozen_example8" "$COMMON_DIR/frozen_example16" --include='*.md' --include='*.txt'; then rec agent_visible_leak FAIL "agent-visible text references researcher-only material"; else rec agent_visible_leak PASS "no researcher-only references in frozen configurations"; fi
# summary
status=$([[ $blocking_fail -eq 0 ]] && echo PASS || echo BLOCKED)
printf '\npreflight: %s (pinned_binary_ok=%s, dry_run=%s, utc=%s)\n' "$status" "$pinned_ok" "$dry" "$(utc_now)"
if [[ -n "$json_out" ]]; then { printf '{\n  "utc": "%s", "status": "%s", "pinned_binary_ok": %s, "dry_run": %s, "checks": {\n' "$(utc_now)" "$status" "$([[ $pinned_ok -eq 1 ]] && echo true || echo false)" "$([[ $dry -eq 1 ]] && echo true || echo false)"; first=1; for k in "${!R[@]}"; do [[ $first -eq 1 ]] || printf ',\n'; first=0; printf '    %s: {"result": %s, "detail": %s}' "$(jq -Rn --arg s "$k" '$s')" "$(jq -Rn --arg s "${R[$k]%%|*}" '$s')" "$(jq -Rn --arg s "${R[$k]#*|}" '$s')"; done; printf '\n  }\n}\n'; } > "$json_out"; fi
[[ $blocking_fail -eq 0 ]] || exit 3
exit 0
