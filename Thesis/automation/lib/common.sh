#!/usr/bin/env bash
# Shared definitions for the Thesis baseline automation.  Source only.
# Every value here is frozen for the study; change nothing mid-study.
set -o pipefail
THESIS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
AUTOMATION_DIR="$THESIS_ROOT/automation"
RUNS_DIR="$THESIS_ROOT/runs"
COMMON_DIR="$THESIS_ROOT/common"
RESEARCHER_ONLY="$THESIS_ROOT/researcher_only"
SESSION_EVIDENCE_ROOT="${THESIS_SESSION_EVIDENCE_ROOT:-$RESEARCHER_ONLY/session_evidence}"   # researcher-only staging during a run; override only for offline tests

# --- pinned baseline system ---------------------------------------------------
CLAUDE_PIN_VERSION="2.1.295"
CLAUDE_BIN_PINNED="$HOME/.local/share/claude/versions/$CLAUDE_PIN_VERSION"
CLAUDE_MODEL="claude-fable-5-1"
# Flags whose presence in `--help` is required (verified, not guessed; see docs/HEADLESS_CLAUDE_SYNTAX.md)
CLAUDE_REQUIRED_FLAGS=(--print --output-format --model --session-id --dangerously-skip-permissions --verbose --disable-slash-commands --no-chrome --version --help)
CLAUDE_FORBIDDEN_FLAGS=(--resume -r --continue -c --fork-session --teleport --from-pr --bg --background --cloud)

# --- frozen Slurm contracts ------------------------------------------------------
SLURM_ACCOUNT=hochhalter-np
SLURM_PARTITION=hochhalter-np
SLURM_NODES=1
SLURM_NTASKS=1
SLURM_CPUS=8
SLURM_MEM=32G
SLURM_TIME=02:00:00
AGENT_SESSION_TIMEOUT_SECONDS=6600   # 1h50m: leaves time inside the 2h agent-host allocation to collect evidence

# --- experiments -----------------------------------------------------------------
# selector -> runs subdir | frozen config dir | run-id prefix | paired-block prefix | frozen id
experiment_field() {  # experiment_field <selector> <field>
  local sel=$1 f=$2
  case "$sel" in
    e1-example8)  local runs=E1_uninterrupted_example8        frozen=frozen_example8  prefix=E1-example8-baseline  block=E1 fid=FROZEN-EX8-v1  exp=E1 ;;
    e2-example16) local runs=E2_interrupted_recovery_example16 frozen=frozen_example16 prefix=E2-example16-baseline block=E2 fid=FROZEN-EX16-v1 exp=E2 ;;
    e3-example8)  local runs=E3_disparate_storage_example8     frozen=frozen_example8  prefix=E3-example8-baseline  block=E3 fid=FROZEN-EX8-v1  exp=E3 ;;
    *) return 1 ;;
  esac
  case "$f" in runs) echo "$runs";; frozen) echo "$frozen";; prefix) echo "$prefix";; block) echo "$block";; fid) echo "$fid";; exp) echo "$exp";; *) return 1;; esac
}
valid_experiment() { experiment_field "$1" runs >/dev/null 2>&1; }
executable_experiment() { [[ "$1" == e1-example8 || "$1" == e2-example16 ]]; }

# --- logging / failure -------------------------------------------------------------
log()  { printf '[%s] %s\n' "$(date -u +%FT%TZ)" "$*"; }
warn() { printf '[%s] WARNING: %s\n' "$(date -u +%FT%TZ)" "$*" >&2; }
die()  { printf '[%s] FATAL: %s\n' "$(date -u +%FT%TZ)" "$*" >&2; exit "${2:-1}"; }
# exit codes: 0 ok | 1 failure | 2 usage | 3 blocked by preflight | 4 refused (would overwrite / ambiguous state)
utc_now() { date -u +%FT%TZ; }
sha256_of() { sha256sum "$1" | cut -c1-64; }
require_cmd() { for c in "$@"; do command -v "$c" >/dev/null 2>&1 || die "required command not found: $c" 3; done; }

# --- manifest helpers (flat YAML keys only) ------------------------------------------
manifest_get() { # manifest_get <manifest> <key>
  sed -n "s/^$2: *//p" "$1" | head -1 | sed 's/^"\(.*\)"$/\1/'
}
manifest_set() { # manifest_set <manifest> <key> <value>   (value written as-is)
  local m=$1 k=$2 v=$3
  grep -q "^$k:" "$m" || die "manifest key not present: $k" 4
  local tmp; tmp=$(mktemp "$m.XXXXXX")
  awk -v k="$k" -v v="$v" 'BEGIN{done=0} { if(!done && index($0, k ":")==1){ print k ": " v; done=1 } else print }' "$m" > "$tmp" && mv "$tmp" "$m"
}

# --- packet state checks --------------------------------------------------------------
dir_only_gitkeep() { # true if directory exists and contains nothing but .gitkeep
  local d=$1; [[ -d "$d" ]] || return 1
  [[ -z "$(find "$d" -mindepth 1 ! -name .gitkeep -print -quit)" ]]
}
refuse_if_nonempty() { # refuse_if_nonempty <dir> <label>
  dir_only_gitkeep "$1" || die "$2 is not empty ($1); refusing to overwrite (fail closed)" 4
}
# optional third argument: redo suffix (e.g. R) for a replacement packet of an aborted trial
trial_dir_of() { echo "$RUNS_DIR/$(experiment_field "$1" runs)/baseline/trial_$(printf '%02d' "$2")${3:-}"; }
run_id_of()    { echo "$(experiment_field "$1" prefix)-$(printf '%02d' "$2")${3:-}"; }

# --- Claude-related environment ------------------------------------------------------------
# Remove any inherited Claude Code session environment (a launch from inside another Claude
# session must not be mistaken for a nested/child session) and set the frozen variables.
scrub_claude_env() {
  local v; for v in $(env | sed -n 's/^\(CLAUDE[A-Z0-9_]*\)=.*/\1/p'); do unset "$v"; done
  export DISABLE_AUTOUPDATER=1
  export CLAUDE_CODE_DISABLE_AUTO_MEMORY=1
  export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
}
claude_version_of() { DISABLE_AUTOUPDATER=1 "$1" --version 2>/dev/null | awk '{print $1}'; }
