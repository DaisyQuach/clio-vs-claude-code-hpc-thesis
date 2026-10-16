# Run summary — E3 Symmetry-Plane Cantilever (E3-SPC-v1)

## 1. Identification
- Trial identifier (`$E3_TRIAL_ID`): `E3-clio-trial_06`
- Staging directory (`$E3_STAGING_DIR`): `/scratch/local/u1282901/16250333/e3/clio/E3-clio-trial_06` (host notch204, agent allocation 16250333; `provenance/node_local_placement.txt`)
- Control commit: `62954055b4e848f2155258c5b8c628eab97c8586` (snapshot `agent-inputs/control/`; `sha256sum -c catalog/checksums.sha256`: every listed file OK except `./.gitignore`, which is absent from the snapshot)
- Assigned task: construct and complete the minimum-compliance topology optimization of the half cantilever (x∈[0,2], y∈[0,1], z∈[0,0.5], symmetry plane z=0.5) exactly as locked in `task/frozen_task_specification.md`, 50 OC iterations with the approved Morphorm runtime, and deliver every artifact in §8.

## 2. Discovery
Collections searched (34 records in `provenance/sources_searched.tsv`): `e3-control` snapshot (all task, catalog, protocol, helper files); `e3-chpc-candidate-archive` by POSIX `ls -R` and `cat` (README, MANIFEST, and README/problem_card/provenance of example_01, example_07, example_13, example_16_restart); `e3-private-source` by `globus ls -r` of collection `6dcea62e-130d-47a9-8b77-80fba6f58693` (manuals/, documentation/, target_materials/) followed by Globus transfers of the selected files. No other location was listed, opened or read; the private collection's host path was not read directly.

## 3. Artifact selection (detail: `provenance/artifact_selections.md`)
- **example_07** (full 2×1×1 Helmholtz cantilever): ADAPTED — same material, load, support names, SIMP minimum, filter radius/penalty, OC, 50 iterations; journal halved to z∈[0,0.5] with sideset `ss_sym` added; deck extended with the `ss_sym` dispz=0 condition and the filter symmetry plane.
- **example_16_restart**: NOT USED (two-stage restart; specification requires one uninterrupted run).
- **example_01**: NOT USED (tet bracket, non-design block, tractions, kernel filter).
- **example_13**: NOT USED (2-D, pave QUAD4, traction).
- **Private source**: specification, README, software_contract.md, compute_resources.md, version_provenance.yaml, User Manual USED; Theory Manual listed but not staged (not needed); problem figure staged but the specification text was authoritative.

## 4. Staging (detail: `staging-manifest/`)
- 17 files, 2,669,516 bytes staged into `$E3_STAGING_DIR` (12 by Globus from e3-private-source via `staging-inbox/`, each verified against the collection `MANIFEST.sha256` whose SHA-256 d856bed2… equals the catalog value; 5 by `stage_file.sh` from e3-chpc-candidate-archive, manifest verification PASS). Globus task ids: `staging-manifest/globus_transfers.tsv`.
- 5 files, 14,269 bytes returned into `work/reference/` with `return_file.sh` (example_07 deck and journal, compute_resources.md, software_contract.md, problem_specification.md). The User Manual was converted to text in place (`work/manual_text/user_manual.txt`), not copied.
- Source/copy SHA-256 pairs match for every line of `staged_files.tsv` and `returned_files.tsv`.

## 5. Mesh
- Generated on the agent host with the approved Cubit (`cubit-edu/2026.8`, `cubit -batch -nographics -nojournal -input mesh.jou`, exit 0, 2026-10-13T18:54:39Z–18:54:42Z) from `outputs/mesh.jou` (adapted from example_07; `wd = 0.5`, `scheme map`, size 0.0416667, `sideset 1 add surface with z_coord > wd − esize/2` named `ss_sym`). Output `outputs/mesh.exo` (SHA-256 af069820…), Exodus II dimension 3.
- Verification (`outputs/mesh_verification.json`, bundled `exo_summary.py`, `expect_ok: true`): 13,824 HEX8 elements; 15,925 nodes; bbox [0,0,0]–[2.0,1.0,0.5]; one block `block_1` with all 13,824 elements; `ns_fix` 325 nodes; `ns_load` 13 nodes; `ss_sym` 1,152 faces. Every value equals the locked value.

## 6. Input deck and generated configuration
Accepted deck: `outputs/input_deck.i` (= `work/run02/input_deck.i`). Translated with `XMLGenerator input_deck.i` (exit 0) in `work/run02/`; generated files in `outputs/generated_config/`. Locked setting → where it appears in the generated configuration:
| Locked setting | Deck | Generated configuration |
|---|---|---|
| E = 1.0, ν = 0.3 on block_1 | material 1 / block 1 | `analyze_2_input_deck.xml` Material Models/material_1: Youngs Modulus 1.0, Poissons Ratio 0.3; Spatial Model/Domains/block_1 |
| SIMP exponent 3.0, minimum 1e-3; criterion minimum_ersatz 1e-3 | material_interpolation 1, criterion 1 | `analyze_2_input_deck.xml` Penalty Function (objective and residual): Type SIMP, Exponent 3.0, Minimum Value 1e-3 |
| ns_fix ux=uy=uz=0 | boundary_condition 1 | `analyze_2_input_deck.xml` Essential BCs: Displacement X/Y/Z with ID 1–3, Sides ns_fix, Value 0 |
| ss_sym uz=0 via sideset | boundary_condition 2 | `analyze_2_input_deck.xml` Essential BCs: Displacement Z with ID 4, Sides ss_sym, Value 0 |
| Load −1.0 in y on ns_load (13 nodes) | load 1 | `analyze_2_input_deck.xml` Concentrated Loads: Dof 1, Value −1.0, Nodes ns_load |
| Compliance objective, weight 1, analyze service | objective, service 2 | `interface.xml` Optimizer/Objective; `analyze_2_operations.xml` Compute Objective Value (Internal Elastic Energy); `engine_operations.xml` Aggregator Weight 1 |
| Volume ≤ 0.15, less_than, engine service | constraint 1, service 1 | `interface.xml` Constraint NormalizedTargetValue 0.15 (ReferenceValue Design Volume); `engine_operations.xml` ComputeVolume |
| Density, initial 0.15 | study | `engine_operations.xml` InitializeField Uniform Value 0.15 |
| OC, default tolerances, normalize_in_aggregator false | study | `interface.xml` Optimizer Package OC; OCControlStagnationTolerance 1e-4, OCObjectiveStagnationTolerance 1e-8, OCGradientTolerance 1e-8 (runtime defaults); no normalization element in the Aggregator |
| update_problem true, frequency 1 | service 1, study | `engine_operations.xml` Update Problem, UpdateProblemFrequency 1 |
| max_iterations 50 | study | `interface.xml` Convergence/MaxIterations 50; `engine_operations.xml` MaxIterations 50 |
| Helmholtz, radius 0.15, sticking penalty 1.0, symmetry sideset ss_sym | study-level `filter_type helmholtz`, `filter_radius_absolute 0.15`, `boundary_sticking_penalty 1.0`, `symmetry_plane_location_names ss_sym` | `analyze_helmholtz_input_deck.xml` Parameters: Length Scale 0.043301 (= 0.15/(2√3)), Surface Length Scale 1.0, Symmetry Plane Sides {ss_sym} |
| Services: engine + analyze, 1 processor each, no decomposition | service 1, 2 | `mpirun.source`: `-np 1` PlatoMain, `-np 1` analyze_MPMD (mechanical), `-np 1` analyze_MPMD (Helmholtz filter service added automatically) |
| Output dispx dispy dispz; engine control + topology | output 1 | `analyze_2_input_deck.xml` Output Plottable {displacement_x, displacement_y, displacement_z}; `engine_operations.xml` PlatoMainOutput inputs topology, control |

Translation history: `work/run01/` used the manual's `begin filter … end filter` form; its generated `analyze_helmholtz_input_deck.xml` lacked the symmetry sideset (`xml_params.py`: MISSING symmetry). It was **not** submitted. `work/run02/` used the equivalent study-level keywords (User Manual Table 2.5.12); all other generated files are byte-identical to run01. Verification record: `outputs/generated_config/VERIFICATION_xml_params.tsv` (one "MISSING algorithm" line is a probe pattern, not a setting; OC appears as Optimizer `Package`).
Note: `engine_operations.xml` ComputeVolume uses `PenaltyExponent 1.0 / MinimumValue 0.0`; that is the engine's linear volume measure for the constraint, not the structural SIMP interpolation, which is in the analyze configuration as locked.

## 7. Execution
Commands (agent host, UTC): `source …/load_morphorm_e3.sh`; `cubit -batch -nographics -nojournal -input mesh.jou` (18:54:39Z); `python3 exo_summary.py …` (18:55:17Z); `XMLGenerator input_deck.i` in work/run01 (18:55:31Z) and work/run02 (18:56:23Z); `python3 xml_params.py work/run02 …` (18:56:47Z); `sbatch --parsable jobs/morphorm_spc_run02.sbatch` (18:57:36Z); `wait_job.sh 16251472 …` (three bounded waits); `sacct -j 16251472 … -P` → `jobs/sacct_16251472.txt`; `hash_outputs.sh`.
Slurm jobs submitted (all in `jobs/job_ids.txt`):
| Job ID | Script | Resources | State | ExitCode | Start–End (local) | Elapsed | Node | MaxRSS |
|---|---|---|---|---|---|---|---|---|
| 16251472 | `jobs/morphorm_spc_run02.sbatch` (= `outputs/job_script.sbatch`) | hochhalter-np, 1 node, 1 task, 8 cpus, 32G, 02:00:00 (frozen values, no GPU) | COMPLETED | 0:0 | 2026-10-13T12:57:37–13:15:17 (MDT) | 00:17:40 | notch272 | 1,822,544 K |
The job sourced the approved software interface, printed `module list` (chpc/1.0, gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8; `outputs/run_logs/slurm-16251472.out`), hashed its inputs, and ran `bash mpirun.source` in `work/run02/` (Morphorm start 18:57:46Z). No Morphorm executable ran on the agent host. No job failed or was cancelled.

## 8. Completed stages and iteration counts
- Single uninterrupted optimization reached the iteration cap: `morphorm_oc_optimizer_diagnostics.txt` has 51 iteration rows (Iter 0 … 50), F-count 1 … 51 (`outputs/run_logs/diagnostics_run02.json`).
- Stopping message of the optimizer: `****** Optimization stopping due to exceeding maximum number of iterations. ******`
- Objective F(X): 2.654786e+06 at iteration 0 → 1.044701e+05 at iteration 50; constraint H1(X) at iteration 50 = −1.63e-13 (volume fraction at target); abs(dX) 1.14e-01 at the last step (no stagnation stop).
- Final analyze output `iteration50.exo` (time value 50): nodal Topology min 1.01e-08 / max 0.939, displacement X/Y/Z present; per-node check (`outputs/run_logs/bc_check_iteration50.txt`): max|u_z| on the 1,225 nodes of z = 0.5 is 0.0 (symmetry condition enforced), max|u| on the 325 nodes of x = 0 is 0.0, 13 loaded nodes with mean u_y = −1.607e+04; Σ(−u_y) over ns_load = 2.0894e+05 = 2 × F(X), consistent with F = ½ fᵀu. Topology mean 0.157.
- Engine output `engine_output.exo`: 51 time steps, nodal fields `control` and `topology`.

## 9. Key output files (SHA-256; full list in `outputs/SHA256SUMS.txt`, 27 entries)
| File | SHA-256 |
|---|---|
| outputs/mesh.exo | af069820471b044cfa76a23316ccb07cb95dcbcbaf0ebb863df54785627ca64d |
| outputs/mesh.jou | 7d1ed45abb665cb159ca29a1a0aa3914f68c4f0879cabe6a25e25d24d58efd8e |
| outputs/mesh_verification.json | d37ca675238200df81f9cfb4b3243d5560df87ccaae1764061504a6c2998d619 |
| outputs/input_deck.i | b96a080889406a03dfbbe3e56220a9c47817f010bc99edd970d1cf2f59452b04 |
| outputs/job_script.sbatch | 6eec8c92c7af280971db5922e6cd80e69384817e5c7ab0744fa1c382d90da7c5 |
| outputs/generated_config/interface.xml | 2f545669f80885d182291e9aad47d74baf8403082364f79f67542f653a616885 |
| outputs/generated_config/analyze_2_input_deck.xml | 9bc13ac9c61c0d8b3c7c73b5c0bce38e31c7d35b53e45483c2fd5238bea222e8 |
| outputs/generated_config/analyze_helmholtz_input_deck.xml | e0b190ab3e8c71334d7b7ec5f0567dbcdae40f7a371b943a553d6eb54fae5436 |
| outputs/generated_config/engine_operations.xml | c5b07640e3f1427a5f763631a2f7f9c3ec1ea54e97160106efe598afc0c67c1b |
| outputs/generated_config/mpirun.source | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| outputs/morphorm_oc_optimizer_diagnostics.txt | 5bf3294ab40a1a55925134eb0ef493c7cb725e0964ae54cb3ce1ee62ae18e4f4 |
| outputs/engine_output.exo | 9b053a7c2d14ab5200f97efc1b927f3c6a5c787e754ddbd16e6212a1a988f7c9 |
| outputs/final_analyze_output.exo | 7b9510366799145234e5d149e7916485b20f3ed58138e1f7d6d62f12afb7ceb7 |
| outputs/run_logs/slurm-16251472.out | 6ccdbea32487ff2e5d7c95af63c8f67fd5940704b567c43a300e05b8caa9d340 |
| outputs/run_logs/morphorm_run.log | 24f51bf3b88158d9283abd03eca2f99f5418a3726091ea5e77b1dfc81695f555 |

## 10. Failures, retries, cancelled jobs, unresolved issues, deviations
- Deviations from the specification: none. All locked values were realized and verified in the mesh and in the generated configuration; the run reached iteration 50.
- Retries: one re-translation (run01 → run02) before any submission, because the filter-block form did not propagate `symmetry_plane_location_names` to the generated Helmholtz configuration; run01 was never submitted and its files are kept in `work/run01/` as a record. No Slurm job failed, was cancelled or was resubmitted.
- Minor observations (not deviations): `sha256sum -c` of the control snapshot reports `./.gitignore` missing from the snapshot (not a task file). `globus --version` is not a valid option of the pinned CLI (harmless probe). `outputs/opt_criteria_history.csv` and the JSON/TXT verification records in `outputs/run_logs/` are extra deliverables, kept for traceability.
- No accepted deliverable was overwritten.

## 11. Final artifact paths (relative to the trial root)
`outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`, `outputs/input_deck.i`, `outputs/job_script.sbatch`, `outputs/generated_config/{interface.xml, analyze_2_input_deck.xml, analyze_helmholtz_input_deck.xml, engine_input_deck.xml, analyze_2_operations.xml, analyze_helmholtz_operations.xml, engine_operations.xml, mpirun.source, VERIFICATION_xml_params.tsv}`, `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`, `outputs/opt_criteria_history.csv`, `outputs/run_logs/{slurm-16251472.out, slurm-16251472.err, morphorm_run.log, xmlgenerator.log, cubit_mesh.log, diagnostics_run02.json, final_analyze_output.json, bc_check_iteration50.txt}`, `outputs/SHA256SUMS.txt`; `jobs/job_ids.txt`, `jobs/morphorm_spc_run02.sbatch`, `jobs/sacct_16251472.txt`, `jobs/submissions.tsv`; `logs/slurm-16251472.{out,err}`; `provenance/sources_searched.tsv`, `provenance/artifact_selections.md`, `provenance/node_local_placement.txt`, `provenance/control_and_source_versions.txt`; `staging-manifest/staged_files.tsv`, `staging-manifest/returned_files.tsv`, `staging-manifest/globus_transfers.tsv`; `work/run_summary.md`, `work/notes.log`, `work/run01/`, `work/run02/`, `work/mesh/`, `work/verify/`, `work/reference/`, `work/manual_text/`.
