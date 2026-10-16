# Run Summary — Trial E1-example8-baseline-03

## 1. Trial identifier and assigned workflow

- Trial identifier (`THESIS_TRIAL_ID`): **E1-example8-baseline-03**
- Frozen configuration: `FROZEN-EX8-v1` (sha256 `cf15ac52f018defeba40afbedc910d757c08609c6a9adaa4a1b0e0428a570b4d`); all 11 packet files verified against `agent_inputs/FROZEN_CONFIG_FILES.sha256` (`sha256sum -c`: all OK, 2026-10-09T13:13:07Z).
- Workflow: half cantilever (x∈[0,2], y∈[0,1], z∈[0,0.5]) minimum-compliance topology optimization with a Helmholtz filter whose symmetry plane is the cut-plane sideset `ss_sym`; OC optimizer, 50 iterations.
- Agent host: Slurm job 16159197 (`agent_E1-example8-baseline-03_session_main`, hochhalter-np, 8 CPUs, 32 GB, 02:00:00). Trial root: `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_03`.
- Software interface used in every shell and in the job script: `source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh` (loads `chpc/1.0 gcc/11.2.0 openmpi/5.0.3 morphorm/approved-runtime cubit-edu/2026.8`; `module list` recorded in `logs/slurm-16159209.out`).
- Documentation used: only `agent_inputs/manuals/Morphorm_User_Manual.pdf` and `Morphorm_Theory_Manual.pdf` (text extracted with `pdftotext` into `work/manual_text/` for reading).

## 2. Mesh

- Generated on the agent host with the approved Cubit in batch mode:
  `cubit -batch -nographics -nojournal -input mesh.jou` run in `work/mesh/` (start 2026-10-09T13:15:29Z, end 13:15:32Z, exit 0; stdout `work/mesh/cubit_stdout.log`, stderr empty).
- Journal: `work/mesh/mesh.jou` → deliverable `outputs/mesh.jou`. Procedure: `brick x 2.0 y 1.0 z 0.5`, moved so the corner is at the origin; `volume 1 scheme map`; exact intervals by curve length (48 / 24 / 12 → h = 1/24); `block 1` = volume 1, named `block_1`, element type HEX8; `nodeset 1` = surface x=0 named `ns_fix`; `nodeset 2` = curve x=2,y=0 named `ns_load`; `sideset 1` = surface z=0.5 named `ss_sym`; `export mesh "mesh.exo" dimension 3`.
- Mesh file: `work/mesh/mesh.exo` (sha256 `100f542b3be49a1fcfeda176069cc040b9f5e656263efadaf6a7a442ba9b54f9`), copied unchanged to `work/run2/mesh.exo` (the run directory) and `outputs/mesh.exo`.
- Verification (2026-10-09T13:17:11Z, `python3 -I work/verify/verify_mesh.py work/mesh/mesh.exo`, record `work/mesh/mesh_verification.json` → `outputs/mesh_verification.json`, 35 checks, all pass):

| Item | Expected | Found |
|---|---|---|
| dimension | 3 | 3 |
| elements / nodes | 13,824 / 15,925 | 13,824 / 15,925 |
| element blocks | 1, `block_1`, HEX8, all 13,824 elements | 1, `block_1`, HEX8, 13,824 |
| bounding box | [0,2]×[0,1]×[0,0.5] | [0,2]×[0,1]×[0,0.5] |
| structure | 49×25×13 coordinate levels, every element extent = 1/24 in x,y,z | 49/25/13; extents 0.041666667 ± 2e-15 |
| `ns_fix` | 325 nodes = every node with x=0 | 325, all at x=0, complete |
| `ns_load` | 13 nodes = every node with x=2, y=0, z∈[0,0.5] | 13, all at x=2,y=0, z from 0 to 0.5, complete |
| `ss_sym` | 1,152 faces, all on z=0.5 | 1,152 faces (1,152 distinct elements), all face nodes at z=0.5 |

## 3. Input deck and generated runtime configuration

Deck files: `work/run1/input_deck.i` (attempt 1, not accepted, see §7) and `work/run2/input_deck.i` (accepted; → `outputs/input_deck.i`, sha256 `05f4bc71017ed8cf6d5615768690c3d7e0000c8c733341783072d4686bc1832d`). Translation: `XMLGenerator input_deck.i` in the run directory (run1 at 2026-10-09T13:17:21Z, run2 at 13:18:24Z; both exit 0, empty stderr; stdout in `xmlgen_stdout.log`). The generated files used by the accepted run are in `outputs/generated_config/` (`interface.xml`, `analyze_2_input_deck.xml`, `analyze_helmholtz_input_deck.xml`, `engine_input_deck.xml`, `analyze_2_operations.xml`, `analyze_helmholtz_operations.xml`, `engine_operations.xml`, `mpirun.source`); their sha256 values were also printed by the job itself (`logs/slurm-16159209.out`) and match `outputs/SHA256SUMS.txt`.

Automated verification of the generated configuration: `python3 -I work/verify/verify_generated_config.py work/run2` at 2026-10-09T13:19:40Z, 63 checks, all pass (`outputs/generated_config_verification.json`). Locked setting → deck line → location in the generated configuration:

| Locked setting | Deck (`input_deck.i`) | Generated configuration |
|---|---|---|
| Engine service, 1 proc, `update_problem true`, `update_problem_frequency 1` | `service 1`: `code engine`, `number_processors 1`, `update_problem true`, `update_problem_frequency 1` | `interface.xml` Performer `engine_1`; `Optimizer/UpdateProblemStage` = "Update Problem", `Options/ProblemUpdateFrequency 1`; `engine_operations.xml` operation `Update Problem` with `UpdateProblemFrequency 1`; `mpirun.source` `-np 1` PlatoMain |
| Analyze service, 1 proc | `service 2`: `code analyze`, `number_processors 1` | Performer `analyze_2`; `mpirun.source` `-np 1 analyze_MPMD --input-config=analyze_2_input_deck.xml` (plus auto-wired `analyze_helmholtz`, `-np 1`); no mesh decomposition (three single-rank performers) |
| Mechanical, 3-D | `scenario 1`: `type mechanical`, `dimensions 3` | `analyze_2_input_deck.xml`: `Physics Mechanical`, `PDE Constraint Elliptic`, `Spatial Dimension 3`, `Input Mesh mesh.exo` |
| Material E=1.0, ν=0.3 on `block_1` | `material 1`: `isotropic_elastic`, `youngs_modulus 1.0`, `poissons_ratio 0.3`; `block 1`: `name block_1`, `material_id 1` | `Material Models/material_1/Isotropic Linear Elastic`: `Youngs Modulus 1.0`, `Poissons Ratio 0.3`; `Spatial Model/Domains/block_1`: `Element Block block_1`, `Material Model material_1` |
| Fixed support `ns_fix`, u_x=u_y=u_z=0 | `boundary_condition 1`: `fixed_value`, nodeset `ns_fix`, `dispx dispy dispz`, `0.0 0.0 0.0` | `Essential Boundary Conditions`: "Displacement X/Y/Z with ID 1/2/3", `Type Fixed Value`, `Index 0/1/2`, `Sides ns_fix`, `Value 0.0` |
| Symmetry `ss_sym`, u_z=0 through the sideset | `boundary_condition 2`: `fixed_value`, `location_type sideset`, `location_name ss_sym`, `dispz`, `0.0` | "Displacement Z with ID 4": `Index 2`, `Sides ss_sym`, `Value 0.0` (accepted by XMLGenerator and by analyze; runtime check below) |
| Load: nodal −1.0 in y on every `ns_load` node, nothing else | `load 1`: `concentrated_load`, nodeset `ns_load`, `direction y`, `value -1.0` | `Concentrated Loads/Concentrated Load with ID 0`: `Dof 1`, `Value -1.0`, `Nodes ns_load`; `Mechanical Natural Boundary Conditions` empty; no body loads |
| Objective: weighted sum, single compliance criterion, weight 1, analyze service | `criterion 1 type mechanical_compliance`; `objective 1`: `weighted_sum`, `criterion_ids 1`, `service_ids 2`, `scenario_ids 1`, `weights 1` | `Criteria/My Objective`: `Internal Elastic Energy`, `Domains {block_1}`; `interface.xml` stage "Compute Objective Value": `Compute Objective Value` on `analyze_2`, `Aggregate Data` on `engine_1`; `engine_operations.xml` Aggregator `Weight 1`, no normalization |
| Constraint: volume ≤ 0.15, `less_than`, engine service | `criterion 2 type volume`; `constraint 1`: `criterion_id 2`, `relative_target 0.15`, `type less_than`, `service_id 1`, `scenario_id 1` | `interface.xml` `Optimizer/Constraint`: `NormalizedTargetValue 0.15`, `ReferenceValueName Design Volume`; stage "Compute Constraint Value 1" operation `Compute Constraint Value 1` on `engine_1` (`engine_operations.xml` `ComputeVolume`) |
| Density discretization, uniform initial density 0.15 | `study`: `discretization density`, `initialize_method uniform`, `initial_density_value 0.15` | `engine_operations.xml` `Initialize Field`: `Method Uniform`, `Value 0.15`; `SetLowerBounds/SetUpperBounds` `Discretization density`; `BoundConstraint` 0.0–1.0 |
| SIMP single phase, exponent 3.0, minimum 1e-3; criterion `minimum_ersatz_material_value 1e-3` | `material_interpolation 1`: `single_phase`, `simp`, `penalty_exponent 3.0`, `minimum_value 1e-3` (referenced by `residual 1`); `criterion 1`: `material_penalty_exponent 3.0`, `minimum_ersatz_material_value 1e-3` | `analyze_2_input_deck.xml` `Residual/Mechanical Residual`: `Material Interpolation Model Single-Phase`, `Penalty Function` `SIMP`, `Exponent 3.0`, `Minimum Value 1e-3`; `Criteria/My Objective/Penalty Function`: `SIMP`, `Exponent 3.0`, `Minimum Value 1e-3` |
| OC optimizer, default tolerances, `normalize_in_aggregator false` | `study`: `optimization_algorithm oc`, `normalize_in_aggregator false` | `interface.xml` `Optimizer/Package OC`; `OCControlStagnationTolerance 1e-4`, `OCObjectiveStagnationTolerance 1e-8`, `OCGradientTolerance 1e-8` (runtime defaults); Aggregator without normalization |
| `max_iterations 50` | `study`: `max_iterations 50` | `interface.xml` `Optimizer/Convergence/MaxIterations 50`; `engine_operations.xml` `PlatoMainOutput/MaxIterations 50` |
| Helmholtz filter, absolute radius 0.15, boundary-sticking penalty 1.0, symmetry plane `ss_sym` | `study`: `filter_type helmholtz`, `filter_radius_absolute 0.15`, `boundary_sticking_penalty 1.0`, `symmetry_plane_location_names ss_sym` | `analyze_helmholtz_input_deck.xml` `Scenarios/Parameters`: `Length Scale 0.043301` (numerically 0.15 / (2√3); XMLGenerator produced the identical value from `radius_absolute 0.15` in attempt 1, so this is the runtime's conversion of the locked absolute radius 0.15 to the PDE length scale ℓΩ of Theory Manual Eq. 4.4.8 — the manuals do not state the conversion factor, this is my observation), `Surface Length Scale 1.0`, `Symmetry Plane Sides {ss_sym}`; `Physics Helmholtz Filter`; `Domains/block_1`. Filter wired as performer `analyze_helmholtz` ("Filter Control"/"Filter Gradient" in every objective/constraint stage of `interface.xml`) |
| Output: dispx, dispy, dispz from analyze; engine output of control and topology | `output 1`: `service_id 2`, `data dispx dispy dispz` | `analyze_2_input_deck.xml` `Output/Plottable {displacement_x, displacement_y, displacement_z}`; `analyze_2_operations.xml` `Visualization` (`OutputFrequency 1`); `engine_operations.xml` `PlatoMainOutput` inputs `topology`, `control`; `engine_input_deck.xml` output file `engine_output` (exodus) |
| Mesh | `mesh`: `name mesh.exo` | `Input Mesh mesh.exo` in both analyze decks; `engine_input_deck.xml` `<mesh>mesh.exo</mesh>`, block 1 material 1 |

Runtime evidence that the locked conditions were actually enforced (approved `python3`, scripts in `work/verify/`):
- `check_runtime_bcs.py` on `analyze_id_2_output_scenario_id_1/iteration0.exo` and `iteration50.exo` (`outputs/runtime_bc_check_iteration50.json`): all three displacement components are exactly 0 on all 325 x=0 nodes; u_z is exactly 0 on all 1,225 nodes of the z=0.5 plane (`ss_sym`) while u_x,u_y there are nonzero and u_z elsewhere is nonzero; u_y < 0 on all 13 loaded nodes.
- `check_runtime_filter_symmetry.py` on `engine_output.exo`, state 0 (uniform control 0.15) (`outputs/runtime_filter_symmetry_check.json`): filtered `topology` on deep symmetry-plane nodes = 0.14965 vs deep interior 0.14940 (ratio 1.0017, i.e. not penalized), whereas the real z=0 face is pulled down to 0.0745 (ratio 0.499) by the boundary-sticking term — the filter treats `ss_sym` as a reflective plane and penalizes only the real outer boundaries.

## 4. Execution

Commands (all from the trial root unless noted; every shell sourced the approved software interface first):

```
sha256sum -c agent_inputs/FROZEN_CONFIG_FILES.sha256                       # packet integrity (all OK)
pdftotext -layout agent_inputs/manuals/*.pdf work/manual_text/...           # manuals to text for reading
cd work/mesh && cubit -batch -nographics -nojournal -input mesh.jou         # mesh (13:15:29Z–13:15:32Z, exit 0)
python3 -I work/verify/verify_mesh.py work/mesh/mesh.exo                    # mesh verification (13:17:11Z, all pass)
cp work/mesh/mesh.exo work/run1/ ; cd work/run1 && XMLGenerator input_deck.i   # attempt 1 translation (13:17:21Z, exit 0)
python3 -I work/verify/verify_generated_config.py work/run1                 # 62/63 pass: symmetry plane missing -> not accepted
cp work/mesh/mesh.exo work/run2/ ; cd work/run2 && XMLGenerator input_deck.i   # attempt 2 translation (13:18:24Z, exit 0)
python3 -I work/verify/verify_generated_config.py work/run2                 # 63/63 pass (13:19:40Z)
sbatch jobs/job_script.sbatch                                               # 13:19:56Z -> "Submitted batch job 16159209"
sacct -j 16159209 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P > jobs/sacct_16159209.txt
python3 -I work/verify/verify_results.py work/run2 work/run2/analyze_id_2_output_scenario_id_1/iteration50.exo   # 13:31:06Z, all pass
python3 -I work/verify/check_runtime_bcs.py ... iteration0.exo / iteration50.exo ; python3 -I work/verify/check_runtime_filter_symmetry.py work/run2/engine_output.exo 0
bash work/verify/assemble_outputs.sh "$PWD" 16159209                        # 13:31:07Z: copies deliverables, writes outputs/SHA256SUMS.txt (sha256sum -c OK)
```

Slurm jobs submitted in this trial (also in `jobs/job_ids.txt`):

| Job ID | Script | Purpose | Resources | State | ExitCode | Submit / Start / End (UTC) | Elapsed | MaxRSS | Node |
|---|---|---|---|---|---|---|---|---|---|
| 16159209 | `jobs/job_script.sbatch` (= `outputs/job_script.sbatch`, copy `work/run2/job_script.sbatch`) | 50-iteration optimization, run directory `work/run2` | account/partition hochhalter-np, 1 node, 1 task × 8 CPUs, 32G, 02:00:00, no GPU | COMPLETED | 0:0 | 13:19:56 / 13:19:57 / 13:29:36 | 00:09:39 | 1,375,872 K (batch step) | notch351 |

The job script sources the approved interface, prints `module list` and executable paths, prints sha256 of the deck/mesh/generated files, then runs `bash mpirun.source > morphorm_run.log 2>&1` (3 single-rank performers: PlatoMain, analyze_MPMD physics, analyze_MPMD Helmholtz). Morphorm ran 13:20:01Z–13:29:36Z, exit 0. Scheduler files: `logs/slurm-16159209.out`, `logs/slurm-16159209.err` (empty); copies in `outputs/run_logs/`. Scheduler record: `jobs/sacct_16159209.txt`. No job was cancelled; the optimization was not run on the agent host.

## 5. Completed stages and iteration counts

- Mesh generation: complete. Mesh verification: complete (35/35). Deck translation: complete (attempt 2 accepted). Generated-configuration verification: complete (63/63). Optimization job: complete. Result verification: complete (15/15, `outputs/results_verification.json`). Deliverable assembly and manifest: complete.
- Iterations reached: **50 of 50**. `morphorm_oc_optimizer_diagnostics.txt` lists iterations 0–50 contiguously (51 function evaluations); `engine_output.exo` holds 51 design states (iterations 0–50, Exodus time stamps 1–51) with nodal `control` and `topology`; analyze wrote `iteration0.exo` … `iteration50.exo` (51 files), each with nodal `Topology`, `displacement X/Y/Z`.
- Optimizer stopping message (last lines of the diagnostics file): `****** Optimization stopping due to exceeding maximum number of iterations. ******` — the run reached the iteration cap; no convergence stop occurred. Engine log: `Terminate signal received on Performer 'engine_1'` / `Terminate stage requested. Exiting.` (normal shutdown).
- Diagnostics: iteration 0: F(X) = 2.654786e+06, H1(X) = −1.564817e−02, abs(dX) = 0.15; iteration 50: F(X) = 1.044701e+05, Norm(F') = 7.033815e+03, H1(X) = −1.628697e−13 (volume constraint active/satisfied), abs(dX) = 1.142971e−01, abs(dF) = 6.611695e+01 (both still far above the 1e-4 / 1e-8 stagnation tolerances, consistent with stopping only on the cap).

## 6. Key output files (deliverables in `outputs/`) with SHA-256

| Path | SHA-256 |
|---|---|
| `outputs/mesh.jou` | f6b8895d6ae78974fdfe7049c4e683c7bed184e9bc1a557a5c1e7985657b359c |
| `outputs/mesh.exo` | 100f542b3be49a1fcfeda176069cc040b9f5e656263efadaf6a7a442ba9b54f9 |
| `outputs/mesh_verification.json` | 0c340d49ffe9df9741ee00bf870a9ce6be8e61b50f727eb68f36e62515952900 |
| `outputs/input_deck.i` | 05f4bc71017ed8cf6d5615768690c3d7e0000c8c733341783072d4686bc1832d |
| `outputs/job_script.sbatch` | 3e1a19e3d9dbe2fd8908864e67e7d837e2ffb4a8045bee213b075d686bc01202 |
| `outputs/generated_config/interface.xml` | f472563b804e84b4e5590c12ec80403bf446562b6ef923daf51814133d258a75 |
| `outputs/generated_config/analyze_2_input_deck.xml` | 062429a12242027c1f6ec7871f893ae120475fbd547f64840f9fcd0158a4a39c |
| `outputs/generated_config/analyze_helmholtz_input_deck.xml` | e0b190ab3e8c71334d7b7ec5f0567dbcdae40f7a371b943a553d6eb54fae5436 |
| `outputs/generated_config/engine_input_deck.xml` | 7f3edc06119d4155981b3861c2c2263f268e6a3f56f7577cc0aa202f3b35169a |
| `outputs/generated_config/analyze_2_operations.xml` | fbabf1a1c037533ce5dc1b1ba6a97ce9d70a795c1128735196a3e624aa73efa0 |
| `outputs/generated_config/analyze_helmholtz_operations.xml` | 402ffc30789914bd0c1c7bf429aa2f08ea22b0040960d015b9c71fd716404854 |
| `outputs/generated_config/engine_operations.xml` | c5b07640e3f1427a5f763631a2f7f9c3ec1ea54e97160106efe598afc0c67c1b |
| `outputs/generated_config/mpirun.source` | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| `outputs/morphorm_oc_optimizer_diagnostics.txt` | 5bf3294ab40a1a55925134eb0ef493c7cb725e0964ae54cb3ce1ee62ae18e4f4 |
| `outputs/engine_output.exo` | 1aaed1e511062be4f851104be922563fc2efbb3f735cf87f3db19a779c05f200 |
| `outputs/final_analyze_output.exo` (= `work/run2/analyze_id_2_output_scenario_id_1/iteration50.exo`) | 37e132d17c1295ccb662ebba04d6217e1dc77ac03c443ac32103cde40227dca0 |
| `outputs/run_logs/slurm-16159209.out` | df51bdb123d002f42743254fe8f4a333b7d08c1dc8083c2a49ddf0ed652ceefe |
| `outputs/run_logs/slurm-16159209.err` (empty) | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| `outputs/run_logs/morphorm_run.log` | 24f51bf3b88158d9283abd03eca2f99f5418a3726091ea5e77b1dfc81695f555 |
| `outputs/run_logs/engine_1_0.log` / `analyze_2_1.log` / `analyze_helmholtz_2.log` | 0251658e… / 3d69be4b… / 75a3d26e… (full values in `outputs/SHA256SUMS.txt`) |
| `outputs/run_logs/opt_criteria_history.csv`, `xmlgen_stdout.log`, `cubit_stdout.log` | fc58edec… / 9fc113f1… / 04304cd2… |
| `outputs/generated_config_verification.json`, `results_verification.json`, `runtime_bc_check_iteration50.json`, `runtime_filter_symmetry_check.json` | 9783a95c… / 47b3c315… / 135c4e59… / a8534e8d… |
| `outputs/SHA256SUMS.txt` | covers all 29 files above (produced with `sha256sum`; `sha256sum -c` OK) |

## 7. Failures, retries, cancelled jobs, unresolved issues, deviations

- **Attempt 1 (`work/run1/`, not submitted, kept):** the deck declared the Helmholtz filter as a first-class `begin filter 1 … end filter` block (`type helmholtz`, `radius_absolute 0.15`, `boundary_sticking_penalty 1.0`, `symmetry_plane_location_names ss_sym`) referenced by `filter_ids 1`. XMLGenerator exited 0, and the generated `analyze_helmholtz_input_deck.xml` contained `Length Scale 0.043301` and `Surface Length Scale 1.0`, but **no symmetry-plane sideset** — the `symmetry_plane_location_names` keyword of the filter block was not translated. Per the specification's generated-configuration requirement this configuration does not apply the locked setting, so attempt 1 was not run. Decision: re-express the same locked filter values with the manual's equivalent legacy study-level keywords (`filter_type helmholtz`, `filter_radius_absolute 0.15`, `boundary_sticking_penalty 1.0`, `symmetry_plane_location_names ss_sym`, User Manual §2.5.4 Table 2.5.12). Attempt 2 (`work/run2/`) then produced `Symmetry Plane Sides {ss_sym}` together with the identical length scales; all other generated files were byte-identical to attempt 1 (`diff -q`). No locked value was changed between the attempts — only the deck syntax used to express the filter.
- Essential boundary condition through a sideset: the manual states Dirichlet conditions are applied to nodesets but lists `sideset` as an accepted `location_type`; the locked specification requires the u_z=0 condition on `ss_sym` through the sideset. The deck uses `location_type sideset` / `location_name ss_sym`; XMLGenerator translated it (`Sides ss_sym`), analyze accepted it, and the runtime displacement check confirms u_z = 0 on all 1,225 cut-plane nodes. No deviation.
- Checker corrections (not run issues): my first `verify_results.py` expected the engine output's last Exodus time stamp to be 50 and displacement names `displacement_x`; the engine stamps iterations 0–50 as times 1–51 and names the fields `displacement X/Y/Z`. The checker expectations were corrected (51 states; name normalization) and rerun; the run itself was unchanged.
- Informational XMLGenerator messages about defaults (e.g. `filter_radius_scale 2.0`, `boundary_sticking_penalty`) were reviewed; the generated Helmholtz configuration carries the locked values (length scale from R = 0.15, surface length scale 1.0, `ss_sym`).
- Cancelled jobs: none. Failed jobs: none. Retries of the optimization: none (one submission, one uninterrupted 50-iteration run). Unresolved issues: none. Deviations from the specification: **none**. No restricted material was accessed; no files outside the trial root were modified.

## 8. Final artifact paths

- Deliverables: `outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`, `outputs/input_deck.i`, `outputs/job_script.sbatch`, `outputs/generated_config/{interface.xml, analyze_2_input_deck.xml, analyze_helmholtz_input_deck.xml, engine_input_deck.xml, analyze_2_operations.xml, analyze_helmholtz_operations.xml, engine_operations.xml, mpirun.source}`, `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`, `outputs/run_logs/` (Slurm stdout/stderr, `morphorm_run.log`, the three performer logs, criteria history, XMLGenerator and Cubit stdout), `outputs/SHA256SUMS.txt`; supplementary verification records `outputs/generated_config_verification.json`, `outputs/results_verification.json`, `outputs/runtime_bc_check_iteration50.json`, `outputs/runtime_filter_symmetry_check.json`.
- Scheduler evidence: `jobs/job_ids.txt`, `jobs/job_script.sbatch`, `jobs/sacct_16159209.txt`, `jobs/submission_log.txt`, `logs/slurm-16159209.out`, `logs/slurm-16159209.err`.
- Work area: `work/mesh/` (journal, mesh, Cubit logs, verification), `work/run1/` (attempt 1 deck and generated files, not run), `work/run2/` (accepted run directory incl. all 51 analyze iteration files under `analyze_id_2_output_scenario_id_1/`), `work/verify/` (verification and assembly scripts), `work/manual_text/` (manual text extracts), `work/run_summary.md` (this file).
