# Run summary — trial `E2-example16-baseline-05` (Session A: Stage 1; Session B: Stage 2 continuation)

**STATUS: Stage 1 is COMPLETE and verified (Session A, job 16168729). Stage 2 is COMPLETE and verified (Session B, job 16169770):
40 further iterations (local 0–40 = overall 20–60) with a seamless restart from the Stage-1 iteration-20 `control` field — first
Stage-2 compliance 2.360040e+05 = Stage-1 iteration-20 compliance (criteria-history values identical to 17 significant digits;
initial `control` field bit-identical to Stage-1 Exodus step 21). The whole two-stage workflow is complete.** One Stage-2 attempt
(job 16169758, `restart_iteration 20`) was cancelled by me after 1 min 42 s because it had read the iteration-19 state; see §7.

Session B (this process) found, from the persistent files alone, that Session A had completed and verified Stage 1 and had created
nothing for Stage 2. Session B therefore re-used every Stage-1 artifact unchanged (mesh, checkpoint, deck, generated configuration,
verification records) and performed only Stage 2. All Session-A text below is kept verbatim; Session-B additions are marked **[Session B]**.

## 1. Trial identifier and assigned workflow

| Item | Value |
|---|---|
| Trial identifier (`THESIS_TRIAL_ID`) | `E2-example16-baseline-05` |
| Frozen configuration | `FROZEN-EX16-v1` (`agent_inputs/FROZEN_CONFIG_SHA256.txt`: `a67d6cba…1a86b`) |
| Workflow | Full cantilever, two-stage restart (warm-start) workflow, `agent_inputs/scientific_problem_specification.md` |
| Session | Session A — construct the workflow, run and verify **Stage 1 only**, then stop. **[Session B]** — new process (`recovery_prompt.md`): determine completed work from the persistent files, then run Stage 2 to completion |
| Agent host | Session A: Slurm job 16168659 (`agent_E2…`, partition/account `hochhalter-np`, node notch274, 8 CPUs), session started 2026-10-09T23:54Z. **[Session B]**: Slurm job 16169529 (`agent_E2-example16-baseline-05_session_b`, same partition/account, 8 CPUs, 02:00:00), started 2026-10-10T00:26:04Z; Session-B work 00:27Z–01:10Z |
| Approved software interface | `source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh` (SHA-256 `38848816a3798fbf939f235121898aa7624077e51a13716a1a03cc0e1d7843c0`); after sourcing: `chpc/1.0, gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8` |
| Documentation used | only `agent_inputs/manuals/Morphorm_User_Manual.pdf` and `Morphorm_Theory_Manual.pdf` (text extracted with `pdftotext` to `work/manual_text/`) |

## 2. Mesh

**Generation.** Coreform Cubit 2026.8 (approved module) in batch mode on the agent host (permitted by
`compute_resources.md`), journal `work/mesh/mesh.jou` (deliverable copy `outputs/mesh.jou`):

```
cd work/mesh && source …/load_approved_software.sh
cubit -batch -nographics -nojournal -input mesh.jou > cubit_batch.log 2>&1     # exit 0
```
Timestamps: MESH_GEN_START_UTC=2026-10-09T23:57:03Z, MESH_GEN_END_UTC=2026-10-09T23:57:06Z (`work/mesh/cubit_timestamps.txt`).

Journal content: `brick x 2 y 1 z 1`, moved by (1, 0.5, 0.5) so the corner sits at the origin; `curve all interval 24`,
`curve with x_coord > 0.5 and x_coord < 1.5 interval 48` (48 × 24 × 24), `volume 1 scheme map`, `mesh volume 1`;
`block 1` = volume 1, named `block_1`, element type HEX8; `nodeset 1` = surface with centre x = 0 → `ns_fix`;
`nodeset 2` = curve with centre x = 2, y = 0 → `ns_load`; no sidesets; `export mesh "mesh.exo" dimension 3 overwrite`.

**Files.** `work/mesh/mesh.exo` → `outputs/mesh.exo` (SHA-256 `bc1a1d3a880f9411fb487e2bf0270312b96dfe46515570c76e8827625733a56f`);
copied unchanged into the Stage-1 run directory `work/stage1/run/mesh.exo` (same SHA-256). Cubit log `outputs/mesh_cubit_batch.log`.

**Verification** (`work/verification/verify_mesh.py`, run with the runtime `python3 -I` + netCDF4 at 2026-10-09T23:57:40Z;
record `outputs/mesh_verification.json`, ALL_CHECKS_PASS = true):

| Check | Locked | Found |
|---|---|---|
| Dimension | 3 | 3 |
| Elements / nodes | 27,648 / 30,625 | 27,648 / 30,625 |
| Element block | exactly one, `block_1`, HEX8, all elements | 1 block, id 1, name `block_1`, HEX8, 27,648 elements |
| Bounding box | [0,2]×[0,1]×[0,1] | x [0.0, 2.0], y [0.0, 1.0], z [0.0, 1.0] |
| Element size | uniform h = 1/24 | 49×25×25 node grid; h_x = h_y = h_z = 0.0416667 (min/max 0.041666666 / 0.041666667); every element a cube of edge 1/24; total volume 2.0 |
| `ns_fix` | all 625 nodes on x = 0 | nodeset id 1 `ns_fix`: 625 nodes, x ∈ [0,0], y ∈ [0,1], z ∈ [0,1]; independent coordinate count of nodes at x = 0 is 625 |
| `ns_load` | 25 nodes on edge x = 2, y = 0, z ∈ [0,1] | nodeset id 2 `ns_load`: 25 nodes, x ∈ [2,2], y ∈ [0,0], z ∈ [0,1]; independent count 25 |
| Sidesets | none required | 0 |

## 3. Input deck(s) and where each locked setting appears in the generated runtime configuration

**Stage-1 deck:** `work/stage1/input_deck.i` = `work/stage1/run/input_deck.i` = `outputs/stage1/input_deck.i`
(SHA-256 `dec3b4b3e22a3df3979b978f6c192c0c7ea06a94d56fac564b919b888675d742`). Translated with
`XMLGenerator input_deck.i` in `work/stage1/run` (exit 0; XMLGEN_START/END_UTC = 2026-10-10T00:00:07Z; log
`outputs/stage1/generated_config/xmlgenerator.log`). Generated files used by the accepted Stage-1 job are preserved in
`outputs/stage1/generated_config/` (`interface.xml`, `engine_input_deck.xml`, `engine_operations.xml`,
`analyze_2_input_deck.xml`, `analyze_2_operations.xml`, `analyze_helmholtz_input_deck.xml`, `analyze_helmholtz_operations.xml`, `mpirun.source`).

Automated verification of the generated configuration (`work/verification/verify_generated_config.py`, 38 checks, all PASS,
record `outputs/stage1/generated_config/generated_config_verification.json`) — locked setting → deck keyword → generated location:

| Locked setting | Deck | Generated configuration (as executed) |
|---|---|---|
| Services: engine + analyze, 1 processor each, single-rank, no decomposition | `service 1 code engine number_processors 1`; `service 2 code analyze number_processors 1` | `interface.xml` performers `engine_1` (engine), `analyze_2` (analyze), `analyze_helmholtz` (analyze, auto-wired by the Helmholtz filter); `mpirun.source`: three `-np 1` ranks (`PlatoMain`, `analyze_MPMD` ×2) |
| `update_problem true`, `update_problem_frequency 1` on the engine service | in `service 1` (+ `update_problem_frequency 1` in study) | `engine_operations.xml` `Update Problem` op `<UpdateProblemFrequency>1`; `interface.xml` `<ProblemUpdateFrequency>1`, `<UpdateProblemStage>Update Problem` |
| Mechanical 3-D scenario | `scenario 1 type mechanical dimensions 3` | `analyze_2_input_deck.xml` `Spatial Dimension 3`, `Physics Mechanical`, `PDE Constraint Elliptic` |
| Material E = 1.0, ν = 0.3 on `block_1` | `material 1 isotropic_elastic youngs_modulus 1.0 poissons_ratio 0.3`; `block 1 name block_1 material_id 1` | `Material Models/material_1/Isotropic Linear Elastic: Youngs Modulus 1.0, Poissons Ratio 0.3`; `Spatial Model/Domains/block_1 → material_1`; `engine_input_deck.xml` block index 1 material 1 |
| Fixed support `ns_fix`, u_x=u_y=u_z=0 | `boundary_condition 1 fixed_value nodeset ns_fix dispx dispy dispz 0 0 0` | `Essential Boundary Conditions`: Displacement X/Y/Z (Index 0/1/2), Fixed Value, Sides `ns_fix`, Value 0.0 — nothing else |
| Load: concentrated nodal load, dir y, −1.0 per node on `ns_load` (total −25); no tractions/body forces | `load 1 concentrated_load nodeset ns_load direction y value -1.0` | `Concentrated Loads/Concentrated Load with ID 0: Dof 1, Value -1.0, Nodes ns_load`; `Mechanical Natural Boundary Conditions` empty; no body loads |
| Objective: weighted sum, single compliance criterion, weight 1, by analyze | `criterion 1 mechanical_compliance`; `objective 1 weighted_sum criterion_ids 1 service_ids 2 scenario_ids 1 weights 1` | `interface.xml` stage `Compute Objective Value`: Filter Control (analyze_helmholtz) → Compute Objective Value (analyze_2) → Aggregate Data (engine_1, Weight 1); criterion `My Objective` = `Internal Elastic Energy` on `{block_1}` |
| Constraint: volume ≤ 15 %, `relative_target 0.15`, `less_than`, evaluated by the engine | `criterion 2 volume`; `constraint 1 criterion_id 2 relative_target 0.15 type less_than service_id 1` | `interface.xml` `<Constraint>`: `NormalizedTargetValue 0.15`, `ReferenceValueName Design Volume`; stage `Compute Constraint Value 1` runs `ComputeVolume` on `engine_1` (`engine_operations.xml`, SIMP exponent 1.0 / min 0.0 = plain volume) |
| Density discretization, uniform initial density 0.15 | `discretization density`, `initialize_method uniform`, `initial_density_value 0.15` | `engine_operations.xml` `Initialize Field: Method Uniform, Value 0.15`; stage `Initial Guess`; bounds ops `Discretization density`; `BoundConstraint` 0.0–1.0 |
| SIMP single phase, exponent 3.0, minimum 1e-3 | `material_interpolation 1 single_phase simp penalty_exponent 3.0 minimum_value 1e-3`; residual `material_interpolation_id 1` | `analyze_2_input_deck.xml` `Residual/Mechanical Residual: Material Interpolation Model Single-Phase, Penalty Function SIMP, Exponent 3.0, Minimum Value 1e-3` |
| Compliance criterion `minimum_ersatz_material_value 1e-3` | in `criterion 1` | `Criteria/My Objective/Penalty Function: SIMP, Exponent 3.0, Minimum Value 1e-3` |
| Optimizer OC, default tolerances, `normalize_in_aggregator false` | `optimization_algorithm oc`, `normalize_in_aggregator false` | `interface.xml` `<Optimizer><Package>OC`, `OCControlStagnationTolerance 1e-4`, `OCObjectiveStagnationTolerance 1e-8`, `OCGradientTolerance 1e-8`; Aggregator has no normalization element |
| Helmholtz filter, absolute radius 0.15, boundary-sticking penalty 1.0, no symmetry plane | `filter 1 type helmholtz radius_absolute 0.15 boundary_sticking_penalty 1.0`; study `filter_ids 1` | `analyze_helmholtz_input_deck.xml` `Physics Helmholtz Filter`; **`Length Scale 0.043301`** (= 0.15 / (2√3), the translator's radius→length-scale conversion, confirmed by probe: radius 0.30 → 0.086603) ; **`Surface Length Scale 1.0`** (= boundary_sticking_penalty; probe 0.5 → 0.5); no symmetry sideset parameters |
| Output: dispx, dispy, dispz from analyze; engine output of `control` and `topology` | `output 1 service_id 2 data dispx dispy dispz` | `analyze_2_input_deck.xml` `Output/Plottable {displacement_x, displacement_y, displacement_z}`; `engine_operations.xml` `PlatoMainOutput` inputs `topology`, `control` (Nodal Field); stage `Output To File` |
| Stage 1: `max_iterations 20` | `max_iterations 20` | `interface.xml` `<Convergence><MaxIterations>20`; `PlatoMainOutput <MaxIterations>20` |
| Stage 1: restart-file writing enabled, all 21 states saved | `write_restart_file true`, `isosurface_output_frequency 1` | `PlatoMainOutput <WriteRestart>true`, **`<OutputFrequency>1`** (every iteration); `engine_input_deck.xml` output file `engine_output` (exodus) |
| Stage 1 is a fresh run (no restart read) | no `restart_iteration` / `initial_guess_*` | translator INFO `restart_iteration` default 0; `Initialize Field` is `Uniform` (no file read) |

Benign translator messages: INFO lines "`filter_radius_absolute` was not set" / "`boundary_sticking_penalty` default 1.0" refer to the
legacy study-level keywords; the filter-block values are what reach `analyze_helmholtz_input_deck.xml` (verified by probes, §7).

**[Session B] Stage-2 (continuation) deck:** `work/stage2/run/input_deck.i` = `outputs/stage2/input_deck.i`
(SHA-256 `ddcc41eb390762301e811b7ae17e3d3c1736192b293814ec9410c2469ad07a33`). It is the Stage-1 deck with every §6 block unchanged
(services, scenario, residual, load, boundary condition, material, block, SIMP interpolation, criteria, objective, constraint, filter, output,
`optimization_algorithm oc`, `normalize_in_aggregator false`, `update_problem_frequency 1`, `write_restart_file true`,
`isosurface_output_frequency 1`) and these study changes: `max_iterations 40`; the uniform-initialization keywords removed; restart keywords from
manual §2.5.10 (Table 2.5.40): `initial_guess_file_name restart_input.exo`, `initial_guess_field_name control`, **`restart_iteration 21`**.
`restart_input.exo` is a byte-exact copy of the checkpoint `outputs/stage1/engine_output.exo` (SHA-256 `58dee776…5a07e8`, verified in the
run directory and in `outputs/stage2/restart_input.exo`). The mesh is the unchanged `outputs/mesh.exo` (SHA-256 `bc1a1d3a…3a56f`) copied to `work/stage2/run/mesh.exo`.
Translated with `XMLGenerator input_deck.i` in `work/stage2/run` (exit 0, XMLGEN_START/END_UTC = 2026-10-10T00:32:30Z/00:32:31Z; log
`outputs/stage2/generated_config/xmlgenerator.log`, which no longer contains the "restart_iteration default 0" / "initial_guess_field_name not set" INFO lines).
Generated files used by the accepted Stage-2 job: `outputs/stage2/generated_config/` (same 8 files as Stage 1).

Automated verification of the Stage-2 generated configuration (`work/verification/verify_generated_config_stage2.py` = the Stage-1 script with the
Stage-2 expectations; 39 checks, all PASS; record `outputs/stage2/generated_config/generated_config_verification.json`). The 33 formulation checks of §3
(material, SIMP, compliance ersatz minimum, load, displacement BCs, Helmholtz length scale 0.043301 / surface length scale 1.0 / no symmetry, OC
with default tolerances, constraint 0.15, aggregator without normalization, update-problem frequency 1, performers/ranks, output fields) pass with
values identical to Stage 1; `analyze_2_input_deck.xml`, `analyze_helmholtz_input_deck.xml`, `analyze_*_operations.xml`, `engine_input_deck.xml` and
`mpirun.source` are byte-identical to the Stage-1 files (same SHA-256). Stage-2-specific settings → generated location:

| Locked Stage-2 setting | Deck | Generated configuration (as executed) |
|---|---|---|
| `max_iterations 40` | `max_iterations 40` | `interface.xml` `<Convergence><MaxIterations>40`; `engine_operations.xml` `PlatoMainOutput <MaxIterations>40` |
| Restart source file = copy of the checkpoint | `initial_guess_file_name restart_input.exo` | `engine_operations.xml` `Initialize Field`: `<Method>FromFieldOnInputMesh`, `<FromFieldOnInputMesh><Name>restart_input.exo` (no `Uniform` element) |
| Restart field = `control` (raw design variable, not `topology`) | `initial_guess_field_name control` | `<VariableName>control</VariableName>` |
| Saved state = iteration-20 design = Exodus time step 21 | `restart_iteration 21` | `<Iteration>21</Iteration>` (the translator passes the keyword through unchanged; probe with 20 gave `<Iteration>20`) |
| Restart file written / output every iteration | `write_restart_file true`, `isosurface_output_frequency 1` | `PlatoMainOutput <WriteRestart>true`, `<OutputFrequency>1` (41 saved states in the Stage-2 engine output) |
| Everything else | unchanged | `interface.xml` differs from Stage 1 only in `MaxIterations`; `engine_operations.xml` only in `MaxIterations` and the `Initialize Field` operation |

## 4. Execution — commands, job IDs, states, exit codes

Every job was submitted through Slurm with exactly the frozen resources (`--account=hochhalter-np --partition=hochhalter-np
--nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00`, no GPU). Morphorm was never run on the agent host.

| Job ID | Script | Purpose | State | ExitCode | Submit / Start / End (UTC) | Elapsed | Node | MaxRSS |
|---|---|---|---|---|---|---|---|---|
| **16168729** | `jobs/stage1_job.sbatch` (= `outputs/stage1/job_script.sbatch`) | Stage 1 (20 iterations) | COMPLETED | 0:0 | 2026-10-10T00:01:23Z (sbatch) / 00:01:50Z / 00:20:16Z (`sacct` prints local 18:01:32 / 18:01:50 / 18:20:16) | 00:18:26 | notch272 | 2.27 GB |
| 16169758 **[Session B]** | `jobs/stage2_job.sbatch` (attempt-1 copy: `work/stage2/attempt1_restart20_cancelled_job16169758/job_script_attempt1.sbatch`) | Stage 2 attempt 1, `restart_iteration 20` | **CANCELLED by me** (`scancel`) | 0:0 (batch step 0:15 = SIGTERM) | 00:29:47Z / 00:30:10Z / 00:31:52Z (local 18:29:47 / 18:30:10 / 18:31:52) | 00:01:42 | notch272 | 2.18 GB |
| **16169770 [Session B]** | `jobs/stage2_job.sbatch` (= `outputs/stage2/job_script.sbatch`) | **Stage 2, `restart_iteration 21` (40 iterations)** | **COMPLETED** | **0:0** | 00:32:31Z / 00:32:39Z / 01:08:15Z (local 18:32:31 / 18:32:39 / 19:08:15) | 00:35:36 | notch272 | 2.36 GB |

`jobs/job_ids.txt` contains exactly these three IDs in submission order (Session A: 16168729; Session B: 16169758 cancelled, 16169770 completed).
`sacct -P` records: `jobs/stage2_attempt1_sacct_16169758.txt`, `jobs/stage2_sacct_16169770.txt` (copies under `outputs/stage2/run_logs/`); submission/cancel
timestamps `jobs/stage2_submit_timestamps.txt`. Scheduler stdout/stderr: `logs/stage2_16169758.{out,err}` (err = the Slurm cancellation notice),
`logs/stage2_16169770.{out,err}` (err empty; out contains `module list` after sourcing the approved interface — `chpc/1.0, gcc/11.2.0, openmpi/5.0.3,
morphorm/approved-runtime, cubit-edu/2026.8` — input SHA-256s including `restart_input.exo`, the `Initialize Field` restart settings, `mpirun.source`, timestamps).
Inside job 16169770: STAGE2_JOB_START_UTC=2026-10-10T00:32:42Z, MORPHORM_START_UTC=00:32:50Z, MORPHORM_END_UTC=01:08:15Z, MORPHORM_EXIT_CODE=0.
The Stage-2 job script is the Stage-1 script with the run directory `work/stage2/run`, log names `stage2_%j`, and an extra echo of the restart settings;
frozen `#SBATCH` resources unchanged. `sacct -P` record: `jobs/stage1_sacct_16168729.txt`
(copy in `outputs/stage1/run_logs/`). Scheduler stdout/stderr: `logs/stage1_16168729.out` (contains `module list` after sourcing the
approved interface, input SHA-256s, `mpirun.source`, timestamps) and `logs/stage1_16168729.err` (empty); copies in `outputs/stage1/run_logs/`.
Inside the job: MORPHORM_START_UTC=2026-10-10T00:02:03Z, MORPHORM_END_UTC=2026-10-10T00:20:16Z, MORPHORM_EXIT_CODE=0.

Commands used (agent host, in order; every Morphorm/Cubit shell first ran `source …/load_approved_software.sh`):
```
cat agent_inputs/*.md agent_inputs/FROZEN_CONFIG_*            # read all frozen inputs
pdftotext -layout agent_inputs/manuals/Morphorm_User_Manual.pdf work/manual_text/user_manual.txt
pdftotext -layout agent_inputs/manuals/Morphorm_Theory_Manual.pdf work/manual_text/theory_manual.txt
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh ; module list ; which cubit XMLGenerator PlatoMain analyze_MPMD python3
cd work/mesh && cubit -batch -nographics -nojournal -input mesh.jou > cubit_batch.log 2>&1
python3 -I work/verification/verify_mesh.py work/mesh/mesh.exo > work/mesh/mesh_verification.json
cp -p work/mesh/mesh.exo work/stage1/run/mesh.exo ; cp -p work/stage1/input_deck.i work/stage1/run/
cd work/stage1/run && XMLGenerator input_deck.i > xmlgenerator.log 2>&1          # attempt 1 (see §7), moved to work/stage1/xmlgen_attempt1_default_outfreq/
XMLGenerator input_deck.i   (in work/stage1/xmlgen_probe/{A_outfreq1,B_filtervals,C_study_outfreq1,D_isosurf1})   # translator probes, see §7
cd work/stage1/run && XMLGenerator input_deck.i > xmlgenerator.log 2>&1          # final translation (deck with isosurface_output_frequency 1)
python3 -I work/verification/verify_generated_config.py work/stage1/run stage1 > work/stage1/generated_config_verification.json
sbatch --parsable jobs/stage1_job.sbatch        -> 16168729 ; echo 16168729 >> jobs/job_ids.txt
squeue -j 16168729  (polled) ; sacct -j 16168729 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P > jobs/stage1_sacct_16168729.txt
python3 -I work/verification/verify_stage1_results.py work/stage1/run > work/stage1/stage1_results_verification.json
cp -p … outputs/… ; (cd outputs && find . -type f ! -name SHA256SUMS.txt | sort | xargs sha256sum > SHA256SUMS.txt && sha256sum -c SHA256SUMS.txt)
```
The job script (`jobs/stage1_job.sbatch`) sources the approved interface, prints `module list`, `cd`s to `work/stage1/run`,
prints SHA-256 of all inputs, sets `OMP_NUM_THREADS=1` and runs `bash mpirun.source > morphorm_stage1.log 2>&1`, then prints the diagnostics.

**[Session B] commands (agent host, in order; every XMLGenerator/python3 shell first ran `source …/load_approved_software.sh`; Morphorm itself ran only inside Slurm jobs):**
```
cat agent_inputs/*.md agent_inputs/FROZEN_CONFIG_*            # read all frozen inputs
cat work/run_summary.md jobs/* logs/* outputs/stage1/{input_deck.i,morphorm_oc_optimizer_diagnostics.txt,stage1_results_verification.json}   # recover state
(cd outputs && sha256sum -c SHA256SUMS.txt)                    # 33/33 OK ; sha256sum work/stage1/run/engine_output.exo outputs/stage1/engine_output.exo (identical)
grep -n -i restart work/manual_text/user_manual.txt ; sed -n 3840,3925p work/manual_text/user_manual.txt      # manual §2.5.10 restart keywords
mkdir -p work/stage2/run ; cp -p outputs/mesh.exo work/stage2/run/mesh.exo ; cp -p outputs/stage1/engine_output.exo work/stage2/run/restart_input.exo   # 00:28:15Z
# deck template work/stage2/input_deck.i (RESTART_ITER placeholder) -> work/stage2/run/input_deck.i (20) and work/stage2/xmlgen_probe/restart21/input_deck.i (21)
cd work/stage2/run && XMLGenerator input_deck.i > xmlgenerator.log 2>&1          # attempt 1 (restart_iteration 20), exit 0, 00:29Z
cd work/stage2/xmlgen_probe/restart21 && XMLGenerator input_deck.i > xmlgenerator.log 2>&1   # translator probe: <Iteration>21</Iteration>, everything else identical
python3 -I work/verification/verify_generated_config_stage2.py work/stage2/run stage2 20 > work/stage2/generated_config_verification_attempt1_restart20.json   # 39/39 PASS
sbatch --parsable jobs/stage2_job.sbatch        -> 16169758 ; echo 16169758 >> jobs/job_ids.txt      # 00:29:47Z
# monitored work/stage2/run/morphorm_oc_optimizer_diagnostics.txt: first row F(X) = 2.388394e+05 = Stage-1 iteration 19 -> wrong saved state
scancel 16169758                                               # 00:31:52Z ; sacct -j 16169758 ... -P > jobs/stage2_attempt1_sacct_16169758.txt
mv work/stage2/run work/stage2/attempt1_restart20_cancelled_job16169758 ; mkdir -p work/stage2/run ; cp -p outputs/mesh.exo work/stage2/run/mesh.exo ; cp -p outputs/stage1/engine_output.exo work/stage2/run/restart_input.exo
# work/stage2/run/input_deck.i with restart_iteration 21 (+ explanatory comment)
cd work/stage2/run && XMLGenerator input_deck.i > xmlgenerator.log 2>&1          # attempt 2, exit 0, 00:32:30Z-00:32:31Z
python3 -I work/verification/verify_generated_config_stage2.py work/stage2/run stage2 21 > work/stage2/generated_config_verification.json   # 39/39 PASS ; diff vs attempt 1: only <Iteration>
sbatch --parsable jobs/stage2_job.sbatch        -> 16169770 ; echo 16169770 >> jobs/job_ids.txt      # 00:32:31Z
# monitored: first row F(X) = 2.360040e+05 = Stage-1 iteration 20 -> seamless ; squeue polled until the job left the queue (01:08Z)
bash work/stage2/finalize_stage2.sh   # sacct -j 16169770 ... -P > jobs/stage2_sacct_16169770.txt ; verify_stage2_results.py ; continuation_evidence.py ; cp deliverables ; manifest
python3 -I work/verification/verify_stage2_results.py work/stage2/run > work/stage2/stage2_results_verification.json     # re-run after patch (see §7), 11/11 PASS
python3 -I work/verification/continuation_evidence.py work/stage1/run work/stage2/run work/stage2/run/input_deck.i 21 > work/stage2/continuation_evidence.json   # 5/5 PASS
(cd outputs && find . -type f ! -name SHA256SUMS.txt | sort | xargs sha256sum > SHA256SUMS.txt && sha256sum -c SHA256SUMS.txt)   # 72/72 OK, 01:09:18Z
```

## 5. Completed stages, iteration counts, stopping messages, continuation evidence

| Stage | Status | Iterations reached | Stopping message |
|---|---|---|---|
| **Stage 1** | **COMPLETE** (job 16168729) | iterations 0–20 (21 diagnostic rows; `max_iterations 20` reached) | `****** Optimization stopping due to exceeding maximum number of iterations. ******` |
| **Stage 2 [Session B]** | **COMPLETE** (job 16169770) | local iterations 0–40 (41 diagnostic rows; `max_iterations 40` reached) = overall iterations 20–60 | `****** Optimization stopping due to exceeding maximum number of iterations. ******` |

Stage-1 optimizer diagnostics (`outputs/stage1/morphorm_oc_optimizer_diagnostics.txt`), objective F(X) = compliance:
iteration 0: 4.893235e+06 (uniform 0.15 design); … iteration 19: 2.388394e+05; **iteration 20: 2.360040e+05**
(`opt_criteria_history.csv`: 2.3600395811001546e+05). Constraint H1 ≈ 0 (volume constraint active, |H1| < 1e-12) from iteration 6 on;
abs(dX) = 0.2 (OC move limit) every iteration.

**Checkpoint (verified, `outputs/stage1/stage1_results_verification.json`, all 11 checks PASS):**
`outputs/stage1/engine_output.exo` (unmodified copy of `work/stage1/run/engine_output.exo`,
SHA-256 `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8`, 12,383,296 bytes) holds **21 saved states**
(Exodus time steps 1…21, time values 1.0…21.0) with nodal fields **`control`** (raw design variable) and **`topology`** (filtered density)
on the 30,625-node / 27,648-element mesh. **Mapping: Exodus time step k = optimizer iteration k−1**, i.e.
state 1 (time 1.0) = iteration 0 = uniform `control` 0.15 everywhere (verified: min = max = 0.15), and
**state 21 (time 21.0, the last state) = the iteration-20 design** (control mean 0.168639, topology mean 0.143509; state 20 = iteration 19:
control mean 0.168837). Stage 2 must read the **`control`** field of the **iteration-20 (last) saved state**, and its first evaluated
compliance must equal the Stage-1 iteration-20 compliance **2.360040e+05** (if it equals 2.388394e+05 instead, the iteration-19 state was read).
No separate `engine_restart.exo` was produced by the engine (see §7); the engine output file above is the checkpoint required by §7 of the specification.

**[Session B] Stage-2 results and continuation evidence** (`outputs/stage2/continuation_evidence.json`, 5 checks PASS; `outputs/stage2/stage2_results_verification.json`, 11 checks PASS):

| Item | Value |
|---|---|
| Checkpoint used | `outputs/stage1/engine_output.exo` (SHA-256 `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8`), unmodified; read by Stage 2 as the exact copy `work/stage2/run/restart_input.exo` = `outputs/stage2/restart_input.exo` (same SHA-256) |
| Field read | `control` (raw design variable), `initial_guess_field_name control` → `<VariableName>control` |
| Saved state read | Exodus time step 21 = **Stage-1 iteration 20** (`restart_iteration 21` → `<Iteration>21`). The Stage-1 file stores iteration k at time step k+1 (step 1 = uniform 0.15 = iteration 0), and the engine interprets `restart_iteration` as the time-step index (established empirically, §7) |
| Stage-1 compliance, iteration 19 / **20** | 2.388394e+05 / **2.360040e+05** (criteria history `2.3600395811001546e+05`) |
| **Stage-2 first evaluated compliance (local iteration 0)** | **2.360040e+05** (criteria history `2.3600395811001546e+05`; relative difference to Stage-1 iteration 20 = **0.0**); Norm(F') 1.191537e+04 and H1 3.964884e-13 also identical to the Stage-1 iteration-20 row |
| Saved-field comparison | Stage-2 engine-output state 1 `control` field vs every Stage-1 saved state: max abs difference 0.0 **only** for Stage-1 step 21 (iteration 20); vs step 20 (iteration 19) the max difference is 0.2 (one OC move). The filtered `topology` field of state 1 also equals the Stage-1 iteration-20 `topology` (max abs diff 0.0) |
| Wrong-state attempt | job 16169758 with `restart_iteration 20`: first compliance 2.388394e+05 = Stage-1 **iteration 19** (time step 20) → cancelled, corrected to 21 (§7) |
| Stage-2 compliance history | local 0: 2.360040e+05 → 10: 2.227304e+05 → 20: 2.177796e+05 → 30: 2.150537e+05 → **40 (overall 60): 2.135584e+05** (criteria history last value in `outputs/stage2/run_logs/opt_criteria_history.csv`); H1 ≈ 0 (|H1| < 1e-12, volume constraint active) at every iteration; abs(dX) ≤ 0.2 |
| Stage-2 engine output | `outputs/stage2/engine_output.exo` (SHA-256 `ec46d954…1e9a6`, 22,183,456 bytes): 41 saved states (times 1.0…41.0) = local iterations 0–40, fields `control`/`topology`, 30,625 nodes / 27,648 elements; state 1 control mean 0.168639 (= Stage-1 state 21), state 41 control mean 0.166562, topology mean 0.142964 |
| Stage-2 final analyze output | `outputs/stage2/final_analyze_output.exo` = `work/stage2/run/analyze_id_2_output_scenario_id_1/iteration40.exo` (local iteration 40 = overall 60; fields `Topology`, `displacement X/Y/Z`, 1 time step) |
| Equivalence to one uninterrupted 60-iteration run | Stage 2 starts from exactly the Stage-1 iteration-20 design with the identical formulation and OC settings; the compliance sequence is monotonically decreasing across the junction (iteration 19: 2.388394e+05, 20: 2.360040e+05, 21 = Stage-2 local 1: 2.336399e+05) |

Final analyze output: `outputs/stage1/final_analyze_output.exo` = `work/stage1/run/analyze_id_2_output_scenario_id_1/iteration20.exo`
(nodal fields `Topology`, `displacement X/Y/Z`, 1 time step). Per-iteration analyze files `iteration0…20.exo` remain in the run directory.

## 6. Key output files (deliverables) with SHA-256 (full list in `outputs/SHA256SUMS.txt`)

| Path | SHA-256 |
|---|---|
| `outputs/mesh.jou` | `d9726ba906efaf9a2096bb53e1ac5e3fc7ac14cad19bca6796b0762a32c6603e` |
| `outputs/mesh.exo` | `bc1a1d3a880f9411fb487e2bf0270312b96dfe46515570c76e8827625733a56f` |
| `outputs/mesh_verification.json` | `16682e224cebc530423cf1f27d446aa49e780e4c9922a31ec8d0ca9b79ac7ef1` |
| `outputs/stage1/input_deck.i` | `dec3b4b3e22a3df3979b978f6c192c0c7ea06a94d56fac564b919b888675d742` |
| `outputs/stage1/job_script.sbatch` | `6288fb5d8914214c72a0419f9100df22d1d5d35fc007a13ab572836ed5b86a20` |
| `outputs/stage1/generated_config/interface.xml` | `5a5069736df8b3ba8ff727c07ae73515f8803f069b460a3b24d7783dcb8ec669` |
| `outputs/stage1/generated_config/engine_operations.xml` | `09dabcc015dd9e0ab88dbe54a8a2f0496ff19b9abfe94bf5c46107d6238fa40d` |
| `outputs/stage1/generated_config/analyze_2_input_deck.xml` | `a6f7d5bf3d61607bec82781d3afad5231a493e602331ea7a3b54f7e9b3c162d5` |
| `outputs/stage1/generated_config/analyze_helmholtz_input_deck.xml` | `c813b81a2c43cbac181b51c3ae12cad319473e7c2725afd29c2637fedec2dcbf` |
| `outputs/stage1/generated_config/mpirun.source` | `5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc` |
| `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt` | `4aaeaa78e77e9f065e3e0ab91d0205a13cdf600a7c76d9f8fc492b06092772f1` |
| **`outputs/stage1/engine_output.exo` (checkpoint, 21 states)** | **`58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8`** |
| `outputs/stage1/final_analyze_output.exo` | `1baf67b8cb33f9878f9d64e92529248ab924c4b04f32a6ba9500526c40aa116d` |
| `outputs/stage1/run_logs/stage1_16168729.out` | `69b293e15f4ebaa552cbed914612de43bb7d604e698bc1cc54c63758d4475eb8` |
| `outputs/stage1/run_logs/morphorm_stage1.log` | `24f51bf3b88158d9283abd03eca2f99f5418a3726091ea5e77b1dfc81695f555` |
| `outputs/stage1/run_logs/opt_criteria_history.csv` | `069b44f16f2760ce6d93194a63ad39bc7a4032bd069be0f80aff81a145943f0d` |

**[Session B] Stage-2 deliverables:**

| Path | SHA-256 |
|---|---|
| `outputs/stage2/input_deck.i` | `ddcc41eb390762301e811b7ae17e3d3c1736192b293814ec9410c2469ad07a33` |
| `outputs/stage2/job_script.sbatch` | `6039085f6b5ce7b0c0b00045eed1a9cf2b35ccfe7d05bb6089e0a4c8e1c1e9a6` |
| `outputs/stage2/generated_config/interface.xml` | `ce3472f6107d147906912492c2272117eb09b082d9984e38d7eef95b1f080288` |
| `outputs/stage2/generated_config/engine_operations.xml` | `de4341334d3c99814ea20139addc61561a25508268c3d2eebe97d80e819e9336` |
| `outputs/stage2/generated_config/analyze_2_input_deck.xml` (identical to Stage 1) | `a6f7d5bf3d61607bec82781d3afad5231a493e602331ea7a3b54f7e9b3c162d5` |
| `outputs/stage2/generated_config/analyze_helmholtz_input_deck.xml` (identical to Stage 1) | `c813b81a2c43cbac181b51c3ae12cad319473e7c2725afd29c2637fedec2dcbf` |
| `outputs/stage2/generated_config/mpirun.source` (identical to Stage 1) | `5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc` |
| **`outputs/stage2/restart_input.exo` (exact copy of the checkpoint)** | **`58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8`** |
| `outputs/stage2/morphorm_oc_optimizer_diagnostics.txt` | `e206a8507f1c5233305540358ebbbb59df034d8b3219946bbbb097c71f0b2be1` |
| `outputs/stage2/engine_output.exo` (41 states) | `ec46d954b50af857e3373fb8f716fd5e81a97efb13caa1d99088f9af5f71e9a6` |
| `outputs/stage2/final_analyze_output.exo` (overall iteration 60) | `99f38f171ce7c3347f176230d50629d508a01a7dd062c7f26b9a920e7cfa6643` |
| `outputs/stage2/continuation_evidence.json` | `a1909b2ff0e6665d0695d25ddbdea8107aef5e7fa279c86455d7da4b046967d9` |
| `outputs/stage2/stage2_results_verification.json` | `7806b9312b9da6aebb59251db3f007e0e2344a7d825e34d769873b7567adc42b` |
| `outputs/stage2/run_logs/stage2_16169770.out` | `78aa0fc45f895a4ad2a77f6924637c5d164b475b2d7e51883dcb002ae6bf1a12` |
| `outputs/stage2/run_logs/opt_criteria_history.csv` | `df93a4b10ef9f26ec75ab67a8bad9b0a83f8ce41b9abe35e4a41c507803ae0f4` |

`outputs/SHA256SUMS.txt` covers every file under `outputs/` except itself (generated with `sha256sum`, verified with `sha256sum -c`: all OK).
**[Session B]** It was regenerated after Stage 2 at 2026-10-10T01:09:18Z: 72 entries = 72 files, `sha256sum -c` 72/72 OK. No Stage-1 deliverable was
modified or replaced (all Stage-1 hashes above unchanged; the Stage-1 checkpoint hash was re-verified before and after Stage 2).

## 7. Failures, retries, cancelled jobs, unresolved issues, deviations

- **No failed, retried or cancelled Slurm jobs.** One job submitted (16168729), COMPLETED, exit 0, stderr empty.
- **Translation attempt 1 replaced before submission (not a run).** The first `XMLGenerator` translation of the deck (without
  `isosurface_output_frequency`) produced `PlatoMainOutput <OutputFrequency>5</OutputFrequency>` in `engine_operations.xml`, i.e. the engine
  would have written its output only every 5th iteration, which would violate the locked requirement of 21 saved states (iterations 0–20).
  The output block keyword `output_frequency 1` and a study-level `output_frequency 1` (rejected: "not recognized in block 'study'") did not change it.
  The study keyword `isosurface_output_frequency 1` (named by the translator's own INFO message; not documented in the manuals) sets
  `OutputFrequency` to 1 and changes nothing else (interface.xml and all other generated files byte-identical). **Decision:** add
  `isosurface_output_frequency 1` to the Stage-1 study block; this affects only the engine output write frequency, not any locked value.
  Attempt-1 files are kept in `work/stage1/xmlgen_attempt1_default_outfreq/`; probe decks/outputs in `work/stage1/xmlgen_probe/{A_outfreq1,B_filtervals,C_study_outfreq1,D_isosurf1}`
  (probe B used radius 0.30 / penalty 0.5 solely to confirm the filter-block mapping; it was never run).
  Result confirmed after the run: 21 saved states present.
- **`engine_restart.exo` not produced.** The manual says `write_restart_file true` writes `engine_restart.exo`; the run directory contains no such
  file although `<WriteRestart>true</WriteRestart>` is in the executed configuration. The specification designates the engine output file
  (`engine_output.exo`, 21 states, `control` + `topology`) as the checkpoint, and that file is complete, so this is recorded as an observation only.
- Translator INFO messages about unset legacy keywords (`filter_radius_absolute`, `boundary_sticking_penalty`, `restart_iteration`, `projection_type`,
  `filter_service`) are benign; the filter-block values were verified in the generated Helmholtz deck (probe B).
- The Helmholtz "filter length scale" in the generated configuration is 0.043301 = 0.15/(2√3), the translator's conversion of the locked absolute
  radius 0.15; the surface length scale is 1.0 = the locked boundary-sticking penalty. These are the values "as executed".
- Shell note: the first attempt to source the approved interface was piped through `tail`, so it ran in a subshell and showed no modules; re-sourcing
  directly worked (no effect on any artifact).
- The analyze visualization directory is named `analyze_id_2_output_scenario_id_1` (manual: `analyze_id_{svid}_output_scenario_id_{scid}`), as expected.
- Deviations from the specification: **none**. Unresolved issues: none. *(Session A)*

**[Session B] failures, retries, cancelled jobs, observations:**
- **Cancelled job 16169758 (Stage-2 attempt 1, `restart_iteration 20`) — wrong saved state read.** The manual defines `restart_iteration` as "which
  iteration (time step) in the initial guess file" and the translator passes the value through unchanged (`<Iteration>20`), so it was not determinable
  before running whether the engine counts optimizer iterations (0-based, iteration 20 = step 21) or Exodus time steps (1-based). Attempt 1 used the nominal
  value 20; its first evaluated compliance was **2.388394e+05 = Stage-1 iteration 19** (Norm(F') 1.207748e+04 and H1 4.834189e-13 also equal to the
  iteration-19 row), i.e. the engine read Exodus time step 20 = the iteration-19 design. Exactly the condition described in spec §7 ("equals some other
  Stage-1 iteration's compliance"): I cancelled the job with `scancel` at 00:31:52Z (1 min 42 s after start, during local iteration 0→1), preserved its run
  directory as `work/stage2/attempt1_restart20_cancelled_job16169758/` (deck, generated config, diagnostics, Morphorm log, partial `engine_output.exo`,
  verification record, job-script copy; evidence copies in `outputs/stage2/run_logs/attempt1_restart20_cancelled_job16169758/`), and corrected the deck to
  **`restart_iteration 21`** (= time step 21 = iteration-20 design). The corrected translation differs from attempt 1 only in `<Iteration>21</Iteration>`
  (all other generated files byte-identical). Job 16169770 then started from 2.360040e+05 = Stage-1 iteration 20 (confirmed also by the bit-identical `control`
  field). What was wrong: the `restart_iteration` keyword is the 1-based Exodus time-step index of the restart file, not the 0-based optimizer iteration number.
  Nothing from the cancelled job was used; its partial outputs are kept under `work/` only as evidence.
- **Empty `engine_restart.exo` (0 bytes)** appeared in the Stage-2 run directory at job start (18:32 local), although none appeared in Stage 1. It is not a
  valid Exodus/NetCDF file and is not used by the workflow (Stage 2 read `restart_input.exo`; the deliverable engine output is `engine_output.exo`). Observation only.
- **Verification-script crash and re-run (no effect on any run).** The first execution of `verify_stage2_results.py` (inside `finalize_stage2.sh`) aborted on the
  empty `engine_restart.exo` (NetCDF "Unknown file format"), so the first copy of `stage2_results_verification.json` was empty. I patched the script to record
  such a file as unreadable instead of aborting, re-ran it (11/11 PASS), replaced the empty JSON in `work/stage2/` and `outputs/stage2/`, and regenerated the manifest.
  The replaced file was never a valid deliverable (0 bytes); this is the only replacement of a file under `outputs/` in Session B.
- Translator probe `work/stage2/xmlgen_probe/restart21/` (deck with `restart_iteration 21`, translated before attempt 1 to see whether the translator applies an offset; it does not). Never run.
- Stage-2 `morphorm_stage2.log` contains only the Morphorm banner (same SHA-256 as the Stage-1 log); per-performer logs are `engine_1_0`, `analyze_2_1`, `analyze_helmholtz_2`
  (copied with a `.log` suffix into `outputs/stage2/run_logs/`).
- Session-A hand-off note said the expected first Stage-2 compliance was 2.360040e+05; this was confirmed.
- Deviations from the specification in Session B: **none** (frozen resources, approved interface, locked formulation and iteration counts all as specified; the
  cancelled attempt is recorded, not hidden). Unresolved issues: none.

## 8. Final artifact paths

```
outputs/mesh.jou, outputs/mesh.exo, outputs/mesh_verification.json, outputs/mesh_cubit_batch.log
outputs/stage1/input_deck.i
outputs/stage1/job_script.sbatch
outputs/stage1/generated_config/{interface.xml, engine_input_deck.xml, engine_operations.xml, analyze_2_input_deck.xml,
    analyze_2_operations.xml, analyze_helmholtz_input_deck.xml, analyze_helmholtz_operations.xml, mpirun.source,
    xmlgenerator.log, xmlgenerator_timestamps.txt, generated_config_verification.json}
outputs/stage1/morphorm_oc_optimizer_diagnostics.txt
outputs/stage1/engine_output.exo                      <- CHECKPOINT (21 saved states, fields control/topology)
outputs/stage1/final_analyze_output.exo               <- iteration 20 analyze output
outputs/stage1/run_logs/{stage1_16168729.out, stage1_16168729.err, morphorm_stage1.log, engine_1_0.log, analyze_2_1.log,
    analyze_helmholtz_2.log, opt_criteria_history.csv, iteration20_criteria_history.csv, stage1_sacct_16168729.txt,
    verify_mesh.py, verify_generated_config.py, verify_stage1_results.py}
outputs/stage1/stage1_results_verification.json
outputs/SHA256SUMS.txt
jobs/job_ids.txt (16168729), jobs/stage1_job.sbatch, jobs/stage1_sacct_16168729.txt, jobs/stage1_submit_timestamps.txt
logs/stage1_16168729.out, logs/stage1_16168729.err
work/mesh/ (journal, mesh, Cubit log, timestamps, verification), work/stage1/run/ (complete Stage-1 run directory incl. iteration0..20.exo),
work/stage1/xmlgen_attempt1_default_outfreq/, work/stage1/xmlgen_probe/, work/verification/, work/manual_text/
outputs/stage2/input_deck.i
outputs/stage2/job_script.sbatch
outputs/stage2/generated_config/{interface.xml, engine_input_deck.xml, engine_operations.xml, analyze_2_input_deck.xml,
    analyze_2_operations.xml, analyze_helmholtz_input_deck.xml, analyze_helmholtz_operations.xml, mpirun.source,
    xmlgenerator.log, xmlgenerator_timestamps.txt, generated_config_verification.json}
outputs/stage2/restart_input.exo                      <- exact copy of the Stage-1 checkpoint read by Stage 2
outputs/stage2/morphorm_oc_optimizer_diagnostics.txt
outputs/stage2/engine_output.exo                      <- 41 saved states (local iterations 0-40), fields control/topology
outputs/stage2/final_analyze_output.exo               <- local iteration 40 = overall iteration 60 analyze output
outputs/stage2/continuation_evidence.json             <- spec section 7 evidence (values compared, saved state used)
outputs/stage2/stage2_results_verification.json
outputs/stage2/run_logs/{stage2_16169770.out, stage2_16169770.err, morphorm_stage2.log, engine_1_0.log, analyze_2_1.log,
    analyze_helmholtz_2.log, opt_criteria_history.csv, iteration40_criteria_history.csv, stage2_sacct_16169770.txt,
    verify_generated_config_stage2.py, verify_stage2_results.py, continuation_evidence.py,
    attempt1_restart20_cancelled_job16169758/{stage2_16169758.out, stage2_16169758.err, stage2_attempt1_sacct_16169758.txt,
        input_deck.i, engine_operations.xml, morphorm_oc_optimizer_diagnostics.txt, morphorm_stage2_attempt1.log,
        generated_config_verification_attempt1_restart20.json}}
outputs/SHA256SUMS.txt                                <- regenerated after Stage 2 (72 files)
jobs/job_ids.txt (16168729, 16169758, 16169770), jobs/stage2_job.sbatch, jobs/stage2_sacct_16169770.txt,
    jobs/stage2_attempt1_sacct_16169758.txt, jobs/stage2_submit_timestamps.txt
logs/stage2_16169758.{out,err}, logs/stage2_16169770.{out,err}
work/stage2/run/ (complete Stage-2 run directory incl. iteration0..40.exo), work/stage2/input_deck.i (template),
work/stage2/attempt1_restart20_cancelled_job16169758/ (cancelled attempt, kept), work/stage2/xmlgen_probe/restart21/,
work/stage2/{generated_config_verification.json, generated_config_verification_attempt1_restart20.json,
    stage2_results_verification.json, continuation_evidence.json, stage2_timestamps.txt, finalize_stage2.sh}
work/verification/{verify_generated_config_stage2.py, verify_stage2_results.py, continuation_evidence.py}
work/run_summary_session_a_backup.md                  <- verbatim copy of the Session-A summary before this update
```

**Hand-off note written by Session A (Stage 2 was then performed by Session B exactly as described, with `restart_iteration 21`, see above):** checkpoint = `outputs/stage1/engine_output.exo` (SHA-256 above); restart from the
`control` field of its last saved state (Exodus step 21 = iteration 20); expected first Stage-2 compliance = 2.360040e+05; Stage-2 deck must keep
every §6 setting identical, `max_iterations 40`, and should read a copy of the checkpoint placed at `outputs/stage2/restart_input.exo`.

**[Session B] Final state: both stages complete.** Stage 1 (job 16168729): iterations 0–20, checkpoint with 21 states. Stage 2 (job 16169770): local
iterations 0–40 = overall 20–60, seamless restart from the Stage-1 iteration-20 `control` field (first Stage-2 compliance 2.360040e+05 = Stage-1 iteration-20
compliance, criteria-history values identical, initial design field bit-identical), final compliance 2.135584e+05 at overall iteration 60. All deliverables are
at their locked paths under `outputs/`, `outputs/SHA256SUMS.txt` regenerated (72/72 OK), `jobs/job_ids.txt` lists all three submitted jobs. Session B ended 2026-10-10T01:11:45Z
within agent-host allocation 16169529.
