# Run summary — trial E1-example8-baseline-04R2

## 1. Trial identifier and assigned workflow

- Trial identifier (THESIS_TRIAL_ID): `E1-example8-baseline-04R2`
- Frozen configuration: `FROZEN-EX8-v1` (hash cf15ac52f018defeba40afbedc910d757c08609c6a9adaa4a1b0e0428a570b4d)
- Workflow: half cantilever with a Helmholtz symmetry-plane filter (`agent_inputs/scientific_problem_specification.md`); minimum-compliance density topology optimization, OC optimizer, exactly 50 iterations.
- Agent host: Slurm allocation 16167163 (`agent_E1`, node notch351, partition hochhalter-np). This allocation was provided by the researcher harness, not submitted by me; it is not listed in `jobs/job_ids.txt`.
- Software: `source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh` in every agent-host shell and in the job script. After sourcing, `module list` shows chpc/1.0, gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8. Only the two manuals in `agent_inputs/manuals/` were consulted (text extracted with `pdftotext` into `work/manual_text/` for grepping; no other documentation, examples, meshes, decks or outputs were accessed).
- Trial root: `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E1_uninterrupted_example8/baseline/trial_04R2`. All paths below are relative to it unless absolute.

## 2. Mesh

**Generation.** Coreform Cubit 2026.8 in batch mode on the agent host (mesh generation is permitted on the agent host by `compute_resources.md`):

```
cd work/mesh
cubit -batch -nographics -nojournal -input mesh.jou > cubit_mesh.log 2>&1     # rc=0
```

- Journal: `work/mesh/mesh.jou` (deliverable copy `outputs/mesh.jou`). Procedure: `brick x 2 y 1 z 0.5`, moved by (1, 0.5, 0.25) so the corner is at the origin; `volume 1 size 0.0416666666666667`, `scheme map`, `mesh volume 1`; `block 1` = volume 1, named `block_1`, element type HEX8; `nodeset 1` = surface with x_coord < 0.001 (the x = 0 face), named `ns_fix`; `nodeset 2` = curve with x_coord > 1.999 and y_coord < 0.001 (the edge x = 2, y = 0), named `ns_load`; `sideset 1` = surface with z_coord > 0.499 (the cut plane z = 0.5), named `ss_sym`; `export mesh "mesh.exo" dimension 3 overwrite`.
- Timestamps (UTC): generation start 2026-10-09T21:44:55Z, end 2026-10-09T21:44:57Z.
- A throw-away probe journal (`work/cubit_probe/probe.jou`, log `probe.log`, run 2026-10-09T21:44:30Z) was used first to confirm Cubit's surface/curve ids and the `with x_coord ...` filter syntax; it exported nothing.
- Mesh file: `work/mesh/mesh.exo` (1,052,996 bytes), SHA-256 `a0903af49bddaee81bac1a7aa63259a3e22859501aecc2cd838912b161877629`; identical copies at `work/run2/mesh.exo` (the file the accepted run read) and `outputs/mesh.exo`.

**Verification** (before any optimization; `work/scripts/verify_mesh.py`, approved runtime `python3 -I` with netCDF4, read-only; record `work/mesh/mesh_verification.json` → `outputs/mesh_verification.json` and human-readable `outputs/mesh_verification.txt`; verified 2026-10-09T21:45:37Z). All 24 checks PASS:

| Item | Locked | Verified |
|---|---|---|
| Dimension | 3 | 3 |
| Elements / nodes | 13,824 / 15,925 | 13,824 / 15,925 |
| Element type | HEX8 structured | HEX8 (8 nodes/element), every element edge = 1/24 (min 0.04166666666666519, max 0.04166666666666807) |
| Grid | 48 × 24 × 12, h = 1/24 | 49 / 25 / 13 distinct x / y / z coordinates, uniform spacing 1/24 |
| Bounding box | [0,2] × [0,1] × [0,0.5] | [0.0, 2.0] × [0.0, 1.0] × [0.0, 0.5] |
| Element block | one block `block_1`, all elements | 1 block, name `block_1`, 13,824 elements |
| `ns_fix` | all nodes on x = 0 (325) | 325 nodes, all at x = 0, equal to the set of all mesh nodes with x = 0 |
| `ns_load` | all nodes on x = 2, y = 0, z ∈ [0,0.5] (13) | 13 nodes, all at x = 2, y = 0, z from 0.0 to 0.5, equal to the set of all mesh nodes on that edge |
| `ss_sym` | all faces on z = 0.5 (1,152) | 1,152 faces, every face node at z = 0.5, 1,152 distinct elements (= 48 × 24, full plane) |

## 3. Input deck and generated runtime configuration

- Accepted deck: `work/run2/input_deck.i` → `outputs/input_deck.i` (SHA-256 `de5db3ed546fa505a151aa1636e776058b56002d56fe00182a5cf6c92ec6aa22`). Rejected first deck: `work/run1/input_deck.i` (see section 7).
- Translation: `cd work/run2 && XMLGenerator input_deck.i > xmlgenerator.log 2>&1` (rc=0), 2026-10-09T21:46:41Z. Generated files (all kept in `outputs/generated_config/`): `interface.xml`, `analyze_2_input_deck.xml`, `analyze_2_operations.xml`, `analyze_helmholtz_input_deck.xml`, `analyze_helmholtz_operations.xml`, `engine_input_deck.xml`, `engine_operations.xml`, `mpirun.source` (+ `xmlgenerator.log`, the automated check record `generated_config_verification.json`, and `pre_submission_input_sha256.txt`).
- Automated verification of the generated configuration (`work/scripts/verify_generated_config.py`, 61 checks, all PASS, 2026-10-09T21:48Z; record `outputs/generated_config/generated_config_verification.json`). Mapping of each locked setting to the deck and to the generated configuration:

| Locked setting | Deck (input_deck.i) | Generated configuration (file : element) |
|---|---|---|
| Engine service, 1 proc, `update_problem true`, `update_problem_frequency 1` | `service 1`: code engine, number_processors 1, update_problem true, update_problem_frequency 1 | interface.xml: Performer engine_1 (code engine); Optimizer/Options/ProblemUpdateFrequency = 1; UpdateProblemStage "Update Problem". engine_operations.xml: Operation "Update Problem" UpdateProblemFrequency = 1. mpirun.source: `-np 1 ... PlatoMain engine_input_deck.xml` |
| Analyze service, 1 proc | `service 2`: code analyze, number_processors 1 | interface.xml: Performer analyze_2; mpirun.source: `-np 1 ... analyze_MPMD --input-config=analyze_2_input_deck.xml` |
| Helmholtz filter service (wired automatically), single rank, no decomposition | — | interface.xml: Performer analyze_helmholtz; mpirun.source: `-np 1 ... analyze_MPMD --input-config=analyze_helmholtz_input_deck.xml`; no decomposition step, mesh read as `mesh.exo` by all three performers |
| Mechanical 3-D scenario on mesh.exo | `scenario 1`: type mechanical, dimensions 3, service_id 2, residual_ids 1, output_id 1; `mesh 1`: name mesh.exo | analyze_2_input_deck.xml: Physics = Mechanical, PDE Constraint = Elliptic, Spatial Dimension = 3, Input Mesh = mesh.exo; engine_input_deck.xml: mesh = mesh.exo, one block (index 1) |
| Material E = 1.0, ν = 0.3 on block_1 | `material 1`: isotropic_elastic, youngs_modulus 1.0, poissons_ratio 0.3; `block 1`: name block_1, material_id 1 | analyze_2_input_deck.xml: Material Models/material_1/Isotropic Linear Elastic: Youngs Modulus = 1.0, Poissons Ratio = 0.3; Spatial Model/Domains/block_1 (Element Block = block_1, Material Model = material_1) — the only domain |
| Fixed support ns_fix: u_x = u_y = u_z = 0 | `boundary_condition 1`: fixed_value, nodeset ns_fix, dispx dispy dispz, 0 0 0 | analyze_2_input_deck.xml: Essential Boundary Conditions "Displacement X with ID 1" (Index 0), "Displacement Y with ID 2" (Index 1), "Displacement Z with ID 3" (Index 2): Type Fixed Value, Sides = ns_fix, Value = 0.0 |
| Symmetry ss_sym: u_z = 0 through the sideset | `boundary_condition 2`: fixed_value, location_type sideset, location_name ss_sym, dispz, 0.0 | analyze_2_input_deck.xml: "Displacement Z with ID 4": Type Fixed Value, Index 2, Sides = ss_sym, Value = 0.0 |
| Load: concentrated nodal load, direction y, −1.0 per node on ns_load, no other loads | `load 1`: concentrated_load, nodeset ns_load, direction y, value -1.0 | analyze_2_input_deck.xml: Concentrated Loads/"Concentrated Load with ID 0": Dof = 1 (y), Value = −1.0, Nodes = ns_load; "Mechanical Natural Boundary Conditions" empty; no body loads |
| Objective: weighted sum, single compliance criterion, weight 1, analyze service | `criterion 1`: mechanical_compliance; `objective 1`: weighted_sum, criterion_ids 1, service_ids 2, scenario_ids 1, weights 1 | analyze_2_input_deck.xml: Criteria/"My Objective": Scalar Function Type = Internal Elastic Energy (compliance), Domains {block_1}; engine_operations.xml: Aggregator weight 1 (single term); interface.xml stage "Compute Objective Value": operation on analyze_2 |
| Compliance criterion `minimum_ersatz_material_value 1e-3` | `criterion 1`: minimum_ersatz_material_value 1e-3 | analyze_2_input_deck.xml: Criteria/"My Objective"/Penalty Function: Type SIMP, Exponent 3.0, Minimum Value 1e-3 |
| SIMP single phase, exponent 3.0 (runtime default), minimum 1e-3 | `material_interpolation 1`: single_phase, simp, penalty_exponent 3.0, minimum_value 1e-3; referenced by `residual 1` material_interpolation_id 1 | analyze_2_input_deck.xml: Residual/Mechanical Residual: Material Interpolation Model = Single-Phase, Response = Linear, Penalty Function: Type SIMP, Exponent 3.0, Minimum Value 1e-3 |
| Constraint volume ≤ 15 %: relative_target 0.15, less_than, engine service | `criterion 2`: volume; `constraint 1`: criterion_id 2, relative_target 0.15, type less_than, service_id 1 | interface.xml: Optimizer/Constraint: NormalizedTargetValue = 0.15, ReferenceValueName = Design Volume (single constraint); stage "Compute Constraint Value 1": ComputeVolume on engine_1 |
| Density discretization, uniform initial density 0.15 | `study`: discretization density, initialize_method uniform, initial_density_value 0.15 | engine_operations.xml: InitializeField Method Uniform Value 0.15; SetLowerBounds/SetUpperBounds Discretization = density; interface.xml BoundConstraint 0.0–1.0 |
| OC optimizer, default tolerances, max_iterations 50 | `study`: optimization_algorithm oc, max_iterations 50 (no tolerance keywords) | interface.xml: Optimizer Package = OC, Convergence/MaxIterations = 50, OCControlStagnationTolerance 1e-4, OCObjectiveStagnationTolerance 1e-8, OCGradientTolerance 1e-8 (the runtime defaults, per xmlgenerator.log); engine_operations.xml PlatoMainOutput MaxIterations 50 |
| `normalize_in_aggregator false` | `study`: normalize_in_aggregator false | engine_operations.xml: "Aggregate Data" Aggregator contains only Weighting (Weight 1); no normalization element |
| Helmholtz filter, absolute radius 0.15 | `study`: filter_type helmholtz, filter_radius_absolute 0.15 | analyze_helmholtz_input_deck.xml: Physics = Helmholtz Filter, Parameters/Length Scale = 0.043301 (= 0.15 / (2√3), the generator's radius-to-length-scale conversion; 0.15/(2·1.7320508) = 0.0433013) |
| Boundary-sticking penalty 1.0 | `study`: boundary_sticking_penalty 1.0 | analyze_helmholtz_input_deck.xml: Parameters/Surface Length Scale = 1.0 |
| Cut-plane sideset declared as filter symmetry plane | `study`: symmetry_plane_location_names ss_sym | analyze_helmholtz_input_deck.xml: Parameters/Symmetry Plane Sides = {ss_sym} |
| Output dispx, dispy, dispz from analyze; engine output of control and topology | `output 1`: service_id 2, data dispx dispy dispz | analyze_2_input_deck.xml: Output/Plottable = {displacement_x, displacement_y, displacement_z}; analyze_2_operations.xml Visualization OutputFrequency 1; engine_operations.xml PlatoMainOutput inputs `topology` and `control`; engine_input_deck.xml output file engine_output |

Decisions and assumptions in the deck (none alters a locked value):
- The Helmholtz filter is declared with the study-level keywords (`filter_type helmholtz`, `filter_radius_absolute`, `boundary_sticking_penalty`, `symmetry_plane_location_names`) rather than a `filter` block, because with the `filter` block form (work/run1) XMLGenerator did not emit the symmetry-plane sideset (see section 7). The manual states the two forms are equivalent for a single filter.
- `penalty_exponent 3.0` is written explicitly in the material_interpolation block; it equals the runtime default and the generated value is 3.0.
- No `scenario_id` is given on the volume constraint (manual: optional for volume criteria evaluated without physics); the generated constraint evaluates on the engine as required.
- Output frequency, solver package (tacho), engine output frequency (PlatoMainOutput OutputFrequency 5 in engine_operations.xml, generator default) and all optimizer tolerances were left at runtime defaults because the specification does not lock them. Despite the engine-side frequency of 5, `engine_output.exo` contains 51 time steps (iterations 0–50) — see section 5.
- The essential symmetry condition is given with `location_type sideset` exactly as the specification requires; the manual's BC chapter describes nodesets, but XMLGenerator accepted the sideset and emitted `Sides = ss_sym`, and the run executed without error.

## 4. Execution

Commands used on the agent host (all after sourcing the approved software interface), in order:

```
cat agent_inputs/*.md agent_inputs/FROZEN_CONFIG_*             # read packet
pdftotext -layout agent_inputs/manuals/Morphorm_User_Manual.pdf work/manual_text/user_manual.txt
pdftotext -layout agent_inputs/manuals/Morphorm_Theory_Manual.pdf work/manual_text/theory_manual.txt
cd work/cubit_probe && cubit -batch -nographics -nojournal -input probe.jou > probe.log 2>&1   # geometry-id/filter syntax probe
cd work/mesh && cubit -batch -nographics -nojournal -input mesh.jou > cubit_mesh.log 2>&1     # mesh (2026-10-09T21:44:55Z–21:44:57Z)
python3 -I work/scripts/verify_mesh.py work/mesh/mesh.exo > work/mesh/mesh_verification.json # rc=0, 2026-10-09T21:45:37Z
cd work/run1 && cp ../mesh/mesh.exo . && XMLGenerator input_deck.i > xmlgenerator.log 2>&1   # rc=0, 2026-10-09T21:45:54Z (filter-block form; rejected)
cd work/run2 && cp ../mesh/mesh.exo . && XMLGenerator input_deck.i > xmlgenerator.log 2>&1   # rc=0, 2026-10-09T21:46:41Z (accepted)
python3 -I work/scripts/verify_generated_config.py work/run2 > work/run2/generated_config_verification.json   # rc=0 (61/61)
python3 -I work/scripts/verify_generated_config.py work/run1 > work/run1/generated_config_verification.json   # rc=1 (symmetry sideset missing)
sha256sum work/run2/{input_deck.i,mesh.exo,*.xml,mpirun.source} > work/run2/pre_submission_input_sha256.txt
sbatch jobs/morphorm_ex8.sbatch                                   # "Submitted batch job 16167268", 2026-10-09T21:48:33Z
squeue -j 16167268 ... (polled every 15 s)
sacct -j 16167268 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P > jobs/sacct_16167268.txt
python3 -I work/scripts/verify_result.py work/run2 > work/run2/result_verification.json   # rc=0 after fixing the script's own expectations (section 7)
cp ... outputs/ ; cd outputs && find . -type f ! -name SHA256SUMS.txt | sort | sed 's|^\./||' | xargs sha256sum > SHA256SUMS.txt && sha256sum -c SHA256SUMS.txt
```

Slurm jobs submitted in this trial (also in `jobs/job_ids.txt`):

| Job ID | Script | Resources | Submit (UTC) | Start | End | Elapsed | State | ExitCode | Node | MaxRSS |
|---|---|---|---|---|---|---|---|---|---|---|
| 16167268 | `jobs/morphorm_ex8.sbatch` (= `outputs/job_script.sbatch`) | account hochhalter-np, partition hochhalter-np, 1 node, 1 task × 8 CPUs, 32 GB, 02:00:00, no GPU | 2026-10-09T21:48:33Z | 21:48:35Z | 21:58:29Z | 00:09:54 | COMPLETED | 0:0 | notch351 | 1,683,452 KB (batch step) |

- The job script sources the approved software interface, prints `module list`, the executable paths and the SHA-256 of every input, then runs `bash mpirun.source 2>&1 | tee morphorm_run.log` in `work/run2` (`--chdir`). Scheduler stdout/stderr: `logs/morphorm_16167268.out` / `.err` (stderr empty); copies in `outputs/run_logs/`. `sacct` record: `jobs/sacct_16167268.txt` (copy in `outputs/run_logs/`).
- Inside the job (from the stdout): JOB_START 2026-10-09T21:48:38Z, MORPHORM_START 21:48:41Z, MORPHORM_END 21:58:29Z, MORPHORM_EXIT_CODE 0, JOB_END 21:58:29Z; `module list` shows chpc/1.0, gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8; the input checksums printed by the job match `pre_submission_input_sha256.txt` and the manifest.
- The optimization was not run on the agent host. Mesh generation, translation and verification scripts ran on the agent host.

## 5. Completed stages and iteration counts

- Mesh generation: complete. Deck translation: complete (run2 accepted). Mesh and generated-configuration verification: complete, all checks pass. Optimization job 16167268: complete, exit 0. Post-run verification (`work/scripts/verify_result.py`, 12 checks, all PASS, record `outputs/run_logs/result_verification.json`): complete.
- Iterations reached: **50** (the locked cap). `morphorm_oc_optimizer_diagnostics.txt` has rows for iterations 0 through 50 (51 rows, F-count 1–51). `opt_criteria_history.csv` has 51 objective values (iteration 0: 2.6547864698604103e+06; iteration 50: 1.0447014052065862e+05). `engine_output.exo` has 51 time steps (iterations 0–50 stored as steps 1–51) with nodal fields `control` and `topology`. `analyze_id_2_output_scenario_id_1/` holds `iteration0.exo` … `iteration50.exo` (51 files) with nodal `Topology`, `displacement X/Y/Z` and element `My Objective`.
- Stopping message of the optimizer (last line of the diagnostics file):
  `****** Optimization stopping due to exceeding maximum number of iterations. ******`
  No convergence stop occurred before iteration 50.
- Final diagnostics row (iteration 50): F(X) = 1.044701e+05, Norm(F') = 7.033815e+03, H1(X) = −1.628697e−13 (volume constraint active and satisfied), abs(dX) = 1.142971e−01, abs(dF) = 6.611695e+01. Final filtered `topology` field: min 1.01e−08, max 0.939, mean 0.157; final `control`: min 0.0, max 1.0, mean 0.185. All displacement fields finite.

## 6. Key output files (deliverables) and SHA-256

Full list in `outputs/SHA256SUMS.txt` (32 files, verified with `sha256sum -c`).

| Path | SHA-256 |
|---|---|
| outputs/mesh.jou | 81015a5a81019a6d28a03f6159ace73939004af7be6feecbf849e4ab4abf5e9e |
| outputs/mesh.exo | a0903af49bddaee81bac1a7aa63259a3e22859501aecc2cd838912b161877629 |
| outputs/mesh_verification.json | 979e035a72de55c14619eba43c1ad293cd75d7d519268e8dbe811b5fd3b93b4e |
| outputs/mesh_verification.txt | 7f283c43fb84ebfe8002c7992c3d5d3b3c9a81067c69c913b40e26cab6c57ab9 |
| outputs/input_deck.i | de5db3ed546fa505a151aa1636e776058b56002d56fe00182a5cf6c92ec6aa22 |
| outputs/job_script.sbatch | 2f0c7d8b5455debeb793d71989b9e278f21b9d7151d300afc79313d98091e533 |
| outputs/generated_config/interface.xml | 2f545669f80885d182291e9aad47d74baf8403082364f79f67542f653a616885 |
| outputs/generated_config/analyze_2_input_deck.xml | 062429a12242027c1f6ec7871f893ae120475fbd547f64840f9fcd0158a4a39c |
| outputs/generated_config/analyze_2_operations.xml | fbabf1a1c037533ce5dc1b1ba6a97ce9d70a795c1128735196a3e624aa73efa0 |
| outputs/generated_config/analyze_helmholtz_input_deck.xml | e0b190ab3e8c71334d7b7ec5f0567dbcdae40f7a371b943a553d6eb54fae5436 |
| outputs/generated_config/analyze_helmholtz_operations.xml | 402ffc30789914bd0c1c7bf429aa2f08ea22b0040960d015b9c71fd716404854 |
| outputs/generated_config/engine_input_deck.xml | 7f3edc06119d4155981b3861c2c2263f268e6a3f56f7577cc0aa202f3b35169a |
| outputs/generated_config/engine_operations.xml | c5b07640e3f1427a5f763631a2f7f9c3ec1ea54e97160106efe598afc0c67c1b |
| outputs/generated_config/mpirun.source | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| outputs/generated_config/xmlgenerator.log | 9fc113f16e3b84cc2928356da9d08e6e7bf5e7d2e71a6af1ae97a1681483cc9d |
| outputs/generated_config/generated_config_verification.json | 50dc66f6aa94f51c6dd5acd7f365f777f7d1fc59d217988829aa7fc242a3406c |
| outputs/generated_config/pre_submission_input_sha256.txt | b2c21b5a3eee9e64131fb0901b025eefa6ce7b3fa6ddd9e3eb0826a74a0929b8 |
| outputs/morphorm_oc_optimizer_diagnostics.txt | 5bf3294ab40a1a55925134eb0ef493c7cb725e0964ae54cb3ce1ee62ae18e4f4 |
| outputs/engine_output.exo | 1aaed1e511062be4f851104be922563fc2efbb3f735cf87f3db19a779c05f200 |
| outputs/final_analyze_output.exo (= work/run2/analyze_id_2_output_scenario_id_1/iteration50.exo) | 37e132d17c1295ccb662ebba04d6217e1dc77ac03c443ac32103cde40227dca0 |
| outputs/run_logs/morphorm_16167268.out | 8e440c7224e0dba8dbc5492e3e75765e5754f0d4cd4ffb967419a6230f394572 |
| outputs/run_logs/morphorm_16167268.err (empty) | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| outputs/run_logs/morphorm_run.log | 24f51bf3b88158d9283abd03eca2f99f5418a3726091ea5e77b1dfc81695f555 |
| outputs/run_logs/engine_1_0.log | 0251658e45de22150ad3d5052e7ad8107c075731e60eae010c11292552d6c5c7 |
| outputs/run_logs/analyze_2_1.log | 2887e623584622a47dbadad9c3e5b4f70be10979422e7ac342d88c71307f06d7 |
| outputs/run_logs/analyze_helmholtz_2.log | 6432b78e6dad6f712f0450665e5e6ef86aef8ea4aa81f40d786d6d93f19be932 |
| outputs/run_logs/opt_criteria_history.csv | fc58edec337c12168c1d4a61bd25900d1cc46c334323e0e1432061d82c9c24d0 |
| outputs/run_logs/iteration50_criteria_history.csv | fc58edec337c12168c1d4a61bd25900d1cc46c334323e0e1432061d82c9c24d0 |
| outputs/run_logs/result_verification.json | d6be8adcecfb4c6fb9208404bb8e3ff848721c2ec4183026eaedd75c0f4ef8ff |
| outputs/run_logs/sacct_16167268.txt | 0adfa672373e774a2c6aa66abbc00556427312780b17d76f096c2b194881fa9c |
| outputs/run_logs/cubit_mesh.log | 194f083187667eb998bbe894c10d5e28cd3a53115e6a2cba7cd271b4f1a6f9fe |
| outputs/.gitkeep (researcher placeholder, empty) | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |

No accepted deliverable was overwritten by a later attempt (each was written once, from the run2 artifacts).

## 7. Failures, retries, cancelled jobs, unresolved issues, deviations

- **Rejected translation attempt (work/run1, no job submitted).** The first deck declared the Helmholtz filter with a `begin filter 1 … end filter` block (`type helmholtz`, `radius_absolute 0.15`, `boundary_sticking_penalty 1.0`, `symmetry_plane_location_names ss_sym`) referenced by `filter_ids 1`. XMLGenerator exited 0 and emitted the length scale (0.043301) and surface length scale (1.0), but `analyze_helmholtz_input_deck.xml` contained no symmetry-plane sideset, which the specification's generated-configuration requirement forbids. The attempt is preserved in `work/run1/` (deck, generated files, `xmlgenerator.log`, failing `generated_config_verification.json`). It was never run.
- **Retry (work/run2, accepted).** Same deck with the filter expressed through the study-level keywords (the manual's documented equivalent form). Every other generated file is byte-identical to run1; the Helmholtz file now contains `Symmetry Plane Sides = {ss_sym}`. This is the configuration that job 16167268 executed.
- **Verifier correction (no effect on the run).** The first version of `work/scripts/verify_result.py` assumed an `iteration,objective,...` CSV layout, engine time-step labels equal to the iteration number, and underscore-style displacement names; the actual outputs use a one-row-per-criterion CSV, time steps 1–51 for iterations 0–50, and names `displacement X/Y/Z`. The script's expectations were corrected and it was re-run (all 12 checks pass); the run artifacts were not touched.
- **Cancelled jobs:** none. **Failed jobs:** none. One job was submitted in total.
- **Deviations from the specification:** none identified. The run reached the 50-iteration cap, every locked setting is present in the generated configuration, and no locked value was changed. The Helmholtz "Length Scale" value in the generated file (0.043301) is the generator's own conversion of the locked absolute radius 0.15 (R/(2√3)); the deck carries the locked value 0.15.
- **Unresolved issues:** none. Minor note: the cubit probe directory was first created under `work/manual_text/work/` because of a shell working-directory drift and was moved to `work/cubit_probe/` before any further work; nothing outside the trial root was touched.
- **Restricted material:** none sought or used.

## 8. Final artifact paths

- `outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`, `outputs/mesh_verification.txt`
- `outputs/input_deck.i`, `outputs/job_script.sbatch`
- `outputs/generated_config/{interface.xml, analyze_2_input_deck.xml, analyze_2_operations.xml, analyze_helmholtz_input_deck.xml, analyze_helmholtz_operations.xml, engine_input_deck.xml, engine_operations.xml, mpirun.source, xmlgenerator.log, generated_config_verification.json, pre_submission_input_sha256.txt}`
- `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`
- `outputs/run_logs/{morphorm_16167268.out, morphorm_16167268.err, morphorm_run.log, engine_1_0.log, analyze_2_1.log, analyze_helmholtz_2.log, opt_criteria_history.csv, iteration50_criteria_history.csv, result_verification.json, sacct_16167268.txt, cubit_mesh.log}`
- `outputs/SHA256SUMS.txt`
- `jobs/job_ids.txt` (16167268), `jobs/morphorm_ex8.sbatch`, `jobs/sacct_16167268.txt`; `logs/morphorm_16167268.out`, `logs/morphorm_16167268.err`
- `work/run_summary.md` (this file); working records: `work/mesh/`, `work/run1/` (rejected translation), `work/run2/` (accepted run directory with all 51 per-iteration analyze files), `work/scripts/` (verify_mesh.py, verify_generated_config.py, verify_result.py), `work/cubit_probe/`, `work/manual_text/`
