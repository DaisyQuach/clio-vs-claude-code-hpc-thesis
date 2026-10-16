# Scientific Problem Specification — Frozen Workflow EX8 (Half Cantilever with a Helmholtz Symmetry-Plane Filter)

Frozen configuration ID: `FROZEN-EX8-v1` (integrity hash in `FROZEN_CONFIG_SHA256.txt`). Every value below is locked.
Do not change, approximate, or "improve" any of them. If a locked value cannot be realized, preserve the state and report the
blocking condition in `work/run_summary.md` instead of substituting a different value.

## 1. Problem statement

Minimum-compliance topology optimization of one half of a three-dimensional cantilever beam, exploiting the beam's mid-width
symmetry plane. The full cantilever is a 2 × 1 × 1 brick fixed on its x = 0 face and loaded by a transverse line load along its
bottom free edge. Only the half z ∈ [0, 0.5] is modeled; the cut plane z = 0.5 is a symmetry plane for both the structural
model and the density filter.

## 2. Geometry (locked)

| Item | Value |
|---|---|
| Design domain | brick x ∈ [0, 2.0], y ∈ [0, 1.0], z ∈ [0, 0.5] (corner at the origin) |
| Symmetry (cut) plane | z = 0.5 |
| Units | consistent, dimensionless |

## 3. Mesh (locked)

| Item | Value |
|---|---|
| Element type | HEX8, structured (mapped) mesh |
| Element size | uniform h = 1/24 = 0.0416667 in x, y and z |
| Element count | 48 × 24 × 12 = 13,824 elements; 15,925 nodes |
| Element block | exactly one block named `block_1` containing every element (entire domain is optimizable; no fixed or non-design blocks) |
| Nodeset `ns_fix` | all nodes on the face x = 0 (325 nodes) |
| Nodeset `ns_load` | all nodes on the edge x = 2, y = 0, spanning z ∈ [0, 0.5] (13 nodes) |
| Sideset `ss_sym` | all element faces lying on the cut plane z = 0.5 (1,152 faces) |
| Mesh generator | approved Coreform Cubit in batch mode (no graphics); export Exodus II, dimension 3 |
| Mesh verification | before any optimization, verify element/node counts, bounding box, block name, nodeset sizes and the sideset size, and keep the verification record |

## 4. Material (locked)

Isotropic linear elastic, Young's modulus E = 1.0, Poisson's ratio ν = 0.3, assigned to `block_1`.

## 5. Boundary conditions and load (locked)

| Item | Value |
|---|---|
| Fixed support | `ns_fix`: u_x = u_y = u_z = 0 (nodeset, fixed value) |
| Structural symmetry | `ss_sym`: u_z = 0 (normal displacement fixed on the cut plane; applied through the sideset) |
| Load | concentrated nodal load on every node of `ns_load`, direction y, value −1.0 per node (total −13.0); no tractions, no body forces, no other loads |

## 6. Optimization formulation (locked)

| Item | Value |
|---|---|
| Objective | minimize mechanical compliance; weighted-sum objective with the single compliance criterion, weight 1, evaluated by the analyze service |
| Constraint | volume ≤ 15 % of the design-domain volume: `relative_target 0.15`, type `less_than`, evaluated by the engine service |
| Discretization | density; uniform initial density 0.15 |
| Material interpolation | SIMP (single phase), exponent 3.0 (runtime default), minimum value 1e-3; the compliance criterion also uses `minimum_ersatz_material_value 1e-3` |
| Optimizer | Optimality Criteria (OC), runtime default tolerances; `normalize_in_aggregator false`; `update_problem true` on the engine service with `update_problem_frequency 1` |
| Iterations | exactly `max_iterations 50`; the run must reach the iteration cap (a convergence stop before 50 iterations is a deviation that must be reported) |
| Filter | Helmholtz (PDE) filter, absolute radius 0.15, boundary-sticking penalty 1.0, with the cut-plane sideset `ss_sym` declared as a symmetry plane of the filter, so the filter treats the cut as a reflective plane and the sticking penalty acts only on the real outer boundaries |
| Services | engine service and analyze service, one processor each; single-rank performers; no mesh decomposition |
| Output | nodal displacements dispx, dispy, dispz from analyze; engine output of the `control` and `topology` fields |

**Generated-configuration requirement.** Morphorm translates the input deck into runtime configuration files (XMLGenerator output).
Before submitting the optimization, verify in the *generated* Helmholtz configuration that the filter length scale, the surface
(boundary-sticking) length scale and the symmetry-plane sideset are all present, and verify in the generated analyze configuration
that the material, SIMP values, load and all three displacement conditions are present. A setting that appears in the input deck but
not in the generated configuration is not applied; such a run does not satisfy this specification. Keep the generated configuration
files that were used by the accepted run.

## 7. Execution (locked)

- Run the optimization with the approved Morphorm runtime (`software_contract.md`) as a Slurm batch job using the frozen resources in `compute_resources.md`.
- One uninterrupted optimization of 50 iterations. Do not run Morphorm on the agent-host node.

## 8. Required deliverables (locked paths, relative to the trial root)

| Path | Content |
|---|---|
| `outputs/mesh.jou` | the Cubit journal (or equivalent scripted procedure) that produced the mesh |
| `outputs/mesh.exo` | the Exodus mesh used by the accepted run |
| `outputs/mesh_verification.txt` (or `.json`) | the mesh verification record |
| `outputs/input_deck.i` | the Morphorm input deck of the accepted run |
| `outputs/job_script.sbatch` | the Slurm script of the accepted run |
| `outputs/generated_config/` | every XMLGenerator output file used by the accepted run (`interface.xml`, `*_input_deck.xml`, `*_operations.xml`, `mpirun.source`) |
| `outputs/morphorm_oc_optimizer_diagnostics.txt` | optimizer diagnostics (iteration history) of the accepted run |
| `outputs/engine_output.exo` | engine output (design history) of the accepted run |
| `outputs/final_analyze_output.exo` | the final analyze output file (iteration 50: density field and displacements) |
| `outputs/run_logs/` | stdout/stderr of the accepted Slurm job and the Morphorm run log(s) |
| `outputs/SHA256SUMS.txt` | SHA-256 of every file under `outputs/` (excluding itself) |
| `jobs/job_ids.txt` | one Slurm job ID per line for every job submitted in this trial (including failed or cancelled ones) |
| `work/run_summary.md` | the run summary required by `provenance_requirements.md` |
