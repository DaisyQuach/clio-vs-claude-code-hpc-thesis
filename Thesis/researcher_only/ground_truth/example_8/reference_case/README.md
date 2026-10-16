# Example 8 reference package (rebuilt from the canonical sources, 2026-10-09)

Researcher-only. Rebuilt from scratch with the canonical journal/deck/driver (see `../SOURCE_AUDIT.md`): the mesh was regenerated with the
approved Cubit, the deck translated and executed with the approved Morphorm runtime through `sbatch` jobs on the frozen Slurm contract.
No historical output was copied in; historical runs were used only as validation evidence (`REFERENCE_VALIDATION.md`).

| Directory / file | Content |
|---|---|
| `inputs/` | immutable copies of the canonical journal, deck and driver; the documented symmetry-honored variant deck; `README.md` with the diff |
| `mesh/` | regenerated `topology_mech_ex8.exo` (SHA-256 `46dd51a81e3502200c4b12223ebd2aacc95c4082311ad9e76128b41b3340f0f3`), Cubit log, `mesh_validation.json` (8/8), `mesh_sha256.txt`, timestamps |
| `preflight_run_canonical/`, `preflight_run_symmetry_honored_variant/` | XMLGenerator translations checked against the frozen formulation before execution (`preflight_check.{json,txt}`, `generated_config_sha256.txt`) |
| `run_canonical/` | **canonical shipped deck as executed**: deck, driver, mesh copy, generated XML, `mpirun.source`, `runmorphorm.{stdout,stderr}`, performer logs, `morphorm_oc_optimizer_diagnostics.txt`, `opt_criteria_history.csv`, `engine_output.exo` (51 states), `analyze_id_2_output_scenario_id_1/iteration{0..50}.exo` + criteria histories, `time_v.txt`, `timestamps.txt`, `inputs_sha256.txt`, `outputs_sha256.txt` |
| `run_symmetry_honored_variant/` | same content for the **symmetry-honored variant** (filter symmetry plane present in the generated configuration) |
| `results/` | `ex8_canonical_{summary.json,criterion_history.csv}`, `ex8_symmetry_honored_variant_{summary.json,criterion_history.csv}` |
| `figures/` | final topologies (ParaView 6.0.1, density ≥ 0.5, undeformed, colored by displacement magnitude; mirrored panels) |
| `jobs/` | sbatch scripts, `submissions.log`, `job_ids.txt`, `scontrol_*.txt`, `sacct_accounting.psv` |
| `logs/` | Slurm stdout/stderr per job |
| `environment/` | module/executable/runtime-hash captures per job |
| `tools/` | scripts used (mesh validation, generated-config check, summary, evidence, rendering, scoring, manifest) |
| `acceptance_spec.json`, `ACCEPTANCE_SPEC.md` | predeclared acceptance specification and private tolerances |
| `GROUND_TRUTH_CONSTRUCTION_REPORT.md`, `REFERENCE_VALIDATION.md` | how it was built; how it compares with the manual and historical evidence |
| `SHA256SUMS.txt` | SHA-256 of every file in this package (`sha256sum -c SHA256SUMS.txt`) |

Final outputs of record: `run_canonical/analyze_id_2_output_scenario_id_1/iteration50.exo` (compliance 1.468985e5) and
`run_symmetry_honored_variant/analyze_id_2_output_scenario_id_1/iteration50.exo` (compliance 1.044701e5). Which one is the accepted E1
reference is the researcher's decision (`acceptance_spec.json: reference_policy`, currently `undecided`).
