# Candidate package example_16_restart — Morphorm Example 16 (optimization restart)

**Classification:** restart-specific workflow. **Source:** Morphorm Examples Manual, topology optimization / mechanical, Example 16.

Demonstrates checkpointing and restarting an optimization on the full 2 × 1 × 1 Helmholtz-filter cantilever
(structured HEX8, 48 × 24 × 24). Stage 1 (`topology_mech_ex16.i`) runs 20 OC iterations with `write_restart_file true`.
The restart deck (`topology_mech_ex16_restart.i`) runs 40 further iterations from a saved design
(`initial_guess_file_name initialguess.exo`, `initial_guess_field_name control`, `restart_iteration 20`). Physics, filter
and constraint settings are those of the full Helmholtz cantilever. The restart stage needs a stage-1 output, which is a
result and is not included.

| File (`selected_source_materials/`) | What it is |
|---|---|
| `topology_mech_ex16.i` | shipped stage-1 input deck |
| `topology_mech_ex16_restart.i` | shipped restart input deck |
| `topology_mech_ex16.jou` | shipped Cubit journal |
