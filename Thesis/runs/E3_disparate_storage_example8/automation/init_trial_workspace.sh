#!/usr/bin/env bash
# Create or verify a fresh E3 per-trial workspace. Never deletes or overwrites trial content.
# Usage: init_trial_workspace.sh --system baseline|clio --trial-dir <E3>/<system>/trial_NN [--dry-run]
#   Creates any missing standard directory (agent-inputs work staging-manifest jobs logs outputs provenance) with .gitkeep,
#   writes manifest.yaml from the template if absent, or appends the E3 distributed-context fields if an older
#   manifest lacks them (original preserved under setup/preexisting_state/). Refuses a workspace that is not fresh.
source "$(dirname "${BASH_SOURCE[0]}")/lib/e3_common.sh"
sys=""; td=""; dry=0
while [[ $# -gt 0 ]]; do case "$1" in --system) sys=${2:?}; shift 2;; --trial-dir) td=${2:?}; shift 2;; --dry-run) dry=1; shift;;
  -h|--help) sed -n '2,7p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
td=$(e3_guard_trial_dir "$sys" "$td") || exit $?; tid=$(trial_id_of "$sys" "$td")
for d in "${WRITABLE_TRIAL_DIRS[@]}"; do [[ ! -d "$td/$d" ]] || dir_is_fresh "$td/$d" || die "$td/$d is not fresh; refusing (use a new trial directory)" 4; done
[[ ! -d "$td/agent-inputs" ]] || dir_is_fresh "$td/agent-inputs" || die "$td/agent-inputs is already populated; refusing" 4
if [[ $dry == 1 ]]; then log "DRY RUN: $td would be initialized as $tid (no changes made)"; exit 0; fi
for d in "${TRIAL_DIRS[@]}"; do mkdir -p "$td/$d"; [[ -e "$td/$d/.gitkeep" ]] || : > "$td/$d/.gitkeep"; done
tmpl="$E3_AUTOMATION/templates/trial_manifest.yaml"
render() { sed -e "s|@TRIAL_ID@|$tid|g" -e "s|@SYSTEM@|$sys|g" -e "s|@CREATED_UTC@|$(utc_now)|g" "$1"; }
if [[ ! -f "$td/manifest.yaml" ]]; then
  render "$tmpl" > "$td/manifest.yaml"; log "wrote $td/manifest.yaml"
elif ! grep -q '^e3dc_trial_id:' "$td/manifest.yaml"; then
  bk="$E3_ROOT/setup/preexisting_state/${sys}_$(basename "$td")_manifest.pre_e3dc.yaml"; mkdir -p "$(dirname "$bk")"
  [[ -e "$bk" ]] || cp -p "$td/manifest.yaml" "$bk"
  { echo; echo "# --- E3 distributed-context fields (appended $(utc_now); original copy: setup/preexisting_state/$(basename "$bk")) ---"
    render "$tmpl" | sed -n '/^e3dc_/p'; } >> "$td/manifest.yaml"
  log "appended E3 distributed-context fields to existing $td/manifest.yaml"
else log "manifest.yaml already has E3 fields"; fi
log "workspace ready: $td ($tid)"
