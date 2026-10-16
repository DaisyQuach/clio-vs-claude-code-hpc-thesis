#!/usr/bin/env bash
# E3 filesystem sandbox (PROTOTYPE) — run one command in a bubblewrap mount namespace that exposes only the E3
# trial-specific paths, the candidate archive, the approved software, and system/scheduler paths.
# Usage:
#   launch_e3_sandbox.sh --system baseline|clio --trial-dir <E3>/<system>/trial_NN
#                        [--staging-dir DIR] [--control-dir DIR] [--claude-config-dir DIR] [--claude-bin FILE]
#                        [--globus-posix-fallback] [--scheduler direct|none] [--print-args] -- <command> [args...]
#   --staging-dir          node-local per-trial staging directory (read-write), e.g. $SLURM_TMPDIR/e3/<system>/<trial>
#   --control-dir          checkout of the private control repository at the pinned commit (read-only)
#   --claude-config-dir    isolated per-session Claude configuration directory (read-write)
#   --claude-bin           pinned Claude Code executable; mounted read-only at /opt/e3/bin/claude (neutral path)
#   --globus-posix-fallback  also expose globus_source_root/ read-only (only under the recorded researcher fallback decision)
#   --scheduler direct     expose Slurm client binaries, configuration and the munge socket (DEFAULT; see README:
#                          jobs submitted this way run OUTSIDE the sandbox)
#   --scheduler none       expose no scheduler interface (the agent cannot submit jobs)
#   --print-args           print the bwrap argument list and exit (no sandbox started)
# Mechanism: /usr/bin/bwrap (bubblewrap 0.4.0, RHEL 8 OS package, unprivileged user namespaces; no setuid, no root).
# Writes nothing itself. Never binds the E3 root, researcher_only/, setup/, Morphorm_ground_truth, E1/E2, ThesisExperiments,
# or any home directory. Exit codes: 2 usage | 4 refused (denied path would be exposed) | otherwise the command's status.
set -o pipefail
E3_ROOT=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8
SB_DIR="$E3_ROOT/automation/sandbox"
BWRAP=/usr/bin/bwrap

die() { echo "launch_e3_sandbox: $1" >&2; exit "${2:-2}"; }
system=""; td=""; sd=""; cd_=""; cfg=""; cbin=""; gfb=0; sched=direct; print=0
while [[ $# -gt 0 ]]; do case "$1" in
  --system) system=${2:?}; shift 2;; --trial-dir) td=${2:?}; shift 2;; --staging-dir) sd=${2:?}; shift 2;;
  --control-dir) cd_=${2:?}; shift 2;; --claude-config-dir) cfg=${2:?}; shift 2;; --claude-bin) cbin=${2:?}; shift 2;;
  --globus-posix-fallback) gfb=1; shift;; --scheduler) sched=${2:?}; shift 2;; --print-args) print=1; shift;;
  --) shift; break;; -h|--help) sed -n '2,22p' "$0"; exit 0;; *) die "unknown argument: $1";; esac; done
[[ $system == baseline || $system == clio ]] || die "--system must be baseline or clio"
[[ $sched == direct || $sched == none ]] || die "--scheduler must be direct or none"
[[ $print == 1 || $# -gt 0 ]] || die "no command given (use -- <command>)"
[[ -x $BWRAP ]] || die "bubblewrap not found at $BWRAP" 4
td=$(realpath -e -- "$td" 2>/dev/null) || die "trial dir not found"
[[ "$(dirname "$td")" == "$E3_ROOT/$system" && "$(basename "$td")" =~ ^trial_[0-9]{2}[A-Z]?$ ]] || die "trial dir must be $E3_ROOT/$system/trial_NN" 4
[[ -d "$td/agent-inputs" ]] || die "trial dir has no agent-inputs/" 4
[[ ! -e "$td/agent_inputs" ]] || die "legacy agent_inputs/ present in trial dir; refusing" 4

# ---- denied roots: refuse if any exposed source path is at/under/above one of them --------------------
mapfile -t DENIED < <(grep -v '^\s*#' "$SB_DIR/denied_paths.txt" | sed '/^\s*$/d')
# the account home directory is denied too (taken from $HOME at run time so no account path is written here)
HOME_REAL=$(realpath -m -- "$HOME")
under() { [[ "$1" == "$2" || "$1" == "$2"/* ]]; }
check_exposed() { local p d; p=$(realpath -m -- "$1")
  for d in "${DENIED[@]}" "${2-$HOME_REAL}"; do [[ -n "$d" ]] || continue
    under "$p" "$d" && die "refused: $p is inside denied root $d" 4
    under "$d" "$p" && die "refused: exposing $p would expose denied root $d" 4
  done; }

args=(--unshare-user --unshare-pid --unshare-ipc --unshare-uts --unshare-cgroup-try
      --die-with-parent --new-session --hostname e3-sandbox
      --proc /proc --dev /dev --tmpfs /tmp --tmpfs /run --dir /tmp/e3home
      --ro-bind /usr /usr --symlink usr/bin /bin --symlink usr/sbin /sbin --symlink usr/lib /lib --symlink usr/lib64 /lib64
      --ro-bind /etc /etc
      --ro-bind /uufs/chpc.utah.edu/sys /uufs/chpc.utah.edu/sys)
[[ -d /var/lib/sss/pipes ]] && args+=(--ro-bind /var/lib/sss/pipes /var/lib/sss/pipes)
if [[ $sched == direct ]]; then
  args+=(--ro-bind /uufs/notchpeak.peaks/sys /uufs/notchpeak.peaks/sys)
  [[ -S /var/run/munge/munge.socket.2 ]] && args+=(--ro-bind /var/run/munge /run/munge --symlink ../run /var/run)
fi

ro() { check_exposed "$1"; args+=(--ro-bind "$1" "${2:-$1}"); }
rw() { check_exposed "$1"; args+=(--bind "$1" "${2:-$1}"); }

# approved software: the loader, E3-local modulefiles and runtime copies only (not the researcher-side README/inventory)
for p in load_morphorm_e3.sh modulefiles runtime; do ro "$E3_ROOT/automation/environment/$p"; done
# candidate archive (read-only)
ro "$E3_ROOT/chpc_candidate_archive"
# private source collection only under the recorded researcher fallback decision
[[ $gfb == 1 ]] && ro "$E3_ROOT/globus_source_root"
# trial workspace: writable directories read-write; packet, manifest and README read-only (mounted after, so they win)
rw "$td"
ro "$td/agent-inputs"
[[ -f "$td/manifest.yaml" ]] && ro "$td/manifest.yaml"
[[ -f "$td/README.md" ]] && ro "$td/README.md"
[[ -n "$sd" ]] && { sd=$(realpath -e -- "$sd") || die "staging dir not found"; rw "$sd"; }
[[ -n "$cd_" ]] && { cd_=$(realpath -e -- "$cd_") || die "control dir not found"; ro "$cd_"; }
[[ -n "$cfg" ]] && { cfg=$(realpath -e -- "$cfg") || die "claude config dir not found"; rw "$cfg"; }
if [[ -n "$cbin" ]]; then
  cbin=$(realpath -e -- "$cbin") || die "claude binary not found"
  # single-file exemption from the home-directory denial: only the pinned executable file itself, at a neutral path
  [[ "$(basename "$cbin")" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ && -f "$cbin" ]] || die "--claude-bin must be a pinned versions/<x.y.z> file" 4
  check_exposed "$cbin" ""; args+=(--ro-bind "$cbin" /opt/e3/bin/claude)
fi
args+=(--chdir "$td")

# environment: start empty, pass only what the trial needs (no account-home path)
envv=(HOME=/tmp/e3home TMPDIR=/tmp LANG="${LANG:-C.UTF-8}" TERM=dumb
      PATH=/opt/e3/bin:/usr/local/bin:/usr/bin:/bin
      E3_SANDBOX=1 E3_SANDBOX_SYSTEM="$system" E3_TRIAL_ROOT="$td")
[[ -n "$sd" ]] && envv+=(E3_STAGING_DIR="$sd")
[[ -n "$cfg" ]] && envv+=(CLAUDE_CONFIG_DIR="$cfg")
[[ $sched == direct ]] && envv+=(PATH=/opt/e3/bin:/usr/local/bin:/usr/bin:/bin:/uufs/notchpeak.peaks/sys/installdir/slurm/std/bin)
for v in $(env | sed -n 's/^\(SLURM_[A-Z0-9_]*\)=.*/\1/p'); do envv+=("$v=${!v}"); done
for v in DISABLE_AUTOUPDATER CLAUDE_CODE_DISABLE_AUTO_MEMORY CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC E3_TRIAL_ID E3_SYSTEM; do
  [[ -n "${!v:-}" ]] && envv+=("$v=${!v}"); done

if [[ $print == 1 ]]; then printf '%q ' "$BWRAP" "${args[@]}" -- /usr/bin/env -i "${envv[@]}" "$@"; echo; exit 0; fi
exec "$BWRAP" "${args[@]}" -- /usr/bin/env -i "${envv[@]}" "$@"
