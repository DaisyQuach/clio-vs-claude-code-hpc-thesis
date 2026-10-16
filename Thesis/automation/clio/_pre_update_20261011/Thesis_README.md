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
| `runs/*/clio/` | reserved for the CLIO system; nothing implemented in this build | — |
| `researcher_only/ground_truth/` | source audits, rebuilt references, acceptance specs, scorer tools | **researcher-only, never agent-visible** |
| `researcher_only/session_evidence/` | per-session launch records, streams, transcripts (staged here during a run) | researcher-only |
| `researcher_only/scores/`, `researcher_only/evaluation_figures/` | scoring records and figures | researcher-only |

Path note: `/uufs/chpc.utah.edu/common/home/u1282901/chet/Daisy/Thesis` and `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis` are the same directory.
