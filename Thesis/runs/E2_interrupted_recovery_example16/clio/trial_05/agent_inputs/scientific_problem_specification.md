# Scientific Problem Specification — Frozen Workflow EX16 (Full Cantilever, Two-Stage Restart Workflow)

Frozen configuration ID: `FROZEN-EX16-v1` (integrity hash in `FROZEN_CONFIG_SHA256.txt`). Every value below is locked.
Do not change, approximate, or "improve" any of them. If a locked value cannot be realized, preserve the state and report the
blocking condition in `work/run_summary.md` instead of substituting a different value.

## 1. Problem statement

Minimum-compliance topology optimization of a three-dimensional cantilever beam, run as a **staged (restartable) workflow**:
Stage 1 runs the optimization for a fixed number of iterations and saves the design at every iteration; Stage 2 resumes from the
design saved at the end of Stage 1 and continues the same optimization for a further fixed number of iterations, so that the two stages
together are equivalent to one uninterrupted run.

## 2. Geometry (locked)

| Item | Value |
|---|---|
| Design domain | brick x ∈ [0, 2.0], y ∈ [0, 1.0], z ∈ [0, 1.0] (corner at the origin); full width, no symmetry reduction |
| Units | consistent, dimensionless |

## 3. Mesh (locked)

| Item | Value |
|---|---|
| Element type | HEX8, structured (mapped) mesh |
| Element size | uniform h = 1/24 = 0.0416667 in x, y and z |
| Element count | 48 × 24 × 24 = 27,648 elements; 30,625 nodes |
| Element block | exactly one block named `block_1` containing every element (entire domain optimizable) |
| Nodeset `ns_fix` | all nodes on the face x = 0 (625 nodes) |
| Nodeset `ns_load` | all nodes on the edge x = 2, y = 0, spanning z ∈ [0, 1] (25 nodes) |
| Sidesets | none required |
| Mesh generator | approved Coreform Cubit in batch mode (no graphics); export Exodus II, dimension 3 |
| Mesh verification | before any optimization, verify element/node counts, bounding box, block name and nodeset sizes, and keep the verification record |

## 4. Material (locked)

Isotropic linear elastic, Young's modulus E = 1.0, Poisson's ratio ν = 0.3, assigned to `block_1`.

## 5. Boundary conditions and load (locked)

| Item | Value |
|---|---|
| Fixed support | `ns_fix`: u_x = u_y = u_z = 0 (nodeset, fixed value) |
| Load | concentrated nodal load on every node of `ns_load`, direction y, value −1.0 per node (total −25.0); no tractions, no body forces, no other loads |
| Symmetry | none |

## 6. Optimization formulation (locked, identical in both stages)

| Item | Value |
|---|---|
| Objective | minimize mechanical compliance; weighted-sum objective with the single compliance criterion, weight 1, evaluated by the analyze service |
| Constraint | volume ≤ 15 % of the design-domain volume: `relative_target 0.15`, type `less_than`, evaluated by the engine service |
| Discretization | density; Stage 1 starts from a uniform initial density 0.15 |
| Material interpolation | SIMP (single phase), exponent 3.0 (runtime default), minimum value 1e-3; the compliance criterion also uses `minimum_ersatz_material_value 1e-3` |
| Optimizer | Optimality Criteria (OC), runtime default tolerances; `normalize_in_aggregator false`; `update_problem true` on the engine service with `update_problem_frequency 1` |
| Filter | Helmholtz (PDE) filter, absolute radius 0.15, boundary-sticking penalty 1.0; no symmetry plane |
| Services | engine service and analyze service, one processor each; single-rank performers; no mesh decomposition |
| Output | nodal displacements dispx, dispy, dispz from analyze; engine output of the `control` and `topology` fields |

**Generated-configuration requirement.** Before submitting each stage, verify in the *generated* runtime configuration (XMLGenerator
output) that the filter length scale and surface length scale, the material, SIMP values, load, displacement conditions, iteration cap,
restart-file writing (Stage 1) and the restart source file/field/saved state (Stage 2) are all present as locked. A setting that appears in
the input deck but not in the generated configuration is not applied. Keep the generated configuration files used by each accepted stage.

## 7. Staged workflow (locked)

| Stage | Locked requirement |
|---|---|
| Stage 1 | `max_iterations 20`, starting from the uniform initial density; restart-file writing enabled so that the engine output file stores the `control` (raw design variable) and `topology` (filtered density) nodal fields at every iteration (21 saved states, iterations 0–20). Stage 1 is complete when the optimizer stops at the iteration cap and the engine output with all saved states is preserved. |
| Checkpoint | the Stage-1 engine output file is the checkpoint. Preserve it unmodified (and its SHA-256). Stage 2 reads a copy of it. |
| Stage 2 | resumes from the design saved at the **end of Stage 1, i.e. the iteration-20 design**, read from the **`control`** field (not the filtered `topology` field), and runs `max_iterations 40` further iterations, so the overall workflow reaches iteration 60. |
| Continuation evidence | the continuation is correct only if Stage 2's first evaluated compliance equals Stage 1's compliance at iteration 20 (seamless restart). Verify this from the optimizer diagnostics of both stages and from the saved fields, and record the evidence. If the first Stage-2 compliance equals some other Stage-1 iteration's compliance, the restart read the wrong saved state; correct the restart settings so the iteration-20 design is used, and record what was wrong. |

## 8. Execution (locked)

- Each stage runs with the approved Morphorm runtime (`software_contract.md`) as its own Slurm batch job with the frozen resources (`compute_resources.md`). Do not run Morphorm on the agent-host node.
- Stage 2 must not start until Stage 1 has completed and its checkpoint is preserved.

## 9. Required deliverables (locked paths, relative to the trial root)

| Path | Content |
|---|---|
| `outputs/mesh.jou` | the Cubit journal (or equivalent scripted procedure) that produced the mesh |
| `outputs/mesh.exo` | the Exodus mesh used by both stages |
| `outputs/mesh_verification.txt` (or `.json`) | the mesh verification record |
| `outputs/stage1/input_deck.i` | Stage-1 input deck |
| `outputs/stage1/job_script.sbatch` | Stage-1 Slurm script |
| `outputs/stage1/generated_config/` | XMLGenerator output used by Stage 1 |
| `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt` | Stage-1 optimizer diagnostics |
| `outputs/stage1/engine_output.exo` | Stage-1 engine output (the checkpoint, 21 saved states) |
| `outputs/stage1/final_analyze_output.exo` | Stage-1 final analyze output (iteration 20) |
| `outputs/stage1/run_logs/` | Stage-1 Slurm stdout/stderr and Morphorm log(s) |
| `outputs/stage2/input_deck.i` | Stage-2 (continuation) input deck |
| `outputs/stage2/job_script.sbatch` | Stage-2 Slurm script |
| `outputs/stage2/generated_config/` | XMLGenerator output used by Stage 2 |
| `outputs/stage2/restart_input.exo` | the exact copy of the checkpoint read by Stage 2 |
| `outputs/stage2/morphorm_oc_optimizer_diagnostics.txt` | Stage-2 optimizer diagnostics |
| `outputs/stage2/engine_output.exo` | Stage-2 engine output |
| `outputs/stage2/final_analyze_output.exo` | Stage-2 final analyze output (local iteration 40 = overall iteration 60) |
| `outputs/stage2/continuation_evidence.txt` (or `.json`) | the continuation evidence of §7 (values compared, saved state used) |
| `outputs/stage2/run_logs/` | Stage-2 Slurm stdout/stderr and Morphorm log(s) |
| `outputs/SHA256SUMS.txt` | SHA-256 of every file under `outputs/` (excluding itself); regenerate after Stage 2 |
| `jobs/job_ids.txt` | one Slurm job ID per line for every job submitted in this trial (including failed or cancelled ones) |
| `work/run_summary.md` | the run summary required by `provenance_requirements.md`, stating which stages are complete |
