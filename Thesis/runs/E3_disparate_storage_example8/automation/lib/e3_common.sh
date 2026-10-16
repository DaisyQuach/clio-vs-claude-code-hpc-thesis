#!/usr/bin/env bash
# Shared definitions for E3 (distributed-context) automation. Source only.
# Non-destructive by design: nothing here deletes, moves or edits a source collection, and every
# scientific source path is checked against the permitted roots before it is read.
set -o pipefail

# --- roots (canonical paths only) -------------------------------------------------------
E3_CANONICAL_ROOT=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8
DAISY_ROOT=/uufs/chpc.utah.edu/common/home/chet/Daisy
THESIS_ROOT=$DAISY_ROOT/Thesis
# E3_ROOT_OVERRIDE exists only for offline plumbing tests on a scratch copy; counted runs refuse it.
if [[ -n "${E3_ROOT_OVERRIDE:-}" ]]; then
  E3_ROOT=$E3_ROOT_OVERRIDE; E3_TEST_MODE=1
  [[ "$(realpath -m "$E3_ROOT")" != "$E3_CANONICAL_ROOT" ]] || { echo "E3_ROOT_OVERRIDE must not be the canonical root" >&2; exit 2; }
else
  E3_ROOT=$E3_CANONICAL_ROOT; E3_TEST_MODE=0
fi
E3_AUTOMATION=$E3_ROOT/automation
E3_GLOBUS_ROOT=$E3_ROOT/globus_source_root
E3_ARCHIVE_ROOT=$E3_ROOT/chpc_candidate_archive
E3_RESEARCHER_ONLY=$E3_ROOT/researcher_only
E3_RUNTIME_DIR=$E3_ROOT/.agent_runtime          # per-session Claude config dirs (mode 700), outside every trial workspace

# Approved software interface (E3 remediation): the E3 loader and its E3-local modulefiles/runtime copies.
# These are allowed (read/execute) for trials; the rest of automation/ stays forbidden.
E3_ENV_LOADER=$E3_AUTOMATION/environment/load_morphorm_e3.sh
E3_GLOBUS_CLI_DIR=$E3_AUTOMATION/environment/tools/globus-cli-3.43.0     # pinned Globus CLI (agent-executable)
E3_SOFTWARE_ROOTS=( "$E3_ENV_LOADER" "$E3_AUTOMATION/environment/modulefiles" "$E3_AUTOMATION/environment/runtime" "$E3_GLOBUS_CLI_DIR" )
# Globus (catalog v5): the private source collection is reached only by Globus; the CHPC mapped collection is permitted
# only as destination, inside the trial's staging-inbox/.
E3_GLOBUS_SOURCE_ID=6dcea62e-130d-47a9-8b77-80fba6f58693        # daisy-e3-private-source (guest, read-only)
E3_GLOBUS_DEST_ID=7cf0baa1-8bd0-4e91-a1e6-c19042952a7c          # CHPC DMZ mapped collection (destination only)

# Permitted read-only collections: alias -> root (researcher-side verification uses all of them)
declare -A E3_COLLECTIONS=( [e3-private-source]=$E3_GLOBUS_ROOT [e3-chpc-candidate-archive]=$E3_ARCHIVE_ROOT )
# Collections an agent may read by POSIX path (the private source is Globus-only for agents)
declare -A E3_AGENT_POSIX_COLLECTIONS=( [e3-chpc-candidate-archive]=$E3_ARCHIVE_ROOT )

# Locations a trial must never read (researcher-only, other experiments, obsolete tree, originals, software trees)
E3_FORBIDDEN_ROOTS=(
  "$E3_RESEARCHER_ONLY"
  "$E3_ROOT/setup"
  "$E3_ROOT/automation"
  "$E3_RUNTIME_DIR"
  "$E3_ROOT/baseline"            # other trials; the audit allows the trial's own directory first
  "$E3_ROOT/clio"
  "$THESIS_ROOT/researcher_only"
  "$THESIS_ROOT/runs/E1_uninterrupted_example8"
  "$THESIS_ROOT/runs/E2_interrupted_recovery_example16"
  "$DAISY_ROOT/ThesisExperiments"
  "$DAISY_ROOT/Morphorm_Full_Examples_Tests"
  "$DAISY_ROOT/Morphorm_ground_truth"
  "$DAISY_ROOT/Morphorm"
  "$DAISY_ROOT/morphorm_manuals"
  "$DAISY_ROOT/experiments_groundTruth"
)
# Plain-text patterns searched for in session evidence by the boundary audit
E3_FORBIDDEN_PATTERNS=(researcher_only Morphorm_ground_truth Morphorm_Full_Examples_Tests ThesisExperiments
  E1_uninterrupted_example8 E2_interrupted_recovery_example16 examplesmanual topology_mech_ex8 morphorm_manuals
  "Daisy/Morphorm/" experiments_groundTruth)

# --- logging / failure ------------------------------------------------------------------
# exit codes: 0 ok | 1 failure | 2 usage | 3 action required (blocked, nothing launched) | 4 refused (would overwrite / unsafe)
utc_now() { date -u +%FT%TZ; }
log()  { printf '[%s] %s\n' "$(utc_now)" "$*"; }
warn() { printf '[%s] WARNING: %s\n' "$(utc_now)" "$*" >&2; }
die()  { printf '[%s] FATAL: %s\n' "$(utc_now)" "$*" >&2; exit "${2:-1}"; }
sha256_of() { sha256sum "$1" | cut -c1-64; }
require_cmd() { local c; for c in "$@"; do command -v "$c" >/dev/null 2>&1 || return 1; done; }
under() { [[ "$1" == "$2" || "$1" == "$2"/* ]]; }     # under <abs path> <abs root>
# Replace the expanded home directory with the literal string $HOME in anything written to records,
# so records never contain the account-specific home path.
redact_home() { local h=$HOME; sed "s|${h//|/\\|}|\$HOME|g"; }
account_token() { id -un; }

# --- path guards ---------------------------------------------------------------------------
is_forbidden() { local p r; p=$(realpath -m -- "$1"); for r in "${E3_FORBIDDEN_ROOTS[@]}"; do under "$p" "$r" && return 0; done; return 1; }
collection_of() { local p a; p=$(realpath -m -- "$1"); for a in "${!E3_COLLECTIONS[@]}"; do under "$p" "${E3_COLLECTIONS[$a]}" && { echo "$a"; return 0; }; done; return 1; }
e3_guard_source() { # refuse any source path that is forbidden or not inside a permitted collection
  is_forbidden "$1" && die "refused: $1 is in a forbidden location" 4
  collection_of "$1" >/dev/null || die "refused: $1 is not inside a permitted collection" 4
}
trial_id_of() { # trial_id_of <system> <trial dir> -> E3-<system>-trial_NN
  echo "E3-$1-$(basename "$2")"
}
e3_guard_trial_dir() { # e3_guard_trial_dir <system> <dir> -> prints canonical trial dir or dies
  local sys=$1 d; d=$(realpath -m -- "$2")
  [[ "$sys" == baseline || "$sys" == clio ]] || die "system must be baseline or clio" 2
  [[ "$d" == "$E3_ROOT/$sys/trial_"[0-9][0-9] ]] || die "trial dir must be $E3_ROOT/$sys/trial_NN (got $d)" 2
  [[ -L "$d" ]] && die "trial dir must not be a symlink" 4
  echo "$d"
}

# --- node-local staging root (CHPC: Slurm prolog sets TMPDIR=/scratch/local/<account>/<jobid>; $SLURM_TMPDIR is unset) ---
# Verified by the readiness pilot (jobs 16172237, 16172265): per-job, fresh, writable, owner = account, xfs; not removed
# at job end, so a new job ID guarantees a fresh directory. Prints the root or returns 1.
e3_node_local_root() {
  local r=${TMPDIR:-}
  [[ -n "${SLURM_JOB_ID:-}" && -n "$r" && -d "$r" && -w "$r" ]] || return 1
  [[ "$r" == /scratch/local/* && "$(basename "$r")" == "$SLURM_JOB_ID" && -O "$r" ]] || return 1
  echo "$r"
}

# --- trial records -------------------------------------------------------------------------
TRIAL_DIRS=(agent-inputs work staging-manifest staging-inbox jobs logs outputs provenance)
WRITABLE_TRIAL_DIRS=(work staging-manifest staging-inbox jobs logs outputs provenance)   # staging-inbox/: Globus destination only
dir_is_fresh() { # true if the directory exists and holds nothing but .gitkeep / README.md
  [[ -d "$1" ]] || return 1
  [[ -z "$(find "$1" -mindepth 1 ! -name .gitkeep ! -name README.md -print -quit)" ]]
}
append_tsv() { # append_tsv <file> <header> <fields...>
  local f=$1 h=$2; shift 2; mkdir -p "$(dirname "$f")"
  [[ -s "$f" ]] || printf '%s\n' "$h" > "$f"
  local IFS=$'\t'; printf '%s\n' "$*" >> "$f"
}
record_command() { # record_command <trial dir> <rc> <command...>  -> provenance/automation_commands.tsv
  local td=$1 rc=$2; shift 2
  append_tsv "$td/provenance/automation_commands.tsv" $'utc\texit_status\tcommand' "$(utc_now)" "$rc" "$(printf '%q ' "$@" | redact_home)"
}
manifest_get() { sed -n "s/^$2: *//p" "$1" | head -1 | sed 's/^"\(.*\)"$/\1/'; }
manifest_set() { # manifest_set <manifest> <key> <value>; key must already exist (flat YAML)
  local m=$1 k=$2 v=$3 tmp
  grep -q "^$k:" "$m" || die "manifest key not present: $k" 4
  tmp=$(mktemp "$m.XXXXXX")
  awk -v k="$k" -v v="$v" 'BEGIN{d=0} { if(!d && index($0, k ":")==1){ print k ": " v; d=1 } else print }' "$m" > "$tmp" && mv "$tmp" "$m"
}
action_required() { # action_required <trial dir> <code> <message> : write ACTION_REQUIRED and stop with exit 3
  local td=$1 code=$2 msg=$3 f
  f="$td/logs/ACTION_REQUIRED_${code}.md"
  if [[ -d "$td/logs" && -w "$td/logs" && "${E3_DRY_RUN:-0}" != 1 ]]; then
    { echo "# ACTION REQUIRED: $code"; echo; echo "UTC: $(utc_now)"; echo; echo "$msg" | redact_home; echo
      echo "Nothing was launched. Resolve the condition above and rerun; this file is kept as a record."; } > "$f"
    warn "action required ($code): see $f"
  else
    warn "action required ($code): $msg"
  fi
  exit 3
}

# --- read-only source verification --------------------------------------------------------------
verify_collections() { # prints one line per collection; returns 1 if any fails
  local a r rc=0
  for a in $(printf '%s\n' "${!E3_COLLECTIONS[@]}" | sort); do
    r=${E3_COLLECTIONS[$a]}
    if [[ -f "$r/MANIFEST.sha256" ]] && (cd "$r" && sha256sum -c --quiet MANIFEST.sha256 >/dev/null 2>&1); then
      echo "$a PASS manifest_sha256=$(sha256_of "$r/MANIFEST.sha256") files=$(wc -l < "$r/MANIFEST.sha256")"
    else echo "$a FAIL"; rc=1; fi
  done
  return $rc
}
