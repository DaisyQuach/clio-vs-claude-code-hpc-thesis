# Artifact selections — E3-baseline-trial_06 (E3-SPC-v1)

Every candidate artifact examined, with the decision and reasons. Collections and paths are those of the permitted
catalog (`agent-inputs/control/catalog/permitted_storage_catalog.yaml`). Nothing was examined outside them.

## e3-control (snapshot `agent-inputs/control/`, commit 62954055b4e848f2155258c5b8c628eab97c8586)

| Artifact | Decision | How used / why |
|---|---|---|
| `task/frozen_task_specification.md` (E3-SPC-v1) | **used** | the locked specification; every setting of the mesh, deck and job was taken from it |
| `task/required_deliverables.md`, `task/task_prompt.md` | used | deliverable checklist |
| `catalog/permitted_storage_catalog.yaml`, `catalog/artifact_cards/*.yaml` | used | to discover the collections and to pre-screen candidate packages (classification, summary, "no symmetry plane" notes) |
| `protocol/*.md` | used | access, staging, cache and provenance rules followed throughout |
| `scripts/non_destructive_preflight_helpers/*` | used | record_search.sh, globus_stage_file.sh, verify_collection.sh, record_node_placement.sh, hash_outputs.sh (stage_file.sh/return_file.sh were not needed: no archive file had to be copied byte-for-byte; the archive decks were read in place and adapted in `work/`) |
| `catalog/checksums.sha256` | used | verified all 24 snapshot files; `.gitignore` is listed but was not part of the snapshot archive (not a scientific input) |

## e3-private-source (Globus collection 6dcea62e-130d-47a9-8b77-80fba6f58693; all files staged by `globus_stage_file.sh`)

| Artifact | Decision | How used / why |
|---|---|---|
| `MANIFEST.sha256` | used | transferred first by the helper; every staged file was checked against it |
| `README.md`, `documentation/curated_readme.md`, `documentation/MANIFEST_README.md` | used (read) | orientation only |
| `documentation/curated_permitted_materials/software_contract.md` | **used** | approved commands: `cubit -batch -nographics -nojournal -input`, `XMLGenerator <deck.i>`, `bash mpirun.source`; runtime `python3` for verification |
| `documentation/curated_permitted_materials/compute_resources.md` | **used** | frozen `#SBATCH` resources copied verbatim into `jobs/morphorm_oc50_symplane.sbatch`; rule "do not run the optimization on the agent host" |
| `documentation/version_provenance.yaml` | used (read) | versions recorded in the run summary; confirmed the manual checksums |
| `manuals/Morphorm_User_Manual.pdf` | **used** | text-extracted (pdftotext) into `$E3_STAGING_DIR/derived/`; consulted for the Helmholtz filter keywords (`radius_absolute`, `boundary_sticking_penalty`, `symmetry_plane_location_names`, Tables 2.5.12/2.5.15), boundary-condition, load, material_interpolation, output and study keywords |
| `manuals/Morphorm_Theory_Manual.pdf` | **not staged / not used** | formulation background only; no deck syntax or locked value depends on it |
| `target_materials/symmetry_plane_cantilever/problem_specification.md` | used | SHA-256 f1bd0b56… identical to the control copy of the specification (confirmed by `diff`) |
| `target_materials/symmetry_plane_cantilever/README.md`, `permitted_starting_materials/README.md` | used (read) | confirm that no starting deck/journal/mesh exists for this task |
| `target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png` | staged, not needed | the specification text was sufficient; the figure's legend (README) agrees with ns_fix / ns_load / ss_sym |
| `MANIFEST.tsv` | staged, not used | duplicate of the manifest listing |

## e3-chpc-candidate-archive (read-only POSIX; manifest verified PASS)

| Package | Decision | Reasons |
|---|---|---|
| `example_07/` (full 2×1×1 Helmholtz cantilever, 48×24×24 HEX8, OC, 50 it.) | **adapted** (primary template) | Same physics, material (E=1, ν=0.3), load (concentrated −1 per node on ns_load), SIMP minimum 1e-3, volume 0.15 on the engine service, Helmholtz radius 0.15 with sticking penalty 1.0, OC, 50 iterations, `update_problem`, `normalize_in_aggregator false`, uniform initial density 0.15 — all equal to the locked values. Its journal (`topology_mech_ex7.jou`) was adapted to the half domain: width 1.0 → 0.5 (48×24×12), added sideset `ss_sym` on z = 0.5, export name `mesh.exo`. Its deck (`topology_mech_ex7.i`) was adapted: added `boundary_condition 2` (fixed_value, sideset `ss_sym`, dispz = 0), referenced it in the residual, added `type single_phase` / `model simp` to the material_interpolation block, added `symmetry_plane_location_names ss_sym` (study block), mesh name `mesh.exo`. Nothing was copied byte-for-byte; the adapted files are `work/mesh/mesh.jou` and `work/run/input_deck.i`. |
| `example_16_restart/` (two-stage restart of the same cantilever) | **not used** | Same physics as Example 7 but split into 20 + 40 iterations with a restart file; the specification requires one uninterrupted 50-iteration run. Its journal differs from Example 7 only in the export file name. Read for confirmation only. |
| `example_01/` (bolted L-bracket, tet mesh, kernel filter, tractions, fixed block) | **not used** | Different geometry, element type, filter type (kernel), load type (traction), non-design block and 100 iterations; nothing in it is closer to the locked settings than Example 7. Read to confirm the general deck block structure. |
| `example_13/` (2-D L-bracket, QUAD4, Helmholtz, traction) | **not used** | Two-dimensional, different geometry, load type and iteration count; only confirms the Helmholtz filter block syntax already present in Example 7. |
| `example_*/problem_geometry_figure.png` | not used | figures were not opened; the text decks/journals were sufficient |

## Deviations from the candidate template that were required by the specification

- `symmetry_plane_location_names ss_sym` placed in the **filter block** (manual Table 2.5.12 syntax) was accepted by XMLGenerator but **not translated**: the generated `analyze_helmholtz_input_deck.xml` lacked a symmetry-plane entry (attempt kept in `work/xmlgen_tests/attempt0_filter_block_keyword/`). Placing the keyword in the **study block** (legacy position) produced `Symmetry Plane Sides = {ss_sym}`; this deck (`work/run/input_deck.i`) is the accepted one. Scratch translations: `work/xmlgen_tests/A_study_keyword/` (adopted), `B_both/` (equivalent), `C_normalize_true/` (only to confirm that `normalize_in_aggregator false` is represented by the absence of a `<Normals>` element).
- The User Manual states essential boundary conditions must be on nodesets; the specification requires u_z = 0 through the sideset `ss_sym`. The deck follows the specification; XMLGenerator translated it to an Essential Boundary Condition with `Sides = ss_sym`, `Index 2`, value 0 (verified in `analyze_2_input_deck.xml`).
