# Run summary — E3-baseline-trial_05 (E3-SPC-v1 Symmetry-Plane Cantilever)

## 1. Identification
- Trial identifier ($E3_TRIAL_ID): `E3-baseline-trial_05`
- Node-local staging directory ($E3_STAGING_DIR): `/scratch/local/u1282901/16173748/e3/baseline/E3-baseline-trial_05` (host notch274, agent-host Slurm job 16173748; placement record `provenance/node_local_placement.txt`)
- Control-repository commit: `62954055b4e848f2155258c5b8c628eab97c8586` (snapshot `agent-inputs/control/`; checksum file verified, see `provenance/control_and_source_versions.txt`)
- Assigned task: construct and complete the Symmetry-Plane Cantilever minimum-compliance topology optimization exactly as locked in `task/frozen_task_specification.md` (E3-SPC-v1): half domain 2 × 1 × 0.5, 48 × 24 × 12 HEX8, Helmholtz filter with symmetry plane, OC, 50 iterations, Slurm execution with the frozen resources, all deliverables at their locked paths.

## 2. Discovery (detail: `provenance/sources_searched.tsv`)
- **e3-control**: read every file of the snapshot (README, task, catalog, 5 artifact cards, protocol, helpers); `sha256sum -c catalog/checksums.sha256` → all present files OK; the listed `.gitignore` is absent from the snapshot (pre-existing packet condition, not a scientific input).
- **e3-private-source** (Globus guest collection `6dcea62e-130d-47a9-8b77-80fba6f58693`, accessed only with the pinned Globus CLI): `globus ls --recursive` of the root listed `manuals/` (User and Theory Manual), `documentation/` (curated readme, manifest readme, version provenance, software contract, compute-resource contract) and `target_materials/symmetry_plane_cantilever/` (README, specification, figure, empty permitted_starting_materials/). The host path was never read directly.
- **e3-chpc-candidate-archive** (read-only POSIX): `verify_collection.sh` → manifest PASS (manifest SHA-256 3c89c503…, matches the catalog); `find` listed 4 packages (example_01, example_07, example_13, example_16_restart); the archive README and each package's README, problem_card.yaml and provenance.yaml were read in place.
- No other location was listed, searched or opened. Source identifiers (MORPHORM-*) were not resolved.

## 3. Artifact selection (detail: `provenance/artifact_selections.md`)
| Candidate | Decision |
|---|---|
| example_07 full Helmholtz cantilever (deck + journal) | **adapted** — template for the half-domain journal and deck (same material, load, SIMP minimum, volume fraction, filter radius/penalty, OC, 50 iterations) |
| example_16_restart | examined, not used (restart workflow; the spec requires one uninterrupted run) |
| example_01 | examined, not used (bracket, tets, kernel filter, tractions, non-design block) |
| example_13 | examined, not used (2-D) |
| private source: specification, software contract, compute resources, version provenance, User Manual | **used** |
| private source: Theory Manual | listed, not staged, not read (not needed) |
| private source: problem figure | staged with the target package, not needed for construction |

## 4. Staging (detail: `staging-manifest/`)
- Staged into `$E3_STAGING_DIR`: 13 files, 2661915 bytes total (`staging-manifest/staged_files.tsv`): 2 files from e3-chpc-candidate-archive (`stage_file.sh`, cp -p) and 11 files from e3-private-source (`globus_stage_file.sh`: Globus transfer into `staging-inbox/`, MANIFEST.sha256 check, cp -p into staging; transfer tasks in `staging-manifest/globus_transfers.tsv`). Every source/staged SHA-256 pair matches.
- Returned from staging into the workspace: none (`staging-manifest/returned_files.tsv` contains the header only). All staged material was read in staging; the adapted journal and deck were authored under `work/` and the Slurm job needed nothing from staging. Staged originals were not modified.
- Manual text extraction (`pdftotext`) was written to `work/manual_text/` inside the trial root only.

## 5. Mesh
- Generator: approved Coreform Cubit (`cubit-edu/2026.8` via the approved loader), `cubit -batch -nographics -nojournal -input mesh.jou` on the agent host, 2026-10-10T07:45:20Z–07:45:23Z, exit 0 (`outputs/run_logs/cubit_run.log`).
- Journal `work/mesh/mesh.jou` → `outputs/mesh.jou` (adapted from Example 7: width 0.5, sideset ss_sym on z = 0.5). Mesh `work/mesh/mesh.exo` (copied unchanged to `work/run/mesh.exo` for the run) → `outputs/mesh.exo`.
- Verification (`work/mesh/verify_mesh.py` with the runtime python3/netCDF4, record `outputs/mesh_verification.json`), 2026-10-10T07:46Z, **all 16 checks PASS**: num_dim 3; 13,824 HEX8 elements; 15,925 nodes; one block `block_1` containing all elements; bounding box x [0, 2], y [0, 1], z [0, 0.5]; 49 × 25 × 13 node grid, uniform spacing 0.0416667 in x, y, z; `ns_fix` 325 nodes all on x = 0; `ns_load` 13 nodes all on x = 2, y = 0 spanning z ∈ [0, 0.5]; `ss_sym` 1,152 faces all on z = 0.5; no other sets.

## 6. Input deck and generated configuration
- Deck: `work/run/input_deck.i` → `outputs/input_deck.i` (SHA-256 5edae270…). Translated with `XMLGenerator input_deck.i` on the agent host (2026-10-10T07:50Z, exit 0, `outputs/generated_config/xmlgenerator.log`). Generated files used by the run: `outputs/generated_config/{interface.xml, analyze_2_input_deck.xml, analyze_2_operations.xml, analyze_helmholtz_input_deck.xml, analyze_helmholtz_operations.xml, engine_input_deck.xml, engine_operations.xml, mpirun.source}`; scripted verification record `outputs/generated_config/generated_config_verification.txt` (29 checks, ALL PASS, with SHA-256 of each file).
- Locked settings and where each appears in the generated configuration:

| Locked setting | Deck | Generated configuration |
|---|---|---|
| Engine service, 1 processor, update_problem true, frequency 1 | service 1 | interface.xml performer engine_1, `<UpdateProblemStage>`, `<ProblemUpdateFrequency>1`; engine_operations.xml `<UpdateProblemFrequency>1`; mpirun.source `-np 1` |
| Analyze service, 1 processor | service 2 | interface.xml performer analyze_2; mpirun.source `-np 1` (Helmholtz filter also runs as a 1-rank analyze performer, as the manual states) |
| Material E = 1.0, ν = 0.3 on block_1 | material 1, block 1 | analyze_2_input_deck.xml Material Models/material_1 Isotropic Linear Elastic (Youngs Modulus 1.0, Poissons Ratio 0.3); Spatial Model/block_1 → material_1 |
| SIMP single phase, exponent 3.0, minimum 1e-3 | material_interpolation 1 | analyze_2_input_deck.xml Residual/Penalty Function SIMP Exponent 3.0 Minimum Value 1e-3, Material Interpolation Model Single-Phase |
| Compliance criterion minimum_ersatz_material_value 1e-3 | criterion 1 | analyze_2_input_deck.xml Criteria/My Objective Internal Elastic Energy, SIMP Exponent 3.0, Minimum Value 1e-3 |
| ns_fix u_x = u_y = u_z = 0 | boundary_condition 1 | analyze_2_input_deck.xml Essential BCs: Displacement X/Y/Z with ID 1–3, Sides ns_fix, Value 0 |
| ss_sym u_z = 0 through the sideset | boundary_condition 2 (location_type sideset) | analyze_2_input_deck.xml Essential BCs: Displacement Z with ID 4, Index 2, Sides ss_sym, Value 0 |
| Load: concentrated, ns_load, y, −1.0 per node; no other loads | load 1 | analyze_2_input_deck.xml Concentrated Load with ID 0: Dof 1, Value −1.0, Nodes ns_load; Natural BCs empty; no body load |
| Objective weighted sum, single compliance criterion, weight 1, analyze service | objective | interface.xml stage Compute Objective Value (analyze_2) → Aggregate Data; engine_operations.xml Aggregator Weight 1 |
| Volume ≤ 0.15, less_than, engine service | constraint 1 | interface.xml `<NormalizedTargetValue>0.15`, Compute Constraint Value 1 performed by engine_1 |
| Density discretization, initial density 0.15 | study | engine_operations.xml InitializeField Uniform 0.15, Discretization density |
| OC, default tolerances, normalize_in_aggregator false | study | interface.xml `<Package>OC`, OC tolerances 1e-4/1e-8/1e-8; engine_operations.xml Aggregator without Normalize |
| max_iterations 50 | study | interface.xml `<MaxIterations>50`; engine_operations.xml PlatoMainOutput MaxIterations 50 |
| Helmholtz filter, radius 0.15, sticking penalty 1.0, symmetry plane ss_sym | filter 1 (+ study-level `symmetry_plane_location_names ss_sym`) | analyze_helmholtz_input_deck.xml Parameters: Length Scale 0.043301 (= 0.15/(2√3), the runtime's conversion of the absolute radius), Surface Length Scale 1.0, Symmetry Plane Sides {ss_sym} |
| Output dispx dispy dispz; engine output control and topology | output 1 | analyze_2_input_deck.xml Output Plottable {displacement_x, displacement_y, displacement_z}; interface.xml Output To File → PlatoMainOutput inputs topology, control |
| Single-rank performers, no decomposition | — | mpirun.source: three performers each `-np 1` |

- Finding: with `symmetry_plane_location_names ss_sym` only inside the filter block, XMLGenerator omitted the symmetry plane from the Helmholtz configuration (first translation kept in `work/xmlgen_tests/initial_block_only/`). The documented study-level form (`work/xmlgen_tests/A_legacy`, `B_block_plus_study`) produces `Symmetry Plane Sides {ss_sym}`; the accepted deck keeps the filter block and adds the study-level keyword. No optimization was run with the incomplete configuration.

## 7. Execution
Commands used (agent host notch274 unless stated; the approved interface was sourced in every shell and in the job script):
```
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh
# discovery / records
agent-inputs/control/scripts/non_destructive_preflight_helpers/record_node_placement.sh
agent-inputs/control/scripts/non_destructive_preflight_helpers/verify_collection.sh <chpc_candidate_archive root>
agent-inputs/control/scripts/non_destructive_preflight_helpers/record_search.sh <alias> <path> <method> <purpose>   # 14 entries
globus ls --recursive 6dcea62e-130d-47a9-8b77-80fba6f58693:/
# staging
agent-inputs/control/scripts/non_destructive_preflight_helpers/stage_file.sh <archive>/example_07/selected_source_materials/topology_mech_ex7.{i,jou}
work/stage_private_source.sh   # sequential globus_stage_file.sh for 11 private-source files (log work/logs/stage_private_source.log)
pdftotext -layout $E3_STAGING_DIR/e3-private-source/manuals/Morphorm_User_Manual.pdf work/manual_text/user_manual.txt
# mesh (agent host, permitted by compute_resources.md)
cd work/mesh && cubit -batch -nographics -nojournal -input mesh.jou          # 07:45:20Z–07:45:23Z, exit 0
python3 -I verify_mesh.py mesh.exo > mesh_verification.json                 # all checks pass
# deck translation and verification (agent host; translation only, no optimization)
cd work/run && XMLGenerator input_deck.i                                     # first attempt 07:48:45Z (filter-block-only deck), accepted translation 07:50Z
python3 -I work/verify_generated_config.py work/run > work/run/generated_config_verification.txt   # 29/29 PASS, 07:50:46Z
# optimization (Slurm only)
sbatch --parsable jobs/morphorm_spc_v1.sbatch                                 # 07:50:46Z -> job 16174284
sacct -j 16174284 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P > jobs/sacct_16174284.txt
python3 -I work/verify_outputs.py work/run/analyze_id_2_output_scenario_id_1/iteration50.exo work/run/engine_output.exo
bash work/collect_deliverables.sh 16174284; agent-inputs/control/scripts/non_destructive_preflight_helpers/hash_outputs.sh
```
Slurm jobs submitted in this trial (also `jobs/job_ids.txt`): **one**.

| Job ID | Script | Resources | State | Exit code | Submit / Start / End (scheduler local time, UTC−6) | Elapsed | Node |
|---|---|---|---|---|---|---|---|
| 16174284 | `jobs/morphorm_spc_v1.sbatch` (= `outputs/job_script.sbatch`) | account hochhalter-np, partition hochhalter-np, 1 node, 1 task, 8 CPUs, 32G, 02:00:00, no GPU | COMPLETED | 0:0 (batch step 0:0; Morphorm `bash mpirun.source` rc=0) | 01:50:46 / 01:50:47 / 02:07:48 (= 07:50:46Z / 07:50:47Z / 08:07:48Z) | 00:17:01 | notch274 |

The job script sources the approved interface, prints `module list` (chpc/1.0, gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8 — see `outputs/run_logs/slurm-16174284.out`), changes to `work/run/` (trial workspace), hashes its inputs and runs `bash mpirun.source` (PlatoMain + analyze_MPMD + analyze_MPMD Helmholtz, one rank each). Morphorm ran 2026-10-10T07:50:57Z–08:07:47Z. The optimization was not run on the agent host. The job read only `work/run/` and the approved software interface. Peak memory (MaxRSS, batch step) 1,386,148 KB.

## 8. Completed stages and iteration count
- Stage 1 (discovery, staging) — complete. Stage 2 (mesh generation and verification) — complete, all checks pass. Stage 3 (deck, translation, generated-configuration verification) — complete, 29/29 checks pass. Stage 4 (Slurm optimization) — complete.
- Iterations reached: **50 of 50** (`outputs/morphorm_oc_optimizer_diagnostics.txt` lists iterations 0–50, 51 function evaluations; `outputs/engine_output.exo` holds 51 design time steps; `outputs/final_analyze_output.exo` is `iteration50.exo`, time value 50).
- Optimizer stopping message (verbatim): `****** Optimization stopping due to exceeding maximum number of iterations. ******` — i.e. the run reached the iteration cap, as required; no convergence stop occurred.
- Final diagnostics line: `50  51  1.044701e+05  7.033815e+03  -1.628697e-13  1.142971e-01  6.611695e+01` (Iter, F-count, F(X), Norm(F'), H1(X), abs(dX), abs(dF)). The volume constraint is active (H1 ≈ 0; mean filtered density 0.157 over the nodes, matching the 15 % target to within the nodal-average approximation). Final analyze output fields: Topology, displacement X/Y/Z (nodal), My Objective (element).

## 9. Key output files (SHA-256 in `outputs/SHA256SUMS.txt`, 26 files)
| Deliverable | SHA-256 |
|---|---|
| `outputs/mesh.jou` | 4db39589bdf5dd781f5bec65a5320d6696243f71350b2cd5c3f6f2efdf1122d1 |
| `outputs/mesh.exo` | 243b45446f2ff64c48dcafc7dd64de96151d39c3e5bc413470aac964769923fb |
| `outputs/mesh_verification.json` | b5ceb0bd4077a95e790ee2f8f4fa06b40f13eb541dc3f2499bfc6730a08ccffc |
| `outputs/input_deck.i` | 5edae27083a20d17fe853d1499da94d570c4336bcd42339c11e0bf6ad008ce68 |
| `outputs/job_script.sbatch` | 592702429a9d23ba9b6ca4d98e3731c63cdf7a40c8de8c8c42f2f55acafeae7e |
| `outputs/generated_config/interface.xml` | 2f545669f80885d182291e9aad47d74baf8403082364f79f67542f653a616885 |
| `outputs/generated_config/analyze_2_input_deck.xml` | 9bc13ac9c61c0d8b3c7c73b5c0bce38e31c7d35b53e45483c2fd5238bea222e8 |
| `outputs/generated_config/analyze_2_operations.xml` | fbabf1a1c037533ce5dc1b1ba6a97ce9d70a795c1128735196a3e624aa73efa0 |
| `outputs/generated_config/analyze_helmholtz_input_deck.xml` | e0b190ab3e8c71334d7b7ec5f0567dbcdae40f7a371b943a553d6eb54fae5436 |
| `outputs/generated_config/analyze_helmholtz_operations.xml` | 402ffc30789914bd0c1c7bf429aa2f08ea22b0040960d015b9c71fd716404854 |
| `outputs/generated_config/engine_input_deck.xml` | 7f3edc06119d4155981b3861c2c2263f268e6a3f56f7577cc0aa202f3b35169a |
| `outputs/generated_config/engine_operations.xml` | c5b07640e3f1427a5f763631a2f7f9c3ec1ea54e97160106efe598afc0c67c1b |
| `outputs/generated_config/mpirun.source` | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| `outputs/generated_config/generated_config_verification.txt` | fc12848d3ae5671413c2d0b9ff08c064cb1d0e94b21a3c43c58a05b083de4346 |
| `outputs/generated_config/xmlgenerator.log` | 7193ee5e7a3bb2fc3ff0d03cc7b3a47a74bd4282c563f5cdeb040d37dbf479ea |
| `outputs/morphorm_oc_optimizer_diagnostics.txt` | 5bf3294ab40a1a55925134eb0ef493c7cb725e0964ae54cb3ce1ee62ae18e4f4 |
| `outputs/engine_output.exo` | 9b053a7c2d14ab5200f97efc1b927f3c6a5c787e754ddbd16e6212a1a988f7c9 |
| `outputs/final_analyze_output.exo` (= `work/run/analyze_id_2_output_scenario_id_1/iteration50.exo`) | 7b9510366799145234e5d149e7916485b20f3ed58138e1f7d6d62f12afb7ceb7 |
| `outputs/opt_criteria_history.csv`, `outputs/iteration50_criteria_history.csv` (supplementary) | fc58edec337c12168c1d4a61bd25900d1cc46c334323e0e1432061d82c9c24d0 (identical content) |
| `outputs/run_logs/slurm-16174284.out` | 9ffc7af463435d6407f04696a515733ea82a31daadf5a7eb5d154be8dd917dd1 |
| `outputs/run_logs/slurm-16174284.err` (empty) | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| `outputs/run_logs/morphorm_run.log` | 24f51bf3b88158d9283abd03eca2f99f5418a3726091ea5e77b1dfc81695f555 |
| `outputs/run_logs/cubit_run.log` | 841f142304488f7d082c80a0671dd9e2f7ec63cd3d696ff60a70cd509ab81153 |
| `outputs/run_logs/output_files_verification.txt` | dba9826102bc6465a03cbefa242e3cc2bd99dd05f25782e9f6a1b8cc863edf95 |

All deliverables are byte-identical (`cp -p`, SHA-256 cross-checked) to the files in the run directory `work/run/` that the accepted job used or produced.

## 10. Failures, retries, cancelled jobs, deviations
- Slurm: no failed or cancelled jobs; one submission, completed with exit 0.
- Deck translation: the first XMLGenerator translation (filter-block-only deck) produced a Helmholtz configuration without the symmetry-plane sideset; it was never run. The deck was corrected (study-level `symmetry_plane_location_names ss_sym` added, filter block retained) and re-translated before any submission. The first attempt and two syntax tests are preserved in `work/xmlgen_tests/`. No deliverable was overwritten.
- Housekeeping: `work/run/output_files_verification.txt` was briefly copied to `outputs/` by hand, then removed and placed at `outputs/run_logs/output_files_verification.txt` before `SHA256SUMS.txt` was generated; the file content is unchanged and `SHA256SUMS.txt` covers the final layout.
- Control snapshot: `catalog/checksums.sha256` lists `.gitignore`, which is absent from the snapshot (pre-existing); every present file verified OK.
- Deviations from E3-SPC-v1: **none**. All locked values were realized and verified in the mesh and in the generated runtime configuration; the run reached the 50-iteration cap.
- Unresolved issues: none.

## 11. Final artifact paths (relative to the trial root)
- Scientific: `outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`, `outputs/input_deck.i`, `outputs/job_script.sbatch`, `outputs/generated_config/` (8 XMLGenerator files + verification record + XMLGenerator log), `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`, `outputs/opt_criteria_history.csv`, `outputs/iteration50_criteria_history.csv`, `outputs/run_logs/` (Slurm stdout/stderr, Morphorm run log, Cubit log, output verification), `outputs/SHA256SUMS.txt`.
- Scheduler: `jobs/job_ids.txt`, `jobs/morphorm_spc_v1.sbatch`, `jobs/sacct_16174284.txt`, `jobs/submissions.log`; scheduler logs also in `logs/slurm-16174284.{out,err}`.
- Distributed context: `provenance/sources_searched.tsv`, `provenance/artifact_selections.md`, `provenance/node_local_placement.txt`, `provenance/control_and_source_versions.txt`, `staging-manifest/staged_files.tsv`, `staging-manifest/globus_transfers.tsv`, `staging-manifest/returned_files.tsv` (header only; nothing returned).
- Working material (kept, not deliverables): `work/mesh/`, `work/run/` (complete run directory incl. per-iteration `analyze_id_2_output_scenario_id_1/`), `work/xmlgen_tests/`, `work/manual_text/`, `work/*.py`, `work/*.sh`, `work/logs/`; staged copies in `$E3_STAGING_DIR` (left in place; released with the allocation); Globus transfer record in `staging-inbox/`.
- This summary: `work/run_summary.md`.
