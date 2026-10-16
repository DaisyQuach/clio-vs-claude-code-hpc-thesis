# Run summary — E3-baseline-trial_04 (E3-SPC-v1 Symmetry-Plane Cantilever)

## 1. Trial identifier, staging directory, control commit, assigned task
- Trial identifier (`$E3_TRIAL_ID`): `E3-baseline-trial_04`
- Trial root: `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_04`
- Node-local staging directory (`$E3_STAGING_DIR`): `/scratch/local/u1282901/16173746/e3/baseline/E3-baseline-trial_04` (host notch274, agent-host Slurm job 16173746; placement record in `provenance/node_local_placement.txt`)
- Control commit used: `62954055b4e848f2155258c5b8c628eab97c8586` (snapshot `agent-inputs/control/`, catalog version 5; `catalog/checksums.sha256` PASS for all 27 present files)
- Assigned task: construct and complete the Symmetry-Plane Cantilever minimum-compliance topology optimization exactly as locked in `task/frozen_task_specification.md` (specification `E3-SPC-v1`, SHA-256 f1bd0b56…): half cantilever x∈[0,2], y∈[0,1], z∈[0,0.5], structured HEX8 48×24×12, Helmholtz filter with the cut plane as filter symmetry plane, OC, exactly 50 iterations, run through Slurm with the frozen resources, all deliverables at locked paths.

## 2. Discovery
Detail: `provenance/sources_searched.tsv` (30 entries, in order). Collections searched, all from `catalog/permitted_storage_catalog.yaml`:
- `e3-control` — the snapshot in `agent-inputs/control/` (task, catalog, cards, protocol, helpers), read in full first.
- `e3-chpc-candidate-archive` — recursive POSIX listing (`find`) of the read-only root, manifest verified PASS (`verify_collection.sh`), then `README.md` and every package (`example_01`, `example_07`, `example_13`, `example_16_restart`: README, problem card, provenance, deck(s), journal) read in place.
- `e3-private-source` — `globus ls --recursive` of collection `6dcea62e-130d-47a9-8b77-80fba6f58693` (root: `MANIFEST.sha256`, `MANIFEST.tsv`, `README.md`, `documentation/`, `manuals/`, `target_materials/`), followed by Globus staging of the needed files (section 4). The host path of this collection was never read.
- `e3-trial-inbox-destination` — used only as the Globus destination for this trial's `staging-inbox/`.
No other location was listed, searched or opened. The approved software interface was used only by sourcing its loader.

## 3. Artifact selection
Detail: `provenance/artifact_selections.md`.
- USED: control specification/protocol/helpers; private-source specification, target README files, software contract, compute-resource contract, curated documentation and version provenance; Morphorm User Manual (deck syntax: filter-block keywords, Helmholtz `symmetry_plane_location_names`, sideset `fixed_value` boundary condition, `material_interpolation`, service `update_problem`, output block, output file layout).
- ADAPTED (read in place, not copied): candidate `example_07` (full-domain Helmholtz cantilever): its journal idiom and deck layout were followed; every task-specific value was set from the specification (half domain, `ss_sym` sideset, u_z = 0 on the sideset, explicit SIMP block, filter symmetry plane, `update_problem_frequency 1` on the engine service).
- NOT USED: `example_16_restart` (two-stage restart; the task is one uninterrupted run), `example_13` (2-D, traction), `example_01` (tet mesh, kernel filter, fixed blocks); Theory Manual (not staged; not needed); target figure (staged, not opened).

## 4. Staging
Detail: `staging-manifest/staged_files.tsv`, `staging-manifest/globus_transfers.tsv`, `staging-manifest/returned_files.tsv`.
- Staged from `e3-private-source` by Globus into `staging-inbox/` and then (manifest-checked, `cp -p`) into `$E3_STAGING_DIR/e3-private-source/`: 12 files, 2,660,751 bytes (README.md, MANIFEST.tsv, documentation/MANIFEST_README.md, curated_readme.md, version_provenance.yaml, curated_permitted_materials/compute_resources.md, software_contract.md, target_materials/symmetry_plane_cantilever/README.md, problem_specification.md, permitted_starting_materials/README.md, geometry_and_loading_figure.png, manuals/Morphorm_User_Manual.pdf). The collection `MANIFEST.sha256` (1,482 bytes) was transferred first (13 Globus tasks, all SUCCEEDED); its SHA-256 equals the catalog value d856bed2…. Source and staged SHA-256 matched for every file.
- Staged from `e3-chpc-candidate-archive`: none (packages were read in place; nothing from them was copied).
- Returned from staging into the workspace: none (0 files, 0 bytes). The Slurm job needed only files written under `work/` (journal, mesh, deck, generated configuration). `staging-manifest/returned_files.tsv` holds the header and a note.
- The manual's text was extracted on the agent host with `pdftotext` into `work/manual_text/user_manual.txt` for keyword searches (workspace copy, not a source modification).

## 5. Mesh
- Journal `work/mesh/mesh.jou` (deliverable `outputs/mesh.jou`), written from the specification: brick 2 × 1 × 0.5 moved so its corner is at the origin, `scheme map`, size 0.0416667, `block_1` HEX8, `ns_fix` = nodes with x < h/2, `ns_load` = nodes with x > 2 − h/2 and y < h/2, `ss_sym` = surface with z > 0.5 − h/2, exported Exodus II dimension 3.
- Generated on the agent host (permitted for meshing) with the approved Cubit: `cubit -batch -nographics -nojournal -input mesh.jou` (cubit-edu/2026.8 through the approved loader), 2026-10-10T07:12:55Z–07:12:58Z, exit 0 (`outputs/run_logs/cubit_run.log`). Mesh file `work/mesh/mesh.exo` → copied byte-identically to `work/run/mesh.exo` (used by the run) and `outputs/mesh.exo`.
- Verification (`work/scripts/verify_mesh.py` with the runtime's python3/netCDF4, record `outputs/mesh_verification.json`, 2026-10-10T07:13:34Z): PASS, 19/19 checks. num_dim 3; 13,824 elements; 15,925 nodes; one block `block_1`, HEX8, 13,824 elements; bounding box x [0, 2], y [0, 1], z [0, 0.5]; 49 × 25 × 13 coordinate planes (48 × 24 × 12 cells), h = 0.0416667 in x, y, z; `ns_fix` 325 nodes, all at x = 0 and equal to the full x = 0 node set; `ns_load` 13 nodes, all at x = 2, y = 0, z spanning [0, 0.5]; `ss_sym` 1,152 faces, all four nodes of every face at z = 0.5; exactly two nodesets and one sideset.

## 6. Input deck and locked settings in the generated configuration
Deck: `work/run/input_deck.i` (deliverable `outputs/input_deck.i`). Translated with `XMLGenerator input_deck.i` in `work/run/` (2026-10-10T07:17Z, exit 0, log `outputs/generated_config/xmlgenerator.log`). Generated files (deliverable `outputs/generated_config/`): `interface.xml`, `engine_input_deck.xml`, `engine_operations.xml`, `analyze_2_input_deck.xml`, `analyze_2_operations.xml`, `analyze_helmholtz_input_deck.xml`, `analyze_helmholtz_operations.xml`, `mpirun.source`. Scripted verification `work/scripts/verify_generated_config.py` → `outputs/generated_config/generated_config_verification.json`: PASS, 55/55 checks, before submission.

| Locked setting | Deck | Generated configuration |
|---|---|---|
| Material E = 1.0, ν = 0.3 on `block_1` | `material 1`, `block 1 name block_1 material_id 1` | `analyze_2_input_deck.xml` Material Models/material_1/Isotropic Linear Elastic: Youngs Modulus 1.0, Poissons Ratio 0.3; Spatial Model/Domains/block_1 → material_1 |
| SIMP exponent 3.0, minimum 1e-3 | `material_interpolation 1` (single_phase, simp, penalty_exponent 3.0, minimum_value 1e-3) | `analyze_2_input_deck.xml` Residual/Mechanical Residual/Penalty Function: SIMP, Exponent 3.0, Minimum Value 1e-3; Material Interpolation Model Single-Phase |
| Compliance criterion `minimum_ersatz_material_value 1e-3` | `criterion 1` | `analyze_2_input_deck.xml` Criteria/My Objective: Internal Elastic Energy on {block_1}, Penalty Function SIMP, Exponent 3.0, Minimum Value 1e-3 |
| Fixed support `ns_fix` u_x=u_y=u_z=0 (nodeset) | `boundary_condition 1` | Essential Boundary Conditions: Displacement X/Y/Z with ID 1/2/3, Fixed Value, Sides ns_fix, Value 0 |
| Symmetry `ss_sym` u_z = 0 through the sideset | `boundary_condition 2` (location_type sideset, dispz, 0) | Essential Boundary Conditions: Displacement Z with ID 4, Fixed Value, Sides ss_sym, Value 0 (no other condition on ss_sym) |
| Load −1.0 per node, direction y, on `ns_load`; no other loads | `load 1` concentrated_load | Concentrated Loads/Concentrated Load with ID 0: Dof 1, Value −1.0, Nodes ns_load; Natural Boundary Conditions list empty; no body loads |
| Objective weighted sum, single compliance criterion, weight 1, analyze service | `objective` weighted_sum, service_ids 2 | `interface.xml` stage Compute Objective Value → operation on performer analyze_2; `engine_operations.xml` Aggregator Weighting = {1} |
| Volume ≤ 15 %, less_than, engine service | `constraint 1` relative_target 0.15, service_id 1 | `interface.xml` Optimizer/Constraint NormalizedTargetValue 0.15, ReferenceValueName Design Volume; stage Compute Constraint Value 1 on performer engine_1 (ComputeVolume) |
| Density discretization, initial density 0.15 | `study` discretization density, initial_density_value 0.15 | `engine_operations.xml` InitializeField Uniform 0.15; SetLower/UpperBounds Discretization density; bounds 0.0–1.0 |
| OC, default tolerances, `normalize_in_aggregator false` | `study` optimization_algorithm oc, normalize_in_aggregator false | `interface.xml` Optimizer Package OC, OCControlStagnationTolerance 1e-4, OCObjectiveStagnationTolerance 1e-8, OCGradientTolerance 1e-8 (runtime defaults); Aggregator has no normalization element |
| `update_problem true`, frequency 1 on the engine service | `service 1` update_problem true, update_problem_frequency 1 | `interface.xml` Optimizer ProblemUpdateFrequency 1 + UpdateProblemStage "Update Problem" on engine_1; `engine_operations.xml` Update Problem UpdateProblemFrequency 1 |
| `max_iterations 50` | `study` max_iterations 50 | `interface.xml` Convergence/MaxIterations 50; `engine_operations.xml` PlatoMainOutput MaxIterations 50, WriteRestart false |
| Helmholtz filter, radius 0.15, sticking penalty 1.0, symmetry plane `ss_sym` | `filter 1` helmholtz, radius_absolute 0.15, boundary_sticking_penalty 1.0, symmetry_plane_location_names ss_sym; plus `study` symmetry_plane_location_names ss_sym (see note) | `analyze_helmholtz_input_deck.xml` Physics Helmholtz Filter; Parameters: Length Scale 0.043301 (= 0.15 / (2√3), the runtime's conversion of the absolute radius), Surface Length Scale 1.0, Symmetry Plane Sides {ss_sym} |
| Engine + analyze services, one processor each, single-rank performers, no decomposition | `service 1`/`service 2` number_processors 1 | `mpirun.source`: three performers (PlatoMain engine, analyze_MPMD mechanical, analyze_MPMD Helmholtz) each `-np 1`; no decomposition step |
| Output dispx dispy dispz from analyze; engine output of control and topology | `output 1` output_data true, data dispx dispy dispz | `analyze_2_input_deck.xml` Output/Plottable {displacement_x, displacement_y, displacement_z}; `interface.xml` stage Output To File: PlatoMainOutput inputs topology and control; `engine_input_deck.xml` output file engine_output |

Note on the filter symmetry plane: the first translation (deck with `symmetry_plane_location_names` only inside the filter block) produced a Helmholtz configuration without the symmetry-plane sideset; that attempt was not used and is preserved in `work/xmlgen_tests/attempt1_filter_block_only/`. Tests in `work/xmlgen_tests/A` and `B` showed that this XMLGenerator build propagates the study-level keyword; the accepted deck keeps the recommended filter block and adds the study-level keyword, which yields `Symmetry Plane Sides = {ss_sym}`. The accepted generated files were verified after this retranslation and before submission.

## 7. Execution
Commands (agent host, after `source …/load_morphorm_e3.sh`): `cubit -batch -nographics -nojournal -input mesh.jou`; `python3 -I work/scripts/verify_mesh.py work/mesh/mesh.exo work/mesh/mesh_verification.json`; `XMLGenerator input_deck.i` (in `work/run/`); `python3 -I work/scripts/verify_generated_config.py work/run work/run/generated_config_verification.json`; `sbatch jobs/morphorm_run.sbatch`; `squeue`/`sacct` monitoring; `python3 -I work/scripts/verify_run_outputs.py work/run work/run/run_output_verification.json`; `hash_outputs.sh`. Staging and record-keeping commands used the control helpers (`record_search.sh`, `globus_stage_file.sh`, `verify_collection.sh`, `record_node_placement.sh`) with the pinned Globus CLI.

Slurm job (the only submission; `jobs/job_ids.txt`, `jobs/submissions.tsv`):
| Job ID | Script | Submitted (UTC) | Start–End (UTC) | State | Exit | Node | Elapsed | MaxRSS |
|---|---|---|---|---|---|---|---|---|
| 16174185 | `jobs/morphorm_run.sbatch` (copy `outputs/job_script.sbatch`) | 2026-10-10T07:18:50Z | 07:18:51Z – 07:35:51Z | COMPLETED | 0:0 | notch274 | 00:17:00 | 1,389,864 KB |

Resources exactly as frozen: account hochhalter-np, partition hochhalter-np, 1 node, 1 task, 8 CPUs per task, 32G, 02:00:00, no GPU. The script sources the approved interface, prints `module list` (in `outputs/run_logs/slurm-16174185.out`), hashes the inputs, runs `bash mpirun.source` in `work/run/` (Morphorm 07:19:01Z–07:35:51Z, exit 0). The scheduler placed the job on notch274, the same physical node that hosts the agent allocation (16173746); the optimization ran inside its own allocation 16174185, not inside the agent-host allocation. `sacct` record: `jobs/sacct_16174185.txt`.

## 8. Completed stages and iteration counts
- Mesh generation and verification: complete (PASS).
- Deck translation and generated-configuration verification: complete (PASS, 55 checks) before submission.
- Optimization: complete. Optimizer diagnostics (`outputs/morphorm_oc_optimizer_diagnostics.txt`) list iterations 0–50 (51 rows, 51 function evaluations); last row: iteration 50, F(X) 1.044701e+05, Norm(F') 7.033815e+03, H1(X) −1.63e−13, abs(dX) 1.143e−01, abs(dF) 6.61e+01. Stopping message: "Optimization stopping due to exceeding maximum number of iterations." The iteration cap of 50 was reached; no early convergence stop.
- Outputs verified (`outputs/run_logs/run_output_verification.json`, PASS 11/11): `engine_output.exo` has 51 time steps with nodal fields `control` and `topology` on 15,925 nodes / 13,824 elements; `analyze_id_2_output_scenario_id_1/iteration50.exo` (deliverable `outputs/final_analyze_output.exo`) holds nodal `Topology`, `displacement X/Y/Z` and element `My Objective` (final Topology min 1.01e−08, max 0.939, mean 0.157); `opt_criteria_history.csv` holds 51 objective values. Performer logs show no errors; the engine "Terminate stage requested" message is the normal shutdown.

## 9. Key output files and SHA-256 (full list in `outputs/SHA256SUMS.txt`, 30 files)
| File | SHA-256 |
|---|---|
| `outputs/mesh.jou` | 35a9949042d7a3cae8352c7be4bddb6f6dd31b622e22cdb2cfc16dd065c4c213 |
| `outputs/mesh.exo` | 33a069f6d4cf5ad4f7da464b18c51b1bfe09e1debf72ea181f3a75e948fe2c4a |
| `outputs/mesh_verification.json` | ba6c7632956d8b322964647cb464878d3c875756ba7edf49ea7ce62e4c0d5899 |
| `outputs/input_deck.i` | 68d05787b8d4c66a1ddc52581c2bfeceb2d699e1dd45e590401155c7a1b9fbf4 |
| `outputs/job_script.sbatch` | 20a5afb0cefbabe7c2b01e4d0ee2157517c32f25d9e669b11db011d811021c3a |
| `outputs/generated_config/interface.xml` | 2f545669f80885d182291e9aad47d74baf8403082364f79f67542f653a616885 |
| `outputs/generated_config/analyze_helmholtz_input_deck.xml` | e0b190ab3e8c71334d7b7ec5f0567dbcdae40f7a371b943a553d6eb54fae5436 |
| `outputs/generated_config/analyze_2_input_deck.xml` | 9bc13ac9c61c0d8b3c7c73b5c0bce38e31c7d35b53e45483c2fd5238bea222e8 |
| `outputs/generated_config/mpirun.source` | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| `outputs/morphorm_oc_optimizer_diagnostics.txt` | 5bf3294ab40a1a55925134eb0ef493c7cb725e0964ae54cb3ce1ee62ae18e4f4 |
| `outputs/engine_output.exo` | 9b053a7c2d14ab5200f97efc1b927f3c6a5c787e754ddbd16e6212a1a988f7c9 |
| `outputs/final_analyze_output.exo` | 7b9510366799145234e5d149e7916485b20f3ed58138e1f7d6d62f12afb7ceb7 |
| `outputs/run_logs/slurm-16174185.out` | 35026206e6c4253c9bf31f3ba7d87a86f80d0b6972b0f7f049f726af78e67d1f |
| `outputs/run_logs/morphorm_run.log` | 24f51bf3b88158d9283abd03eca2f99f5418a3726091ea5e77b1dfc81695f555 |

## 10. Failures, retries, cancelled jobs, unresolved issues, deviations
- No failed or cancelled Slurm jobs; one submission, completed.
- Translation retry (no job involved): the first XMLGenerator translation did not carry the filter symmetry plane into the generated Helmholtz configuration (section 6 note). The deck was corrected and retranslated before any submission; the first attempt is preserved under `work/xmlgen_tests/`. Record-keeping note: the control-snapshot checksum check reports `.gitignore` as missing because that file is not part of the snapshot; all present files verified (`provenance/control_and_source_versions.txt`).
- The output-verification script was corrected once (field-name matching, criteria CSV layout) and re-run; the run itself was not changed.
- Deviations from the specification: none. All locked values were realized and verified in the generated configuration; the run reached the 50-iteration cap uninterrupted. Observation only: Slurm placed job 16174185 on the same physical node as the agent-host allocation; it ran in its own allocation with the frozen resources (section 7).

## 11. Final artifact paths
- `outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`
- `outputs/input_deck.i`, `outputs/job_script.sbatch`, `outputs/generated_config/` (8 XMLGenerator files + `xmlgenerator.log` + `generated_config_verification.json`)
- `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`
- `outputs/run_logs/` (Slurm stdout/stderr, `morphorm_run.log`, performer logs `engine_1_0.log`, `analyze_2_1.log`, `analyze_helmholtz_2.log`, `opt_criteria_history.csv`, `iteration50_criteria_history.csv`, `run_output_verification.json`, `cubit_run.log`, `sacct_16174185.txt`)
- `outputs/SHA256SUMS.txt`
- `jobs/job_ids.txt`, `jobs/morphorm_run.sbatch`, `jobs/sacct_16174185.txt`, `jobs/submissions.tsv`; scheduler logs also in `logs/slurm-16174185.out|err`
- `provenance/sources_searched.tsv`, `provenance/artifact_selections.md`, `provenance/node_local_placement.txt`, `provenance/control_and_source_versions.txt`
- `staging-manifest/staged_files.tsv`, `staging-manifest/globus_transfers.tsv`, `staging-manifest/returned_files.tsv`
- `work/run_summary.md` (this file); working copies in `work/mesh/`, `work/run/` (accepted run directory, left intact), `work/scripts/`, `work/xmlgen_tests/`, `work/manual_text/`
