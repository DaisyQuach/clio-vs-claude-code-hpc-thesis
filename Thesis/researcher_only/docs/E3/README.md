# E3 documentation (researcher-only)

E3 = disparate-storage deployment of the Symmetry-Plane Cantilever (Example 8) workflow. Baseline complete 2026-10-10
(5 valid trials, all accepted; attempt 02 excluded); **CLIO not yet run**.

| Document | Path |
|---|---|
| Baseline execution report (frozen config, job IDs, deviations, integrity) | `E3_BASELINE_EXECUTION_REPORT.md` |
| Baseline preflight report | `E3_BASELINE_PREFLIGHT_REPORT.md` |
| Setup, remediation, procedural-access, readiness, pilot, permission and Globus reports | `setup_reports/` |
| Evaluation and results | `Thesis/researcher_only/evaluation_figures/E3_baseline_prelim/E3_BASELINE_EVALUATION.md` |
| Combined E1/E2/E3 results | `Thesis/researcher_only/evaluation_figures/combined_E1_E2_E3/` |
| Original plan (superseded) | `../E3_PLAN.md` |

## What stays in the E3 run folder (`Thesis/runs/E3_disparate_storage_example8/`) and why
| Path | Why it cannot move before CLIO |
|---|---|
| `automation/` (incl. `environment/` 6.4 GB, `clio/`) | the pinned control repo (commit 62954055), the hash-locked Globus collection, the loader/modulefiles and the Globus CLI venv hard-code these paths; the 37 automation files are hash-checked by every job; CLIO runner is there (CLIO deferred) |
| `setup/baseline_execution/` (freeze, jobs, preflight, postprocess, manifests) | read by the counted-trial and postprocessing jobs |
| `setup/source_inventory.sha256`, `setup/remediation/`, `setup/preexisting_state/`, `setup/integrity/` | read by `verify_readonly_sources.sh` / `init_trial_workspace.sh`; integrity snapshots |
| `setup/CLIO_*.md`, `setup/RESEARCHER_ACTION_REQUIRED.md`, `setup/E3_BLOCKER_STATUS.yaml` | CLIO materials (not modified) |

Moved on 2026-10-10: `MOVED_FILES.tsv` (old path → new path, sha256; byte-identical). A one-line pointer stays at each old path so script
messages, trial manifests and older cross-references still resolve. Historical hash lists in `setup/` (e.g. `E3_SETUP_SHA256SUMS.txt`) list the
original bytes, which these moved copies keep. Full consolidation of E3 automation into `Thesis/automation` is planned after CLIO. (This folder moved from `Thesis/docs/E3/` to `Thesis/researcher_only/docs/E3/` on 2026-10-10.)
Note: `E3_BASELINE_EXECUTION_REPORT.md` is a living document and was updated after the move (§4 item 8); its MOVED_FILES.tsv hash is the as-moved version.
