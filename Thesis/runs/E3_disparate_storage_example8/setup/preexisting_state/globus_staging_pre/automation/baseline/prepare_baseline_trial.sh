#!/usr/bin/env bash
# Prepare one fresh E3 baseline trial workspace: verify it is fresh, read the private control repository at its pinned
# commit noninteractively, and copy ONLY the frozen agent-visible control packet into <trial>/agent-inputs/.
# Usage: prepare_baseline_trial.sh --trial-dir <E3>/baseline/trial_NN --clone-root DIR [--staging-dir S]
#          [--config FILE] [--accept-legacy-agent-inputs] [--dry-run]
#   --clone-root   where the temporary clone is made (node-local, e.g. $TMPDIR/e3/_control); never inside the trial
#   --staging-dir  node-local staging directory to announce to the agent (optional; announced as $E3_STAGING_DIR otherwise)
#   --accept-legacy-agent-inputs  record a researcher decision to proceed although the pre-E3 packet directory
#                  agent_inputs/ (frozen E1 configuration and manuals) is present in the trial
#   --dry-run      check everything that can be checked without writing; print the plan
# Exit: 0 ok | 2 usage | 3 action required (ACTION_REQUIRED file in logs/) | 4 refused (not fresh / unsafe)
source "$(dirname "${BASH_SOURCE[0]}")/../lib/e3_common.sh"
td=""; cr=""; sd=""; cfg="$E3_AUTOMATION/baseline/baseline_e3_config.env"; legacy_ok=0; dry=0
while [[ $# -gt 0 ]]; do case "$1" in
  --trial-dir) td=${2:?}; shift 2;; --clone-root) cr=${2:?}; shift 2;; --staging-dir) sd=${2:?}; shift 2;; --config) cfg=${2:?}; shift 2;;
  --accept-legacy-agent-inputs) legacy_ok=1; shift;; --dry-run) dry=1; shift;;
  -h|--help) sed -n '2,13p' "$0"; exit 0;; *) die "unknown argument: $1" 2;; esac; done
td=$(e3_guard_trial_dir baseline "$td") || exit $?; tid=$(trial_id_of baseline "$td"); export E3_DRY_RUN=$dry
[[ -f "$cfg" ]] || { [[ $dry == 1 ]] && cfg="$E3_AUTOMATION/baseline/baseline_e3_config.env.example"; }
[[ -f "$cfg" ]] || die "config not found: $cfg (copy baseline_e3_config.env.example and fill it)" 2
# shellcheck disable=SC1090
source "$cfg"
: "${E3_CONTROL_REPO_URL:?config: E3_CONTROL_REPO_URL}" "${E3_CONTROL_COMMIT:?config: E3_CONTROL_COMMIT}" "${E3_GLOBUS_MODE:?config: E3_GLOBUS_MODE}"
[[ "$E3_CONTROL_COMMIT" =~ ^[0-9a-f]{40}$ ]] || die "E3_CONTROL_COMMIT must be a full 40-hex commit" 2
[[ -n "$cr" ]] || die "--clone-root is required" 2
cr=$(realpath -m -- "$cr"); under "$cr" "$td" && die "clone root must be outside the trial dir" 2

# 1. freshness (never overwrite)
"$E3_AUTOMATION/init_trial_workspace.sh" --system baseline --trial-dir "$td" --dry-run >/dev/null || die "trial workspace is not fresh: $td" 4
if [[ -d "$td/agent_inputs" ]]; then
  [[ $legacy_ok == 1 ]] || action_required "$td" legacy_agent_inputs_present \
"The trial directory contains the pre-E3 packet directory agent_inputs/ (frozen E1 Example-8 configuration and the two manuals).
An agent in this trial would see it next to agent-inputs/. A researcher must decide: (a) move it out of the trial directory to a
researcher-only archive, or (b) accept it explicitly by rerunning with --accept-legacy-agent-inputs (recorded in provenance)."
  log "legacy agent_inputs/ present; accepted by researcher flag (recorded)"
fi

# 2. control repository readable noninteractively at the pinned commit
export GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=20 -o StrictHostKeyChecking=yes"
if ! timeout 60 git ls-remote --quiet "$E3_CONTROL_REPO_URL" >/dev/null 2>&1; then
  action_required "$td" control_repo_unreadable "git ls-remote $E3_CONTROL_REPO_URL failed noninteractively (no prompt allowed). Check SSH key/agent or gh credentials on this node."
fi
if [[ $dry == 1 ]]; then
  log "DRY RUN: control repository reachable: $E3_CONTROL_REPO_URL"
  log "DRY RUN: would clone into $cr/$tid, check out $E3_CONTROL_COMMIT, verify catalog/checksums.sha256,"
  log "         copy task/ catalog/ protocol/ scripts/ README.md into $td/agent-inputs/control/, write trial_context.md,"
  log "         permitted_roots.txt and CONTROL_COMMIT.txt, then make agent-inputs/ read-only."
  exit 0
fi
"$E3_AUTOMATION/init_trial_workspace.sh" --system baseline --trial-dir "$td" >/dev/null
clone="$cr/$tid"; [[ -e "$clone" ]] && die "clone target exists: $clone (refusing reuse)" 4
mkdir -p "$cr"
timeout 300 git clone --quiet --no-checkout "$E3_CONTROL_REPO_URL" "$clone" 2>"$td/logs/control_clone.stderr" || action_required "$td" control_repo_clone_failed "git clone failed; see logs/control_clone.stderr"
record_command "$td" 0 git clone --quiet --no-checkout "$E3_CONTROL_REPO_URL" "$clone"
git -C "$clone" -c advice.detachedHead=false checkout --quiet --detach "$E3_CONTROL_COMMIT" || action_required "$td" control_commit_missing "pinned commit $E3_CONTROL_COMMIT is not in $E3_CONTROL_REPO_URL"
[[ "$(git -C "$clone" rev-parse HEAD)" == "$E3_CONTROL_COMMIT" ]] || die "checked-out commit differs from the pin" 1
(cd "$clone" && sha256sum -c --quiet catalog/checksums.sha256) || die "control repository checksums fail at $E3_CONTROL_COMMIT" 1

# 3. prompt identity: the automation prompt must equal the frozen task prompt in the repository
psha=$(sha256_of "$E3_AUTOMATION/baseline/baseline_e3_prompt.md")
[[ "$psha" == "$(sha256_of "$clone/task/task_prompt.md")" ]] || die "baseline_e3_prompt.md differs from task/task_prompt.md at the pinned commit" 1

# 4. copy only the frozen agent-visible packet (git archive: tracked files only, no .git)
ai="$td/agent-inputs"; mkdir -p "$ai/control"
git -C "$clone" archive --format=tar "$E3_CONTROL_COMMIT" README.md task catalog protocol scripts | tar -x -C "$ai/control"
record_command "$td" $? git archive "$E3_CONTROL_COMMIT" README.md task catalog protocol scripts
rm -f -- "$ai/.gitkeep"
echo "$E3_CONTROL_COMMIT" > "$ai/CONTROL_COMMIT.txt"
{ printf '# alias\tabsolute root (read-only collections usable by the record-keeping helpers)\n'
  printf 'e3-private-source\t%s\n' "$E3_GLOBUS_ROOT"
  printf 'e3-chpc-candidate-archive\t%s\n' "$E3_ARCHIVE_ROOT"
  printf 'e3-control\t%s\n' "$ai/control"; } > "$ai/permitted_roots.txt"
case "$E3_GLOBUS_MODE" in
  globus) gl="Globus collection \`${E3_GLOBUS_COLLECTION_ID:-unset}\` (noninteractive Globus CLI) is the only permitted access method; the path shown is the host path, for provenance only. Do not read it directly.";;
  posix_readonly_fallback) die "posix_readonly_fallback is withdrawn: Globus is mandatory for E3" 2;;
  *) die "E3_GLOBUS_MODE must be globus or posix_readonly_fallback" 2;;
esac
cat > "$ai/trial_context.md" <<CTX
# Trial context

| Item | Value |
|---|---|
| Trial identifier | \`$tid\` (also in \$E3_TRIAL_ID) |
| Trial root (working directory) | \`$td\` |
| Node-local staging directory | \`${sd:-\$E3_STAGING_DIR}\` (also in \$E3_STAGING_DIR) |
| Control repository commit | \`$E3_CONTROL_COMMIT\` (snapshot in \`agent-inputs/control/\`) |
| e3-private-source | \`$E3_GLOBUS_ROOT\` — $gl |
| e3-chpc-candidate-archive | \`$E3_ARCHIVE_ROOT\` (read-only POSIX) |
| Approved software interface | \`source $E3_ENV_LOADER\` |
| Record-keeping helpers | \`agent-inputs/control/scripts/non_destructive_preflight_helpers/\` (they read \`agent-inputs/permitted_roots.txt\`) |

\`agent-inputs/\` is read-only. Write only in \`work/ jobs/ logs/ outputs/ provenance/ staging-manifest/\` and the staging directory.

Access: read only this trial root, the two collections above, the control snapshot and the approved software interface.
Researcher-only records, other trials and experiments, original software/source trees, completed reference material, and
scoring or validation records are prohibited for the session and for every Slurm job it submits. Trials run under the
researcher's account, so this is a procedural rule rather than a filesystem restriction; every path used is audited
(\`agent-inputs/control/protocol/access_rules.md\`).
CTX
(cd "$ai" && find . -type f -print0 | sort -z | xargs -0 sha256sum) > "$td/provenance/agent_inputs.sha256"
chmod -R a-w "$ai"
{ echo "utc: $(utc_now)"; echo "trial_id: $tid"; echo "control_repo_url: $E3_CONTROL_REPO_URL"; echo "control_commit: $E3_CONTROL_COMMIT"
  echo "prompt_sha256: $psha"; echo "globus_mode: $E3_GLOBUS_MODE"; echo "access_model: ${E3_ACCESS_MODEL:-unset}"; echo "legacy_agent_inputs_present: $([[ -d $td/agent_inputs ]] && echo yes || echo no)"
  echo "legacy_agent_inputs_accepted_by_flag: $legacy_ok"; echo "agent_inputs_files: $(wc -l < "$td/provenance/agent_inputs.sha256")"; } > "$td/provenance/preparation.txt"
manifest_set "$td/manifest.yaml" e3dc_control_repo_url "\"$E3_CONTROL_REPO_URL\""
manifest_set "$td/manifest.yaml" e3dc_control_commit "$E3_CONTROL_COMMIT"
manifest_set "$td/manifest.yaml" e3dc_globus_mode "$E3_GLOBUS_MODE"
log "prepared $tid: agent-inputs/ populated from $E3_CONTROL_COMMIT and made read-only"
echo "$clone"
