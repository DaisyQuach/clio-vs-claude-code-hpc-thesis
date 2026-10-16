# Thesis — Controlled, Fully Automated Experiment Suite (Morphorm Manual Examples 8 and 16)

Built 2026-10-09 (UTC). Read `EXPERIMENTAL_DESIGN.md` first, then `BUILD_REPORT.md` (status, blockers, approval items)
and `automation/README.md` (how to run). Nothing in this tree runs a counted trial without the explicit guards described there.

| Path | Content | Visibility |
|---|---|---|
| `EXPERIMENTAL_DESIGN.md` | what E1, E2 and E3 test, replicates, measures, limits | researcher |
| `BUILD_REPORT.md` | audit results, reference job IDs, hashes, created files, dry-run results, approval checklist | researcher |
| `common/frozen_example8/` | frozen agent-visible configuration for the Example 8 workflow (E1 and E3) | **agent-visible** (copied into packets) |
| `common/frozen_example16/` | frozen agent-visible configuration for the Example 16 workflow (E2) | **agent-visible** (copied into packets) |
| `common/scripts/` | approved-software loader, frozen-configuration hashing, environment capture | agent-visible (loader only) |
| `automation/` | fully headless Claude Code baseline automation for E1/E2 (dry-run and counted modes); E3 automation index: `automation/E3_README.md` | researcher |
| `researcher_only/docs/` (moved from `docs/` 2026-10-10; `docs/` now holds pointers) | headless syntax verification, fresh-session enforcement, visibility boundary, E3 plan (superseded); E3 reports: `researcher_only/docs/E3/` | researcher-only |
| `runs/E1_uninterrupted_example8/baseline/trial_01..05` | planned E1 packets | agent-visible during a trial |
| `runs/E2_interrupted_recovery_example16/baseline/trial_01..05` | planned E2 packets | agent-visible during a trial |
| `runs/E3_disparate_storage_example8/baseline/trial_01..05` | planned, non-executable E3 packets | — |
| `automation/clio/` | CLIO arm automation (added 2026-10-11): planned-packet preparation, preflight, one fresh CLIO deployment per session, E1/E2 runners, evidence collection and supplementary verification. It reuses the baseline scripts unchanged; see `automation/clio/README.md` | researcher |
| `runs/E1_…/clio/trial_01..05`, `runs/E2_…/clio/trial_01..05` | planned CLIO packets (2026-10-11), byte-identical `agent_inputs/` to the paired baseline packets; not yet run | agent-visible during a trial |
| `runs/E3_…/clio/trial_01..05` | planned E3 CLIO workspaces; runner `runs/E3_…/automation/clio/run_clio_e3_trial_v2.sh` (2026-10-11); not yet run | agent-visible during a trial |
| `researcher_only/ground_truth/` | source audits, rebuilt references, acceptance specs, scorer tools | **researcher-only, never agent-visible** |
| `researcher_only/session_evidence/` | per-session launch records, streams, transcripts (staged here during a run) | researcher-only |
| `researcher_only/scores/`, `researcher_only/evaluation_figures/` | scoring records and figures | researcher-only |

Path note: `/uufs/chpc.utah.edu/common/home/u1282901/chet/Daisy/Thesis` and `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis` are the same directory.

**CLIO arm status (2026-10-11):** automation and planned packets are in place for E1, E2 and E3, and no counted CLIO trial has run. Counted runs are refused until the CLIO version and blueprint placeholders in `automation/clio/clio_trial_config.env` are filled in. The baseline packets, evidence and scores were not changed. Pre-update copies of this file and `automation/README.md` are in `automation/clio/_pre_update_20261011/`.
