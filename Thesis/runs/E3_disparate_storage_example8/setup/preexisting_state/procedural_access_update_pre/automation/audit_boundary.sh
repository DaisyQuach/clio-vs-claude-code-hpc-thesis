#!/usr/bin/env bash
# Post-trial boundary audit (read-only): did the trial use restricted locations, write outside its workspace,
# or change a read-only source collection?
# Usage: audit_boundary.sh --system S --trial-dir D --since <marker created at trial start> [--staging S] [--json OUT]
# Inputs: logs/session/tool_inputs.jsonl (extracted from the session stream by the run script), the E3 tree, the collections.
# Verdict: PASS | REVIEW (broad scans of ancestor directories, or no tool record) | FAIL (forbidden path used, source or
# researcher_only changed, file changed under the E3 root outside the trial). Exit 0 for PASS/REVIEW, 1 for FAIL.
source "$(dirname "${BASH_SOURCE[0]}")/lib/e3_common.sh"
sys=""; td=""; mk=""; jo=""; sd=""
while [[ $# -gt 0 ]]; do case "$1" in --system) sys=${2:?}; shift 2;; --trial-dir) td=${2:?}; shift 2;; --since) mk=${2:?}; shift 2;;
  --staging) sd=${2:?}; shift 2;; --json) jo=${2:?}; shift 2;; -h|--help) sed -n '2,8p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
td=$(e3_guard_trial_dir "$sys" "$td") || exit $?; [[ -f "$mk" ]] || die "marker file not found: $mk" 2
out="$td/provenance/boundary_audit.txt"; ti="$td/logs/session/tool_inputs.jsonl"
tmp=$(mktemp -d); printf '%s\n' "${E3_FORBIDDEN_ROOTS[@]}" > "$tmp/forbidden"
{ printf '%s\n' "${E3_COLLECTIONS[@]}" "${E3_SOFTWARE_ROOTS[@]}" "$td"; [[ -n "$sd" ]] && echo "$sd"; } > "$tmp/allowed"
fail=0; review=0
{ echo "utc: $(utc_now)"; echo "trial_dir: $td"; echo "since_marker: $(stat -c %y "$mk")"
  echo "## 1. paths used in agent tool calls"
  if [[ -s "$ti" ]]; then
    python3 -I "$E3_AUTOMATION/lib/classify_tool_paths.py" "$ti" "$tmp/forbidden" "$tmp/allowed" > "$tmp/cls"
    if [[ -s "$tmp/cls" ]]; then sed 's/^/  /' "$tmp/cls"; else echo "  none"; fi
    echo "  tool_calls_examined: $(wc -l < "$ti")"
  else echo "  NO_TOOL_RECORD (logs/session/tool_inputs.jsonl missing or empty)"; : > "$tmp/cls"; fi
  echo "## 2. files changed under the E3 root outside this trial since the marker"
  ch=$(find "$E3_ROOT" \( -path "$td" -o -path "$E3_RUNTIME_DIR" \) -prune -o -newer "$mk" -type f -print 2>/dev/null)
  if [[ -n "$ch" ]]; then echo "$ch" | sed 's/^/  CHANGED /'; else echo "  none"; fi
  echo "## 3. read-only collections"; verify_collections | sed 's/^/  /'
  echo "## 4. researcher_only changed since marker"
  ro=$(find "$E3_RESEARCHER_ONLY" -newer "$mk" 2>/dev/null); [[ -z "$ro" ]] && echo "  none" || echo "$ro" | sed 's/^/  CHANGED /'
  echo "## 5. informational: restricted names mentioned anywhere in trial records (quotes of rules or cards are expected)"
  for p in "${E3_FORBIDDEN_PATTERNS[@]}"; do n=$(grep -rlF -- "$p" "$td/work" "$td/provenance" "$td/logs" 2>/dev/null | grep -v boundary_audit.txt | wc -l); [[ $n -gt 0 ]] && echo "  '$p' in $n file(s)"; done; true
} > "$out" 2>&1
rm -f -- "$tmp/forbidden" "$tmp/allowed" "$tmp/cls"; rmdir -- "$tmp"
grep -q '^  FORBIDDEN\|CHANGED \| FAIL' "$out" && fail=1
grep -q '^  ANCESTOR\|NO_TOOL_RECORD' "$out" && review=1
if [[ $fail == 1 ]]; then v=FAIL; elif [[ $review == 1 ]]; then v=REVIEW; else v=PASS; fi
echo "verdict: $v" >> "$out"
[[ -n "$jo" ]] && printf '{"verdict":"%s","report":"%s"}\n' "$v" "$out" > "$jo"
redact_home < "$out"; [[ $v != FAIL ]]
