#!/usr/bin/env bash
# Launch ONE completely new, fully headless Claude Code process for one agent session.
# Usage: launch_headless_claude.sh --trial-dir D --run-id ID --session-label LABEL --prompt-file P
#          (--dry-run | --execute-counted) [--via-slurm | --local] [--evidence-dir E]
#   --dry-run          build everything, write the launch plan, make no model call (and no sbatch)
#   --execute-counted  really launch (refused unless the pinned 2.1.292 executable verifies)
#   --via-slurm        wrap the launch in an sbatch job with the frozen agent-host contract and wait (default for counted)
#   --local            run in the current shell/allocation (used inside the sbatch wrapper)
# Fresh-session guarantees: new process, new UUID (--session-id), isolated CLAUDE_CONFIG_DIR per session
# (no memory, no project state, no transcript visible to any other session), never --resume/--continue/--fork-session.
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
td=""; rid=""; label=""; pf=""; mode=""; via=slurm; ev=""
while [[ $# -gt 0 ]]; do case "$1" in
  --trial-dir) td=${2:?}; shift 2;; --run-id) rid=${2:?}; shift 2;; --session-label) label=${2:?}; shift 2;; --prompt-file) pf=${2:?}; shift 2;;
  --dry-run) mode=dry; shift;; --execute-counted) mode=counted; shift;; --via-slurm) via=slurm; shift;; --local) via=local; shift;; --evidence-dir) ev=${2:?}; shift 2;;
  -h|--help) sed -n '2,11p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
[[ -n "$td" && -n "$rid" && -n "$label" && -n "$pf" && -n "$mode" ]] || die "missing required arguments (see --help)" 2
td=$(cd "$td" && pwd -P) || die "trial dir not found" 2
[[ -f "$pf" ]] || die "prompt file not found: $pf" 2
[[ "$label" =~ ^[a-z0-9_]+$ ]] || die "session label must be [a-z0-9_]+" 2
require_cmd uuidgen jq timeout
# --- binary selection (fail closed for counted runs) ---------------------------------
bin="$CLAUDE_BIN_PINNED"
if [[ ! -x "$bin" || "$(claude_version_of "$bin")" != "$CLAUDE_PIN_VERSION" ]]; then
  if [[ "$mode" == dry && -n "${THESIS_CLAUDE_BIN_OVERRIDE:-}" && -x "$THESIS_CLAUDE_BIN_OVERRIDE" ]]; then bin="$THESIS_CLAUDE_BIN_OVERRIDE"; pinned_note="DRY-RUN OVERRIDE: pinned $CLAUDE_PIN_VERSION unavailable; plan rendered with $(claude_version_of "$bin")"; warn "$pinned_note"
  else die "pinned Claude Code $CLAUDE_PIN_VERSION not available at $CLAUDE_BIN_PINNED; a counted launch is refused" 3; fi
else pinned_note="pinned executable verified ($CLAUDE_PIN_VERSION)"; fi
# --- evidence directory (researcher-only staging; copied into the packet by the collector) ----
if [[ -z "$ev" ]]; then if [[ "$mode" == dry ]]; then ev="$SESSION_EVIDENCE_ROOT/$rid/dryrun_$(date -u +%Y%m%dT%H%M%SZ)/$label"; else ev="$SESSION_EVIDENCE_ROOT/$rid/$label"; fi; fi
if [[ "$mode" == counted && -e "$ev/session_record.json" ]]; then die "session evidence already exists: $ev (refusing to overwrite)" 4; fi
mkdir -p "$ev"; chmod 700 "$SESSION_EVIDENCE_ROOT" "$ev" 2>/dev/null || true
sid=$(uuidgen); [[ -s "$ev/session_id.txt" && "$via" == local ]] && sid=$(cat "$ev/session_id.txt")   # inner run reuses the id chosen by the wrapper
echo "$sid" > "$ev/session_id.txt"
[[ "$(readlink -f "$pf")" == "$(readlink -f "$ev/prompt.md")" ]] || cp -p "$pf" "$ev/prompt.md"; psha=$(sha256_of "$pf"); echo "$psha  $(basename "$pf")" > "$ev/prompt.sha256"
cfg="$THESIS_ROOT/.agent_runtime/$rid/$label/claude_config"; mkdir -p "$cfg"; chmod 700 "$THESIS_ROOT/.agent_runtime" "$cfg"   # neutral path: Claude Code persists large tool outputs under its config dir and the path appears in transcripts
# --- command (flags verified from --help by preflight; nothing guessed) ---------------
cmd=("$bin" --print --verbose --output-format stream-json --model "$CLAUDE_MODEL" --dangerously-skip-permissions
     --session-id "$sid" --disable-slash-commands --no-chrome -- "$(cat "$pf")")
for f in "${CLAUDE_FORBIDDEN_FLAGS[@]}"; do for a in "${cmd[@]:1:9}"; do [[ "$a" == "$f" ]] && die "forbidden flag in command: $f" 1; done; done
{ echo "# exact headless launch command (argv, shell-quoted); executed with cwd=$td"; printf '%q ' "${cmd[@]}"; echo; } > "$ev/launch_command.txt"
cat > "$ev/launch_env.txt" <<EOF
DISABLE_AUTOUPDATER=1
CLAUDE_CODE_DISABLE_AUTO_MEMORY=1
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
CLAUDE_CONFIG_DIR=$cfg
THESIS_TRIAL_ID=$rid
THESIS_SESSION_LABEL=$label
cwd=$td
timeout_seconds=$AGENT_SESSION_TIMEOUT_SECONDS
inherited CLAUDE* variables: scrubbed
EOF
plan() { jq -n --arg rid "$rid" --arg lbl "$label" --arg sid "$sid" --arg td "$td" --arg bin "$bin" --arg ver "$(claude_version_of "$bin")" --arg model "$CLAUDE_MODEL" \
   --arg psha "$psha" --arg ev "$ev" --arg cfg "$cfg" --arg mode "$mode" --arg via "$via" --arg note "$pinned_note" --arg utc "$(utc_now)" \
   --argjson cmd "$(printf '%s\n' "${cmd[@]}" | jq -R . | jq -s .)" \
   '{run_id:$rid, session_label:$lbl, session_id:$sid, trial_dir:$td, executable:$bin, executable_version:$ver, model:$model, prompt_sha256:$psha,
     evidence_dir:$ev, config_dir:$cfg, mode:$mode, via:$via, pinned_note:$note, planned_utc:$utc, argv:$cmd,
     fresh_session_guarantees:["new process","new --session-id UUID","isolated CLAUDE_CONFIG_DIR (no memory/project state shared)","no --resume/--continue/--fork-session","no session reuse"]}'; }
if [[ "$mode" == dry ]]; then plan > "$ev/launch_plan.json"; log "DRY RUN: no model call, no sbatch. Plan written to $ev/launch_plan.json"; cat "$ev/launch_command.txt"; exit 0; fi

# ====================== counted execution ======================
prepare_config_dir() {  # isolated per-session Claude config: credentials copy + minimal global config
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
}
if [[ "$via" == slurm ]]; then
  plan > "$ev/launch_plan.json"
  sb="$ev/agent_host.sbatch"
  cat > "$sb" <<EOF
#!/bin/bash -l
#SBATCH --job-name=agent_${rid}_${label}
#SBATCH --account=$SLURM_ACCOUNT
#SBATCH --partition=$SLURM_PARTITION
#SBATCH --nodes=$SLURM_NODES
#SBATCH --ntasks=$SLURM_NTASKS
#SBATCH --cpus-per-task=$SLURM_CPUS
#SBATCH --mem=$SLURM_MEM
#SBATCH --time=$SLURM_TIME
#SBATCH --output=$ev/agent_host_%j.out
#SBATCH --error=$ev/agent_host_%j.err
# Agent-host job (frozen contract).  Runs exactly one headless Claude Code session.
echo "agent_host_job=\$SLURM_JOB_ID node=\$(hostname -s) start_utc=\$(date -u +%FT%TZ)"
exec "$AUTOMATION_DIR/launch_headless_claude.sh" --trial-dir "$td" --run-id "$rid" --session-label "$label" --prompt-file "$ev/prompt.md" --execute-counted --local --evidence-dir "$ev"
EOF
  log "submitting agent-host job for $rid/$label (sbatch --wait)"; echo "$(utc_now) sbatch --wait --parsable $sb" >> "$ev/submissions.log"
  jid=$(sbatch --wait --parsable "$sb"); src=$?; echo "$jid" > "$ev/agent_host_job_id.txt"; echo "$(utc_now) sbatch returned rc=$src job=$jid" >> "$ev/submissions.log"
  sacct -j "$jid" --parsable2 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,TotalCPU,NodeList > "$ev/agent_host_sacct.psv" 2>/dev/null || true
  [[ -f "$ev/session_record.json" ]] || die "agent-host job $jid ended without a session record (see $ev/agent_host_$jid.err)" 1
  jq -r '"session \(.session_id) rc=\(.exit_code) timeout_hit=\(.timeout_hit) transcript=\(.transcript_path)"' "$ev/session_record.json"
  exit "$(jq -r '.exit_code' "$ev/session_record.json")"
fi
# ---- local execution (inside the agent-host job, or an existing allocation with --local) ----
prepare_config_dir
"$COMMON_DIR/scripts/capture_environment.sh" --output "$ev/agent_host_environment.txt" >/dev/null 2>&1 || true
scrub_claude_env
export CLAUDE_CONFIG_DIR="$cfg" THESIS_TRIAL_ID="$rid" THESIS_SESSION_LABEL="$label"
auth=$("$bin" auth status --json 2>/dev/null || true); echo "$auth" > "$ev/auth_status_isolated_config.json"
start=$(utc_now); echo "$start" > "$ev/start_utc.txt"; log "launching session $sid ($label) for $rid in $td"
( cd "$td" && timeout --foreground -k 60 "$AGENT_SESSION_TIMEOUT_SECONDS" "${cmd[@]}" < /dev/null > "$ev/stream.jsonl" 2> "$ev/stderr.log" ); rc=$?
end=$(utc_now); echo "$end" > "$ev/end_utc.txt"; echo "$rc" > "$ev/exit_code.txt"
tout=false; [[ $rc -eq 124 || $rc -eq 137 ]] && tout=true
tr=$(find "$cfg/projects" -name "$sid.jsonl" -print -quit 2>/dev/null || true)
if [[ -n "$tr" ]]; then cp -p "$tr" "$ev/transcript_$sid.jsonl"; trp="$ev/transcript_$sid.jsonl"; else trp=""; warn "no transcript found under $cfg/projects"; fi
grep -E '"type" *: *"result"' "$ev/stream.jsonl" | tail -1 > "$ev/result.json" 2>/dev/null || true
rm -f "$cfg/.credentials.json"   # the copied credential is removed as soon as the session ends
jq -n --arg rid "$rid" --arg lbl "$label" --arg sid "$sid" --arg td "$td" --arg bin "$bin" --arg ver "$(claude_version_of "$bin")" --arg model "$CLAUDE_MODEL" \
  --arg psha "$psha" --arg start "$start" --arg endt "$end" --argjson rc "$rc" --argjson tout "$tout" --arg tr "$trp" --arg st "$ev/stream.jsonl" --arg cfg "$cfg" \
  --arg host "$(hostname -s)" --arg job "${SLURM_JOB_ID:-}" --arg note "$pinned_note" \
  '{run_id:$rid, session_label:$lbl, session_id:$sid, trial_dir:$td, executable:$bin, executable_version:$ver, model:$model, prompt_sha256:$psha,
    start_utc:$start, end_utc:$endt, exit_code:$rc, timeout_hit:$tout, transcript_path:$tr, stream_path:$st, config_dir:$cfg, host:$host,
    agent_host_job_id:$job, pinned_note:$note, resume_used:false, continue_used:false, fork_used:false}' > "$ev/session_record.json"
(cd "$ev" && find . -type f ! -name evidence_SHA256SUMS.txt ! -path './claude_config/*' -print0 | sort -z | xargs -0 sha256sum > evidence_SHA256SUMS.txt)
log "session $sid ended rc=$rc timeout_hit=$tout"
exit "$rc"
