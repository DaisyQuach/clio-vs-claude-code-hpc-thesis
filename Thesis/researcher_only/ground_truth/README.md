# Ground truth (researcher-only)

| Example | Audit | Reference package | Status |
|---|---|---|---|
| Example 8 (E1, E3) | `example_8/SOURCE_AUDIT.md` | `example_8/reference_case/` — canonical shipped deck as executed + symmetry-honored variant; `acceptance_spec.json` (`ACCEPT-EX8-v1`) | complete; `reference_policy` decision pending |
| Example 16 (E2) | `example_16/SOURCE_AUDIT.md` | `example_16/reference_case/` — stage 1 + restart from iteration 20 (`restart_iteration 21`) + shipped restart (`restart_iteration 20`); `acceptance_spec.json` (`ACCEPT-EX16-v1`) | complete; `reference_policy` decision pending |

`tools/`: shared scripts (`validate_mesh.py`, `check_generated_config.py`, `summarize_run.py`, `restart_evidence.py`, `score_trial.py`,
`render_topology_pv.py` + `render_figures.sh` (ParaView 6.0.1), `ref_mesh_job.sh`, `ref_run_job.sh`, `env_capture.sh`, `make_sha256_manifest.sh`).
Each `reference_case/tools/` holds the copies used by that build. Run Python tools with the approved runtime's `python3 -I`.

Agent-visible material must never name anything under this directory.
