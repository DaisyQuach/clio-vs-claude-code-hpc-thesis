#!/bin/bash -l
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --export=NONE
#SBATCH --job-name=e3-baseline-preflight-unscored
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/setup/baseline_execution/preflight/out/preflight-%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/setup/baseline_execution/preflight/out/preflight-%j.err
# E3 baseline Phase 1 preflight (UNSCORED). Same job environment as the counted trials (login shell, --export=NONE,
# hochhalter-np). Does NOT invoke a Claude session/model call, Morphorm, Cubit or any scientific workflow.
# Writes only: its own Slurm out/err, preflight/scratch/trial_root/ (designated preflight workspace), and $TMPDIR.
set -u
E3=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8
P=$E3/setup/baseline_execution/preflight; S=$P/scratch; TR=$S/trial_root
FREEZE=$E3/setup/baseline_execution/freeze/baseline_freeze.json
red() { sed -e "s#${HOME}#\$HOME#g"; }
res=(); ok() { res+=("PASS $1: $2"); echo "PASS $1: $2"; }; bad() { res+=("FAIL $1: $2"); echo "FAIL $1: $2"; }
fz() { jq -r "$1" "$FREEZE"; }
{
echo "== preflight start $(date -u +%FT%TZ) host=$(hostname -s) job=${SLURM_JOB_ID:-} cpus=${SLURM_CPUS_PER_TASK:-} mem_per_node=${SLURM_MEM_PER_NODE:-} partition=${SLURM_JOB_PARTITION:-} account=${SLURM_JOB_ACCOUNT:-}"
echo "== (0) inherited CLAUDE*/ANTHROPIC* variables (names only; expect none)"; env | sed -n 's/^\(CLAUDE[A-Z0-9_]*\|ANTHROPIC[A-Z0-9_]*\)=.*/\1/p' | sed 's/^/  /'; echo "  (end)"
# 1. compute-node environment and node-local TMPDIR
echo "== (1) node-local TMPDIR"
if [[ -n "${TMPDIR:-}" && "$TMPDIR" == /scratch/local/* && "$(basename "$TMPDIR")" == "$SLURM_JOB_ID" && -d "$TMPDIR" && -w "$TMPDIR" && -O "$TMPDIR" ]]; then
  ok tmpdir "TMPDIR=$TMPDIR fs=$(findmnt -n -o FSTYPE -T "$TMPDIR") mode=$(stat -c %a "$TMPDIR") owner_ok"
else bad tmpdir "TMPDIR='${TMPDIR:-unset}' not a fresh per-job /scratch/local dir"; fi
[[ -z "$(find "$TMPDIR" -mindepth 1 -print -quit 2>/dev/null)" ]] && ok tmpdir_fresh "empty at job start" || bad tmpdir_fresh "not empty at job start"
mkdir -p "$TMPDIR/e3_preflight" && echo probe > "$TMPDIR/e3_preflight/probe.txt" && [[ "$(cat "$TMPDIR/e3_preflight/probe.txt")" == probe ]] && ok tmpdir_write "write/read in \$TMPDIR/e3_preflight" || bad tmpdir_write "cannot write \$TMPDIR"
df -hP "$TMPDIR" | sed 's/^/  /'
# 2. GitHub at the frozen commit
echo "== (2) private GitHub at the frozen pin"
export GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=20 -o StrictHostKeyChecking=yes"
URL=$(fz .control_repository.url); PIN=$(fz .control_repository.commit)
head=$(timeout 60 git ls-remote "$URL" refs/heads/main 2>&1 | cut -f1); echo "  remote main = $head"
C="$TMPDIR/e3_preflight/control"
if timeout 300 git clone --quiet --no-checkout "$URL" "$C" 2>&1 && git -C "$C" -c advice.detachedHead=false checkout --quiet --detach "$PIN" && [[ "$(git -C "$C" rev-parse HEAD)" == "$PIN" ]]; then
  ok github_pin "clone + checkout $PIN"
  (cd "$C" && sha256sum -c --quiet catalog/checksums.sha256) && ok control_checksums "catalog/checksums.sha256 verifies at pin" || bad control_checksums "checksums fail"
  [[ "$(sha256sum "$C/task/task_prompt.md" | cut -c1-64)" == "$(fz .prompt.sha256)" && "$(sha256sum "$E3/automation/baseline/baseline_e3_prompt.md" | cut -c1-64)" == "$(fz .prompt.sha256)" ]] \
    && ok prompt_hash "task_prompt.md at pin == baseline_e3_prompt.md == freeze ($(fz .prompt.sha256))" || bad prompt_hash "prompt hash mismatch"
else bad github_pin "clone/checkout of $PIN failed"; fi
# 3. approved private Globus collection (read-only listing only; no research file transferred)
echo "== (3) Globus"
G=$E3/automation/environment/tools/globus-cli-3.43.0/bin/globus; SRC=$(fz .globus.source_collection_id)
"$G" version </dev/null 2>/dev/null | sed -n 's/^Installed version:/  cli/p'
timeout 60 "$G" whoami </dev/null >/dev/null 2>&1 && ok globus_auth "whoami noninteractive" || bad globus_auth "whoami failed"
if timeout 120 "$G" ls "$SRC:/" </dev/null > "$TMPDIR/e3_preflight/ls.txt" 2>&1; then ok globus_collection "ls $SRC:/ -> $(tr '\n' ' ' < "$TMPDIR/e3_preflight/ls.txt")"; else bad globus_collection "ls $SRC:/ failed"; fi
"$E3/automation/verify_readonly_sources.sh" | sed 's/^/  /'; [[ ${PIPESTATUS[0]} -eq 0 ]] && ok source_manifests "collections verify; source MANIFEST.sha256 = $(sha256sum "$E3/globus_source_root/MANIFEST.sha256" | cut -c1-64)" || bad source_manifests "verification failed"
[[ "$(sha256sum "$E3/globus_source_root/MANIFEST.sha256" | cut -c1-64)" == "$(fz .globus.source_manifest_sha256)" ]] && ok source_manifest_frozen "matches freeze" || bad source_manifest_frozen "differs from freeze"
# 4. staging helper (pinned copy) with harmless pilot content only
echo "== (4) staging helper with pilot content"
H="$C/scripts/non_destructive_preflight_helpers/globus_stage_file.sh"
export E3_TRIAL_ROOT=$TR E3_STAGING_DIR="$TMPDIR/e3_preflight/staging" E3_TRIAL_ID=E3-baseline-preflight
mkdir -p "$E3_STAGING_DIR"
out=$(bash "$H" docs/preflight_pilot.txt 2>&1); rc=$?; echo "$out" | sed 's/^/  /'
if [[ $rc -eq 0 && -f "$E3_STAGING_DIR/preflight-pilot-source/docs/preflight_pilot.txt" ]] && \
   [[ "$(sha256sum "$E3_STAGING_DIR/preflight-pilot-source/docs/preflight_pilot.txt" | cut -c1-64)" == "$(awk '{print $1}' "$S/pilot_source/MANIFEST.sha256")" ]]; then
  ok staging_helper "Globus transfer -> staging-inbox -> manifest hash check -> cp into \$TMPDIR verified"
else bad staging_helper "rc=$rc"; fi
bash "$H" ../etc/passwd >/dev/null 2>&1 && bad helper_refusal "accepted '..' path" || ok helper_refusal "refuses '..' path"
sed 's/^/  /' "$TR/staging-manifest/globus_transfers.tsv" "$TR/staging-manifest/staged_files.tsv" 2>/dev/null
unset E3_TRIAL_ROOT E3_STAGING_DIR E3_TRIAL_ID
# 5. runtime loader (no execution of Morphorm/Cubit)
echo "== (5) runtime loader"
[[ "$(sha256sum "$E3/automation/environment/load_morphorm_e3.sh" | cut -c1-64)" == "$(fz .runtime.loader_sha256)" ]] && ok loader_hash "matches freeze" || bad loader_hash "differs"
( source "$E3/automation/environment/load_morphorm_e3.sh" >/dev/null 2>&1; rc=$?
  echo "  loader rc=$rc; modules: $(module -t list 2>&1 | tr '\n' ' ')"
  for x in cubit XMLGenerator; do p=$(command -v "$x" 2>/dev/null); echo "  $x -> ${p:-NOT FOUND}"; done
  env | grep -c ThesisExperiments | sed 's/^/  ThesisExperiments entries in env: /'
  [[ $rc -eq 0 && -n "$(command -v cubit)" && -n "$(command -v XMLGenerator)" ]] ) && ok loader "sourced rc 0; cubit and XMLGenerator resolve (not executed)" || bad loader "loader failed or executables missing"
# 6. pinned Claude Code: version/help only (no session, no auth call, no model call)
echo "== (6) Claude Code pin"
CB="$HOME/$(sed -n 's/^E3_CLAUDE_BIN_REL=\([^ ]*\).*/\1/p' "$E3/automation/baseline/baseline_e3_config.env")"
v=$(DISABLE_AUTOUPDATER=1 "$CB" --version 2>/dev/null); sh=$(sha256sum "$(readlink -f "$CB")" | cut -c1-64)
[[ "$v" == "2.1.295 (Claude Code)" && "$sh" == "$(fz .claude.sha256)" ]] && ok claude_pin "$v sha256=$sh" || bad claude_pin "version='$v' sha=$sh"
hl=$(DISABLE_AUTOUPDATER=1 "$CB" --help 2>/dev/null); miss=""
for f in --print --output-format --model --session-id --dangerously-skip-permissions --verbose --disable-slash-commands --no-chrome; do grep -q -- "$f" <<< "$hl" || miss+=" $f"; done
[[ -z "$miss" ]] && ok claude_flags "all headless flags in --help" || bad claude_flags "missing:$miss"
[[ -f "$HOME/.claude/.credentials.json" ]] && ok claude_credentials_file "present (not read; headless auth is checked by the runner at launch)" || bad claude_credentials_file "missing"
# 7. audit script availability (syntax only; no pycache written)
echo "== (7) audit and runner scripts"
for f in audit_boundary.sh lib/e3_common.sh baseline/run_baseline_e3_trial.sh baseline/prepare_baseline_trial.sh baseline/verify_baseline_trial.sh baseline/collect_baseline_metrics.sh; do bash -n "$E3/automation/$f" || bad syntax "$f"; done
for f in lib/classify_tool_paths.py lib/classify_globus.py; do python3 -I -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$E3/automation/$f" || bad syntax "$f"; done
(cd "$E3" && sha256sum -c --quiet setup/baseline_execution/freeze/automation_files.sha256) && ok automation_frozen "all frozen automation files match the freeze list" || bad automation_frozen "automation differs from freeze"
command -v jq >/dev/null && ok jq "$(jq --version)" || bad jq missing
# 8. designated workspace only
echo "== (8) designated preflight workspace"
echo "preflight $SLURM_JOB_ID $(date -u +%FT%TZ)" > "$TR/preflight_write_probe.txt" && ok workspace_write "wrote $TR/preflight_write_probe.txt" || bad workspace_write "cannot write"
for t in 01 02 03 04 05; do "$E3/automation/baseline/verify_baseline_trial.sh" --trial-dir "$E3/baseline/trial_$t" --planned > /dev/null && ok "trial_${t}_untouched" "verify --planned PASS" || bad "trial_${t}_untouched" "verify --planned FAIL"; done
nf=$(printf '%s\n' "${res[@]}" | grep -c '^FAIL'); echo "== preflight end $(date -u +%FT%TZ) failures=$nf"
printf '%s\n' "${res[@]}" > "$P/out/preflight-$SLURM_JOB_ID.checks"
} 2>&1 | red
CK="$P/out/preflight-$SLURM_JOB_ID.checks"; nf=$(grep -c '^FAIL' "$CK" 2>/dev/null)
[[ -s "$CK" && "$nf" == 0 ]] && exit 0 || exit 1
