# Candidate package example_07 — Morphorm Example 7 (full cantilever, Helmholtz filter)

**Classification:** distinct workflow. **Source:** Morphorm Examples Manual, topology optimization / mechanical, Example 7.

Minimum-compliance optimization of a full 2 × 1 × 1 cantilever, fixed on its x = 0 face and loaded by a transverse
concentrated line load (direction y, −1 per node) along the edge x = 2, y = 0. Structured HEX8 mesh (48 × 24 × 24, element
size 1/24), one design block, nodesets `ns_fix` and `ns_load`. E = 1.0, ν = 0.3, SIMP minimum value 1e-3, weighted-sum
compliance objective, relative volume constraint 0.15 evaluated by the engine service, Helmholtz filter
(`radius_absolute 0.15`, `boundary_sticking_penalty 1.0`), OC, 50 iterations. The example demonstrates how the Helmholtz
filter's boundary term removes the boundary-sticking artifact. It models the whole domain and declares no symmetry plane.

| File (`selected_source_materials/`) | What it is |
|---|---|
| `topology_mech_ex7.i` | shipped input deck |
| `topology_mech_ex7.jou` | shipped Cubit journal |
| `problem_geometry_figure.png` | manual figure of the meshed design domain, supports and load (no result) |
