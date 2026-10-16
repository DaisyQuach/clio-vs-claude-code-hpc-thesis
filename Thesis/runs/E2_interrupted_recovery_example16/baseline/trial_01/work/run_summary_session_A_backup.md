# Run summary — Session A (Stage 1 only)

**STATUS: Stage 1 is COMPLETE and verified. Stage 2 has NOT been started.** No Stage-2 or continuation deck, job script
or job was created, translated, submitted or run in this session (per the Session-A instruction to stop after Stage 1).

## 1. Trial identifier and assigned workflow

| Item | Value |
|---|---|
| Trial identifier (`THESIS_TRIAL_ID`) | `E2-example16-baseline-01` |
| Trial root | `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_01` |
| Frozen configuration | `FROZEN-EX16-v1` (`a67d6cba7f0ce35ae6dc227f33b39056514be9494d6e15bc8e58524dfba1a86b`) |
| Assigned workflow | Full cantilever, two-stage restart (warm-start) workflow EX16: Stage 1 = 20 OC iterations from uniform density 0.15 with restart-file writing; Stage 2 = 40 further iterations restarted from the iteration-20 `control` field of the Stage-1 engine output (overall iteration 60) |
| This session | Session A: construct + validate the workflow, run and verify Stage 1 only, then stop |
| Agent host | Slurm job `16162352` on `notch351` (agent-host allocation), session started 2026-10-09T17:24Z |
| Software | `source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh` (script SHA-256 `38848816a3798fbf939f235121898aa7624077e51a13716a1a03cc0e1d7843c0`) → modules `chpc/1.0, gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8`; Coreform Cubit 2026.8 build fdca55e4; runtime Python 3.13.5 (numpy 2.3.1, netCDF4 1.7.2) |
| Documentation used | only `agent_inputs/manuals/Morphorm_User_Manual.pdf` and `Morphorm_Theory_Manual.pdf` (text extracted with `pdftotext` to `work/manual_text/` for reading) |

## 2. Mesh

**Generation** (agent host, approved Cubit in batch mode, 2026-10-09T17:26:32Z–17:26:35Z):

```
cd work/mesh && cubit -batch -nographics -nojournal -input mesh.jou > cubit_mesh.log 2>&1   # exit 0
```

Journal `work/mesh/mesh.jou` (= `outputs/mesh.jou`): `brick x 2.0 y 1.0 z 1.0`, moved so the corner is at the origin;
`volume 1 scheme map`, `volume 1 size 0.041666666667`, `curve with length > 1.5 interval 48`, `curve with length < 1.5 interval 24`;
`block 1 add volume 1`, `block 1 name "block_1"`, `block 1 element type HEX8`; `nodeset 1 add surface with x_coord < 0.001` named
`ns_fix`; `nodeset 2 add curve with x_coord > 1.999 and y_coord < 0.001` named `ns_load`; `export mesh "mesh.exo" dimension 3 overwrite`.
The only Cubit warning is the licensing banner line "No RLM logins were valid" followed by a successful student-license login; the run exited 0.

**Files:** `work/mesh/mesh.exo` → `outputs/mesh.exo` (byte-identical), SHA-256 `bdeceb5a251e3c82f75258cd2e83e7e9b9136d298635869042c7af5eaeee0fdc`;
Cubit log `outputs/mesh_cubit.log`; verification script `work/mesh/verify_mesh.py` (runtime python3 + netCDF4, run 2026-10-09T17:27:07Z);
verification record `outputs/mesh_verification.json` (ALL_CHECKS_PASS = true).

**Verification result** (all locked §3 values met):

| Check | Locked | Measured |
|---|---|---|
| Dimension | 3 | 3 |
| Elements / nodes | 27,648 / 30,625 | 27,648 / 30,625 |
| Element type / structure | HEX8 mapped | HEX8 (8 nodes/elem), 49×25×25 unique coordinates = 48×24×24 cells |
| Element size | h = 1/24 = 0.0416667 uniform | spacing min/max 0.041666666–0.041666667 in x, y, z; element volume 7.2338e-5 (= h³), total 2.0000 |
| Bounding box | [0,2]×[0,1]×[0,1] | x [0.0, 2.0], y [0.0, 1.0], z [0.0, 1.0] |
| Blocks | exactly one, `block_1`, all elements | 1 block, id 1, name `block_1`, 27,648 elements |
| `ns_fix` | all nodes on x = 0, 625 nodes | id 1, 625 nodes, x ∈ [0,0], y ∈ [0,1], z ∈ [0,1]; independent count of nodes with x = 0: 625 |
| `ns_load` | all nodes on edge x = 2, y = 0, z ∈ [0,1], 25 nodes | id 2, 25 nodes, x = 2, y = 0, z ∈ [0,1]; independent count: 25 |
| Sidesets | none required | 0 |

## 3. Input deck and generated runtime configuration

**Stage-1 deck:** `work/stage1/run/input_deck.i` = `outputs/stage1/input_deck.i`, SHA-256 `9011cd4be59c66f93ffbdb305b069095534d914712ca1a1f45dce87381fda4d3`.
Translation: `cd work/stage1/run && XMLGenerator input_deck.i > xmlgenerator.log 2>&1` (exit 0; first translation 17:27:46Z, final translation 17:30:03Z,
see §7 for the one change between them). Generated files (`interface.xml`, `engine_input_deck.xml`, `engine_operations.xml`, `analyze_2_input_deck.xml`,
`analyze_2_operations.xml`, `analyze_helmholtz_input_deck.xml`, `analyze_helmholtz_operations.xml`, `mpirun.source`, plus `xmlgenerator.log`) are
preserved unmodified in `outputs/stage1/generated_config/`; they are exactly the files the Stage-1 job used (SHA-256s echoed in the job stdout match
`outputs/SHA256SUMS.txt`). Scripted verification: `python3 -I work/stage1/verify_generated_config.py work/stage1/run 1` (17:31:03Z, before submission),
46/46 checks pass; record `outputs/stage1/generated_config_verification.json`.

| Locked setting | Deck (input_deck.i) | Where it appears in the generated configuration |
|---|---|---|
| Services: engine + analyze, 1 processor each, single-rank performers, no decomposition | `service 1 code engine number_processors 1`; `service 2 code analyze number_processors 1` | `interface.xml` Performers `engine_1` (engine), `analyze_2` (analyze), `analyze_helmholtz` (analyze, auto-wired Helmholtz service per manual §2.5.4); `mpirun.source` launches each with `-np 1` (`PlatoMain engine_input_deck.xml`, `analyze_MPMD --input-config=analyze_2_input_deck.xml`, `analyze_MPMD --input-config=analyze_helmholtz_input_deck.xml`) |
| `update_problem true`, `update_problem_frequency 1` on the engine service | service 1 + study | `engine_operations.xml` `<Function>Update Problem</Function> <UpdateProblemFrequency>1`; `interface.xml` `<ProblemUpdateFrequency>1`, `<UpdateProblemStage>Update Problem` |
| Scenario mechanical, 3-D, analyze service | `scenario 1 type mechanical dimensions 3 service_id 2 residual_ids 1 output_id 1` | `analyze_2_input_deck.xml` `Physics = Mechanical`, `PDE Constraint = Elliptic`, `Spatial Dimension = 3`, `Response = Linear` |
| Mesh | `mesh 1 name mesh.exo` | `analyze_2_input_deck.xml`/`analyze_helmholtz_input_deck.xml` `Input Mesh = mesh.exo`; `engine_input_deck.xml` `<mesh>mesh.exo</mesh>` |
| Material E = 1.0, ν = 0.3 on `block_1` | `material 1 isotropic_elastic youngs_modulus 1.0 poissons_ratio 0.3`; `block 1 material_id 1 name block_1` | `analyze_2_input_deck.xml` Material Models/material_1/Isotropic Linear Elastic `Youngs Modulus = 1.0`, `Poissons Ratio = 0.3`; Spatial Model/Domains has only `block_1` → `material_1`; `engine_input_deck.xml` block index 1 material 1 |
| Fixed support `ns_fix`, u_x = u_y = u_z = 0 | `boundary_condition 1 fixed_value nodeset ns_fix degree_of_freedom dispx dispy dispz value 0.0 0.0 0.0` | `analyze_2_input_deck.xml` Essential Boundary Conditions: Displacement X/Y/Z (Index 0/1/2), `Type = Fixed Value`, `Sides = ns_fix`, `Value = 0.0` |
| Load: concentrated nodal load on every node of `ns_load`, direction y, −1.0 per node, no other loads | `load 1 concentrated_load nodeset ns_load direction y value -1.0` | `analyze_2_input_deck.xml` Concentrated Loads: `Dof = 1` (y), `Value = -1.0`, `Nodes = ns_load`; `Mechanical Natural Boundary Conditions` empty (no tractions) |
| Objective: weighted-sum, single compliance criterion, weight 1, analyze service | `criterion 1 mechanical_compliance`; `objective 1 weighted_sum criterion_ids 1 service_ids 2 scenario_ids 1 weights 1` | `analyze_2_input_deck.xml` Criteria/My Objective `Scalar Function Type = Internal Elastic Energy`; `interface.xml` stage "Compute Objective Value" runs on `analyze_2` then engine Aggregator; `engine_operations.xml` Aggregator `<Weight><Value>1` |
| Constraint: volume ≤ 0.15 relative, `less_than`, engine service | `criterion 2 volume`; `constraint 1 criterion_id 2 relative_target 0.15 type less_than service_id 1` | `interface.xml` Optimizer/Constraint `<NormalizedTargetValue>0.15`, `<ReferenceValueName>Design Volume`; stages "Compute Constraint Value/Gradient 1" run `ComputeVolume` on `engine_1` (`engine_operations.xml`) |
| Density discretization, uniform initial density 0.15 | `study discretization density initialize_method uniform initial_density_value 0.15` | `engine_operations.xml` `InitializeField Method Uniform Value 0.15`; `SetLowerBounds/SetUpperBounds Discretization density`; `interface.xml` bounds 0.0–1.0 |
| SIMP single phase, exponent 3.0, minimum 1e-3; compliance `minimum_ersatz_material_value 1e-3` | `material_interpolation 1 type single_phase model simp penalty_exponent 3.0 minimum_value 1e-3` (referenced by residual 1); `criterion 1 material_penalty_exponent 3.0 minimum_ersatz_material_value 1e-3` | `analyze_2_input_deck.xml` Residual/Mechanical Residual `Material Interpolation Model = Single-Phase`, Penalty Function `SIMP`, `Exponent 3.0`, `Minimum Value 1e-3`; Criteria/My Objective Penalty Function `SIMP`, `Exponent 3.0`, `Minimum Value 1e-3` |
| Optimizer OC, default tolerances, `normalize_in_aggregator false` | `study optimization_algorithm oc normalize_in_aggregator false` (no tolerance keywords) | `interface.xml` `<Package>OC`, `OCControlStagnationTolerance 1e-4`, `OCObjectiveStagnationTolerance 1e-8`, `OCGradientTolerance 1e-8` (manual defaults); Aggregator has no `<Normals>` block (a scratch translation with `normalize_in_aggregator true` adds `<Normals>` and an "Initial Criterion Value" stage, so its absence is the `false` setting) |
| Helmholtz filter, absolute radius 0.15, boundary-sticking penalty 1.0, no symmetry plane | `filter 1 type helmholtz radius_absolute 0.15 boundary_sticking_penalty 1.0`; `study filter_ids 1` | `analyze_helmholtz_input_deck.xml` `Physics = Helmholtz Filter`, `Length Scale = 0.043301`, `Surface Length Scale = 1.0`, no symmetry sidesets. Length scale ℓ = R/(2√3): 0.15/(2√3) = 0.0433013 (confirmed by a scratch translation with radius 1.0 → 0.288675 = 1/(2√3)). Surface length scale ℓΓ = boundary_sticking_penalty = 1.0 (theory manual eq. 4.4.8–4.4.10) |
| Iteration cap 20 (Stage 1) | `study max_iterations 20` | `interface.xml` `<Convergence><MaxIterations>20`; `engine_operations.xml` PlatoMainOutput `<MaxIterations>20` |
| Restart-file writing (Stage 1) with `control` and `topology` at every iteration | `study write_restart_file true`; `isosurface_output_frequency 1` (see §7) | `engine_operations.xml` PlatoMainOutput `<WriteRestart>true`, `<OutputFrequency>1`, inputs `topology` and `control` (Nodal Field); `engine_input_deck.xml` `<file>engine_output</file>` |
| Output: dispx, dispy, dispz from analyze; engine output of control/topology | `output 1 service_id 2 data dispx dispy dispz` | `analyze_2_input_deck.xml` `Plottable = {displacement_x, displacement_y, displacement_z}`; `analyze_2_operations.xml` Visualization `OutputFrequency 1`; engine output fields above |
| Stage-2 restart settings | not applicable in Stage 1 (`restart_iteration` left at default 0 → fresh start, per `xmlgenerator.log`) | — |

## 4. Execution

All commands were run from the trial root with the approved software interface sourced in the shell.

```
# environment
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh ; module list
pdftotext -layout agent_inputs/manuals/Morphorm_User_Manual.pdf work/manual_text/user_manual.txt      # manual reading only
pdftotext -layout agent_inputs/manuals/Morphorm_Theory_Manual.pdf work/manual_text/theory_manual.txt
# mesh (agent host)
cd work/mesh && cubit -batch -nographics -nojournal -input mesh.jou > cubit_mesh.log 2>&1              # rc 0, 17:26:32Z–17:26:35Z
python3 -I work/mesh/verify_mesh.py work/mesh/mesh.exo > work/mesh/mesh_verification.json            # rc 0, 17:27:07Z
# deck translation
cp -p work/mesh/mesh.exo work/stage1/run/mesh.exo
cd work/stage1/run && XMLGenerator input_deck.i > xmlgenerator.log 2>&1                              # rc 0 (17:27:46Z, kept in work/stage1/translation_attempt1/)
cd work/stage1/run && XMLGenerator input_deck.i > xmlgenerator.log 2>&1                              # rc 0 (17:30:03Z, final; deck with isosurface_output_frequency 1)
# scratch translations (XMLGenerator only, no Morphorm run) to understand keyword-to-XML mapping: work/stage1/scratch_tests/{A_outfreq1,B_normalize_true,C_radius_default,D_isofreq1}
python3 -I work/stage1/verify_generated_config.py work/stage1/run 1 > work/stage1/generated_config_verification.json   # rc 0, 17:31:03Z
# Stage-1 job
sbatch jobs/stage1_job_script.sbatch          # "Submitted batch job 16162453", 2026-10-09T17:31:10Z
squeue -j 16162453 ... (polled every 30 s until the job left the queue at 17:42:00Z)
sacct -j 16162453 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P > jobs/sacct_16162453.txt
# post-run verification and deliverables
python3 -I work/stage1/verify_stage1_results.py work/stage1/run > work/stage1/stage1_results_verification.json     # rc 0 on the 3rd run (17:42:54Z), see §7
cp -p ... outputs/ (locked paths, §8); cmp confirmed byte-identical copies of mesh.exo, engine_output.exo, final_analyze_output.exo
cd outputs && find . -type f ! -name SHA256SUMS.txt | sort | xargs sha256sum > SHA256SUMS.txt && sha256sum -c SHA256SUMS.txt
```

**Slurm jobs submitted in this trial** (also in `jobs/job_ids.txt`):

| Job ID | Name | Script | Resources | Submit (UTC) | Start (UTC) | End (UTC) | Elapsed | State | Exit code | Node | MaxRSS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16162453 | ex16_stage1 | `jobs/stage1_job_script.sbatch` (= `outputs/stage1/job_script.sbatch`, SHA-256 `3906d096…6085`) | account hochhalter-np, partition hochhalter-np, 1 node, 1 task × 8 CPUs, 32G, 02:00:00, no GPU | 2026-10-09T17:31:10Z | 17:31:11Z | 17:41:52Z | 00:10:41 | COMPLETED | 0:0 | notch351 | 2.30 GB (batch step) |

The job script sources the approved interface, prints `module list` and the executables to stdout, prints the SHA-256 of every input file it uses,
runs `bash mpirun.source > morphorm_stage1.log 2>&1` in `work/stage1/run/`, and exits with the mpirun exit code (0). Scheduler stdout/stderr:
`logs/stage1_16162453.out`, `logs/stage1_16162453.err` (empty), copied to `outputs/stage1/run_logs/`. Accounting: `jobs/sacct_16162453.txt`.
UTC timestamps for every step are in `work/mesh/mesh_timestamps.txt` and `work/stage1/stage1_timestamps.txt`; job start/end are in the job stdout
("UTC Morphorm start 17:31:16Z", "UTC Morphorm end 17:41:52Z").

## 5. Completed stages and iteration counts

| Stage | Status | Iterations reached | Stopping message |
|---|---|---|---|
| Stage 1 | **complete and verified** | 0–20 (21 optimizer rows; final `Iter 20, F-count 21`), i.e. the locked `max_iterations 20` cap | `****** Optimization stopping due to exceeding maximum number of iterations. ******` (last line of `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt`) |
| Stage 2 | **not started** (not created, translated, submitted or run in this session) | — | — |

Stage-1 optimizer diagnostics (compliance F(X), constraint H1(X)):
iteration 0: F = 4.893235e+06, H1 = −1.564817e−02 (uniform 0.15 design); iteration 20: **F = 2.360040e+05**, H1 = 3.964884e−13 (volume constraint active),
Norm(F') = 1.191537e+04, abs(dX) = 0.2, abs(dF) = 2.835402e+03. The full 21-row history is in the diagnostics file and in
`outputs/stage1/run_logs/opt_criteria_history.csv` ("My Objective" row, 21 values ending 2.3600395811001546e+05).
For Stage 2 (future session) the seamless-restart check is: first Stage-2 evaluated compliance must equal **2.360040e+05** (the Stage-1 iteration-20 value).

**Checkpoint (verified 2026-10-09T17:42:54Z, `work/stage1/verify_stage1_results.py`, record `outputs/stage1/checkpoint_verification.json`):**
`work/stage1/run/engine_output.exo` = `outputs/stage1/engine_output.exo` (byte-identical, unmodified), SHA-256
`58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8`, 12,383,296 bytes; **21 time steps** (time values 1.0 … 21.0, i.e. Exodus
step k ↔ optimization iteration k−1; iteration 20 = step 21, time value 21.0); nodal fields `control` and `topology`; 30,625 nodes / 27,648 elements
(matches the mesh); step 1 `control` is exactly uniform 0.15 (the initial design); step 21 `control` min 0.0 / max 1.0 / mean 0.168639, step 21 `topology`
min 5.48e−08 / max 0.926727 / mean 0.143509; all values finite and within [0, 1]. No separate `engine_restart.exo` was produced by the runtime although
`write_restart_file true` was set (`<WriteRestart>true`); the specification defines the Stage-1 **engine output file** as the checkpoint, and it holds all
21 saved states, so Stage 2 must read a copy of `outputs/stage1/engine_output.exo` (field `control`, the iteration-20 state = Exodus time step 21 /
restart iteration 20 — the future session must confirm which index convention `restart_iteration` uses by checking that the first Stage-2 compliance
equals 2.360040e+05, as the specification requires).

Final analyze output: `work/stage1/run/analyze_id_2_output_scenario_id_1/iteration20.exo` = `outputs/stage1/final_analyze_output.exo` (byte-identical),
SHA-256 `1baf67b8cb33f9878f9d64e92529248ab924c4b04f32a6ba9500526c40aa116d`, 1 time step, nodal fields `Topology`, `displacement X`, `displacement Y`,
`displacement Z`, 30,625 nodes. The analyze service wrote `iteration0.exo` … `iteration20.exo` (+ per-iteration criteria history CSVs, 42 files) in
`work/stage1/run/analyze_id_2_output_scenario_id_1/` (all kept).

## 6. Key output files and SHA-256 (full list in `outputs/SHA256SUMS.txt`, 30 files, self-check passed)

| File | SHA-256 |
|---|---|
| `outputs/mesh.jou` | 2f0c2181a6561f0cabd62f19d247e646c7b8d55a047a93bffb23dc7262a66d0c |
| `outputs/mesh.exo` | bdeceb5a251e3c82f75258cd2e83e7e9b9136d298635869042c7af5eaeee0fdc |
| `outputs/mesh_verification.json` | 8a5c7c703e45c6f2548ba3ccfa0de55f4e5e2d38e1a4f5189dc9f6df113bdf05 |
| `outputs/mesh_cubit.log` | 3a2fa5a971bf7c5aa85728dfcc24019f8a51a418e73846b6fee71098ad9d6f98 |
| `outputs/stage1/input_deck.i` | 9011cd4be59c66f93ffbdb305b069095534d914712ca1a1f45dce87381fda4d3 |
| `outputs/stage1/job_script.sbatch` | 3906d096752ff8fd95323bb3cec195860a22980467ffda491cff9f4aac106085 |
| `outputs/stage1/generated_config/interface.xml` | 5a5069736df8b3ba8ff727c07ae73515f8803f069b460a3b24d7783dcb8ec669 |
| `outputs/stage1/generated_config/engine_input_deck.xml` | 7f3edc06119d4155981b3861c2c2263f268e6a3f56f7577cc0aa202f3b35169a |
| `outputs/stage1/generated_config/engine_operations.xml` | 09dabcc015dd9e0ab88dbe54a8a2f0496ff19b9abfe94bf5c46107d6238fa40d |
| `outputs/stage1/generated_config/analyze_2_input_deck.xml` | a6f7d5bf3d61607bec82781d3afad5231a493e602331ea7a3b54f7e9b3c162d5 |
| `outputs/stage1/generated_config/analyze_2_operations.xml` | fbabf1a1c037533ce5dc1b1ba6a97ce9d70a795c1128735196a3e624aa73efa0 |
| `outputs/stage1/generated_config/analyze_helmholtz_input_deck.xml` | c813b81a2c43cbac181b51c3ae12cad319473e7c2725afd29c2637fedec2dcbf |
| `outputs/stage1/generated_config/analyze_helmholtz_operations.xml` | 402ffc30789914bd0c1c7bf429aa2f08ea22b0040960d015b9c71fd716404854 |
| `outputs/stage1/generated_config/mpirun.source` | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| `outputs/stage1/generated_config/xmlgenerator.log` | 7c78de76617cb9b2b77ebe369a0bfeee427b8e27e5691066e65bdfc8003a8f65 |
| `outputs/stage1/generated_config_verification.json` | 16adeb65299c1572bb42f70b1572b9da3c53b8a4c1299cdb7d5f1fe70a88d553 |
| `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt` | 4aaeaa78e77e9f065e3e0ab91d0205a13cdf600a7c76d9f8fc492b06092772f1 |
| `outputs/stage1/engine_output.exo` (checkpoint, 21 states) | 58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8 |
| `outputs/stage1/final_analyze_output.exo` (iteration 20) | 1baf67b8cb33f9878f9d64e92529248ab924c4b04f32a6ba9500526c40aa116d |
| `outputs/stage1/checkpoint_verification.json` | 7bf24cc6cae5b6e72c29db76269bc3a2c78bbedf2e8d9fe736728f38d2f6f1fd |
| `outputs/stage1/run_logs/stage1_16162453.out` | 2b8568174393fcc4e6cf9e54cda2b5792c56ad58b9cd92d77379795d069e390e |
| `outputs/stage1/run_logs/stage1_16162453.err` (empty) | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| `outputs/stage1/run_logs/morphorm_stage1.log` (mpirun stdout: banner only) | 24f51bf3b88158d9283abd03eca2f99f5418a3726091ea5e77b1dfc81695f555 |
| `outputs/stage1/run_logs/engine_1_0.log`, `analyze_2_1.log`, `analyze_helmholtz_2.log` (per-performer console logs) | 0251658e…6c5c7, b42f611e…d2914, c5ec8948…a485f |
| `outputs/stage1/run_logs/opt_criteria_history.csv` (= iteration20_criteria_history.csv) | 069b44f16f2760ce6d93194a63ad39bc7a4032bd069be0f80aff81a145943f0d |
| `outputs/stage1/run_logs/sacct_16162453.txt` | c58e05ce2b66a6610c12ee488cc7faff2e8d6c66f465a4f3c6285b2e903c446f |

## 7. Failures, retries, cancelled jobs, unresolved issues, deviations

- **Cancelled jobs:** none. **Failed jobs:** none. One Slurm job was submitted (16162453) and it completed with exit 0.
- **Deck translated twice (no run in between).** The first translation (kept in `work/stage1/translation_attempt1/`) produced
  `<OutputFrequency>5</OutputFrequency>` on the engine `PlatoMainOutput` operation, the operation that writes `engine_output.exo` and the restart data.
  Scratch translations showed this tag is set by the study keyword `isosurface_output_frequency` (XMLGenerator log: default 5), not by the output block's
  `output_frequency`. Because that operation must save the design at every one of the 21 iterations, the deck sets `isosurface_output_frequency 1`
  (final translation, `<OutputFrequency>1`). This keyword is not a locked value and does not change any locked setting; the result (21 saved states) was
  verified after the run. Every locked value is identical in both translations (the only diff between them is that tag).
- **No `engine_restart.exo`** was written although `write_restart_file true` / `<WriteRestart>true</WriteRestart>` is set. Not treated as a failure:
  the locked checkpoint is the engine output file `engine_output.exo`, which contains the `control` and `topology` fields for all 21 iterations.
- **Verification-script retries (agent-side only, no effect on the run):** `verify_stage1_results.py` was run three times (17:42:17Z, 17:42:34Z,
  17:42:54Z); the first two runs failed on script defects (numpy bool not JSON-serialisable; displacement field names are `displacement X` not
  `displacement_x`). Only the third, passing record is kept (`outputs/stage1/checkpoint_verification.json`); the data were unchanged.
- **Scratch XMLGenerator-only translations** in `work/stage1/scratch_tests/` (A: `output_frequency 1`, B: `normalize_in_aggregator true`,
  C: filter radius 1.0, D: `isosurface_output_frequency 1`) were used solely to learn the keyword→XML mapping; none was submitted or run.
- **Deviations from the specification:** none. All locked values (§2–§8 of the specification) were realised and verified in the generated
  configuration (46/46 checks) and in the results (9/9 checks). The agent host was used only for meshing, deck translation and verification; Morphorm
  ran only inside Slurm job 16162453 with the frozen resources.
- **Unresolved issues:** none for Stage 1. Open item for the next session: Stage 2 (continuation deck with `initial_guess_file_name` = a copy of the
  checkpoint at `outputs/stage2/restart_input.exo`, `initial_guess_field_name control`, `restart_iteration` set to the iteration-20 saved state,
  `max_iterations 40`), plus the continuation evidence (first Stage-2 compliance must equal 2.360040e+05).
- The `pdftotext` utility (`/usr/bin/pdftotext`) was used only to extract the two permitted manuals to text for reading; no other documentation or
  restricted material was accessed.

## 8. Final artifact paths (trial root relative)

| Path | Content | Status |
|---|---|---|
| `outputs/mesh.jou` | Cubit journal | present |
| `outputs/mesh.exo` | Exodus mesh used by Stage 1 (and to be used by Stage 2) | present |
| `outputs/mesh_verification.json` | mesh verification record (`outputs/mesh_cubit.log` = Cubit log) | present |
| `outputs/stage1/input_deck.i` | Stage-1 input deck | present |
| `outputs/stage1/job_script.sbatch` | Stage-1 Slurm script (copy of `jobs/stage1_job_script.sbatch`) | present |
| `outputs/stage1/generated_config/` | XMLGenerator output used by Stage 1 (+ `xmlgenerator.log`) | present |
| `outputs/stage1/generated_config_verification.json` | pre-submission generated-configuration verification record | present |
| `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt` | Stage-1 optimizer diagnostics (iterations 0–20) | present |
| `outputs/stage1/engine_output.exo` | **Stage-1 checkpoint**, 21 saved states (`control`, `topology`) | present, unmodified |
| `outputs/stage1/final_analyze_output.exo` | Stage-1 final analyze output (iteration 20) | present |
| `outputs/stage1/checkpoint_verification.json` | Stage-1 results/checkpoint verification record | present |
| `outputs/stage1/run_logs/` | Slurm stdout/stderr, Morphorm mpirun log, per-performer logs, criteria histories, sacct record | present |
| `outputs/SHA256SUMS.txt` | SHA-256 of every file under `outputs/` except itself (regenerate after Stage 2) | present |
| `jobs/job_ids.txt` | `16162453` | present |
| `jobs/stage1_job_script.sbatch`, `jobs/sacct_16162453.txt`, `jobs/submissions.log` | submitted script, accounting, submission log | present |
| `logs/stage1_16162453.out`, `logs/stage1_16162453.err` | scheduler stdout/stderr | present |
| `work/mesh/` | journal, mesh, Cubit log, verification script/record, timestamps | present |
| `work/stage1/run/` | complete Stage-1 run directory (inputs, generated config, all Morphorm outputs incl. `analyze_id_2_output_scenario_id_1/iteration0..20.exo`) | present, untouched |
| `work/stage1/translation_attempt1/`, `work/stage1/scratch_tests/` | first translation and scratch XMLGenerator tests (never run) | present |
| `work/stage1/verify_generated_config.py`, `work/stage1/verify_stage1_results.py`, `work/mesh/verify_mesh.py` | verification scripts (runtime python3) | present |
| `outputs/stage2/*` | **not created — Stage 2 has not been started** | absent by design |
