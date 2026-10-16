# Artifact selections — E3-baseline-trial_01 (E3-SPC-v1)

Every candidate artifact examined, with the decision and the reason. Collections and paths are as listed in
`catalog/permitted_storage_catalog.yaml`; the complete access log is `provenance/sources_searched.tsv`.

## e3-control (snapshot in agent-inputs/control/, commit 62954055b4e848f2155258c5b8c628eab97c8586)
| Artifact | Decision | Use / reason |
|---|---|---|
| task/frozen_task_specification.md | **used** | the locked specification (E3-SPC-v1) every setting was taken from; byte-identical (SHA-256 f1bd0b56…) to the private-source `problem_specification.md` |
| task/required_deliverables.md, task/task_prompt.md | used | deliverable checklist and task statement |
| catalog/permitted_storage_catalog.yaml, artifact cards | used | defined where to search and the access methods |
| protocol/*.md | used | access, staging, cache and provenance rules followed |
| scripts/non_destructive_preflight_helpers/* | used | record_search, stage_file, globus_stage_file, return_file, verify_collection, record_node_placement, hash_outputs |
| catalog/checksums.sha256 | used | verified: all 27 files present pass; `.gitignore` is listed but absent from the snapshot (noted, not a blocker) |

## e3-private-source (Globus collection 6dcea62e-130d-47a9-8b77-80fba6f58693; staged by globus_stage_file.sh)
| Artifact | Decision | Use / reason |
|---|---|---|
| target_materials/symmetry_plane_cantilever/problem_specification.md | **used** | confirmed identical to the control specification; returned to work/reference/ |
| target_materials/symmetry_plane_cantilever/README.md, permitted_starting_materials/README.md | used (read) | confirm there are no starting materials; workflow must be constructed |
| target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png | staged, not needed | problem figure; the text specification was sufficient and unambiguous (not opened) |
| documentation/curated_permitted_materials/software_contract.md | **used** | approved commands: cubit batch flags, XMLGenerator, `bash mpirun.source`, python3 |
| documentation/curated_permitted_materials/compute_resources.md | **used** | the frozen `#SBATCH` resources in the job script |
| documentation/version_provenance.yaml, curated_readme.md, MANIFEST_README.md, README.md, MANIFEST.tsv | used (read) | versions of manuals/runtime, collection layout |
| manuals/Morphorm_User_Manual.pdf (text extracted with pdftotext into work/manual_text/) | **used** | §2.5/§4.6 filter-block vs legacy keywords and `symmetry_plane_location_names`; §3.3 boundary-condition keywords; §6.10 material-interpolation defaults (SIMP exponent 3.0); §9 output/diagnostics file names and termination messages |
| manuals/Morphorm_Theory_Manual.pdf (text extracted) | used (read) | §4.4 Helmholtz boundary-sticking formulation (surface length scale ℓΓ) for interpreting the generated "Surface Length Scale" |

## e3-chpc-candidate-archive (read-only POSIX; manifest verification PASS)
| Package | Decision | Reason |
|---|---|---|
| example_07 (full 2×1×1 Helmholtz cantilever: deck, journal, README, problem card, provenance; figure not staged) | **adapted** | the closest authentic workflow: same physics, material, load type, SIMP/Helmholtz/OC/50-iteration settings as the target. Its journal was adapted to the half domain (z width 0.5, sideset `ss_sym` added) and its deck was adapted (second boundary condition `ss_sym` dispz=0; Helmholtz symmetry-plane keyword; `mesh.exo`). The PNG figure was not needed and not staged. |
| example_16_restart (stage-1 deck, restart deck, journal) | **not used** | restart-specific two-stage workflow (20 + 40 iterations, `write_restart_file`, `initial_guess_file_name`); the task is one uninterrupted 50-iteration run. Its physics is the full cantilever already covered by Example 7. Examined only (README, problem card, provenance, decks, journal read in place). |
| example_01 (bolted bracket, tet mesh, kernel filter, traction loads, fixed block) | **not used** | different geometry, mesh type, filter type (kernel) and load type; contains nothing the target needs that Example 7 does not. Examined only. |
| example_13 (2-D L-bracket, QUAD4, Helmholtz, traction) | **not used** | 2-D, different geometry and loading; the only relevance (Helmholtz keywords) is already in Example 7. Examined only. |
| archive README.md, MANIFEST.sha256 | used | package overview; manifest verification (PASS) |

## Decisions that affected the deck
1. **Helmholtz symmetry plane.** The User Manual lists `symmetry_plane_location_names` as a filter-block keyword with an
   equivalent legacy study-level keyword. With the filter-block form (and with the legacy keyword added to the study block
   while a filter block was still used) XMLGenerator did **not** emit the sideset into `analyze_helmholtz_input_deck.xml`
   (tests in work/deck/ and work/deck_tests/A/). With the fully legacy form (`filter_type helmholtz`,
   `filter_radius_absolute 0.15`, `boundary_sticking_penalty 1.0`, `symmetry_plane_location_names ss_sym` in the study
   block, no filter block; work/deck_tests/B/) it emits `Symmetry Plane Sides = {ss_sym}`. All other generated files are
   byte-identical between the two forms. The accepted run uses the legacy form, because the specification requires the
   setting to be present in the generated configuration.
2. **Symmetry displacement condition on a sideset.** The manual states Dirichlet conditions are nodeset-only, but the
   specification locks `ss_sym` applied through the sideset. The deck uses `location_type sideset` / `location_name ss_sym`
   as locked; XMLGenerator emitted it as "Displacement Z with ID 4, Sides = ss_sym" in the generated analyze configuration,
   and the run proceeded with it.
3. **SIMP exponent.** Left at the runtime default (3.0) as the specification says; verified as `Exponent = 3.0` in the
   generated analyze configuration. `minimum_value 1e-3` set explicitly in `material_interpolation 1` and
   `minimum_ersatz_material_value 1e-3` in the compliance criterion.
4. `normalize_in_aggregator false` was verified by comparison with a `true` translation (work/deck_tests/C/): `false`
   produces no `<Normals>` block and no "Initial Criterion Value" shared data.
