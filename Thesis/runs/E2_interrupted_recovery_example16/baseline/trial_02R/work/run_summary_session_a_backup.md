# Run Summary — trial `E2-example16-baseline-02R` (Session A: Stage 1 only)

**STATUS: Stage 1 is COMPLETE and verified. Stage 2 has NOT been started** (no Stage-2 deck, job script or job was
created, translated, submitted or run in this session, as instructed by the Session-A prompt).

All paths below are relative to the trial root
`/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_02R` unless absolute.
All timestamps are UTC. Session A ran on the agent-host Slurm allocation `SLURM_JOB_ID=16163810`.

## 1. Trial identifier and assigned workflow

| Item | Value |
|---|---|
| Trial identifier (`THESIS_TRIAL_ID`) | `E2-example16-baseline-02R` |
| Frozen configuration | `FROZEN-EX16-v1`, SHA-256 `a67d6cba7f0ce35ae6dc227f33b39056514be9494d6e15bc8e58524dfba1a86b`; `sha256sum -c agent_inputs/FROZEN_CONFIG_FILES.sha256` → all 12 files OK (checked 2026-10-09 ~19:04Z) |
| Workflow | Full cantilever, two-stage restart (warm-start) workflow EX16: Stage 1 = 20 OC iterations from uniform density 0.15 with restart-file writing; Stage 2 = 40 further iterations resuming from the iteration-20 `control` field |
| Session | Session A — construct the workflow, run and verify Stage 1 only, then stop |
| Software | approved interface `source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh` → modules `chpc/1.0, gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8` (module list recorded in the job stdout `logs/stage1_16164110.out`) |
| Documentation used | only `agent_inputs/manuals/Morphorm_User_Manual.pdf` and `Morphorm_Theory_Manual.pdf` (text extracted with `pdftotext -layout` into `work/manual_text/` for reading) |

## 2. Mesh

**Generation.** Coreform Cubit 2026.8 in batch mode on the agent host (permitted by `compute_resources.md`):

```
cd work/mesh
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
cubit -batch -nographics -nojournal -input mesh.jou > cubit_mesh.log 2>&1     # exit 0
```
Timestamps: `MESH_GEN_START_UTC=2026-10-09T19:06:25Z`, `MESH_GEN_END_UTC=2026-10-09T19:06:28Z` (`work/mesh/mesh_cubit_timestamps.txt`).

Journal `work/mesh/mesh.jou` (deliverable copy `outputs/mesh.jou`): `brick x 2 y 1 z 1`, moved by (1, 0.5, 0.5) so the
corner is at the origin; curves of length 2 → 48 intervals, curves of length 1 → 24 intervals; `volume 1 scheme map`;
`mesh volume 1`; `block 1 add volume 1`, `block 1 name "block_1"`, `block 1 element type HEX8`;
`nodeset 1 add surface in volume 1 with x_coord < 0.001` → `ns_fix`; `nodeset 2 add curve in volume 1 with x_coord > 1.999 and y_coord < 0.001` → `ns_load`;
`export mesh ".../work/mesh/mesh.exo" dimension 3 overwrite`. No sidesets.

**Files.** `work/mesh/mesh.exo` (copied unmodified to `outputs/mesh.exo` and to the run directory `work/stage1/run/mesh.exo`),
SHA-256 `f909589b0e29bc5e99d52bd578c755e7a5f3cf8c2e88883b13994cbdfbe032f8`; Cubit log `work/mesh/cubit_mesh.log`.

**Verification** (`python3 -I work/scripts/verify_mesh.py work/mesh/mesh.exo work/mesh/mesh_verification.json`, runtime python3/netCDF4,
verified 2026-10-09T19:07:11Z; record `outputs/mesh_verification.json`; 20/20 checks pass):

| Quantity | Locked | Observed |
|---|---|---|
| Elements / nodes | 27,648 / 30,625 | 27,648 / 30,625 |
| Element type | HEX8 structured | HEX8, 8 nodes/elem, 49×25×25 unique coordinates (48×24×24 grid) |
| Edge length | h = 1/24 = 0.0416667 uniform | min 0.0416666666667, max 0.0416666666667 (all edges within 1e-9 of 1/24) |
| Bounding box | [0,2]×[0,1]×[0,1] | x [0.0, 2.0], y [0.0, 1.0], z [0.0, 1.0] |
| Element blocks | one, `block_1`, all elements | 1 block, id 1, name `block_1`, 27,648 elements |
| `ns_fix` | all nodes on x = 0 (625) | 625 nodes, x_min = x_max = 0.0, = every node with x = 0 |
| `ns_load` | edge x = 2, y = 0, z ∈ [0,1] (25) | 25 nodes, x = 2.0, y = 0.0, z ∈ [0.0, 1.0], = every node with x = 2 & y = 0 |
| Sidesets | none required | 0 |

## 3. Input deck and generated runtime configuration (Stage 1)

**Deck:** `work/stage1/input_deck.i` (deliverable copy `outputs/stage1/input_deck.i`, SHA-256 `7028aafa1c050dc2a7d1a6a3080bf3ab1c9892ae2b376d4625cb7bdc8fa5afe9`).
**Translation** (`work/stage1/run`): `XMLGenerator input_deck.i > xmlgenerator.log 2>&1` (exit 0), `XMLGEN_START_UTC=2026-10-09T19:09:15Z`.
Generated files (deliverable copies in `outputs/stage1/generated_config/`): `interface.xml`, `engine_input_deck.xml`, `engine_operations.xml`,
`analyze_2_input_deck.xml`, `analyze_2_operations.xml`, `analyze_helmholtz_input_deck.xml`, `analyze_helmholtz_operations.xml`, `mpirun.source`, plus `xmlgenerator.log`.
**Generated-configuration verification:** `python3 -I work/scripts/verify_generated_config.py work/stage1/run 1 work/stage1/generated_config_verification.json`
at 2026-10-09T19:10:40Z → **56/56 checks pass** (record `outputs/stage1/verification/generated_config_verification.json`, includes SHA-256 of each generated file).

| Locked setting | Deck (input_deck.i) | Where it appears in the generated configuration |
|---|---|---|
| Engine + analyze services, 1 processor each, single-rank performers, no decomposition | `service 1 code engine number_processors 1`; `service 2 code analyze number_processors 1` | `interface.xml` Performers `engine_1` (engine), `analyze_2` (analyze), `analyze_helmholtz` (analyze, auto-wired Helmholtz filter service); `mpirun.source`: three `-np 1` launches (`PlatoMain`, `analyze_MPMD` ×2) |
| `update_problem true`, `update_problem_frequency 1` on engine service | in `service 1` | `engine_operations.xml` `<Function>Update Problem</Function> <UpdateProblemFrequency>1`; `interface.xml` `<ProblemUpdateFrequency>1`, `UpdateProblemStage` = `Update Problem` |
| Mechanical, 3-D | `scenario 1 type mechanical dimensions 3` | `analyze_2_input_deck.xml` Physics `Mechanical`, PDE Constraint `Elliptic`, Spatial Dimension 3 |
| Material E = 1.0, ν = 0.3 on `block_1` | `material 1 isotropic_elastic youngs_modulus 1.0 poissons_ratio 0.3`; `block 1 name block_1 material_id 1` | `analyze_2_input_deck.xml` Material Models/material_1/Isotropic Linear Elastic: Youngs Modulus 1.0, Poissons Ratio 0.3; Spatial Model/Domains/block_1 → material_1 |
| Fixed support `ns_fix`, u_x = u_y = u_z = 0 | `boundary_condition 1 fixed_value nodeset ns_fix dispx dispy dispz 0 0 0` | `analyze_2_input_deck.xml` Essential Boundary Conditions: three Fixed Value entries, Index 0/1/2, Sides `ns_fix`, Value 0.0 |
| Concentrated load, direction y, −1.0 per node on `ns_load`; no other loads | `load 1 concentrated_load nodeset ns_load direction y value -1.0` | `analyze_2_input_deck.xml` Concentrated Loads: Dof 1, Value −1.0, Nodes `ns_load`; `Mechanical Natural Boundary Conditions` empty |
| Objective: weighted sum, single compliance criterion, weight 1, analyze service | `criterion 1 mechanical_compliance`; `objective 1 weighted_sum criterion_ids 1 service_ids 2 scenario_ids 1 weights 1` | `analyze_2_input_deck.xml` Criteria/My Objective: Scalar Function Type `Internal Elastic Energy`; `engine_operations.xml` Aggregator Weighting Value 1; `interface.xml` stages `Compute Objective Value/Gradient` on `analyze_2` |
| Constraint volume ≤ 15 %, `less_than`, engine service | `constraint 1 criterion_id 2 (volume) relative_target 0.15 type less_than service_id 1` | `interface.xml` Constraint `NormalizedTargetValue 0.15`, `ReferenceValueName Design Volume`; `engine_operations.xml` `ComputeVolume` (Compute Constraint Value/Gradient 1) on `engine_1` |
| Density discretization, uniform initial density 0.15 | `study discretization density initialize_method uniform initial_density_value 0.15` | `engine_operations.xml` InitializeField Method Uniform Value 0.15; SetLower/UpperBounds Discretization density; `interface.xml` BoundConstraint 0.0–1.0 |
| SIMP single phase, exponent 3.0, minimum 1e-3; compliance criterion `minimum_ersatz_material_value 1e-3` | `material_interpolation 1 single_phase simp penalty_exponent 3.0 minimum_value 1e-3` (on residual 1); `criterion 1 material_penalty_exponent 3.0 minimum_ersatz_material_value 1e-3` | `analyze_2_input_deck.xml` Residual/Mechanical Residual: Material Interpolation Model Single-Phase, Penalty Function SIMP Exponent 3.0 Minimum Value 1e-3; Criteria/My Objective/Penalty Function SIMP Exponent 3.0 Minimum Value 1e-3 |
| OC optimizer, default tolerances | `optimization_algorithm oc` (no tolerance keywords) | `interface.xml` Optimizer Package `OC`, OCControlStagnationTolerance 1e-4, OCObjectiveStagnationTolerance 1e-8, OCGradientTolerance 1e-8 (runtime defaults) |
| `normalize_in_aggregator false` | in `study` | `engine_operations.xml` Aggregator has no `Normals` input (probe translation with `true` adds `Normals`/`Initial Criterion Value`; see §7) |
| Helmholtz filter, absolute radius 0.15, boundary-sticking penalty 1.0, no symmetry plane | `filter 1 type helmholtz radius_absolute 0.15 boundary_sticking_penalty 1.0`; `study filter_ids 1` | `analyze_helmholtz_input_deck.xml` Physics `Helmholtz Filter`: **Length Scale 0.043301** = 0.15/(2√3) (XMLGenerator's radius→ℓ_Ω conversion; probe with radius 0.30 gives 0.086603), **Surface Length Scale 1.0** (= ℓ_Γ, probe with 0.5 gives 0.5); no symmetry sidesets |
| Iteration cap Stage 1 = 20 | `max_iterations 20` | `interface.xml` `<MaxIterations>20`; `engine_operations.xml` PlatoMainOutput `<MaxIterations>20` |
| Restart-file writing, control + topology saved every iteration | `write_restart_file true`, `isosurface_output_frequency 1` | `engine_operations.xml` PlatoMainOutput `<WriteRestart>true`, `<OutputFrequency>1`, Inputs `topology` and `control` (Nodal Field); `engine_input_deck.xml` output file `engine_output` (exodus) |
| Output dispx dispy dispz from analyze | `output 1 service_id 2 data dispx dispy dispz` | `analyze_2_input_deck.xml` Output/Plottable `{displacement_x, displacement_y, displacement_z}`; `analyze_2_operations.xml` Visualization OutputFrequency 1 |
| Mesh | `mesh 1 name mesh.exo` | `engine_input_deck.xml` `<mesh>mesh.exo`; both analyze decks `Input Mesh mesh.exo` |
| Stage 1 is a fresh start (not a restart) | no `restart_iteration`/`initial_guess_*` keywords (XMLGenerator log: `restart_iteration` default 0) | `engine_operations.xml` Initialize Field uses `Uniform`, no file-based initial guess |

**Decisions / assumptions made while writing the deck**
- `verbose true` in the study block (console logging only; adds `<Console><Verbose>true` to `interface.xml`). Not a locked quantity.
- The constraint block omits `scenario_id` (optional for `volume` per the manual §4.3.1) because the volume is evaluated by the engine service as locked. The generated shared-data name is therefore `criterion_2_service_1_scenario_` (harmless).
- Both the residual (`material_interpolation 1`) and the compliance criterion carry explicit SIMP exponent 3.0 / minimum 1e-3 so the generated configuration shows the locked values explicitly; 3.0 equals the runtime default.
- **Output frequency:** the first translation (kept as `work/stage1/attempt1_outputfreq5_generated_config/`, 2026-10-09T19:07:34Z) produced `PlatoMainOutput <OutputFrequency>5`, which would not have saved every iteration. Probe translations (`work/stage1/xmlgen_probes/`) showed that `output_frequency 1` in the output block does not change it and that `output_frequency` in the study block is rejected ("not recognized … IGNORED"), while the study-level keyword `isosurface_output_frequency 1` — named by XMLGenerator itself in its log ("Using default value of 5 for parameter isosurface_output_frequency") — sets `<OutputFrequency>1`. The deck was re-translated with that keyword before anything was submitted; the 5-frequency configuration was never run.
- No OpenMP threading variables were set: `ldd` of `analyze_MPMD`/`PlatoMain` shows no OpenMP library (serial Kokkos), and `mpirun.source` already contains `--oversubscribe`, so the three single-rank performers run inside the 1-task × 8-CPU allocation without modification.

## 4. Execution

Commands (agent host unless noted), in order:
```
sha256sum -c agent_inputs/FROZEN_CONFIG_FILES.sha256                                   # all OK
pdftotext -layout agent_inputs/manuals/Morphorm_User_Manual.pdf work/manual_text/user_manual.txt
pdftotext -layout agent_inputs/manuals/Morphorm_Theory_Manual.pdf work/manual_text/theory_manual.txt
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
(cd work/mesh && cubit -batch -nographics -nojournal -input mesh.jou > cubit_mesh.log 2>&1)        # 19:06:25Z–19:06:28Z, rc 0
python3 -I work/scripts/verify_mesh.py work/mesh/mesh.exo work/mesh/mesh_verification.json        # 19:07:11Z, 20/20 pass
cp work/mesh/mesh.exo work/stage1/run/mesh.exo ; cp work/stage1/input_deck.i work/stage1/run/
(cd work/stage1/run && XMLGenerator input_deck.i > xmlgenerator.log 2>&1)                          # attempt 1, 19:07:34Z, rc 0 (OutputFrequency 5 → superseded)
(cd work/stage1/xmlgen_probes/<radius030|sticking05|normalize_true|outfreq1|study_outfreq1|study_isofreq1> && XMLGenerator input_deck.i)   # keyword-mapping probes, never run
(cd work/stage1/run && rm -f *.xml mpirun.source && XMLGenerator input_deck.i > xmlgenerator.log 2>&1)   # final, 19:09:15Z, rc 0
python3 -I work/scripts/verify_generated_config.py work/stage1/run 1 work/stage1/generated_config_verification.json   # 19:10:40Z, 56/56 pass
sbatch jobs/stage1_job_script.sbatch                                                               # 19:11:01Z → "Submitted batch job 16164110"
squeue -j 16164110 ... (polled until the job left the queue)
sacct -j 16164110 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P > jobs/sacct_16164110.txt
python3 -I work/scripts/verify_stage1_results.py work/stage1/run work/stage1/stage1_results_verification.json   # 19:32:32Z, 16/16 pass
cp ... outputs/ (see §8) ; (cd outputs && find . -type f ! -name SHA256SUMS.txt | sort | xargs sha256sum > SHA256SUMS.txt && sha256sum -c SHA256SUMS.txt)
```
Inside the job (script `jobs/stage1_job_script.sbatch`, deliverable copy `outputs/stage1/job_script.sbatch`; `--chdir work/stage1/run`):
`source …/load_approved_software.sh; module list; bash mpirun.source > morphorm_stage1.log 2>&1` (Morphorm runs only on the compute node, never on the agent host).

| Slurm job | Script | Purpose | State | ExitCode | Submit → Start → End (UTC) | Elapsed | Node | AllocCPUS / ReqMem / MaxRSS |
|---|---|---|---|---|---|---|---|---|
| **16164110** (`ex16_stage1`) | `jobs/stage1_job_script.sbatch` | Stage 1, resources exactly `account=hochhalter-np partition=hochhalter-np nodes=1 ntasks=1 cpus-per-task=8 mem=32G time=02:00:00`, no GPU | COMPLETED | 0:0 (`MORPHORM_RC=0`) | 19:11:01Z → 19:11:12Z → 19:29:51Z | 00:18:39 | notch272 | 8 / 32G / 2,316,192 K |

`jobs/job_ids.txt` contains the single line `16164110` (the only job submitted in this trial; nothing failed or was cancelled).
Scheduler stdout/stderr: `logs/stage1_16164110.out` (includes `module list`, input-file SHA-256s, `MORPHORM_START_UTC=2026-10-09T19:11:20Z`, `MORPHORM_END_UTC=2026-10-09T19:29:51Z`), `logs/stage1_16164110.err` (empty). Accounting: `jobs/sacct_16164110.txt`.

## 5. Completed stages and iteration counts

**Stage 1: COMPLETE.** The OC optimizer ran iterations 0–20 (21 diagnostics rows, 21 function evaluations) and stopped at the
iteration cap with the message `****** Optimization stopping due to exceeding maximum number of iterations. ******`
(`outputs/stage1/morphorm_oc_optimizer_diagnostics.txt`). Stage-1 objective (compliance F(X)) and constraint H1(X) history:

| Iter | F(X) compliance | Norm(F') | H1(X) | abs(dX) |
|---|---|---|---|---|
| 0 | 4.893235e+06 | 5.288704e+05 | −1.564817e−02 | 1.5e−01 |
| 1 | 8.715305e+05 | 1.190725e+05 | 9.426307e−02 | 2.0e−01 |
| 2 | 9.153247e+05 | 7.076490e+04 | 4.184032e−02 | 2.0e−01 |
| 3 | 5.932948e+05 | 3.922089e+04 | 4.846958e−02 | 2.0e−01 |
| 4 | 7.157917e+05 | 5.052073e+04 | 1.676062e−02 | 2.0e−01 |
| 5 | 5.716814e+05 | 3.791666e+04 | 1.721705e−02 | 2.0e−01 |
| 6 | 6.161091e+05 | 4.085972e+04 | −4.378164e−13 | 2.0e−01 |
| 7 | 5.220660e+05 | 3.312145e+04 | −6.858403e−14 | 2.0e−01 |
| 8 | 4.470169e+05 | 2.693147e+04 | −2.564338e−13 | 2.0e−01 |
| 9 | 3.893516e+05 | 2.243726e+04 | −3.237688e−13 | 2.0e−01 |
| 10 | 3.481402e+05 | 1.935145e+04 | 6.715462e−13 | 2.0e−01 |
| 11 | 3.179639e+05 | 1.725104e+04 | 5.812573e−13 | 2.0e−01 |
| 12 | 2.957322e+05 | 1.572357e+04 | −3.227973e−14 | 2.0e−01 |
| 13 | 2.794783e+05 | 1.464060e+04 | 5.512257e−14 | 2.0e−01 |
| 14 | 2.674795e+05 | 1.385789e+04 | −5.665746e−13 | 2.0e−01 |
| 15 | 2.585237e+05 | 1.328678e+04 | −7.141510e−14 | 2.0e−01 |
| 16 | 2.516773e+05 | 1.285511e+04 | −1.626754e−13 | 2.0e−01 |
| 17 | 2.464064e+05 | 1.252720e+04 | 4.223843e−13 | 2.0e−01 |
| 18 | 2.422601e+05 | 1.227652e+04 | −3.567702e−13 | 2.0e−01 |
| 19 | 2.388394e+05 | 1.207748e+04 | 4.834189e−13 | 2.0e−01 |
| **20** | **2.360040e+05** (= 2.3600395811001546e+05 in `opt_criteria_history.csv`) | 1.191537e+04 | 3.964884e−13 | 2.0e−01 |

(The authoritative values are in the diagnostics file. `opt_criteria_history.csv` holds the same 21 objective values on one line labelled `My Objective`.)

**Checkpoint (preserved, unmodified):** `outputs/stage1/engine_output.exo`, SHA-256 `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8`
(byte-identical to the original `work/stage1/run/engine_output.exo`). Verified with the runtime's netCDF4 (`outputs/stage1/verification/stage1_results_verification.json`, 16/16 checks):
21 time steps (time values 1.0 … 21.0 ↔ optimizer iterations 0 … 20, i.e. **time step k+1 holds iteration k; the iteration-20 design is time step 21, the last one**),
nodal variables `control` and `topology` on the 30,625-node / 27,648-element mesh; time-step 1 `control` is uniformly 0.15 (the initial design); every
consecutive saved `control` state differs (max change 0.2 = OC move limit); all `control` values finite and in [0, 1].
Note for Stage 2: the restart must read the **`control`** field at the **iteration-20** saved state (the 21st and last time step), and its first evaluated
compliance must equal the Stage-1 iteration-20 value **2.3600395811001546e+05**.

**Stage 2: NOT STARTED.** No Stage-2 input deck, generated configuration, job script, job, `outputs/stage2/` directory or
continuation evidence exists. Everything Stage 2 needs is persistent: the checkpoint above, `outputs/mesh.exo`, the Stage-1 deck
(`outputs/stage1/input_deck.i`) and the Stage-1 compliance history.

**Final analyze output (iteration 20):** `outputs/stage1/final_analyze_output.exo` = copy of
`work/stage1/run/analyze_id_2_output_scenario_id_1/iteration20.exo` (SHA-256 `1baf67b8cb33f9878f9d64e92529248ab924c4b04f32a6ba9500526c40aa116d`);
nodal variables `Topology`, `displacement X`, `displacement Y`, `displacement Z`. Per-iteration analyze files `iteration0.exo … iteration20.exo` remain in the run directory.

## 6. Key output files and SHA-256 (full manifest: `outputs/SHA256SUMS.txt`, 30 entries, `sha256sum -c` OK)

| Deliverable (locked path) | SHA-256 |
|---|---|
| `outputs/mesh.jou` | `31c4b35c37a8b7122a98f2d45a04543d8831b1cd6dff6ffd0345f9938953a6a3` |
| `outputs/mesh.exo` | `f909589b0e29bc5e99d52bd578c755e7a5f3cf8c2e88883b13994cbdfbe032f8` |
| `outputs/mesh_verification.json` | `de9d66709f1849d65dffb5b91502f8a1bf42060978cb9b94c956d0718bd9c25d` |
| `outputs/stage1/input_deck.i` | `7028aafa1c050dc2a7d1a6a3080bf3ab1c9892ae2b376d4625cb7bdc8fa5afe9` |
| `outputs/stage1/job_script.sbatch` | `3a28889426fc3901cef9d8dec0f31f5ca754e094a0219efad808c80ed0689b34` |
| `outputs/stage1/generated_config/interface.xml` | `833efef281919bb7a4a9c067ebe6c0714fd98a40972196a3b83f83011e5bc00f` |
| `outputs/stage1/generated_config/engine_input_deck.xml` | `7f3edc06119d4155981b3861c2c2263f268e6a3f56f7577cc0aa202f3b35169a` |
| `outputs/stage1/generated_config/engine_operations.xml` | `09dabcc015dd9e0ab88dbe54a8a2f0496ff19b9abfe94bf5c46107d6238fa40d` |
| `outputs/stage1/generated_config/analyze_2_input_deck.xml` | `a6f7d5bf3d61607bec82781d3afad5231a493e602331ea7a3b54f7e9b3c162d5` |
| `outputs/stage1/generated_config/analyze_2_operations.xml` | `fbabf1a1c037533ce5dc1b1ba6a97ce9d70a795c1128735196a3e624aa73efa0` |
| `outputs/stage1/generated_config/analyze_helmholtz_input_deck.xml` | `c813b81a2c43cbac181b51c3ae12cad319473e7c2725afd29c2637fedec2dcbf` |
| `outputs/stage1/generated_config/analyze_helmholtz_operations.xml` | `402ffc30789914bd0c1c7bf429aa2f08ea22b0040960d015b9c71fd716404854` |
| `outputs/stage1/generated_config/mpirun.source` | `5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc` |
| `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt` | `4aaeaa78e77e9f065e3e0ab91d0205a13cdf600a7c76d9f8fc492b06092772f1` |
| `outputs/stage1/engine_output.exo` (checkpoint) | `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8` |
| `outputs/stage1/final_analyze_output.exo` | `1baf67b8cb33f9878f9d64e92529248ab924c4b04f32a6ba9500526c40aa116d` |
| `outputs/stage1/run_logs/stage1_16164110.out` | `d97a2653ec0ad7b9162ef02915920aa1fc4aa681dd66cca66836b8d9f341e7cf` |
| `outputs/stage1/run_logs/morphorm_stage1.log` | `597b2a213ac90ef023b31aa8b56f825f7ba4ab3ec5dfbcbd43794c8a07ccec9a` |
| `outputs/stage1/verification/generated_config_verification.json` | `65fde354e4544032f5b31658c78ef4a75bd707f2f87847e26538e10cffc23dba` |
| `outputs/stage1/verification/stage1_results_verification.json` | `20b5c7f9e24053b8f8745c90b3ec399bdee90071056eeb6672ef30910a946951` |

The job stdout also records the SHA-256 of every input file as seen on the compute node at run time (identical to the manifest values above).

## 7. Failures, retries, cancelled jobs, unresolved issues, deviations

- **Jobs:** one submission (16164110), COMPLETED, exit 0. No failed, re-run or cancelled jobs.
- **Translation retry (before submission, no deliverable overwritten):** first XMLGenerator pass gave engine `OutputFrequency 5`; fixed by adding
  `isosurface_output_frequency 1` to the study block and re-translating (details in §3). The first-attempt files are kept in
  `work/stage1/attempt1_outputfreq5_generated_config/`; the keyword probes are in `work/stage1/xmlgen_probes/` (translation only, never executed).
- **Script fixes (verification tooling only):** `verify_mesh.py` first failed on JSON serialisation of numpy booleans (fixed, re-run); `verify_stage1_results.py`
  first flagged three checks that were artefacts of the script (displacement field names are `displacement X/Y/Z` not `dispx`; the criteria CSV is a single
  comma-separated line; `engine_restart.exo` check) — corrected and re-run, 16/16 pass. The run outputs were not changed.
- **Observation (not a deviation from the specification):** although `write_restart_file true` is set (and `<WriteRestart>true` is in the generated
  `engine_operations.xml`), the runtime did not write a separate `engine_restart.exo` file described in the User Manual §2.5.10. The specification defines
  the checkpoint as the engine output file `engine_output.exo`, which was written with all 21 saved states (`control`, `topology`), so the locked
  Stage-1 requirement is met. Stage 2 should read the checkpoint copy (`outputs/stage2/restart_input.exo`) as the manual allows (`initial_guess_file_name`
  may be the `engine_output.exo` of a previous run).
- **Non-locked keywords used:** `verbose true` (console output) and `isosurface_output_frequency 1` (engine output every iteration, required to satisfy the
  locked "21 saved states"). The latter keyword is not described in the manual; its name and default were reported by the approved XMLGenerator itself.
- **Deviations from the locked specification:** none.
- **Unresolved issues:** none for Stage 1. Stage 2 deliberately not started (session scope).

## 8. Final artifact paths

```
outputs/mesh.jou                                   outputs/stage1/generated_config/{interface.xml, engine_input_deck.xml,
outputs/mesh.exo                                       engine_operations.xml, analyze_2_input_deck.xml, analyze_2_operations.xml,
outputs/mesh_verification.json                         analyze_helmholtz_input_deck.xml, analyze_helmholtz_operations.xml,
outputs/stage1/input_deck.i                            mpirun.source, xmlgenerator.log, xmlgenerator_timestamps.txt}
outputs/stage1/job_script.sbatch                   outputs/stage1/run_logs/{stage1_16164110.out, stage1_16164110.err, morphorm_stage1.log,
outputs/stage1/morphorm_oc_optimizer_diagnostics.txt   engine_1_0.log, analyze_2_1.log, analyze_helmholtz_2.log, opt_criteria_history.csv,
outputs/stage1/engine_output.exo   (CHECKPOINT)        iteration20_criteria_history.csv, sacct_16164110.txt}
outputs/stage1/final_analyze_output.exo            outputs/stage1/verification/{generated_config_verification.json, stage1_results_verification.json}
outputs/SHA256SUMS.txt                             jobs/job_ids.txt, jobs/stage1_job_script.sbatch, jobs/sacct_16164110.txt, jobs/submissions.log
logs/stage1_16164110.out, logs/stage1_16164110.err
work/run_summary.md (this file)
work/mesh/{mesh.jou, mesh.exo, cubit_mesh.log, mesh_verification.json, mesh_cubit_timestamps.txt}
work/stage1/input_deck.i ; work/stage1/run/ (complete Stage-1 run directory incl. analyze_id_2_output_scenario_id_1/iteration{0..20}.exo)
work/stage1/{generated_config_verification.json, stage1_results_verification.json, attempt1_outputfreq5_generated_config/, xmlgen_probes/}
work/scripts/{verify_mesh.py, verify_generated_config.py, verify_stage1_results.py} ; work/manual_text/ (pdftotext extracts of the two manuals)
```
Not present (by design of this session): `outputs/stage2/*`. **Stage 1 complete; Stage 2 not started.**
