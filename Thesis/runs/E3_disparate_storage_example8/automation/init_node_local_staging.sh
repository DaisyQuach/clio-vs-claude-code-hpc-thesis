#!/usr/bin/env bash
# Create a fresh node-local staging directory $TMPDIR/e3/<system>/<trial_id> (Slurm per-job node-local dir) and record its placement.
# Usage: init_node_local_staging.sh --system baseline|clio --trial-dir D [--dry-run]
# Must run inside a Slurm allocation on the agent-host node. Refuses an existing directory (no reuse across trials).
source "$(dirname "${BASH_SOURCE[0]}")/lib/e3_common.sh"
sys=""; td=""; dry=0
while [[ $# -gt 0 ]]; do case "$1" in --system) sys=${2:?}; shift 2;; --trial-dir) td=${2:?}; shift 2;; --dry-run) dry=1; shift;;
  -h|--help) sed -n '2,4p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
td=$(e3_guard_trial_dir "$sys" "$td") || exit $?; tid=$(trial_id_of "$sys" "$td")
nlr=$(e3_node_local_root) || { E3_DRY_RUN=$dry action_required "$td" slurm_allocation \
  "A Slurm allocation with a per-job node-local \$TMPDIR (/scratch/local/<account>/<jobid>) is required to create node-local staging (SLURM_JOB_ID='${SLURM_JOB_ID:-}', TMPDIR='${TMPDIR:-}')."; }
if [[ "$nlr" == *"$(account_token)"* && "${E3_ALLOW_ACCOUNT_NAME_IN_TMPDIR:-0}" != 1 ]]; then
  E3_DRY_RUN=$dry action_required "$td" tmpdir_contains_account_name \
  "The node-local root contains the account name, which the E3 path policy forbids in records unless a researcher accepts it (E3_ALLOW_ACCOUNT_NAME_IN_TMPDIR=1 in the config)."
fi
sd="$nlr/e3/$sys/$tid"
[[ -e "$sd" ]] && die "staging directory already exists: $sd (refusing reuse)" 4
if [[ $dry == 1 ]]; then log "DRY RUN: would create $sd on $(hostname -s)"; echo "$sd"; exit 0; fi
mkdir -p "$sd"; chmod 700 "$sd"
{ echo "utc: $(utc_now)"; echo "host: $(hostname -s)"; echo "slurm_job_id: $SLURM_JOB_ID"; echo "staging_dir: $sd"; echo "node_local_root: \$TMPDIR (Slurm per-job, $(findmnt -n -o FSTYPE -T "$sd"))"
  echo "created_by: automation/init_node_local_staging.sh"; echo "filesystem:"; df -P "$sd" | sed 's/^/  /'; } > "$td/provenance/node_local_placement.automation.txt"
echo "$sd"
