# Run Summary — trial `E2-example16-baseline-02R` (Session A: Stage 1; Session B: recovery + Stage 2)

**STATUS: Stage 1 COMPLETE and verified (Session A). Stage 2 COMPLETE and verified (Session B): 40 further OC iterations
from the Stage-1 iteration-20 `control` design, overall iteration 60 reached, seamless-restart evidence recorded. All locked
deliverables are in place under `outputs/` and covered by `outputs/SHA256SUMS.txt`.**

All paths below are relative to the trial root
`/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_02R` unless absolute.
All timestamps are UTC. Session A ran on the agent-host Slurm allocation `SLURM_JOB_ID=16163810`; Session B (a new headless
Claude Code process with no record of Session A) ran on allocation `SLURM_JOB_ID=16164782` (started 2026-10-09 ~19:34Z).
Session B's additions are marked **[Session B]**; Session A's text is preserved unchanged except where it stated that Stage 2 had not started.
A verbatim copy of the Session-A summary is kept as `work/run_summary_session_a_backup.md`.

**[Session B] Recovery assessment (what was found before continuing).** From the persistent files alone: `work/run_summary.md` stated
Stage 1 complete / Stage 2 not started; `jobs/job_ids.txt` held one job (16164110, COMPLETED 0:0 per `jobs/sacct_16164110.txt`);
`outputs/SHA256SUMS.txt` (30 entries) verified with `sha256sum -c` (all OK) and covered every file under `outputs/`; the frozen inputs verified
against `agent_inputs/FROZEN_CONFIG_FILES.sha256` (12/12 OK); the Stage-1 deck, job script and checkpoint in `outputs/` were byte-identical
to their `work/` originals; the diagnostics showed iterations 0–20 with the iteration-cap stopping message; the checkpoint
`outputs/stage1/engine_output.exo` (SHA-256 `58dee776…5a07e8`) was re-read with the runtime's netCDF4: 21 time steps (1.0…21.0), nodal fields
`control`/`topology`, step 1 uniform 0.15. No `outputs/stage2/` existed. Conclusion: Stage 1 fully complete and verified, nothing to repeat;
Session B continued at the Stage-2 deck.

## 1. Trial identifier and assigned workflow

| Item | Value |
|---|---|
| Trial identifier (`THESIS_TRIAL_ID`) | `E2-example16-baseline-02R` |
| Frozen configuration | `FROZEN-EX16-v1`, SHA-256 `a67d6cba7f0ce35ae6dc227f33b39056514be9494d6e15bc8e58524dfba1a86b`; `sha256sum -c agent_inputs/FROZEN_CONFIG_FILES.sha256` → all 12 files OK (checked 2026-10-09 ~19:04Z) |
| Workflow | Full cantilever, two-stage restart (warm-start) workflow EX16: Stage 1 = 20 OC iterations from uniform density 0.15 with restart-file writing; Stage 2 = 40 further iterations resuming from the iteration-20 `control` field |
| Session | Session A — construct the workflow, run and verify Stage 1 only, then stop. **[Session B]** — recover from the persistent trial root, verify Stage 1, construct/verify/run Stage 2 (continuation), produce all remaining deliverables |
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

### 3b. [Session B] Input deck and generated runtime configuration (Stage 2, continuation)

**Deck:** `work/stage2/input_deck.i` (deliverable copy `outputs/stage2/input_deck.i`, SHA-256 `5300072ceaffa0c4dc3db41da1b073527917f0a59084d485855578b42b45ed19`).
It is the Stage-1 deck with exactly these changes in the `study` block (everything else byte-identical, verified by `diff`):
`max_iterations 20` → `max_iterations 40`; `initialize_method uniform` / `initial_density_value 0.15` replaced by the restart keywords of
User Manual §2.5.10: `initial_guess_file_name restart_input.exo`, `initial_guess_field_name control`, `restart_iteration 21`
(`write_restart_file true` and `isosurface_output_frequency 1` kept so Stage 2 also saves `control`/`topology` every iteration).
A translation probe showed that keeping `initialize_method uniform` alongside the restart keywords changes nothing in the generated
configuration (`work/stage2/xmlgen_probes/ri20_keep_uniform`), so the uniform keywords were dropped for clarity.

**Restart input:** `work/stage2/run/restart_input.exo` = `cp outputs/stage1/engine_output.exo` (deliverable copy `outputs/stage2/restart_input.exo`),
SHA-256 `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8` = the checkpoint, unmodified. Mesh: `cp outputs/mesh.exo work/stage2/run/mesh.exo`
(SHA-256 `f909589b…032f8`, same mesh as Stage 1).

**Translation** (`work/stage2/run`): `XMLGenerator input_deck.i > xmlgenerator.log 2>&1` (exit 0), `XMLGEN_START_UTC=2026-10-09T19:40:18Z`
(`work/stage2/run/xmlgenerator_timestamps.txt`). Generated files (deliverable copies in `outputs/stage2/generated_config/`): the same eight files as Stage 1 plus
`xmlgenerator.log`, `xmlgenerator_timestamps.txt`. `diff` against the Stage-1 generated configuration shows **only** these differences:
`interface.xml` `<MaxIterations>20</MaxIterations>` → `40`; `engine_operations.xml` PlatoMainOutput `<MaxIterations>40` and a new
`<RestartFieldName>control</RestartFieldName>`; `Initialize Field` operation `Method Uniform/Value 0.15` → `Method FromFieldOnInputMesh` with
`<Name>restart_input.exo</Name> <VariableName>control</VariableName> <Iteration>21</Iteration>`. The analyze decks (material, SIMP, load, BCs, output),
Helmholtz deck (Length Scale 0.043301, Surface Length Scale 1.0), engine input deck and `mpirun.source` are byte-identical to Stage 1 (same SHA-256 as in §6).

**Generated-configuration verification:** `python3 -I work/scripts/verify_generated_config.py work/stage2/run 2 work/stage2/generated_config_verification.json 21`
at 2026-10-09T19:40:18Z → **60/60 checks pass** (record `outputs/stage2/verification/generated_config_verification.json`). The script is Session A's, extended in
Session B with six Stage-2 checks: Initialize Field method `FromFieldOnInputMesh`; source file `restart_input.exo`; field `control` (not `topology`);
`<Iteration>` = 21 (expected value passed as argument); `RestartFieldName control`; `restart_input.exo` byte-identical to `outputs/stage1/engine_output.exo`.
All Stage-1 locked-setting checks (filter length scales, material, SIMP, load, BCs, OC defaults, `normalize_in_aggregator false`, update-problem frequency 1,
single-rank performers, output fields) are re-applied to the Stage-2 configuration and pass; `MaxIterations` is checked as 40 in both `interface.xml` and `engine_operations.xml`.

| Locked Stage-2 setting | Deck | Generated configuration |
|---|---|---|
| Resume from the iteration-20 design | `restart_iteration 21` (see below for why 21) | `engine_operations.xml` Initialize Field `<Iteration>21</Iteration>` = checkpoint time step 21 = optimizer iteration 20 (last saved state) |
| Read the `control` field (not `topology`) | `initial_guess_field_name control` | `<VariableName>control</VariableName>`; PlatoMainOutput `<RestartFieldName>control</RestartFieldName>` |
| Read a copy of the checkpoint | `initial_guess_file_name restart_input.exo` | `<Name>restart_input.exo</Name>`; file SHA-256 = checkpoint SHA-256 |
| `max_iterations 40` | `max_iterations 40` | `interface.xml` `<MaxIterations>40`; `engine_operations.xml` PlatoMainOutput `<MaxIterations>40` |
| Everything else identical to Stage 1 | unchanged deck blocks | all other generated files byte-identical to Stage 1 |

**Decision — which `restart_iteration` value selects the iteration-20 design.** The manual defines `restart_iteration` as "which iteration (time step) in the
initial guess file", while the checkpoint stores iteration k at Exodus time step k+1 (Session A, §5). Translation probes (`work/stage2/xmlgen_probes/ri20`, `ri21`,
translation only) showed XMLGenerator passes the value through verbatim as `<Iteration>`, so the manual/generated configuration cannot resolve the convention.
Rather than risk a full 40-iteration run from the wrong state, two 1-iteration probe jobs (identical Stage-2 configuration except `max_iterations 1`; frozen
resources; approved interface) were submitted on compute nodes before Stage 2: job 16164869 (`restart_iteration 20`) → first F(X) **2.388394e+05 = Stage-1 iteration 19**
(wrong state; its iteration 1 then gave 2.360040e+05, exactly the Stage-1 iteration-20 value, confirming a one-step offset); job 16164870 (`restart_iteration 21`) →
first F(X) **2.360040e+05 = Stage-1 iteration 20** (correct). The engine therefore interprets `restart_iteration` as the 1-based Exodus time-step index, and
`restart_iteration 21` was used. Had 20 been used, the restart would have read the iteration-19 design — the failure mode the specification warns about.

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

**[Session B] commands** (agent host unless noted), in order:
```
cat agent_inputs/*.md ...; cat work/run_summary.md jobs/* ; (cd outputs && sha256sum -c SHA256SUMS.txt) ; (cd agent_inputs && sha256sum -c FROZEN_CONFIG_FILES.sha256)   # recovery audit, ~19:36Z
cmp work/stage1/input_deck.i outputs/stage1/input_deck.i ; cmp jobs/stage1_job_script.sbatch outputs/stage1/job_script.sbatch ; cmp work/stage1/run/engine_output.exo outputs/stage1/engine_output.exo
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh
python3 -I <netCDF4 read of outputs/stage1/engine_output.exo: time_whole, name_nod_var, control stats at steps 1/20/21>              # checkpoint re-verified
grep -n -i restart work/manual_text/user_manual.txt ; sed -n 3840,3915p work/manual_text/user_manual.txt                             # manual §2.5.10
(cd work/stage2/xmlgen_probes/{ri20,ri21,ri20_keep_uniform} && XMLGenerator input_deck.i > xmlgenerator.log 2>&1)                   # translation-only probes, 19:38:01Z
mkdir -p work/stage2/probe_runs/ri{20,21} ; cp outputs/mesh.exo ... ; cp outputs/stage1/engine_output.exo .../restart_input.exo ; XMLGenerator input_deck.i   # 1-iteration probe decks
sbatch jobs/stage2_probe_ri20_job_script.sbatch   # 19:39:02Z → 16164869
sbatch jobs/stage2_probe_ri21_job_script.sbatch   # 19:39:02Z → 16164870
sacct -j 16164869 ... -P > jobs/sacct_16164869.txt ; sacct -j 16164870 ... -P > jobs/sacct_16164870.txt
mkdir -p work/stage2/run ; cp outputs/mesh.exo work/stage2/run/mesh.exo ; cp outputs/stage1/engine_output.exo work/stage2/run/restart_input.exo
<write work/stage2/input_deck.i (restart_iteration 21)> ; cp work/stage2/input_deck.i work/stage2/run/
(cd work/stage2/run && XMLGenerator input_deck.i > xmlgenerator.log 2>&1)                                                           # 19:40:18Z, rc 0
python3 -I work/scripts/verify_generated_config.py work/stage2/run 2 work/stage2/generated_config_verification.json 21              # 19:40:18Z, 60/60 pass
sbatch jobs/stage2_job_script.sbatch                                                                                                # 19:40:25Z → "Submitted batch job 16164881"
squeue -j 16164881 ... (polled every 30 s until the job left the queue, 20:02Z)
sacct -j 16164881 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P > jobs/sacct_16164881.txt
python3 -I work/scripts/verify_stage2_results.py work/stage2/run work/stage2/stage2_results_verification.json                      # 20:02:39Z, 15/15 pass
python3 -I work/scripts/continuation_evidence.py work/stage1/run work/stage2/run work/stage2/continuation_evidence.json probe_ri20=work/stage2/probe_runs/ri20 probe_ri21=work/stage2/probe_runs/ri21   # 20:02:40Z, 10/10 pass
cp ... outputs/stage2/ (see §8) ; <write outputs/stage2/continuation_evidence.txt from the JSON>
(cd outputs && find . -type f ! -name SHA256SUMS.txt | sort | xargs sha256sum > SHA256SUMS.txt && sha256sum -c SHA256SUMS.txt)      # 20:03:56Z, 69 entries, all OK
```
Inside the Stage-2 job (script `jobs/stage2_job_script.sbatch`, deliverable copy `outputs/stage2/job_script.sbatch`; `--chdir work/stage2/run`; frozen `#SBATCH` values identical to Stage 1):
`source …/load_approved_software.sh; module list; sha256sum <inputs>; grep FromFieldOnInputMesh engine_operations.xml; bash mpirun.source > morphorm_stage2.log 2>&1`.
The probe job scripts (`jobs/stage2_probe_ri20_job_script.sbatch`, `jobs/stage2_probe_ri21_job_script.sbatch`) have the same structure and frozen resources.

| Slurm job | Script | Purpose | State | ExitCode | Submit → Start → End (UTC) | Elapsed | Node | AllocCPUS / ReqMem / MaxRSS |
|---|---|---|---|---|---|---|---|---|
| **16164110** (`ex16_stage1`) | `jobs/stage1_job_script.sbatch` | Stage 1, resources exactly `account=hochhalter-np partition=hochhalter-np nodes=1 ntasks=1 cpus-per-task=8 mem=32G time=02:00:00`, no GPU | COMPLETED | 0:0 (`MORPHORM_RC=0`) | 19:11:01Z → 19:11:12Z → 19:29:51Z | 00:18:39 | notch272 | 8 / 32G / 2,316,192 K |
| **16164869** (`ex16_s2probe_ri20`) [Session B] | `jobs/stage2_probe_ri20_job_script.sbatch` | restart-convention probe, `restart_iteration 20`, `max_iterations 1`; same frozen resources | COMPLETED | 0:0 (`MORPHORM_RC=0`) | 19:39:02Z → 19:39:05Z → 19:40:16Z | 00:01:11 | notch351 | 8 / 32G / 2,132,032 K |
| **16164870** (`ex16_s2probe_ri21`) [Session B] | `jobs/stage2_probe_ri21_job_script.sbatch` | restart-convention probe, `restart_iteration 21`, `max_iterations 1`; same frozen resources | COMPLETED | 0:0 (`MORPHORM_RC=0`) | 19:39:02Z → 19:39:05Z → 19:40:16Z | 00:01:11 | notch351 | 8 / 32G / 2,208,104 K |
| **16164881** (`ex16_stage2`) [Session B] | `jobs/stage2_job_script.sbatch` | **Stage 2**, `restart_iteration 21`, `max_iterations 40`; same frozen resources, no GPU | COMPLETED | 0:0 (`MORPHORM_RC=0`) | 19:40:25Z → 19:40:26Z → 20:01:44Z | 00:21:18 | notch351 | 8 / 32G / 2,374,708 K |

`jobs/job_ids.txt` contains four lines: `16164110`, `16164869`, `16164870`, `16164881` (every job submitted in this trial; none failed or was cancelled).
Scheduler stdout/stderr: `logs/stage1_16164110.out` (includes `module list`, input-file SHA-256s, `MORPHORM_START_UTC=2026-10-09T19:11:20Z`, `MORPHORM_END_UTC=2026-10-09T19:29:51Z`), `logs/stage1_16164110.err` (empty). Accounting: `jobs/sacct_16164110.txt`.
**[Session B]** `logs/stage2_16164881.out` (includes `module list`, input-file SHA-256s incl. `restart_input.exo`, the generated restart block, `MORPHORM_START_UTC=2026-10-09T19:40:31Z`,
`MORPHORM_END_UTC=2026-10-09T20:01:44Z`), `logs/stage2_16164881.err` (empty); probe logs `logs/stage2_probe_ri20_16164869.{out,err}`, `logs/stage2_probe_ri21_16164870.{out,err}` (err files empty).
Accounting: `jobs/sacct_16164881.txt`, `jobs/sacct_16164869.txt`, `jobs/sacct_16164870.txt`. Submission log: `jobs/submissions.log`.

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

**Stage 2: COMPLETE [Session B].** Job 16164881 ran the OC optimizer for local iterations 0–40 (41 diagnostics rows, 41 function evaluations; local iteration 0 is the
re-evaluation of the restarted design, so 40 further OC updates were taken and the overall workflow reached **iteration 60**) and stopped at the iteration cap with
the message `****** Optimization stopping due to exceeding maximum number of iterations. ******` (`outputs/stage2/morphorm_oc_optimizer_diagnostics.txt`).
Verified by `work/scripts/verify_stage2_results.py` → 15/15 checks (`outputs/stage2/verification/stage2_results_verification.json`): 41 rows 0..40; stopping message;
`engine_output.exo` with 41 saved states (times 1.0…41.0) of `control` and `topology` on the 30,625-node mesh, step 1 non-uniform, all values in [0,1],
consecutive states differ; analyze files `iteration0.exo…iteration40.exo`; `iteration40.exo` has `displacement X/Y/Z`; `opt_criteria_history.csv` has 41 values matching the diagnostics.

Stage-2 objective (compliance F(X)) and constraint H1(X) history (local iteration; overall = local + 20):

| Local iter (overall) | F(X) compliance | Norm(F') | H1(X) | abs(dX) |
|---|---|---|---|---|
| **0 (20)** | **2.360040e+05** (= 2.3600395811001546e+05 in `opt_criteria_history.csv`; **identical to Stage-1 iteration 20**) | 1.191537e+04 | 3.964884e−13 | 1.0e+00 |
| 1 (21) | 2.336399e+05 | 1.177818e+04 | −4.506673e−13 | 2.0e−01 |
| 2 (22) | 2.316195e+05 | 1.165895e+04 | −4.360123e−13 | 2.0e−01 |
| 5 (25) | 2.271416e+05 | 1.140011e+04 | 2.969569e−13 | 2.0e−01 |
| 10 (30) | 2.227304e+05 | 1.114692e+04 | −3.524958e−14 | 2.0e−01 |
| 15 (35) | 2.199248e+05 | 1.098730e+04 | −1.108835e−13 | 1.6e−01 |
| 20 (40) | 2.177796e+05 | 1.085986e+04 | −8.462675e−14 | 1.6e−01 |
| 25 (45) | 2.162735e+05 | 1.077678e+04 | 6.389334e−14 | 1.6e−01 |
| 30 (50) | 2.150537e+05 | 1.071042e+04 | −1.998401e−15 | 1.2e−01 |
| 35 (55) | 2.142015e+05 | 1.066705e+04 | 1.052214e−13 | 1.2e−01 |
| 39 (59) | 2.136843e+05 | 1.063922e+04 | −5.684342e−14 | 1.1e−01 |
| **40 (60)** | **2.135584e+05** (= 2.13558414093044e+05) | 1.063277e+04 | −7.552292e−14 | 1.3e−01 |

(All 41 rows are in the diagnostics deliverable; the compliance decreases monotonically from 2.360040e+05 to 2.135584e+05 and the volume constraint stays active, |H1| < 1e-12.)

**Continuation evidence [Session B]** (`outputs/stage2/continuation_evidence.txt` / `.json`, produced by `work/scripts/continuation_evidence.py`, 10/10 checks):
- *Checkpoint used:* `outputs/stage2/restart_input.exo`, SHA-256 `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8` = `outputs/stage1/engine_output.exo` (byte-identical, also hashed on the compute node in `logs/stage2_16164881.out`).
- *Field:* `control` (deck `initial_guess_field_name control`; generated `<VariableName>control</VariableName>`, `<RestartFieldName>control</RestartFieldName>`), not the filtered `topology`.
- *Saved iteration:* generated `<Iteration>21</Iteration>` = checkpoint Exodus time step 21 (the 21st and last saved state) = Stage-1 optimizer iteration 20.
- *Compliance:* Stage-2 first evaluated compliance (local iteration 0) = **2.360040e+05**; Stage-1 iteration-20 compliance = **2.360040e+05**; at full precision both are
  `236003.95811001546` (`opt_criteria_history.csv` of each stage), relative difference 0. Norm(F') (1.191537e+04) and H1(X) (3.964884e−13) also coincide. The only Stage-1 iteration
  with this compliance is 20 (iteration 19 is 2.388394e+05, iteration 18 is 2.422601e+05).
- *Saved fields:* `control` at Stage-2 engine-output step 1 vs checkpoint step 21: max|Δ| = 0.0 (vs checkpoint step 20: 0.2 — a different design); `topology` step 1 vs checkpoint step 21: max|Δ| = 0.0.
- *What would have been wrong:* `restart_iteration 20` (the literal iteration number) reads time step 20 = the iteration-19 design (probe job 16164869: first compliance 2.388394e+05 = Stage-1
  iteration 19). This was detected by the probe jobs before Stage 2 was submitted and corrected to `restart_iteration 21` (probe job 16164870: first compliance 2.360040e+05); the accepted Stage-2
  run therefore started from the correct state on its only attempt. The probe runs are kept in `work/stage2/probe_runs/` and their diagnostics/logs/scripts in `outputs/stage2/run_logs/restart_probes/`.

**Final analyze output (Stage 2, local iteration 40 = overall iteration 60):** `outputs/stage2/final_analyze_output.exo` = copy of
`work/stage2/run/analyze_id_2_output_scenario_id_1/iteration40.exo` (SHA-256 `99f38f171ce7c3347f176230d50629d508a01a7dd062c7f26b9a920e7cfa6643`); nodal variables `Topology`, `displacement X`, `displacement Y`, `displacement Z`.
Stage-2 engine output: `outputs/stage2/engine_output.exo` (SHA-256 `ec46d954b50af857e3373fb8f716fd5e81a97efb13caa1d99088f9af5f71e9a6`, 41 saved states).

**Final analyze output (iteration 20):** `outputs/stage1/final_analyze_output.exo` = copy of
`work/stage1/run/analyze_id_2_output_scenario_id_1/iteration20.exo` (SHA-256 `1baf67b8cb33f9878f9d64e92529248ab924c4b04f32a6ba9500526c40aa116d`);
nodal variables `Topology`, `displacement X`, `displacement Y`, `displacement Z`. Per-iteration analyze files `iteration0.exo … iteration20.exo` remain in the run directory.

## 6. Key output files and SHA-256 (full manifest: `outputs/SHA256SUMS.txt`, regenerated in Session B at 2026-10-09T20:03:56Z: 69 entries, `sha256sum -c` OK; the 30 Session-A entries are unchanged)

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

**[Session B] Stage-2 deliverables**

| Deliverable (locked path) | SHA-256 |
|---|---|
| `outputs/stage2/input_deck.i` | `5300072ceaffa0c4dc3db41da1b073527917f0a59084d485855578b42b45ed19` |
| `outputs/stage2/job_script.sbatch` | `9698e83815a3d174ecd5cbfb007e4c877e101051a181a187c7645b7283ecd386` |
| `outputs/stage2/generated_config/interface.xml` | `828a2e406e5fa536015b2f9327c2d0b01f0bcc627814a4baee8796e6cf2bd8ca` |
| `outputs/stage2/generated_config/engine_input_deck.xml` | `7f3edc06119d4155981b3861c2c2263f268e6a3f56f7577cc0aa202f3b35169a` (= Stage 1) |
| `outputs/stage2/generated_config/engine_operations.xml` | `de4341334d3c99814ea20139addc61561a25508268c3d2eebe97d80e819e9336` |
| `outputs/stage2/generated_config/analyze_2_input_deck.xml` | `a6f7d5bf3d61607bec82781d3afad5231a493e602331ea7a3b54f7e9b3c162d5` (= Stage 1) |
| `outputs/stage2/generated_config/analyze_2_operations.xml` | `fbabf1a1c037533ce5dc1b1ba6a97ce9d70a795c1128735196a3e624aa73efa0` (= Stage 1) |
| `outputs/stage2/generated_config/analyze_helmholtz_input_deck.xml` | `c813b81a2c43cbac181b51c3ae12cad319473e7c2725afd29c2637fedec2dcbf` (= Stage 1) |
| `outputs/stage2/generated_config/analyze_helmholtz_operations.xml` | `402ffc30789914bd0c1c7bf429aa2f08ea22b0040960d015b9c71fd716404854` (= Stage 1) |
| `outputs/stage2/generated_config/mpirun.source` | `5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc` (= Stage 1) |
| `outputs/stage2/restart_input.exo` (exact copy of the checkpoint) | `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8` (= `outputs/stage1/engine_output.exo`) |
| `outputs/stage2/morphorm_oc_optimizer_diagnostics.txt` | `e206a8507f1c5233305540358ebbbb59df034d8b3219946bbbb097c71f0b2be1` |
| `outputs/stage2/engine_output.exo` | `ec46d954b50af857e3373fb8f716fd5e81a97efb13caa1d99088f9af5f71e9a6` |
| `outputs/stage2/final_analyze_output.exo` | `99f38f171ce7c3347f176230d50629d508a01a7dd062c7f26b9a920e7cfa6643` |
| `outputs/stage2/continuation_evidence.txt` | `199857bb6efd9f63278f35350407e6dd14ac297ae2a4ecf0693e99f8729e9599` |
| `outputs/stage2/continuation_evidence.json` | `9db76a1a935cf38275ddb1fc654ef56bb84db33a495075963712535b293a2456` |
| `outputs/stage2/run_logs/stage2_16164881.out` | `df2a3821a9a0bd03feb4d0e71bbfe953535b6af8f32824e99c9e9b65728f5403` |
| `outputs/stage2/run_logs/morphorm_stage2.log` | `d37be3eb517f1b9b9c68b7e812ddf05586bac93b565ae9efa9ac7cb18985d85f` |
| `outputs/stage2/verification/generated_config_verification.json` | `d98139e071bd0619d7f534c76e3101733c95019e820b61de1c58165677bf954b` |
| `outputs/stage2/verification/stage2_results_verification.json` | `5785ee1c470734db3df241287f32ef614336886f4f529eec905454d65b1f844d` |

Remaining `outputs/stage2/` files (run logs `engine_1_0.log`, `analyze_2_1.log`, `analyze_helmholtz_2.log`, `opt_criteria_history.csv`, `iteration40_criteria_history.csv`, `sacct_16164881.txt`,
`stage2_16164881.err`, the `restart_probes/` evidence and `generated_config/xmlgenerator*.{log,txt}`) are listed with their SHA-256 in `outputs/SHA256SUMS.txt`.

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

**[Session B]**
- **Jobs:** three submissions (16164869, 16164870 probes; 16164881 Stage 2), all COMPLETED, exit 0. No failed, re-run or cancelled jobs. Stage 2 was run once; nothing in `outputs/` was overwritten
  (the Stage-1 deliverables and their hashes are unchanged; the only file regenerated is `outputs/SHA256SUMS.txt`, now 69 entries).
- **Restart-state determination (not a deviation):** the manual's `restart_iteration` ("iteration (time step)") is ambiguous against a checkpoint that stores iteration k at time step k+1. Two
  1-iteration probe jobs resolved it before Stage 2 was submitted: value 20 → iteration-19 design (wrong), value 21 → iteration-20 design (correct). Stage 2 used 21. Details in §3b/§5; probe runs kept
  in `work/stage2/probe_runs/`, translation-only probes in `work/stage2/xmlgen_probes/`. These probes used the frozen resources and the approved interface and are recorded in `jobs/job_ids.txt`.
- **Observation:** the Stage-2 run directory contains a 0-byte `engine_restart.exo` (created at job start, never filled), consistent with Session A's observation that the runtime does not write the
  manual-described restart file; the locked checkpoint convention (engine output file) is unaffected. It is left in `work/stage2/run/` and not delivered.
- **Non-locked keywords used in Stage 2:** the same as Stage 1 (`verbose true`, `isosurface_output_frequency 1`), so Stage 2 also saved `control`/`topology` at every iteration (41 states).
- **Scripts:** `work/scripts/verify_generated_config.py` extended with Stage-2 restart checks (Stage-1 checks untouched); new `work/scripts/verify_stage2_results.py` and
  `work/scripts/continuation_evidence.py`. No script failures in Session B.
- **Deviations from the locked specification:** none.
- **Unresolved issues:** none. Both stages complete.

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
**[Session B] Stage-2 artifacts**
```
outputs/stage2/input_deck.i                         outputs/stage2/generated_config/{interface.xml, engine_input_deck.xml, engine_operations.xml,
outputs/stage2/job_script.sbatch                        analyze_2_input_deck.xml, analyze_2_operations.xml, analyze_helmholtz_input_deck.xml,
outputs/stage2/restart_input.exo  (= CHECKPOINT copy)   analyze_helmholtz_operations.xml, mpirun.source, xmlgenerator.log, xmlgenerator_timestamps.txt}
outputs/stage2/morphorm_oc_optimizer_diagnostics.txt outputs/stage2/run_logs/{stage2_16164881.out, stage2_16164881.err, morphorm_stage2.log, engine_1_0.log,
outputs/stage2/engine_output.exo  (41 saved states)     analyze_2_1.log, analyze_helmholtz_2.log, opt_criteria_history.csv, iteration40_criteria_history.csv, sacct_16164881.txt,
outputs/stage2/final_analyze_output.exo  (iter 60)      restart_probes/{probe_ri20_*, probe_ri21_*, stage2_probe_ri2{0,1}_*.out, stage2_probe_ri2{0,1}_job_script.sbatch, sacct_1616486{9,70}.txt}}
outputs/stage2/continuation_evidence.txt            outputs/stage2/verification/{generated_config_verification.json, stage2_results_verification.json}
outputs/stage2/continuation_evidence.json           outputs/SHA256SUMS.txt (regenerated, 69 entries)
jobs/job_ids.txt (4 IDs), jobs/stage2_job_script.sbatch, jobs/stage2_probe_ri20_job_script.sbatch, jobs/stage2_probe_ri21_job_script.sbatch,
jobs/sacct_16164881.txt, jobs/sacct_16164869.txt, jobs/sacct_16164870.txt, jobs/submissions.log
logs/stage2_16164881.{out,err}, logs/stage2_probe_ri20_16164869.{out,err}, logs/stage2_probe_ri21_16164870.{out,err}
work/stage2/input_deck.i ; work/stage2/run/ (complete Stage-2 run directory incl. restart_input.exo, engine_output.exo, analyze_id_2_output_scenario_id_1/iteration{0..40}.exo)
work/stage2/{generated_config_verification.json, stage2_results_verification.json, continuation_evidence.json, stage2_job_id.txt, xmlgen_probes/, probe_runs/}
work/scripts/{verify_generated_config.py (extended), verify_stage2_results.py, continuation_evidence.py} ; work/run_summary_session_a_backup.md
```
**Stage 1 complete (Session A); Stage 2 complete (Session B); overall iteration 60 reached; all locked deliverables present and hashed.**
