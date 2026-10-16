# Example 8 (Symmetry-Plane Cantilever) — researcher-only reference record

This directory holds **records only**. No completed Example 8 deck, journal, mesh, Exodus output, log, render, history,
tolerance or accepted result was copied into the E3 tree. The authoritative materials stay where they are (read-only):

| Location | What it is | Hash record here |
|---|---|---|
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Morphorm_Full_Examples_Tests/Example8_SymmetryPlane/` | 2026-10-04 full Example 8 run (deck, journal, mesh, run directory, renders, log, README) | `morphorm_full_examples_tests_example8.sha256` (126 files) |
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Morphorm_ground_truth/Example_08/` | 2026-10-06 ground-truth package (original inputs, mesh generation, reference run, scalar results, figures, provenance) | `morphorm_ground_truth_example_08.sha256` (178 files) |
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/ground_truth/example_8/` | thesis reference package used by E1 (source audit, reference_case with acceptance spec, both variants) | its own `reference_case/SHA256SUMS.txt` (not duplicated) |
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Morphorm/docs/examples/input_decks/topology_optimization/mech/topology_mech_ex8.{i,jou}` | shipped Example 8 deck and journal (docs-tree originals) | `../../setup/source_inventory.csv` |
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/morphorm_manuals/examplesmanual.pdf` | Examples Manual (contains the completed Example 8 listings, §7.2.8) | `../../setup/source_inventory.csv` |

Relationship to E1: the E3 frozen task specification (`github_control_repo_worktree/task/frozen_task_specification.md`)
reproduces the locked scientific values of `Thesis/common/frozen_example8/scientific_problem_specification.md`
(FROZEN-EX8-v1) §1–§7 without change; see `frozen_spec_derivation.md`. Whether the E1 reference package and its
`reference_policy: symmetry_honored_variant` apply unchanged to E3 scoring is a **researcher decision** not taken here.

Verification: `sha256sum -c --quiet <record>.sha256` (read-only).
