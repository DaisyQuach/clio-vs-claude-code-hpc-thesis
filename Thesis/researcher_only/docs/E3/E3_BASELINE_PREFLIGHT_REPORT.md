# E3 baseline preflight (Phase 1, unscored) — PASS

| Item | Value |
|---|---|
| Job | **16173723** `e3-baseline-preflight-unscored`, node notch204, hochhalter-np, 1 CPU / 4 GB / 30 min, `--export=NONE` login shell (the counted-trial environment) |
| Window (UTC) | 2026-10-10T05:30:01Z → 05:30:54Z (sacct elapsed 00:01:01) |
| Exit | `COMPLETED 0:0`; 25 checks PASS, 0 FAIL (`out/preflight-16173723.checks`) |
| Script | `e3_baseline_preflight.sbatch` (sha256 in `e3_baseline_preflight.sbatch.sha256`) |
| stdout / stderr | `out/preflight-16173723.out` / `out/preflight-16173723.err` (stderr: only `TERM environment variable not set.`, from the non-interactive login shell) |
| Accounting | `out/sacct_16173723.psv` |

## What was verified
1. **Compute node / `$TMPDIR`:** `TMPDIR=/scratch/local/<account>/16173723`, XFS, owned by the account, empty at start, writable. No `CLAUDE*`/`ANTHROPIC*` variable is inherited with `--export=NONE`.
2. **GitHub:** remote `main` = pin `62954055…8586`; noninteractive clone + checkout at the pin; `catalog/checksums.sha256` verifies; `task/task_prompt.md` at the pin = `baseline_e3_prompt.md` = freeze (`63f84f79…1c20`).
3. **Globus:** pinned CLI 3.43.0, `whoami` noninteractive, approved collection `6dcea62e…8693` listable (read-only listing only; **no E3 research file transferred**). Collections verify; source `MANIFEST.sha256` = freeze (`d856bed2…cc53`).
4. **Staging helper (pinned copy from the clone):** harmless pilot file only, on the CHPC DMZ mapped collection, inside `preflight/scratch/`: Globus transfer → `scratch/trial_root/staging-inbox/` → manifest hash check → `cp -p` into `$TMPDIR` → hash re-check, all PASS (tasks `a80810a5…`, `aee3dc64…`). `..` path refused.
5. **Runtime loader:** hash = freeze; sourced rc 0; modules `morphorm/approved-runtime`, `cubit-edu/2026.8`; `cubit` and `XMLGenerator` resolve to the E3 runtime copies (**not executed**); 0 `ThesisExperiments` entries.
6. **Claude Code:** `2.1.295 (Claude Code)`, sha256 `4503bfe1…f358` = freeze; all headless flags present; credentials file present (not read). **No session, no `auth status`, no model call.**
7. **Audit/runner scripts:** syntax OK; all 37 frozen automation files match `freeze/automation_files.sha256`; jq present.
8. **Workspace:** wrote only in the designated `preflight/scratch/trial_root/` and `$TMPDIR`; baseline trial_01..05 still `verify --planned` PASS.

Not invoked: Claude session/model, Morphorm, Cubit, CLIO, any scientific workflow. Globus tasks of this job ended at 05:30:49Z, before any counted trial.
