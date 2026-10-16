# Example 8 — Source Audit (Helmholtz Filter with a Symmetry Plane)

Researcher-only. Written 2026-10-09 (UTC) before any reference execution for the new `Thesis/` study.
All inspected locations were read only. Absolute paths below are under `/uufs/chpc.utah.edu/common/home/chet/Daisy/`
(the task's spelling `/uufs/chpc.utah.edu/common/home/u1282901/chet/Daisy/` resolves to the same directory; `readlink -f` verified).

## 1. Canonical manual section

| Item | Value |
|---|---|
| Manual file | `morphorm_manuals/examplesmanual.pdf` ("Examples Manual, Release 1.0.0", 716 PDF pages, created 2026-07-15) |
| Manual SHA-256 | `7fc32762247845fb89045c9eac9b422e57d49d4a68b1bdc0ed04864c9271c23d` |
| Section | §7.2.8 "Example 8: Helmholtz Filter with a Symmetry Plane" (Chapter 7 Topology Optimization, §7.2 Mechanical) |
| Pages | PDF pages 506–510 = printed pages 500–504 (printed = PDF − 6); table of contents line 127 confirms printed p. 500 |
| Figures / listing | Fig. 7.2.19 (half domain, mesh, `ns_fix`, `ns_load`, `ss_sym`), Listing 7.2.10 (input deck), Fig. 7.2.20 (optimized half, density ≥ 0.5, colored by displacement magnitude) |
| Dependency | §7.2.7 Example 7 (PDF 500–506, printed 494–499) defines the full 2 × 1 × 1 cantilever that Example 8 halves |
| Extracts kept | `manual_reference/examplesmanual_sec7.2.8_pdf506-510_printed500-504.txt`, page images `examplesmanual_page-50{6..10}.png`, Example 7 context text, User Manual pp. 29–30 (`update_problem_frequency`) |
| RST source of the section | `Morphorm/docs/examples/topology_optimization/mech/examples_topology_optimization_mech_ex8.inc` (SHA-256 `a514539bd6fb29b6757cfe96ebd1aff547a8516b158929c37d5e23a521866427`); it `literalinclude`s the deck below, so the printed listing and the shipped deck share one source |

## 2. Canonical source files (selected)

| Role | Absolute path | SHA-256 | Bytes |
|---|---|---|---|
| **Canonical journal** | `Morphorm/docs/examples/input_decks/topology_optimization/mech/topology_mech_ex8.jou` | `cd852856c747047fe57988f68d31d585cd0800bfc72468b53813cbe2c9ec46a6` | 1391 |
| **Canonical deck** | `Morphorm/docs/examples/input_decks/topology_optimization/mech/topology_mech_ex8.i` | `01a76bf2fcbbd34ba919c0aa7e023c409224a000b2b41c2a6ec48f932986a5ff` | 1898 |
| Driver named by the manual (`python runmorphorm.py topology_mech_ex8.i`) | `Morphorm/engine/python/runmorphorm.py` | `70bd98cebb38bb77b3509b15d178bedd14bace8c775c004771b0217df782ae35` | 2678 |
| Manual Fig. 7.2.19 | `Morphorm/docs/examples/figs/topology_optimization/mech/topology_original_geom_mech_ex8.png` | `2cc53d2243e7fc8435d8413a5bc89f73a194df4c38164310004354c11432563d` | 500087 |
| Manual Fig. 7.2.20 | `Morphorm/docs/examples/figs/topology_optimization/mech/topology_opt_mech_ex8.png` | `8bca07753413e232ccc4272201dd7cdddaa27c9d3c9b8e31b93a1f8c4127f055` | 152223 |

Immutable copies (mode `a-w`) are in `source_inputs/`; per-file hashes in `source_inputs_sha256.tsv`. All source files carry
mtime 2026-08-21 22:13 (the docs checkout); none has changed since the 2026-10-07 package (`Morphorm_ground_truth/Example_08/provenance/source_artifacts.tsv` lists identical hashes).

**No mesh file, criterion history, or completed output for Example 8 exists anywhere in the Morphorm source tree.** The mesh
must be generated from the journal (the manual says so explicitly: `cubit -batch -nographics -nojournal -input topology_mech_ex8.jou`).
The related regression test `morphormtests/enginetests/regression/Analyze_Helmholtz3D_SurfaceLengthScale_SymmPlane_OC` uses a different mesh (`beam.exo`) and is **not** a source for this example.

Files required to reconstruct the example: exactly the journal, the deck, and the driver above (plus Cubit and the approved Morphorm runtime).

## 3. Historical completed outputs (validation evidence only, never copied into the new reference)

| Location | What | Use |
|---|---|---|
| `Morphorm_ground_truth/Example_08/` (2026-10-07, approved runtime, job steps of allocation 16068475) | shipped deck executed unmodified; mesh `0a0a3a7d…500ab4`; final compliance 1.468985e5 at iteration 50; `symmetry_plane_location_names` found to be dropped by XMLGenerator | numerical cross-check of the rebuilt canonical run |
| `experiments_groundTruth/Example8_SymmetryPlane/run_16053535` and `Morphorm_Full_Examples_Tests/Example8_SymmetryPlane` (2026-10-04, developer runtime) | same deck under the developer Spack environment; bitwise identical to the above per `crosscheck_vs_prior_developer_runtime_run.json` | secondary cross-check only |
| `Morphorm_ground_truth/Experiment1/reference_case` (2026-10-09, earlier session) | a *controlled thesis reference derived from Example 8*: 40 × 20 × 10 mesh, SIMP floor 1e-9, `single_criterion`, nodeset symmetry BC. **Not** the manual example | not comparable to the frozen Example 8 formulation; not used |
| `ThesisExperiments/runs/E1_uninterrupted_agent/baseline/trial_0*` (pilot) | agent-constructed meshes/decks (h = 0.05 or 1/32); preliminary evidence | not used for the reference |

## 4. Field-by-field configuration (manual vs shipped deck vs journal)

| Field | Manual statement (printed page) | Shipped deck / journal value | Status |
|---|---|---|---|
| Geometry | half-width cantilever 2 × 1 × 0.5, i.e. Example 7's 2 × 1 × 1 brick cut at the mid-width plane z = 0.5; z ∈ [0, 0.5] modeled (p. 500) | journal: `len 2.0`, `ht 1.0`, `hwd 0.5`; brick moved so the back-bottom-left corner is at the origin (x ∈ [0,2], y ∈ [0,1], z ∈ [0,0.5]) | match |
| Mesh | "structured HEX8 elements" (p. 500, 503); no element count printed | journal: `esize 0.0416667` (= 1/24), scheme map → 48 × 24 × 12 = 13,824 HEX8, 15,925 nodes; block 1 `block_1` HEX8 | journal supplies the resolution; manual silent |
| Fixed support | x = 0 face, nodeset `ns_fix`, all displacements fixed (p. 500, 502) | journal: nodes with x < esize/2 → `ns_fix`; deck BC 1: `fixed_value`, nodeset `ns_fix`, dispx dispy dispz = 0 | match |
| Load | bottom-right edge (x = 2, y = 0), nodeset `ns_load`, transverse −y "concentrated line load" (p. 501–502) | journal: nodes with x > len − esize/2 and y < esize/2 → `ns_load` (13 nodes); deck load 1: `concentrated_load`, nodeset `ns_load`, direction y, value −1 (per node) | match |
| Symmetry (structural) | z = 0.5 cut, sideset `ss_sym`, normal displacement u_z = 0 (p. 500, 502) | journal: surface with z > hwd − esize/2 → sideset 1 `ss_sym` (1,152 faces); deck BC 2: `fixed_value`, sideset `ss_sym`, dispz = 0; residual `boundary_condition_ids 1 2` | match |
| Symmetry (filter) | `symmetry_plane_location_names ss_sym` in the filter block makes the filter "treat the cut as a reflective plane" (p. 500–501) | deck filter 1: `symmetry_plane_location_names ss_sym` | **written identically, but see §5: the runtime drops it** |
| Material | isotropic linear elastic, E = 1.0, ν = 0.3 (p. 500) | deck material 1: `isotropic_elastic`, `youngs_modulus 1.0`, `poissons_ratio 0.3`; block 1 → material 1 | match |
| SIMP / interpolation | not printed as prose; Listing 7.2.10 has `material_interpolation 1 / minimum_value 1e-3` and `minimum_ersatz_material_value 1e-3` on the compliance criterion; no exponent printed | deck identical; generated XML: SIMP exponent 3.0 (runtime default), Minimum Value 1e-3 (both residual and objective) | match (exponent is the documented default) |
| Objective | minimize compliance (p. 501): `objective weighted_sum`, criterion 1 `mechanical_compliance`, service 2, scenario 1, weight 1 | deck identical | match |
| Constraint | volume ≤ 15 %: criterion 2 `volume`, `relative_target 0.15`, `less_than`, `service_id 1` (p. 501–502) | deck identical; generated `NormalizedTargetValue 0.15` vs `Design Volume` | match |
| Filter | Helmholtz, `radius_absolute 0.15`, `boundary_sticking_penalty 1.0` (p. 501) | deck identical; generated `Length Scale 0.043301` (= 0.15 / (2√3)), `Surface Length Scale 1.0` | match |
| Optimizer | Optimality Criteria (p. 501): `optimization_algorithm oc`, `discretization density`, `initial_density_value 0.15`, `normalize_in_aggregator false` | deck identical; generated OC tolerances 1e-4 / 1e-8 / 1e-8 (defaults) | match |
| Iterations | `max_iterations 50` (p. 503) | deck `max_iterations 50` | match |
| Update frequency | listing prints `problem_update_frequency 1` (p. 503) | deck `update_problem_frequency 1` (the keyword the User Manual §2.2.7 defines; the printed spelling is not a parsed key) | documentation keyword difference only |
| Services | listing prints `number_ranks 1` in both service blocks | deck has no `number_ranks` (not a parsed key); `number_processors 1` each; generated `mpirun.source` runs 3 single-rank performers | documentation keyword difference only |
| Output | `dispx dispy dispz` (listing) | deck identical | match |
| Execution | `python runmorphorm.py topology_mech_ex8.i` (p. 504) | driver copied; it runs `XMLGenerator` then `./mpirun.source` | match |
| Published result | Fig. 7.2.20 only: visual; mirroring across z = 0.5 "recovers the full cantilever of Example 7"; no compliance or volume number printed (p. 504) | — | numeric target unavailable from the manual |

## 5. Discrepancy carried forward (not concealed): the filter symmetry plane is dropped at translation

Host-side translation of the unmodified shipped deck with the approved runtime's `XMLGenerator` (this audit, 2026-10-09; see
`reference_case/preflight_canonical/` after the build) produces an `analyze_helmholtz_input_deck.xml` **without** `Symmetry Plane Sides`.
The same finding is documented in `Morphorm_ground_truth/Example_08/scalar_results/generated_filter_xml_symmetry_check.txt` and traced to
`engine/src/input_generator/parser/XMLGeneratorFilterChainUtilities.cpp` (filter-block branch copies only radius/sticking penalty).
Consequently the shipped deck, as executed, applies the boundary-sticking penalty on the cut face and does **not** realize the manual's
central claim (reflective filter across the cut; mirrored half recovers Example 7). The structural u_z = 0 condition *is* applied.

The User Manual (pp. 48, 50, 56) documents the keyword in both forms: inside a `filter` block and as the legacy study-level keyword
(`filter_type helmholtz`, `filter_radius_absolute`, `boundary_sticking_penalty`, `symmetry_plane_location_names` inside `begin study`).
Host-side translation of a variant deck that moves the four filter keywords into the study block (no other change) yields a generated
configuration **byte-identical** to the canonical translation in all seven other files and adds exactly
`<Parameter name="Symmetry Plane Sides" type="Array(string)" value="{ss_sym}"/>` to the Helmholtz deck.

**Decision for the rebuild:** execute both (a) the canonical shipped deck unmodified ("manual listing as executed by the frozen software")
and (b) the documented symmetry-honored variant ("manual formulation as described"). Which of the two is the accepted E1 reference is a
researcher decision recorded in `reference_case/ACCEPTANCE_SPEC.md` (`reference_policy`); until it is set, the scorer returns `needs_review`.
This is flagged in `Thesis/BUILD_REPORT.md`.

## 6. Approved software and Slurm contract (from the read-only pilot workspace)

| Item | Value | Evidence |
|---|---|---|
| Morphorm runtime | `module use ThesisExperiments/common/modulefiles/Core; module load morphorm/approved-runtime` (+ CHPC `gcc/11.2.0`, `openmpi/5.0.3`) | `ThesisExperiments/common/formal_configuration.md` (frozen 2026-10-07T06:13:31Z), `scripts/load_approved_software.sh` (`d459b935…6deab37`) |
| Runtime identity | modulefile `dec9d78b15cd0a5925f9e4907bce8f0f9d6c9859c24e952e51e8a849bc93e58d`; `env.sh` `131300a16632ffa48ddc00948f8fd11610d9aac454a83a86a525027a24acfdf8`; inventory `SHA256SUMS` `fa0d97b93a7990271813eccf8768e14465266853a83ef8adab9e6987b4e3e4d2`; engine `0d767ac7`, analyze `60c5e37c` (PROVENANCE.md) | hashes recomputed 2026-10-09; identical to the frozen record |
| Cubit | personal module `cubit-edu/2026.8` (Coreform Cubit 2026.8+69344, educational license), modulefile `9c5bc2f9e266616ceebd384d82d0859d9977e0085635053061652728704819ad` | `formal_configuration.md`; `approved_tools/coreform_cubit/PROVENANCE.md` |
| Preflight on this host (notch351, 2026-10-09) | modules load; `python3` 3.13.5 with numpy 2.3.1 / netCDF4 1.7.2; `mpiexec` Open MPI 5.0.3; `cubit` wrapper present | this session |
| Slurm contract (Morphorm jobs) | `--account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00`, no GPU | `ThesisExperiments/common/base_inputs/compute_resources.md` (`101ab5c7…0d9818`), `formal_configuration.md` |
| Agent-host contract | same partition/account, 1 node, 8 CPUs, 32 GB, 02:00:00 | `formal_configuration.md` |

## 7. Conclusion

The canonical source for Example 8 is unambiguous: `topology_mech_ex8.jou` + `topology_mech_ex8.i` + `runmorphorm.py`, all hash-pinned above.
Every formulation field needed by the frozen specification is determined by the manual plus the journal (resolution). Reference execution may proceed.
The one meaningful discrepancy (filter symmetry plane dropped by the frozen software) is documented in §5 and is handled by executing both
the canonical deck and a documented variant, with the acceptance policy left to the researcher.
