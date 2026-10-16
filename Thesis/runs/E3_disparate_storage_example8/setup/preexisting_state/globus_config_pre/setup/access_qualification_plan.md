# Access qualification plan (to run later, on a compute node only)

Updated 2026-10-10 UTC (procedural-access update): new control-repository pin; item 7 now checks the procedural
researcher-only policy instead of technical isolation, which is not adopted for E3 (`setup/E3_PROCEDURAL_ACCESS_UPDATE.md`).

**Status: planned, not performed.** Every step needs a Slurm allocation on the agent-host partition, and steps 4–6 need
`$SLURM_TMPDIR`, so nothing here was run during setup. No step runs Morphorm, submits a Morphorm job, or launches an agent.

Run inside one interactive or batch allocation with the frozen agent-host contract:
```
salloc --account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=00:30:00
```
Record everything under a dedicated, non-trial directory, e.g.
`/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/setup/qualification_<UTC>/`
(`Q` below). Use `set -o pipefail`, `GIT_TERMINAL_PROMPT=0`, `GIT_SSH_COMMAND="ssh -o BatchMode=yes"`, and `</dev/null` on every
command so nothing can prompt. Each step records the command, UTC time, host, exit status and output in `Q/results.tsv`.

E3=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8

| # | Requirement | Procedure | Pass criterion |
|---|---|---|---|
| 1 | GitHub control repository readable noninteractively | `git ls-remote git@github.com:DaisyQuach/daisy-e3-distributed-context-control.git`; `git clone --no-checkout` into `$SLURM_TMPDIR/e3/_qual/control`; `git checkout --detach bd0b042de8bd38fe1149e9fc64aea832beb1bf3c` (procedural-access pin; previously `c3b87369…e3b7`); `sha256sum -c catalog/checksums.sha256` | exit 0 for all; HEAD equals the pin; checksums PASS; no prompt (BatchMode) |
| 2 | Private Globus source listable/transferable noninteractively (only if configured; see `GLOBUS_ACTION_REQUIRED.md`) | `globus whoami`; `globus ls <UUID>:/`; `globus transfer <UUID>:/README.md <node-endpoint>:...` only if a node-reachable destination endpoint exists, else record "transfer not applicable on node" | whoami/ls exit 0 without login prompt; listing matches `MANIFEST.tsv`. If not configured: record `NOT_CONFIGURED`, which keeps trials blocked |
| 3 | Candidate archive readable, not writable | `sha256sum -c MANIFEST.sha256` in `$E3/chpc_candidate_archive`; `find ... -perm /222` returns nothing; attempt `touch $E3/chpc_candidate_archive/.qual_write_probe` and `cp /dev/null $E3/chpc_candidate_archive/example_07/README.md` | reads PASS; zero write bits; both write probes fail with "Permission denied" (note: the owner could still `chmod`; see `permissions_audit.md`) |
| 4 | Fresh node-local staging directory | `echo $SLURM_TMPDIR`; `test ! -e $SLURM_TMPDIR/e3/baseline/QUAL`; `mkdir -p` it; `df -P` it; check whether `$SLURM_TMPDIR` contains the account name | directory created empty on the compute node; free space recorded. If `$SLURM_TMPDIR` is unset → record `ACTION_REQUIRED` (trials cannot run). If it contains the account name → researcher decision `E3_ALLOW_ACCOUNT_NAME_IN_TMPDIR` |
| 5 | Harmless artifact staged node-locally and hash-verified | `cp -p $E3/chpc_candidate_archive/README.md $SLURM_TMPDIR/e3/baseline/QUAL/`; compare `sha256sum` of source and copy | hashes equal; source unchanged (manifest re-check PASS) |
| 6 | Harmless artifact returned to a trial-style output directory | `mkdir -p Q/fake_trial/outputs`; `cp -p` the staged file there; hash compare | hashes equal; file is inside `Q/` (not a real trial) |
| 7 | Procedural researcher-only policy is in place (informational; not a technical-isolation test) | Confirm that the prepared `agent-inputs/` holds only the control snapshot, `trial_context.md`, `permitted_roots.txt` and `CONTROL_COMMIT.txt` (no researcher-only file, no completed Example 8 material); confirm that the prompt and `protocol/access_rules.md` state the prohibition; run `automation/audit_boundary.sh` on a scratch test tree with a job script that names a forbidden path | prohibition present in the prompt and protocol; packet clean; audit reports FAIL for the planted forbidden path. Under the E1/E2 procedural model, trial processes run as the owner account and **can** read `researcher_only/`. That is the stated limitation, not a failure of this item (changed 2026-10-10, procedural-access update; the earlier wording expected a technical FAIL) |

Additional checks in the same allocation (non-destructive):
- `"$HOME/.local/share/claude/versions/2.1.295" --version` and `--help` (flags), and `auth status --json` inside a throwaway
  `CLAUDE_CONFIG_DIR` under `$SLURM_TMPDIR` with a copied credential (removed afterwards): `loggedIn: true` (no model call).
- `$E3/automation/baseline/run_baseline_e3_trial.sh --trial-dir $E3/baseline/trial_01 --dry-run` inside the allocation:
  expected to stop only on items still marked action-required.
- `$E3/automation/verify_readonly_sources.sh --with-originals`: PASS before and after.

Clean-up: leave `$SLURM_TMPDIR` to the scheduler; keep `Q/` as the qualification record. Do not delete anything else.
