# E3 CHPC candidate archive (read-only)

Curated, read-only packages of authentic Morphorm example workflows. Each package holds the shipped input files of one
example plus a `README.md`, a machine-readable `problem_card.yaml` (scientific role, classification, included files,
omitted result categories, hashes) and a `provenance.yaml` (original location and checksum of every file).

| Package | Example | Classification | Content |
|---|---|---|---|
| `example_01/` | 1 | general example | bracket deck, journal, geometry figure |
| `example_02/` | 2 | distinct workflow | prune-and-refine continuation deck |
| `example_07/` | 7 | distinct workflow | full Helmholtz-filter cantilever deck, journal, geometry figure |
| `example_16_restart/` | 16 | restart-specific workflow | stage-1 deck, restart deck, journal |

None of these packages contains completed results (Exodus outputs, renders, histories, logs, accepted summaries).
Whether, and how, any of them is useful for a given task is for the reader to judge from the packages themselves.
`MANIFEST.sha256` lists every file in the archive; verify with `sha256sum -c MANIFEST.sha256` from this directory.
Original locations in `provenance.yaml` are provenance records, not access paths.
