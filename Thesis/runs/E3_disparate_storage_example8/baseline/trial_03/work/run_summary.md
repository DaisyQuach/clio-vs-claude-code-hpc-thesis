# Run summary — E3-baseline-trial_03 (Symmetry-Plane Cantilever, E3-SPC-v1)

## 1. Identification
| Item | Value |
|---|---|
| Trial identifier (`$E3_TRIAL_ID`) | `E3-baseline-trial_03` |
| Staging directory (`$E3_STAGING_DIR`) | `/scratch/local/u1282901/16173745/e3/baseline/E3-baseline-trial_03` (node notch274, Slurm per-job `$TMPDIR` of agent-host job 16173745) |
| Control commit | `62954055b4e848f2155258c5b8c628eab97c8586` (snapshot `agent-inputs/control/`, catalog v5; checksums PASS) |
| Assigned task | construct and complete the Symmetry-Plane Cantilever minimum-compliance topology optimization exactly as locked in `task/frozen_task_specification.md` (E3-SPC-v1): half cantilever z ∈ [0, 0.5], HEX8 48×24×12 mesh, Helmholtz filter with the cut plane as a symmetry plane, OC, 50 iterations, Slurm job with the frozen resources; all deliverables of §8 |
| Trial root | `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_03` |

## 2. Discovery (detail: `provenance/sources_searched.tsv`, 12 records)
| Collection | Method | What was found |
|---|---|---|
| `e3-control` (`agent-inputs/control/`) | cat, `sha256sum -c catalog/checksums.sha256` | task prompt, frozen specification, deliverables, catalog, 5 artifact cards, 4 protocol files, helper scripts. Checksums PASS (the `.gitignore` entry is absent from the git-archive snapshot, as expected). |
| `e3-private-source` (Globus guest collection `6dcea62e-…`) | `globus ls -r --long` (pinned CLI), then `globus_stage_file.sh` per file | 13 files: `MANIFEST.sha256`, `MANIFEST.tsv`, `README.md`, `documentation/` (software contract, compute-resource contract, curated readme, manifest readme, version provenance), `manuals/` (User and Theory Manual PDFs), `target_materials/symmetry_plane_cantilever/` (specification, figure, README, empty `permitted_starting_materials/`). The host path was never read directly. |
| `e3-chpc-candidate-archive` (read-only POSIX) | `verify_collection.sh` (MANIFEST PASS, 25 files), `find`, cat of every README, problem card, provenance file, deck and journal | packages `example_01/`, `example_07/`, `example_13/`, `example_16_restart/` |
| `e3-trial-inbox-destination` | Globus destination only (`staging-inbox/`) | 15 transfers recorded in `staging-manifest/globus_transfers.tsv`; never listed as a source |
No other location was listed, searched or opened.

## 3. Artifact selection (detail: `provenance/artifact_selections.md`)
| Candidate | Decision |
|---|---|
| `example_07` full Helmholtz cantilever (deck + journal) | **adapted**: identical cross-section, support, load, material, SIMP, objective, constraint, filter radius/penalty, OC, 50 iterations; width halved, `ss_sym` sideset added, sideset symmetry BC added, `symmetry_plane_location_names ss_sym` added, explicit SIMP block (exponent 3.0, min 1e-3) |
| `example_16_restart` | not used (two-stage restart workflow; the specification requires one uninterrupted run) |
| `example_13` (2-D L-bracket) | not used (2-D, traction load, different constraint/iterations) |
| `example_01` (bolted bracket) | not used (tet mesh, non-design block, tractions, kernel filter) |
| private-source documentation | software contract and compute contract used verbatim; User Manual used for the boundary_condition, filter (study-level keywords), material_interpolation, output and diagnostics syntax; specification and figure used as the authoritative definition |

## 4. Staging (detail: `staging-manifest/staged_files.tsv`, `globus_transfers.tsv`, `returned_files.tsv`)
| Item | Value |
|---|---|
| Staged files | 19 files, 4,923,535 bytes: 13 from `e3-private-source` (4,216,923 bytes, Globus → `staging-inbox/` → `$E3_STAGING_DIR`, each verified against `MANIFEST.sha256`), 6 from `e3-chpc-candidate-archive/example_07/` (706,612 bytes, `stage_file.sh`) |
| Source/copy SHA-256 | matched for every file (recorded per line) |
| Returned files | 2 files, 2,779 bytes: `example_07` deck and journal (the adapted originals) → `work/candidates/example_07/` via `return_file.sh` |
| Node-local placement | `provenance/node_local_placement.txt` (notch274, `/scratch/local`, 1.80 TB free at creation) |
| Derived (not copies) | `work/manual_text/*.txt` = `pdftotext` extraction of the staged manuals, used for keyword search |

## 5. Mesh
- Journal `work/mesh/mesh.jou` → `outputs/mesh.jou` (adapted from `example_07` journal: `wd = 0.5`, added `sideset 1 add surface with z_coord > wd − h/2`, name `ss_sym`).
- Generated 2026-10-10T06:42:39Z–06:42:41Z on the agent host (permitted for meshing) with `cubit -batch -nographics -nojournal -input mesh.jou` (cubit-edu/2026.8 via the approved loader; exit 0; log `outputs/run_logs/cubit_run.log`). Export: Exodus II, dimension 3 → `work/mesh/mesh.exo` = `work/run/mesh.exo` = `outputs/mesh.exo` (SHA-256 `eafdf7d1…e590`).
- Verification `work/scripts/verify_mesh.py` (runtime python3 + netCDF4), record `outputs/mesh_verification.txt`, 26/26 checks PASS at 2026-10-10T06:43:24Z: 13,824 HEX8 elements, 15,925 nodes, one block `block_1` with all elements, bounding box [0,2]×[0,1]×[0,0.5], 49×25×13 node planes, uniform h = 0.041667, `ns_fix` 325 nodes (all nodes with x = 0), `ns_load` 13 nodes (all nodes on x = 2, y = 0, z ∈ [0,0.5]), `ss_sym` 1,152 faces, all on z = 0.5, on 1,152 distinct elements, 1,225 nodes.

## 6. Input deck and generated configuration
Deck: `work/run/input_deck.i` → `outputs/input_deck.i`; translated with `XMLGenerator input_deck.i` at 2026-10-10T06:45:21Z (exit 0) into `outputs/generated_config/` (interface.xml, engine_input_deck.xml, engine_operations.xml, analyze_2_input_deck.xml, analyze_2_operations.xml, analyze_helmholtz_input_deck.xml, analyze_helmholtz_operations.xml, mpirun.source). Verification `work/scripts/verify_generated_config.py`, record `outputs/generated_config_verification.txt`, 63/63 PASS before submission.

| Locked setting | Deck | Generated configuration |
|---|---|---|
| E = 1.0, ν = 0.3 on `block_1` | `material 1`, `block 1 … material_id 1` | `analyze_2_input_deck.xml` Material Models/material_1/Isotropic Linear Elastic: Youngs Modulus 1.0, Poissons Ratio 0.3; Domains/block_1 → material_1 (only domain) |
| `ns_fix` u_x=u_y=u_z=0 (nodeset) | `boundary_condition 1` | Essential Boundary Conditions IDs 1–3: Fixed Value, Index 0/1/2, Sides `ns_fix`, Value 0 |
| `ss_sym` u_z=0 through the sideset | `boundary_condition 2` (`location_type sideset`, `ss_sym`, `dispz`, 0) | Essential Boundary Conditions ID 4: Fixed Value, Index 2, Sides `ss_sym`, Value 0 (realized: u_z = 0 exactly on all 1,225 cut-plane nodes in `final_analyze_output.exo`) |
| Load −1.0 per node, direction y, on `ns_load`; no tractions/body forces | `load 1 concentrated_load … direction y value -1.0` | Concentrated Loads: Dof 1, Value −1.0, Nodes `ns_load`; Natural Boundary Conditions list empty |
| Objective: weighted-sum compliance, weight 1, analyze service; `minimum_ersatz_material_value 1e-3` | `criterion 1`, `objective weighted_sum … service_ids 2 … weights 1` | Criteria/My Objective: Internal Elastic Energy, SIMP exponent 3.0, Minimum Value 1e-3; interface stage "Compute Objective Value" performer `analyze_2`; engine Aggregator weight 1 |
| Constraint volume ≤ 0.15, less_than, engine service | `constraint 1 … relative_target 0.15 … service_id 1` | interface Optimizer/Constraint NormalizedTargetValue 0.15, reference Design Volume; stage "Compute Constraint Value 1" performer `engine_1` (ComputeVolume) |
| Density discretization, initial 0.15 | `discretization density`, `initial_density_value 0.15` | engine_operations: InitializeField Uniform 0.15; bounds Discretization density |
| SIMP single phase, exponent 3.0, min 1e-3 | `material_interpolation 1` | Mechanical Residual: Material Interpolation Model Single-Phase, SIMP Exponent 3.0, Minimum Value 1e-3 |
| OC, default tolerances, `normalize_in_aggregator false`, `update_problem true`, frequency 1 | `optimization_algorithm oc`, `normalize_in_aggregator false`, service 1 `update_problem true`, `update_problem_frequency 1` | Optimizer Package OC, OC tolerances 1e-4/1e-8/1e-8 (defaults), ProblemUpdateFrequency 1, UpdateProblemStage; no normalization element in the Aggregator |
| `max_iterations 50` | `max_iterations 50` | Convergence/MaxIterations 50; PlatoMainOutput MaxIterations 50 |
| Helmholtz filter, radius 0.15, sticking penalty 1.0, symmetry plane `ss_sym` | study-level `filter_type helmholtz`, `filter_radius_absolute 0.15`, `boundary_sticking_penalty 1.0`, `symmetry_plane_location_names ss_sym` | `analyze_helmholtz_input_deck.xml` Parameters: Length Scale 0.043301 (= 0.15/(2√3)), Surface Length Scale 1.0, Symmetry Plane Sides {ss_sym} |
| Services engine + analyze, one processor each, no decomposition | `service 1 engine number_processors 1`, `service 2 analyze number_processors 1` | `mpirun.source`: `-np 1` for PlatoMain, analyze_MPMD (analyze_2) and analyze_MPMD (analyze_helmholtz); no decomposition step |
| Output dispx, dispy, dispz; engine control + topology | `output 1 … data dispx dispy dispz`, `output_data true` | analyze Output Plottable {displacement_x, displacement_y, displacement_z}; PlatoMainOutput inputs `topology`, `control` |

Keyword placement note: with the filter-block form (`begin filter 1 … symmetry_plane_location_names ss_sym … end filter`, as in `example_07`), XMLGenerator emitted the Helmholtz configuration **without** `Symmetry Plane Sides` and logged `filter_radius_absolute`/`boundary_sticking_penalty` as "not set" (scratch translation `work/xmlgen_tests/A_filterblock/`, verification 61/63 with the two symmetry-plane checks FAILED). Per the User Manual (Study › Filters, legacy study-level keywords; forms must not be mixed) the accepted deck declares the Helmholtz filter at study level; all other generated files are byte-identical between the two forms. Other scratch translations: `work/xmlgen_tests/{B_legacy_study,C_mixed,D_filterblock_symm_in_study_only}` (all produced the symmetry sideset; B is the accepted form).

## 7. Execution
Commands (agent host unless noted; approved loader sourced first in every shell and in the job):
```
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh
sha256sum -c catalog/checksums.sha256                    # control snapshot (in agent-inputs/control)
verify_collection.sh <candidate archive root>            # PASS
globus ls -r --long 6dcea62e-130d-47a9-8b77-80fba6f58693:/
globus_stage_file.sh <13 private-source paths>           # Globus → staging-inbox/ → $E3_STAGING_DIR
stage_file.sh <6 example_07 files>                       # candidate archive → $E3_STAGING_DIR
pdftotext -layout <staged manuals> work/manual_text/
cubit -batch -nographics -nojournal -input mesh.jou      # in work/mesh
python3 -I work/scripts/verify_mesh.py work/mesh/mesh.exo work/mesh/mesh_verification.txt
XMLGenerator input_deck.i                                # in work/run (and in work/xmlgen_tests/* scratch)
python3 -I work/scripts/verify_generated_config.py work/run work/run/generated_config_verification.txt
sbatch --parsable jobs/job_morphorm_spc_v1.sbatch        # 2026-10-10T06:46:35Z → job 16174062
sacct -j 16174062 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P > jobs/sacct_16174062.txt
python3 -I work/scripts/verify_outputs.py work/run work/run/output_verification.txt
return_file.sh <example_07 deck, journal> work/candidates/example_07/
hash_outputs.sh
```
Job script: `jobs/job_morphorm_spc_v1.sbatch` (= `outputs/job_script.sbatch`), resources exactly as `compute_resources.md` (account/partition hochhalter-np, 1 node, 1 task, 8 CPUs, 32G, 02:00:00), runs `bash mpirun.source` in `work/run` (trial workspace, visible to the job); `module list` recorded in its stdout.

| Job ID | Script | State | ExitCode | Submit (UTC) | Start (UTC) | End (UTC) | Elapsed | Node |
|---|---|---|---|---|---|---|---|---|
| 16174062 | `jobs/job_morphorm_spc_v1.sbatch` | COMPLETED | 0:0 | 2026-10-10T06:46:35Z | 06:46:44Z | 07:03:44Z | 00:17:00 | notch274 |
Only one job was submitted (`jobs/job_ids.txt`); no job failed or was cancelled. The Morphorm run itself started 06:46:54Z and ended 07:03:44Z with exit 0; MaxRSS 1.39 GB.

## 8. Completed stages and iteration counts
- Discovery and staging: complete. Mesh generation + verification: complete (26/26). Deck translation + generated-configuration verification: complete (63/63). Optimization: complete.
- Optimizer diagnostics (`outputs/morphorm_oc_optimizer_diagnostics.txt`): iterations 0–50 (51 rows), i.e. the iteration cap of 50 was reached; no convergence stop occurred. Stopping message: `****** Optimization stopping due to exceeding maximum number of iterations. ******`
- Objective F(X): 2.654786e+06 (iter 0) → 1.044701e+05 (iter 50); constraint H1(X) at iter 50 = −1.63e−13 (volume constraint active/satisfied); `opt_criteria_history.csv` holds 51 objective values.
- `engine_output.exo`: 51 time steps, nodal fields `control` and `topology` (final topology range 1.0e−8 … 0.939, mean 0.157). `final_analyze_output.exo` (= `analyze_id_2_output_scenario_id_1/iteration50.exo`, time value 50): nodal `Topology`, `displacement X/Y/Z`, element `My Objective`. Output verification `outputs/output_verification.txt`: ALL PASS (u = 0 on `ns_fix`, u_z = 0 on all 1,225 cut-plane nodes, loaded edge displaced in −y).

## 9. Key output files (full list with SHA-256: `outputs/SHA256SUMS.txt`, 30 entries)
| File | SHA-256 |
|---|---|
| `outputs/mesh.jou` | 99f05f124c4d5dc7c32b15a0971a5a2da118f7c1fb1b0af8d6a05e3e87b59722 |
| `outputs/mesh.exo` | eafdf7d1991b2707f83048f55f0f5a7d9bdf374765c267040cf13d342e72e590 |
| `outputs/mesh_verification.txt` | eb48e4770682e14b5976e26c397f9cba6c77b2c7f9e44b3d7c5d0c304633254e |
| `outputs/input_deck.i` | c8d492378a6a2c8595175e408c9218e12177bfd79e4896ccdf04380074362ee5 |
| `outputs/job_script.sbatch` | 586b5456d2c18df2620ee78ed4e7725fb67142ce810755fdd1d874e6a6648e35 |
| `outputs/generated_config/interface.xml` | 2f545669f80885d182291e9aad47d74baf8403082364f79f67542f653a616885 |
| `outputs/generated_config/analyze_helmholtz_input_deck.xml` | e0b190ab3e8c71334d7b7ec5f0567dbcdae40f7a371b943a553d6eb54fae5436 |
| `outputs/generated_config/analyze_2_input_deck.xml` | 9bc13ac9c61c0d8b3c7c73b5c0bce38e31c7d35b53e45483c2fd5238bea222e8 |
| `outputs/generated_config/mpirun.source` | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| `outputs/morphorm_oc_optimizer_diagnostics.txt` | 5bf3294ab40a1a55925134eb0ef493c7cb725e0964ae54cb3ce1ee62ae18e4f4 |
| `outputs/engine_output.exo` | 9b053a7c2d14ab5200f97efc1b927f3c6a5c787e754ddbd16e6212a1a988f7c9 |
| `outputs/final_analyze_output.exo` | 7b9510366799145234e5d149e7916485b20f3ed58138e1f7d6d62f12afb7ceb7 |
| `outputs/run_logs/slurm-16174062.out` | 4f609dde081bf3b70c6c02408285ba97cc80c168757eae9c0bf00007933b26e7 |
The sha256 values of the inputs printed inside the job's stdout (deck, mesh, generated XML) equal those of the deliverables, so the delivered files are the ones the accepted run used.

## 10. Failures, retries, cancelled jobs, unresolved issues, deviations
- No failed, retried or cancelled Slurm jobs. No deviation from any locked value in §1–§7 of E3-SPC-v1.
- Attempt-level issue (resolved before submission, no job involved): the first deck translation (filter-block form) did not carry `symmetry_plane_location_names` into the generated Helmholtz configuration; the deck was changed to the manual's study-level Helmholtz keywords and re-translated (see §6). Both translations are kept (`work/xmlgen_tests/`).
- Observation (not a deviation): the User Manual §3.3 states that essential boundary conditions are applied to nodesets, but the locked specification requires the symmetry condition through the sideset `ss_sym`; the deck follows the specification, XMLGenerator emitted the condition with `Sides ss_sym`, the runtime accepted it, and the final displacement field has u_z = 0 on every cut-plane node.
- Engine output frequency: `engine_output.exo` was written every iteration (51 steps) although the generated PlatoMainOutput lists `OutputFrequency 5` (XMLGenerator default `isosurface_output_frequency`); no output frequency is locked by the specification, none was set in the deck.
- The agent-host allocation and the optimization job both ran on notch274 (single node of the partition); the optimization was executed only inside Slurm job 16174062, never in the agent session.
- Record-keeping note: the three `sources_searched.tsv` lines for reading the staged manuals (06:43–06:45), the figure (06:44) and the staged example_07 copies were appended at 07:05 UTC, after the job; the corresponding staging lines carry the actual copy times.
- Mesh verification script needed one fix (Exodus name decoding) before its first successful run; the record is from the successful run. Output verification script likewise needed one fix (field-name normalization). Neither affected any deliverable file.

## 11. Final artifact paths (relative to the trial root)
- `outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.txt`
- `outputs/input_deck.i`, `outputs/job_script.sbatch`, `outputs/generated_config/` (8 files), `outputs/generated_config_verification.txt`
- `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`, `outputs/output_verification.txt`
- `outputs/run_logs/` (Slurm stdout/stderr, `morphorm_run.log`, three performer logs, criteria histories, `cubit_run.log`, `xmlgenerator.log`, `sacct_16174062.txt`), `outputs/SHA256SUMS.txt`
- `jobs/job_ids.txt`, `jobs/job_morphorm_spc_v1.sbatch`, `jobs/sacct_16174062.txt`, `jobs/submissions.log`; `logs/slurm-16174062.{out,err}`, `logs/staging/`
- `provenance/sources_searched.tsv`, `provenance/artifact_selections.md`, `provenance/node_local_placement.txt`, `provenance/control_and_source_versions.txt`
- `staging-manifest/staged_files.tsv`, `staging-manifest/globus_transfers.tsv`, `staging-manifest/returned_files.tsv`
- `work/run_summary.md` (this file); working files under `work/mesh/`, `work/run/`, `work/scripts/`, `work/xmlgen_tests/`, `work/manual_text/`, `work/candidates/`
