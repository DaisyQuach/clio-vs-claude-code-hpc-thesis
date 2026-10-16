# Run summary — E3-SPC-v1 Symmetry-Plane Cantilever (trial E3-clio-trial_03)

## 1. Identification
- Trial identifier (`$E3_TRIAL_ID`): `E3-clio-trial_03`
- Node-local staging directory (`$E3_STAGING_DIR`): `/scratch/local/u1282901/16246881/e3/clio/E3-clio-trial_03` (host notch204, agent-host Slurm job 16246881; free space at creation 1,888,935,660 KiB of 1,902,232,068 KiB, see `provenance/node_local_placement.txt`)
- Control commit: `62954055b4e848f2155258c5b8c628eab97c8586` (snapshot `agent-inputs/control/`, `sha256sum -c catalog/checksums.sha256` all OK)
- Assigned task: construct and run the Symmetry-Plane Cantilever minimum-compliance topology optimization exactly as locked in `task/frozen_task_specification.md` (E3-SPC-v1): half-domain 2 x 1 x 0.5 HEX8 mesh, Helmholtz filter with the cut plane as filter symmetry plane, OC, exactly 50 iterations, approved Morphorm runtime via Slurm with the frozen resources.
- Trial root: `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_03`

## 2. Discovery
Collections searched (all from `catalog/permitted_storage_catalog.yaml`; detail in `provenance/sources_searched.tsv`, 17 records):
- `e3-control`: snapshot read with `cat`/`find` (task, deliverables, catalog, 5 artifact cards, protocol, helpers).
- `e3-private-source` (Globus collection 6dcea62e-130d-47a9-8b77-80fba6f58693): `globus ls -r --long` of `/`, `/manuals/`, `/documentation/`, `/documentation/curated_permitted_materials/`, `/target_materials/`, `/target_materials/symmetry_plane_cantilever/`. Found: two manuals, software contract, compute contract, version provenance, target specification + figure, empty `permitted_starting_materials/`.
- `e3-chpc-candidate-archive` (read-only POSIX): `verify_collection.sh` + `find`; packages `example_01/`, `example_07/`, `example_13/`, `example_16_restart/` (README, problem_card, provenance, selected_source_materials) examined in place.
- No other location was listed, opened or read. The host path of the private source was never read directly; only Globus was used.

Collection verification (`provenance/control_and_source_versions.txt`): private-source `MANIFEST.sha256` SHA-256 `d856bed27efea0561e35e01ce9e3202bf121c14e3d313b3ec34a4dafa9a8cc53` = catalog value, every staged file matched its entry; candidate-archive `MANIFEST.sha256` SHA-256 `3c89c503d0888be096a9b1740b44d7b9f3de309d5701fdcaef7c40627ba57dac` = catalog value, 25/25 listed files OK, `verify_collection.sh` reports FAIL only because the manifest lists `./.gitignore`, which is absent from the collection (no content mismatch).

## 3. Artifact selection (detail: `provenance/artifact_selections.md`)
- USED: frozen specification, software contract, compute contract, User Manual (keyword reference), private-source `problem_specification.md` (byte-identical to the control copy, checked with `diff`).
- ADAPTED: `example_07` deck and journal as structural templates (full-domain Helmholtz cantilever). Every value was replaced by the locked E3-SPC-v1 value; added half width, `ss_sym` sideset, sideset `dispz` BC, explicit SIMP material interpolation, `symmetry_plane_location_names`.
- NOT USED: `example_16_restart` (restart workflow, not applicable), `example_13` (2-D), `example_01` (kernel filter, fixed block, tractions). Theory Manual and the target figure were staged but not needed.

## 4. Staging (detail: `staging-manifest/`)
- 14 files staged, 4218087 bytes total: 12 from `e3-private-source` by `globus_stage_file.sh` (Globus transfers into `staging-inbox/`, manifest-checked, then `cp -p` into `$E3_STAGING_DIR`; transfer records in `staging-manifest/globus_transfers.tsv`), 2 from `e3-chpc-candidate-archive` by `stage_file.sh`. Source and copy SHA-256 match for every file (`staging-manifest/staged_files.tsv`).
- Returned files: none. No staged file was byte-copied into the trial workspace; `staging-manifest/returned_files.tsv` contains only the header. The manuals were converted to text with `pdftotext -layout` into `work/manual_text/` (derived text, not a copy), and the example_07 files were read from staging while writing new files under `work/`.

## 5. Mesh
- Generated on the agent host (permitted by `compute_resources.md`) with the approved Cubit: `cubit -batch -nographics -nojournal -input mesh.jou` in `work/mesh/` (2026-10-13T17:26:46Z, exit 0). Journal: `outputs/mesh.jou`; mesh: `outputs/mesh.exo` (byte-identical to `work/run2/mesh.exo` used by the run, `cmp` OK).
- Verification (`exo_summary.py --expect …`, 2026-10-13T17:27:10Z, record `outputs/mesh_verification.json`, `expect_ok: true`): 13,824 HEX8 elements, 15,925 nodes, dim 3, bbox [0,0,0]–[2.0,1.0,0.5], one block `block_1` with all 13,824 elements, nodeset `ns_fix` 325 nodes, nodeset `ns_load` 13 nodes, sideset `ss_sym` 1,152 faces. All equal to §3 of the specification.

## 6. Input deck and generated configuration
- Accepted deck: `outputs/input_deck.i` (= `work/run2/input_deck.i`). Generated with `XMLGenerator input_deck.i` in `work/run2/` (2026-10-13T17:28:42Z, exit 0); files in `outputs/generated_config/` (`interface.xml`, `analyze_2_input_deck.xml`, `analyze_2_operations.xml`, `analyze_helmholtz_input_deck.xml`, `analyze_helmholtz_operations.xml`, `engine_input_deck.xml`, `engine_operations.xml`, `mpirun.source`). Verification record: `outputs/run_logs/generated_config_verification.tsv` (`xml_params.py`).
- First translation attempt (`work/run/`, filter declared as `begin filter 1 … end filter`): `analyze_helmholtz_input_deck.xml` contained Length Scale and Surface Length Scale but NOT the symmetry-plane sideset (`xml_params.py` MISSING symmetry; record `work/verify/xml_params_run1_filter_block_form.tsv`). Per the specification this would not have been applied, so the deck was re-translated with the manual's equivalent study-level keywords (User Manual Table 2.5.12). Nothing from `work/run/` was submitted.

| Locked setting | Deck | Generated configuration |
|---|---|---|
| E = 1.0, nu = 0.3 on block_1 | `material 1`, `block 1 name block_1` | `analyze_2_input_deck.xml`: Material Models/material_1 Youngs Modulus 1.0, Poissons Ratio 0.3; Spatial Model/Domains/block_1 |
| ns_fix u_x=u_y=u_z=0 | `boundary_condition 1` | `analyze_2_input_deck.xml`: Essential BCs ID 1,2,3 (Index 0,1,2, Sides ns_fix, Value 0) |
| ss_sym u_z = 0 via sideset | `boundary_condition 2` (`location_type sideset`, `dispz`, 0) | `analyze_2_input_deck.xml`: Essential BC ID 4 (Index 2, Sides ss_sym, Value 0) |
| Load -1.0 per node, y, on ns_load (13 nodes, total -13.0) | `load 1 concentrated_load … direction y value -1.0` | `analyze_2_input_deck.xml`: Concentrated Loads, Dof 1, Value -1.0, Nodes ns_load; no natural BCs |
| Weighted-sum compliance objective, weight 1, analyze service | `objective weighted_sum`, `criterion 1 mechanical_compliance` | `analyze_2_input_deck.xml` Criteria/My Objective Internal Elastic Energy; `engine_operations.xml` Aggregator Weight 1 |
| Volume <= 15 %, less_than, engine service | `constraint 1 relative_target 0.15 service_id 1` | `interface.xml` Optimizer/Constraint NormalizedTargetValue 0.15, ReferenceValueName Design Volume; `engine_operations.xml` ComputeVolume |
| Density, initial 0.15 | `discretization density`, `initial_density_value 0.15` | `engine_operations.xml` InitializeField Uniform Value 0.15 |
| SIMP single phase, exponent 3.0, minimum 1e-3; criterion `minimum_ersatz_material_value 1e-3` | `material_interpolation 1` (`type single_phase`, `model simp`, `penalty_exponent 3.0`, `minimum_value 1e-3`), criterion keyword | `analyze_2_input_deck.xml`: Residual Penalty Function SIMP Exponent 3.0 Minimum Value 1e-3, Material Interpolation Model Single-Phase; Criteria Penalty Function SIMP 3.0 / 1e-3 |
| OC, default tolerances, normalize_in_aggregator false | `optimization_algorithm oc`, `normalize_in_aggregator false` | `interface.xml` Optimizer Package OC, OC*Tolerance defaults (1e-4, 1e-8, 1e-8) |
| update_problem true, frequency 1 | `service 1 update_problem true`, `update_problem_frequency 1` | `engine_operations.xml` Update Problem UpdateProblemFrequency 1; `interface.xml` ProblemUpdateFrequency 1 |
| max_iterations 50 | `max_iterations 50` | `interface.xml` Convergence/MaxIterations 50; `engine_operations.xml` MaxIterations 50 |
| Helmholtz, radius 0.15, sticking 1.0, symmetry plane ss_sym | `filter_type helmholtz`, `filter_radius_absolute 0.15`, `boundary_sticking_penalty 1.0`, `symmetry_plane_location_names ss_sym` (study block) | `analyze_helmholtz_input_deck.xml` Parameters: Length Scale 0.043301, Surface Length Scale 1.0, Symmetry Plane Sides {ss_sym}. (0.043301 = 0.15/(2*sqrt(3)) is the translator's conversion of the radius to the PDE length scale — inference from the value; the deck radius is 0.15.) |
| Services: engine + analyze, 1 processor each, single rank | `service 1/2 number_processors 1` | `mpirun.source`: `-np 1` PlatoMain, `-np 1` analyze_MPMD (mechanical), `-np 1` analyze_MPMD (Helmholtz filter service generated by the translator) |
| Output dispx dispy dispz; engine control + topology | `output 1 data dispx dispy dispz output_data true` | `analyze_2_input_deck.xml` Output Plottable {displacement_x, displacement_y, displacement_z}; `engine_operations.xml` PlatoMainOutput topology, control |

## 7. Execution
Commands (all after `source …/automation/environment/load_morphorm_e3.sh`; modules gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8, recorded by `module list` in `outputs/run_logs/slurm-16247250.out`):
1. `cubit -batch -nographics -nojournal -input mesh.jou` (work/mesh, 17:26:46Z)
2. `python3 exo_summary.py work/mesh/mesh.exo --expect …` (17:27:10Z)
3. `XMLGenerator input_deck.i` in `work/run` (17:27:48Z, filter-block form, rejected) and in `work/run2` (17:28:42Z, accepted)
4. `python3 xml_params.py work/run2 …` (generated-configuration verification)
5. `sbatch --parsable jobs/morphorm_spc_run2.sbatch` -> job **16247250** (17:29:47Z). Script: `jobs/morphorm_spc_run2.sbatch` (= `outputs/job_script.sbatch`), frozen resources `--account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00`, no GPU; it runs `bash mpirun.source` in `work/run2`.
6. `wait_job.sh 16247250 480 …` (two bounded waits), `sacct -j 16247250 … -P` -> `jobs/sacct_16247250.txt`.

Jobs submitted (also `jobs/job_ids.txt`): 16247250 — State COMPLETED, ExitCode 0:0, Submit 2026-10-13T11:29:47 local (17:29:47Z), Start 11:33:04, End 11:42:58, Elapsed 00:09:54, node notch351, MaxRSS 1,442,016 KiB. No other job was submitted, failed or cancelled.

## 8. Completed stages and iteration count
- Single uninterrupted optimization. `morphorm_oc_optimizer_diagnostics.txt` has 51 iteration rows (Iter 0 … 50); last row `50 51 1.044701e+05 7.033815e+03 -1.628697e-13 1.142971e-01 6.611695e+01`; objective 2.654786e+06 at iteration 0 -> 1.044701e+05 at iteration 50 (`outputs/run_logs/diag_summary.json`).
- Stopping message: `****** Optimization stopping due to exceeding maximum number of iterations. ******` — the iteration cap (50) was reached, as required; no convergence stop before 50.
- `engine_output.exo`: 51 time steps, nodal fields `control`, `topology`. `final_analyze_output.exo` (= `analyze_id_2_output_scenario_id_1/iteration50.exo`, time 50): nodal `Topology`, `displacement X/Y/Z`, element `My Objective`, same mesh counts and sets (`outputs/run_logs/final_analyze_output_summary.json`).

## 9. Key output files (SHA-256 in `outputs/SHA256SUMS.txt`, 29 entries)
- `outputs/mesh.exo` e2d2bf4fc353ad2781321225ce9d1a4715b28149e4f07b647df9ddd745bacdf0
- `outputs/mesh.jou` 1d5ff1ad89f5be4fd97a4c61dea6a5fb9f531287c5895c354422b7c44a6dd3c0
- `outputs/mesh_verification.json` d37ca675238200df81f9cfb4b3243d5560df87ccaae1764061504a6c2998d619
- `outputs/input_deck.i` e5bf824a00fccf72bb4f1d4795cf800c7f195a0387e5c91347c99296856dbc97
- `outputs/job_script.sbatch` e66bcdb64e6748676ed0718fd62a20f2e43a40648803049cee50dccb7f53fe4e
- `outputs/generated_config/interface.xml` 2f545669f80885d182291e9aad47d74baf8403082364f79f67542f653a616885
- `outputs/generated_config/analyze_helmholtz_input_deck.xml` e0b190ab3e8c71334d7b7ec5f0567dbcdae40f7a371b943a553d6eb54fae5436
- `outputs/generated_config/analyze_2_input_deck.xml` 9bc13ac9c61c0d8b3c7c73b5c0bce38e31c7d35b53e45483c2fd5238bea222e8
- `outputs/morphorm_oc_optimizer_diagnostics.txt` 5bf3294ab40a1a55925134eb0ef493c7cb725e0964ae54cb3ce1ee62ae18e4f4
- `outputs/engine_output.exo` 9b053a7c2d14ab5200f97efc1b927f3c6a5c787e754ddbd16e6212a1a988f7c9
- `outputs/final_analyze_output.exo` 7b9510366799145234e5d149e7916485b20f3ed58138e1f7d6d62f12afb7ceb7
- `outputs/run_logs/` (slurm-16247250.out/.err, morphorm_run.log, engine_1_0.log, analyze_2_1.log, analyze_helmholtz_2.log, xmlgenerator_stdout.txt, cubit_stdout.txt, opt_criteria_history.csv, verification JSON/TSV): see `outputs/SHA256SUMS.txt`.

## 10. Failures, retries, cancelled jobs, deviations
- No failed or cancelled jobs; one submission.
- Translation retry: the filter-block form of the deck did not propagate `symmetry_plane_location_names` to the generated Helmholtz configuration (work/run, never executed). The study-level keyword form (work/run2) propagated all three Helmholtz settings and was the accepted run. Both deck versions and both translator outputs are kept under `work/`.
- `verify_collection.sh` reported FAIL for the candidate archive solely because its manifest lists an absent `./.gitignore`; all 25 present files verified.
- `penalty_exponent 3.0` was written explicitly in the deck; the specification calls it the runtime default and the generated value is 3.0 either way.
- The `ss_sym` Dirichlet condition is declared with `location_type sideset` as the specification requires; the User Manual §3.3 states that essential BCs are applied to nodesets. XMLGenerator accepted the deck and generated `Sides ss_sym` for the condition, and the analyze service ran to completion, so the locked form was realized; it is recorded here as a documentation/specification tension, not a deviation.
- Unresolved issues: none. Deviations from E3-SPC-v1: none.

## 11. Final artifact paths (relative to the trial root)
`outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`, `outputs/input_deck.i`, `outputs/job_script.sbatch`, `outputs/generated_config/` (8 files), `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`, `outputs/run_logs/` (12 files), `outputs/SHA256SUMS.txt`, `jobs/job_ids.txt`, `jobs/morphorm_spc_run2.sbatch`, `jobs/sacct_16247250.txt`, `jobs/submissions.log`, `logs/slurm-16247250.out`, `logs/slurm-16247250.err`, `work/run_summary.md`, `work/notes.log`, `provenance/sources_searched.tsv`, `provenance/artifact_selections.md`, `provenance/node_local_placement.txt`, `provenance/control_and_source_versions.txt`, `staging-manifest/staged_files.tsv`, `staging-manifest/globus_transfers.tsv`, `staging-manifest/returned_files.tsv`. Working copies: `work/mesh/`, `work/run/` (rejected translation), `work/run2/` (accepted run directory), `work/verify/`, `work/manual_text/`.
