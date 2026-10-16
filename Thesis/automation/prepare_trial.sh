#!/usr/bin/env bash
# Create a planned, empty baseline trial packet from the frozen configuration.
# Usage: prepare_trial.sh --experiment e1-example8|e2-example16|e3-example8 (--trial N [--suffix R] | --all-planned)
#   --suffix R: replacement packet trial_NNR (run id ...-NNR) for a trial aborted by a non-agent cause; the original packet is kept
# Refuses to touch an existing packet that has a manifest or any content.  No model call, no Slurm.
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
exp=""; trial=""; all=0; suffix=""
while [[ $# -gt 0 ]]; do case "$1" in
  --experiment) exp=${2:?}; shift 2;; --trial) trial=${2:?}; shift 2;; --suffix) suffix=${2:?}; shift 2;; --all-planned) all=1; shift;;
  -h|--help) sed -n '2,5p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
valid_experiment "$exp" || die "--experiment must be e1-example8, e2-example16 or e3-example8" 2
[[ $all -eq 1 || -n "$trial" ]] || die "give --trial N or --all-planned" 2
frozen="$COMMON_DIR/$(experiment_field "$exp" frozen)"; fid=$(cat "$frozen/FROZEN_CONFIG_ID.txt"); fhash=$(cut -d' ' -f1 "$frozen/FROZEN_CONFIG_SHA256.txt")
[[ "$fhash" == "$("$COMMON_DIR/scripts/hash_frozen_config.sh" "$frozen")" ]] || die "frozen configuration hash mismatch for $frozen" 3
prepare_one() {
  local n=$1 td rid block; td=$(trial_dir_of "$exp" "$n" "$suffix"); rid=$(run_id_of "$exp" "$n" "$suffix"); block="$(experiment_field "$exp" block)-$(printf '%02d' "$n")"
  if [[ -e "$td" ]]; then [[ -e "$td/manifest.yaml" ]] && die "packet already has a manifest: $td (refusing)" 4; [[ -z "$(find "$td" -mindepth 1 -print -quit)" ]] || die "packet directory not empty: $td (refusing)" 4; fi
  mkdir -p "$td"/{agent_inputs,work,jobs,logs,outputs}; for d in work jobs logs outputs; do : > "$td/$d/.gitkeep"; done
  # agent_inputs: only the frozen, agent-visible documents (plus permitted manuals)
  cp -p "$frozen"/*.md "$td/agent_inputs/"; cp -p "$frozen/FROZEN_CONFIG_ID.txt" "$frozen/FROZEN_CONFIG_SHA256.txt" "$frozen/FROZEN_CONFIG_FILES.sha256" "$td/agent_inputs/"
  mkdir -p "$td/agent_inputs/manuals"; cp -p "$frozen"/manuals/*.pdf "$td/agent_inputs/manuals/"
  if [[ "$exp" == e3-example8 ]]; then cat > "$td/agent_inputs/E3_PLANNED_NOT_EXECUTABLE.md" <<'EOF'
# E3 packet: planned only
This packet is reserved for the future disparate-storage deployment experiment. It is not executable yet: no launcher exists for
E3 and its manifest must remain `status: planned`. A future version adds the storage-distribution independent variable without
changing the frozen Example 8 scientific formulation in this directory.
EOF
  fi
  chmod -R a-w "$td/agent_inputs"
  local ihash; ihash=$("$COMMON_DIR/scripts/hash_frozen_config.sh" "$td/agent_inputs")
  cat > "$td/manifest.yaml" <<EOF
run_id: $rid
status: planned
experiment: $(experiment_field "$exp" exp)
experiment_selector: $exp
workflow: $(experiment_field "$exp" frozen)
paired_block: $block
system: baseline
frozen_configuration_id: $fid
frozen_configuration_sha256: $fhash
agent_inputs_sha256: $ihash
model_identifier: $CLAUDE_MODEL
agent_harness: claude-code
agent_harness_version: "$CLAUDE_PIN_VERSION"
headless: true
slurm_contract: "account=$SLURM_ACCOUNT partition=$SLURM_PARTITION nodes=$SLURM_NODES ntasks=$SLURM_NTASKS cpus=$SLURM_CPUS mem=$SLURM_MEM time=$SLURM_TIME"
created_utc: $(utc_now)
started_utc: null
finished_utc: null
agent_session_ids: null
agent_host_job_ids: null
workflow_job_ids: null
evidence_sha256_manifest: null
packet_verification: null
curation_researcher_reviewed: null
curation_include_in_analysis: null
curation_notes: null
scoring_decision: null
scoring_scored_utc: null
scoring_record: null
EOF
  log "prepared $rid at $td (agent_inputs sha256 $ihash)"
}
if [[ $all -eq 1 ]]; then for n in 1 2 3 4 5; do prepare_one "$n"; done; else prepare_one "$trial"; fi
