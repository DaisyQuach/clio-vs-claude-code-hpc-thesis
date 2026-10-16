# Candidate package example_02 — Morphorm Example 2 (prune-and-refine continuation)

**Classification:** distinct workflow. **Source:** Morphorm Examples Manual, topology optimization / mechanical, Example 2.

A continuation of the Example 1 bracket problem that adds a third service (`code prune`, 4 processors) and the study
method `prune_and_topology`: the mesh is pruned and refined (`number_of_refines 1`, `number_buffer_layers 2`) around an
initial-guess design read from `engine_output.exo`, and the volume constraint is an absolute target. The deck reads the
Example 1 mesh (`topology_mech_ex1.exo`). It cannot run on its own: it needs the Example 1 mesh (journal in
`../example_01/`) and a completed Example 1 engine output, which is a result and is not included.

| File (`selected_source_materials/`) | What it is |
|---|---|
| `topology_mech_ex2.i` | shipped input deck (no journal is shipped for this example) |

Note on origin: Example 2 is not present in the curated example-run collection; its deck was taken from the Morphorm
documentation source tree (see `provenance.yaml`).
