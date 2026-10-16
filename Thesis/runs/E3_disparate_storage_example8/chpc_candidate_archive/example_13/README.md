# Candidate package example_13 — Morphorm Example 13 (2-D L-bracket, Helmholtz filter)

**Classification:** general example (2-D). **Source:** Morphorm Examples Manual, topology optimization / mechanical, Example 13.
**Source identifier:** `MORPHORM-CANDIDATE-EX13` (logical identifier, not a filesystem path).

Two-dimensional minimum-compliance optimization of an L-shaped bracket. The journal draws a 1 × 1 envelope with the
upper-right region removed (leg width 0.4, re-entrant corner at (0.4, 0.4)), meshes it with QUAD4 elements (pave scheme,
element size 0.0125; the journal's header comment says "structured", but the scheme used is pave) and exports a 2-D
Exodus mesh. The top edge of the vertical arm (y = 1) is clamped in `dispx`/`dispy` (nodeset `ns_fix`); a downward
traction (0, −1e5) acts on the right tip edge x = 1 (sideset `ss_load`). Isotropic elastic material (E = 200e9, ν = 0.3),
SIMP minimum value 1e-3, weighted-sum compliance objective, relative volume constraint 0.4 evaluated by the engine service,
Helmholtz filter (`radius_absolute 0.075`, `boundary_sticking_penalty 1.0`), density discretization with initial density
0.5, OC, 30 iterations. It models the whole domain and declares no symmetry plane.

The package is self-contained: the journal generates the mesh that the deck reads; nothing from another example is needed.

| File (`selected_source_materials/`) | What it is |
|---|---|
| `topology_mech_ex13.i` | shipped input deck |
| `topology_mech_ex13.jou` | shipped Cubit journal |
| `problem_geometry_figure.png` | manual figure of the meshed design domain, clamped edge and loaded edge (no result) |

Omitted: meshes, completed outputs, renders, histories, logs (see `problem_card.yaml`).
