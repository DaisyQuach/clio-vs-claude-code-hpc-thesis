# ACTION REQUIRED — compute-node qualification (non-scored), and Claude Code pin record

No allocation was available or requested during remediation (login node notchpeak1, 2026-10-10 UTC), so nothing below
has been run on a compute node yet. This procedure is **non-scored**: it starts no model session for a trial, runs no
Morphorm or Cubit, creates no scientific output, and writes only into a dedicated qualification record directory.

## 1. Allocation (researcher submits; short, frozen account/partition)
```bash
E3=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8
mkdir -p "$E3/setup/qualification"          # qualification records (researcher-side)
sbatch --account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=1 --mem=2G \
       --time=00:15:00 --job-name=e3-qual-nonscored \
       --output="$E3/setup/qualification/e3-qual-%j.out" \
       "$E3/setup/qualification/e3_compute_node_preflight.sbatch"
```
The batch file is to be written by the researcher from the body in §2 (it is shown here, not created, so that nothing can be
submitted by accident).

## 2. Batch body (checks; each line prints `CHECK <name> <value>`)
```bash
#!/bin/bash
set -u
E3=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8
red() { sed "s#$HOME#\$HOME#g; s#$(id -un)#<account>#g"; }       # never write the account name or home path
echo "CHECK utc $(date -u +%FT%TZ)"; echo "CHECK host $(hostname -s)"; echo "CHECK job $SLURM_JOB_ID"
# (a) does $SLURM_TMPDIR exist? exact path, ownership, writability
echo "CHECK slurm_tmpdir_set ${SLURM_TMPDIR:+yes}"
echo "CHECK slurm_tmpdir_path ${SLURM_TMPDIR:-<unset>}" | red
[[ -n "${SLURM_TMPDIR:-}" ]] && { stat -c 'CHECK slurm_tmpdir_owner %U:%G mode %a' "$SLURM_TMPDIR" | red
  [[ -w "$SLURM_TMPDIR" ]] && echo "CHECK slurm_tmpdir_writable yes" || echo "CHECK slurm_tmpdir_writable no"
  df -P "$SLURM_TMPDIR" | tail -1 | awk '{print "CHECK slurm_tmpdir_fs "$1" avail_kB "$4}'
  # (b) account-identifying components
  [[ "$SLURM_TMPDIR" == *"$(id -un)"* ]] && echo "CHECK slurm_tmpdir_contains_account_name yes" || echo "CHECK slurm_tmpdir_contains_account_name no"
  [[ "$SLURM_TMPDIR" == *"$(id -u)"* ]] && echo "CHECK slurm_tmpdir_contains_uid yes" || echo "CHECK slurm_tmpdir_contains_uid no"
  # (c) fresh per-trial staging dir: created new, refused if it exists, mode 700
  q="$SLURM_TMPDIR/e3/_qual/$SLURM_JOB_ID"; [[ -e "$q" ]] && echo "CHECK staging_fresh no (exists)" || { mkdir -p "$q" && chmod 700 "$q" && echo "CHECK staging_fresh yes"; }
  cp -p "$E3/chpc_candidate_archive/README.md" "$q/" && cmp -s "$E3/chpc_candidate_archive/README.md" "$q/README.md" && echo "CHECK staging_copy_hash_equal yes"
  # (d) retention: copy the staging listing back to the record directory BEFORE the job ends
  (cd "$q" && find . -type f -printf '%P\t%s\n' | sort) > "$E3/setup/qualification/staging_listing_$SLURM_JOB_ID.tsv"
  echo "CHECK staging_record_retained setup/qualification/staging_listing_$SLURM_JOB_ID.tsv"
}
# (e) pinned Claude Code (no model call)
B="$HOME/.local/share/claude/versions/2.1.295"
echo "CHECK claude_version $(DISABLE_AUTOUPDATER=1 "$B" --version 2>&1)"
echo "CHECK claude_sha256 $(sha256sum "$B" | cut -c1-64)"
# (f) E3 loader on the compute node (Lmod only; nothing executed)
( source "$E3/automation/environment/load_morphorm_e3.sh" && echo "CHECK loader ok" && command -v XMLGenerator PlatoMain cubit | red | sed 's/^/CHECK resolve /' )
# (g) sandbox on the compute node: harmless probe, with the staging dir mounted
"$E3/automation/sandbox/launch_e3_sandbox.sh" --system baseline --trial-dir "$E3/baseline/trial_01" ${SLURM_TMPDIR:+--staging-dir "$q"} \
   --claude-bin "$B" -- /bin/bash -s -- --with-loader < "$E3/automation/sandbox/sandbox_probe.sh" 2>&1 | red | sed 's/^/SANDBOX /'
echo "CHECK done"
```
Expected outcomes and decisions:
| Check | If it fails |
|---|---|
| `slurm_tmpdir_set no` | node-local staging is impossible as designed → researcher chooses another node-local root (e.g. `/scratch/local`) and records it |
| owner not the account / not writable | same as above |
| `slurm_tmpdir_contains_account_name yes` | the records policy forbids the account name → researcher sets `E3_ALLOW_ACCOUNT_NAME_IN_TMPDIR=1` (recorded) or chooses a different root; automation already refuses otherwise |
| staging not fresh | investigate reuse; never delete another job's data |
| Claude version ≠ 2.1.295 or hash ≠ §3 | stop; write `setup/CLAUDE_VERSION_ACTION_REQUIRED.md`; never substitute |
| loader / sandbox FAIL | resolve before any trial (`automation/sandbox/sandbox_validation_plan.md` B3/B4) |

**Clearing:** each trial creates a new `$SLURM_TMPDIR/e3/<system>/<trial>` and refuses an existing one
(`automation/init_node_local_staging.sh`); the automation deletes nothing. Clearing is left to Slurm's job-end cleanup of
`$SLURM_TMPDIR` — **to be confirmed by this qualification** (submit a second short job on the same node, if obtainable, and
check whether the first job's directory is gone; if not, the researcher decides on an explicit, recorded cleanup step).
**Retention:** staging records are written into the trial directory before the session ends
(`staging-manifest/node_local_final_listing.tsv` by `automation/record_staging_snapshot.sh`, and
`provenance/node_local_placement.automation.txt`), so they survive the purge of `$SLURM_TMPDIR`.

## 3. Pinned Claude Code record (verified on the login node, 2026-10-10 UTC)
| Item | Value |
|---|---|
| Canonical executable path | `$HOME/.local/share/claude/versions/2.1.295` — a regular file (not a symlink; `readlink -f` resolves to itself). `$HOME` is the account home directory; its literal path contains the account name and is withheld under the E3 path policy. This is the path E3 already references (`E3_CLAUDE_BIN_REL` in `automation/baseline/baseline_e3_config.env`). |
| `--version` | `2.1.295 (Claude Code)` (run with `DISABLE_AUTOUPDATER=1`; no model call) |
| SHA-256 | `4503bfe11a6c7fcc1e0b39b5e0d347c04248f750b03b0977b3ad6b531fe6f358` |
| Size / type | 256,113,848 bytes; ELF 64-bit x86-64, BuildID `ca2032b38650b44e05b2074617d524c7475c80f0` |
| Headless flags present in `--help` | `--print`/`-p`, `--output-format`, `--input-format`, `--verbose`, `--model`, `--session-id`, `--dangerously-skip-permissions`, `--permission-mode`, `--disable-slash-commands`, `--no-chrome`, `--no-session-persistence`, `--settings`, `--setting-sources`, `--strict-mcp-config`, `--mcp-config`, `--add-dir`, `--append-system-prompt`, `--allowedTools`, `--disallowedTools`, `--bare` (full text: `setup/remediation/claude_2.1.295_help.txt`, sha256 `550db4f8…5f09`) |
| Flags E3 requires (runner check) | `--print --output-format --model --session-id --dangerously-skip-permissions --verbose --disable-slash-commands --no-chrome` — all present |
| `~/.local/bin/claude` | resolves to `versions/2.1.296`; **not used** by E3 and not followed |
| Inside the sandbox | mounted read-only at `/opt/e3/bin/claude`; `--version` = 2.1.295 |

The exact 2.1.295 executable exists, so `setup/CLAUDE_VERSION_ACTION_REQUIRED.md` was **not** needed. Risk to note: the
pinned file sits in the auto-updater's versions directory, where old versions can be pruned. The SHA-256 above is the
reference; if the file disappears or its hash changes, stop and write `CLAUDE_VERSION_ACTION_REQUIRED.md`.
