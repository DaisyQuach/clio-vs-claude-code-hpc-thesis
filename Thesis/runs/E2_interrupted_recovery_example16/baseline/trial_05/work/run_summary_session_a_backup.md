# Run summary — trial `E2-example16-baseline-05` (Session A: Stage 1 only)

**STATUS: Stage 1 is COMPLETE and verified. Stage 2 has NOT been started** (no Stage-2 deck, generated configuration,
job script or job exists anywhere in this trial root; nothing under `outputs/stage2/`).

## 1. Trial identifier and assigned workflow

| Item | Value |
|---|---|
| Trial identifier (`THESIS_TRIAL_ID`) | `E2-example16-baseline-05` |
| Frozen configuration | `FROZEN-EX16-v1` (`agent_inputs/FROZEN_CONFIG_SHA256.txt`: `a67d6cba…1a86b`) |
| Workflow | Full cantilever, two-stage restart (warm-start) workflow, `agent_inputs/scientific_problem_specification.md` |
| Session | Session A — construct the workflow, run and verify **Stage 1 only**, then stop |
| Agent host | Slurm job 16168659 (`agent_E2…`, partition/account `hochhalter-np`, node notch274, 8 CPUs), session started 2026-10-09T23:54Z |
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

## 4. Execution — commands, job IDs, states, exit codes

Every job was submitted through Slurm with exactly the frozen resources (`--account=hochhalter-np --partition=hochhalter-np
--nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00`, no GPU). Morphorm was never run on the agent host.

| Job ID | Script | Purpose | State | ExitCode | Submit / Start / End (UTC) | Elapsed | Node | MaxRSS |
|---|---|---|---|---|---|---|---|---|
| **16168729** | `jobs/stage1_job.sbatch` (= `outputs/stage1/job_script.sbatch`) | Stage 1 (20 iterations) | COMPLETED | 0:0 | 2026-10-10T00:01:23Z (sbatch) / 00:01:50Z / 00:20:16Z (`sacct` prints local 18:01:32 / 18:01:50 / 18:20:16) | 00:18:26 | notch272 | 2.27 GB |

`jobs/job_ids.txt` contains exactly this one ID (no failed or cancelled jobs). `sacct -P` record: `jobs/stage1_sacct_16168729.txt`
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

## 5. Completed stages, iteration counts, stopping messages, continuation evidence

| Stage | Status | Iterations reached | Stopping message |
|---|---|---|---|
| **Stage 1** | **COMPLETE** (job 16168729) | iterations 0–20 (21 diagnostic rows; `max_iterations 20` reached) | `****** Optimization stopping due to exceeding maximum number of iterations. ******` |
| **Stage 2** | **NOT STARTED** | — | — (no continuation deck/config/job created in this session) |

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

`outputs/SHA256SUMS.txt` covers every file under `outputs/` except itself (generated with `sha256sum`, verified with `sha256sum -c`: all OK).
It must be regenerated after Stage 2.

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
- Deviations from the specification: **none**. Unresolved issues: none.

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
outputs/stage2/  — does not exist (Stage 2 not started)
```

**Hand-off to Session B (Stage 2, not performed here):** checkpoint = `outputs/stage1/engine_output.exo` (SHA-256 above); restart from the
`control` field of its last saved state (Exodus step 21 = iteration 20); expected first Stage-2 compliance = 2.360040e+05; Stage-2 deck must keep
every §6 setting identical, `max_iterations 40`, and should read a copy of the checkpoint placed at `outputs/stage2/restart_input.exo`.
