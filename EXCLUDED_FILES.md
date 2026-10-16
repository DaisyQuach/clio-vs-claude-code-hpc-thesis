# Files left out of this repository

The full record (about 31 GB) stays on CHPC at `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis`. Classes left out:

- `runs/E3_disparate_storage_example8/automation/environment/`: third-party software copies (Coreform Cubit, Morphorm runtime, Globus CLI).
- `.agent_runtime/` directories: per-session CLIO homes, isolated Claude config dirs and clio-core state (runtime state; the session evidence is kept under `logs/` and `researcher_only/session_evidence/`).
- Simulation binaries: `*.exo` / `*.e` Exodus meshes and results, clio-core blob stores (`*.bin_node*`, `*.blob.*`). Their SHA-256 values are in each trial's `outputs/SHA256SUMS.txt` / evidence checksums.
- `*.pdf` (Morphorm/Cubit manuals copied into packets), `*.pem`, `*.key`, `*.sqlite3`, `*.so`, `*.pyc`, `*.snapshot`, `*.lock`, `*.exe`, `.git/`, `__pycache__/`, `.venv/`.
- Any other file larger than 50 MB (listed below).

## Files over 50 MB not matched by the classes above

| Size (MB) | Path |
|---|---|
| 277 | `researcher_only/session_evidence/E1-example8-clio-01/session_main/clio/export_full.json` |
| 276 | `researcher_only/session_evidence/E1-example8-clio-02/session_main/clio/export_full.json` |
| 271 | `researcher_only/session_evidence/E1-example8-clio-03/session_main/clio/export_full.json` |
| 276 | `researcher_only/session_evidence/E1-example8-clio-03R/session_main/clio/export_full.json` |
| 275 | `researcher_only/session_evidence/E1-example8-clio-04/session_main/clio/export_full.json` |
| 286 | `researcher_only/session_evidence/E1-example8-clio-05/session_main/clio/export_full.json` |
| 223 | `researcher_only/session_evidence/E2-example16-clio-01/session_a/clio/export_full.json` |
| 529 | `researcher_only/session_evidence/E2-example16-clio-01/session_b/clio/export_full.json` |
| 225 | `researcher_only/session_evidence/E2-example16-clio-02/session_a/clio/export_full.json` |
| 531 | `researcher_only/session_evidence/E2-example16-clio-02/session_b/clio/export_full.json` |
| 217 | `researcher_only/session_evidence/E2-example16-clio-03/session_a/clio/export_full.json` |
| 535 | `researcher_only/session_evidence/E2-example16-clio-03/session_b/clio/export_full.json` |
| 227 | `researcher_only/session_evidence/E2-example16-clio-04/session_a/clio/export_full.json` |
| 544 | `researcher_only/session_evidence/E2-example16-clio-04/session_b/clio/export_full.json` |
| 224 | `researcher_only/session_evidence/E2-example16-clio-05/session_a/clio/export_full.json` |
| 178 | `researcher_only/session_evidence/E2-example16-clio-05/session_b/clio/export_full.json` |
| 235 | `researcher_only/session_evidence/E2-example16-clio-05R/session_a/clio/export_full.json` |
| 581 | `researcher_only/session_evidence/E2-example16-clio-05R/session_b/clio/export_full.json` |
| 277 | `runs/E1_uninterrupted_example8/clio/trial_01/logs/agent_sessions/session_main/clio/export_full.json` |
| 276 | `runs/E1_uninterrupted_example8/clio/trial_02/logs/agent_sessions/session_main/clio/export_full.json` |
| 271 | `runs/E1_uninterrupted_example8/clio/trial_03/logs/agent_sessions/session_main/clio/export_full.json` |
| 276 | `runs/E1_uninterrupted_example8/clio/trial_03R/logs/agent_sessions/session_main/clio/export_full.json` |
| 275 | `runs/E1_uninterrupted_example8/clio/trial_04/logs/agent_sessions/session_main/clio/export_full.json` |
| 286 | `runs/E1_uninterrupted_example8/clio/trial_05/logs/agent_sessions/session_main/clio/export_full.json` |
| 223 | `runs/E2_interrupted_recovery_example16/clio/trial_01/logs/agent_sessions/session_a/clio/export_full.json` |
| 529 | `runs/E2_interrupted_recovery_example16/clio/trial_01/logs/agent_sessions/session_b/clio/export_full.json` |
| 225 | `runs/E2_interrupted_recovery_example16/clio/trial_02/logs/agent_sessions/session_a/clio/export_full.json` |
| 531 | `runs/E2_interrupted_recovery_example16/clio/trial_02/logs/agent_sessions/session_b/clio/export_full.json` |
| 217 | `runs/E2_interrupted_recovery_example16/clio/trial_03/logs/agent_sessions/session_a/clio/export_full.json` |
| 535 | `runs/E2_interrupted_recovery_example16/clio/trial_03/logs/agent_sessions/session_b/clio/export_full.json` |
| 227 | `runs/E2_interrupted_recovery_example16/clio/trial_04/logs/agent_sessions/session_a/clio/export_full.json` |
| 544 | `runs/E2_interrupted_recovery_example16/clio/trial_04/logs/agent_sessions/session_b/clio/export_full.json` |
| 224 | `runs/E2_interrupted_recovery_example16/clio/trial_05/logs/agent_sessions/session_a/clio/export_full.json` |
| 178 | `runs/E2_interrupted_recovery_example16/clio/trial_05/logs/agent_sessions/session_b/clio/export_full.json` |
| 235 | `runs/E2_interrupted_recovery_example16/clio/trial_05R/logs/agent_sessions/session_a/clio/export_full.json` |
| 581 | `runs/E2_interrupted_recovery_example16/clio/trial_05R/logs/agent_sessions/session_b/clio/export_full.json` |
| 298 | `runs/E3_disparate_storage_example8/clio/trial_02/logs/session/export.json` |
| 298 | `runs/E3_disparate_storage_example8/clio/trial_02/logs/session/clio/export_full.json` |
| 299 | `runs/E3_disparate_storage_example8/clio/trial_03/logs/session/export.json` |
| 299 | `runs/E3_disparate_storage_example8/clio/trial_03/logs/session/clio/export_full.json` |
| 293 | `runs/E3_disparate_storage_example8/clio/trial_04/logs/session/export.json` |
| 293 | `runs/E3_disparate_storage_example8/clio/trial_04/logs/session/clio/export_full.json` |
| 292 | `runs/E3_disparate_storage_example8/clio/trial_05/logs/session/export.json` |
| 292 | `runs/E3_disparate_storage_example8/clio/trial_05/logs/session/clio/export_full.json` |
| 306 | `runs/E3_disparate_storage_example8/clio/trial_06/logs/session/export.json` |
| 306 | `runs/E3_disparate_storage_example8/clio/trial_06/logs/session/clio/export_full.json` |
| 293 | `runs/E3_disparate_storage_example8/clio/trial_07/logs/session/export.json` |
| 293 | `runs/E3_disparate_storage_example8/clio/trial_07/logs/session/clio/export_full.json` |
