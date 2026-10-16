# Candidate package example_01 — Morphorm Example 1 (bolted bracket, static compliance)

**Classification:** general example. **Source:** Morphorm Examples Manual, topology optimization / mechanical, Example 1.

Minimum-compliance topology optimization of a filleted L-bracket with four bolt holes and a mounting hole.
The journal builds the geometry, meshes it with tetrahedra (size 0.24) and defines two blocks: `block_1` (design) and
`block_2` (fixed, non-design material around the bolts), nodesets `ns_1`, `ns_2` (fixed) and sidesets `ss_1`, `ss_2`
(traction loads). The deck uses a mechanical-compliance objective, a relative volume constraint of 0.3, steel properties,
a kernel filter (`radius_scale 2`), Optimality Criteria and 100 iterations.

| File (`selected_source_materials/`) | What it is |
|---|---|
| `topology_mech_ex1.i` | shipped input deck |
| `topology_mech_ex1.jou` | shipped Cubit journal (recorded with Cubit 15.3) |
| `problem_geometry_figure.png` | manual figure of the meshed design domain and boundary regions (no result) |

Omitted: meshes, completed outputs, renders, histories, logs (see `problem_card.yaml`).
