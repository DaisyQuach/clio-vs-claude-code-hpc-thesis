# Artifact selections — E3-baseline-trial_03 (E3-SPC-v1)

Every candidate artifact examined during discovery, the decision taken, and the reason. Collections and access methods
are those of `catalog/permitted_storage_catalog.yaml` (v5). Staged copies are listed in `staging-manifest/staged_files.tsv`.

## e3-control (control snapshot, commit 62954055b4e848f2155258c5b8c628eab97c8586)

| Artifact | Decision | Use / reason |
|---|---|---|
| `task/frozen_task_specification.md` | used | the locked specification E3-SPC-v1; every mesh, material, BC, load, formulation and execution value was taken from it |
| `task/required_deliverables.md`, `task/task_prompt.md` | used | deliverable checklist and task statement |
| `catalog/permitted_storage_catalog.yaml`, `catalog/artifact_cards/*.yaml` | used | discovery: which collections exist, how to reach them, what each package contains |
| `protocol/*.md` | used | access, staging, cache and provenance rules followed throughout |
| `scripts/non_destructive_preflight_helpers/*` | used | record_search.sh, stage_file.sh, globus_stage_file.sh, verify_collection.sh, record_node_placement.sh, hash_outputs.sh |

## e3-private-source (Globus collection 6dcea62e-130d-47a9-8b77-80fba6f58693; listed with `globus ls -r`, 13 files; all staged by `globus_stage_file.sh`)

| Artifact | Decision | Use / reason |
|---|---|---|
| `documentation/curated_permitted_materials/software_contract.md` | used | approved software interface: loader path, `cubit -batch -nographics -nojournal -input`, `XMLGenerator`, `bash mpirun.source` |
| `documentation/curated_permitted_materials/compute_resources.md` | used | frozen `#SBATCH` resources copied verbatim into `jobs/job_morphorm_spc_v1.sbatch` |
| `manuals/Morphorm_User_Manual.pdf` | used | input-deck syntax: boundary_condition block (§3.3), Helmholtz filter keywords `filter_radius_absolute`, `boundary_sticking_penalty`, `symmetry_plane_location_names` (Study › Filters, Tables 2.5.12–2.5.16), material_interpolation block, output block (§5.1), diagnostics/output files (§9). Text extracted with `pdftotext` into `work/manual_text/` for searching. |
| `manuals/Morphorm_Theory_Manual.pdf` | staged, consulted only via text extraction; not needed for any setting | formulation background; no locked value depends on it |
| `target_materials/symmetry_plane_cantilever/problem_specification.md` | used (cross-check) | SHA-256 f1bd0b56… identical to the control copy of the specification |
| `target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png` | used (visual cross-check) | confirms half domain, red `ns_fix` face at x = 0, blue `ns_load` edge at x = 2, y = 0, green `ss_sym` cut plane |
| `target_materials/symmetry_plane_cantilever/README.md`, `permitted_starting_materials/README.md` | read | confirm that no starting deck/journal/mesh is provided and that the workflow must be constructed |
| `README.md`, `MANIFEST.tsv`, `documentation/curated_readme.md`, `documentation/MANIFEST_README.md`, `documentation/version_provenance.yaml` | read | collection overview, per-file hashes, software version provenance (runtime engine 0d767ac7 / analyze 60c5e37c, cubit-edu/2026.8) |

## e3-chpc-candidate-archive (read-only POSIX; manifest verification PASS; all four packages examined by `cat`)

| Package | Decision | Reason |
|---|---|---|
| `example_07/` (full 2×1×1 Helmholtz cantilever, HEX8 48×24×24, OC, 50 it.) | **adapted** (deck, journal; README/problem card/provenance/figure staged for the record) | Closest related workflow: same brick cross-section, same fixed face, same line load (−1 per node on x = 2, y = 0), same E/ν, SIMP min 1e-3, same compliance objective, volume ≤ 0.15 evaluated by the engine, Helmholtz radius 0.15 with sticking penalty 1.0, OC, 50 iterations, update_problem/frequency 1, initial density 0.15, normalize_in_aggregator false. Adaptations: journal width 1.0 → 0.5 (48×24×12 elements), added sideset `ss_sym` on z = 0.5, export name `mesh.exo`; deck: added boundary_condition 2 (`ss_sym`, dispz = 0, applied through the sideset), added `symmetry_plane_location_names ss_sym`, explicit `material_interpolation` block (single_phase SIMP, exponent 3.0, minimum 1e-3), Helmholtz keywords declared at study level (see note below), mesh name `mesh.exo`. |
| `example_16_restart/` (same cantilever, 20 + 40 iterations with restart) | not used | Restart-specific two-stage workflow; the specification requires one uninterrupted 50-iteration run with no restart. Its physics settings duplicate example_07, which was already selected; read only to confirm the keyword usage (`update_problem`, `write_restart_file`). |
| `example_13/` (2-D L-bracket, QUAD4, Helmholtz, traction load, 30 it.) | not used | 2-D problem, traction load on a sideset, different geometry, constraint and iteration count; no symmetry plane. Confirms the Helmholtz filter-block syntax only. |
| `example_01/` (bolted L-bracket, tetrahedra, fixed block, kernel filter, 100 it.) | not used | Unrelated geometry, tet mesh, non-design block, traction loads, kernel filter, `single_criterion` objective; nothing matches the locked settings. |

### Note on the Helmholtz keyword placement (recorded deviation from the candidate's style, not from the specification)
With the filter-block form used by example_07 (`begin filter 1 … symmetry_plane_location_names ss_sym … end filter`),
the approved XMLGenerator produced a Helmholtz configuration with `Length Scale` and `Surface Length Scale` but **without**
`Symmetry Plane Sides`, and it logged that `filter_radius_absolute`/`boundary_sticking_penalty` were "not set" (the surface
length scale came from a default). The specification's generated-configuration requirement therefore failed
(`work/xmlgen_tests/A_filterblock/generated_config_verification.txt`). The User Manual's legacy study-level form
(`filter_type helmholtz`, `filter_radius_absolute 0.15`, `boundary_sticking_penalty 1.0`, `symmetry_plane_location_names ss_sym`
in the study block; forms must not be mixed) produced `Length Scale 0.043301` (= 0.15/(2√3)), `Surface Length Scale 1.0` and
`Symmetry Plane Sides {ss_sym}`, with every other generated file byte-identical. The accepted deck uses the study-level form.
Scratch translations: `work/xmlgen_tests/{A_filterblock,B_legacy_study,C_mixed,D_filterblock_symm_in_study_only}`.
