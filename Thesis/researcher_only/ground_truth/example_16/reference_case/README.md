# Example 16 reference package (rebuilt from the canonical sources, 2026-10-09)

Researcher-only. Rebuilt from scratch with the canonical journal, stage-1 deck, restart deck and driver (see `../SOURCE_AUDIT.md`): mesh regenerated with the
approved Cubit, decks translated and executed with the approved Morphorm runtime through `sbatch` jobs on the frozen Slurm contract. No historical
output was copied in; historical runs were used only as validation evidence (`REFERENCE_VALIDATION.md`).

| Directory / file | Content |
|---|---|
| `inputs/` | immutable canonical copies (journal, `topology_mech_ex16.i`, `topology_mech_ex16_restart.i`, `runmorphorm.py`) and the one-line corrected restart deck (`restart_iteration 21`) with its diff |
| `mesh/` | regenerated `topology_mech_ex16.exo` (SHA-256 `6144707a1940d09299bf21e62846523d2d1561d7f74f77f8bbdc6f395ec8f2ca`), Cubit log, `mesh_validation.json` (7/7), hashes, timestamps |
| `preflight_stage1/`, `preflight_restart_corrected_21/`, `preflight_restart_shipped_20/` | XMLGenerator translations checked against the frozen formulation before execution |
| `stage1/` | **Stage 1** (canonical deck, 20 iterations, `write_restart_file true`): complete run directory; `engine_output.exo` is the checkpoint (21 states, `control` + `topology`) |
| `restart_corrected_21/` | **restart from the iteration-20 design** (manual semantics; `restart_iteration 21`): `initialguess.exo` = byte copy of the stage-1 checkpoint, complete run directory, 40 iterations |
| `restart_shipped_20/` | **restart with the unmodified shipped deck** (`restart_iteration 20` → iteration-19 design): same structure |
| `results/` | per-run `*_summary.json`, `*_criterion_history.csv`, `*_restart_evidence.json` |
| `figures/` | final topologies and the compliance-history comparison |
| `jobs/`, `logs/`, `environment/`, `tools/` | sbatch scripts and accounting; Slurm stdout/stderr; environment captures; scripts used |
| `acceptance_spec.json`, `ACCEPTANCE_SPEC.md` | predeclared acceptance specification and private tolerances |
| `GROUND_TRUTH_CONSTRUCTION_REPORT.md`, `REFERENCE_VALIDATION.md` | how it was built; comparison with the manual and historical evidence |
| `SHA256SUMS.txt` | SHA-256 of every file in this package |

Final outputs of record: `stage1/analyze_id_2_output_scenario_id_1/iteration20.exo` (Stage 1), `restart_corrected_21/analyze_id_2_output_scenario_id_1/iteration40.exo`
(overall iteration 60, manual semantics) and `restart_shipped_20/analyze_id_2_output_scenario_id_1/iteration40.exo` (shipped listing as executed). Which restart
semantics is accepted for E2 is the researcher's decision (`acceptance_spec.json: reference_policy`, currently `undecided`).
