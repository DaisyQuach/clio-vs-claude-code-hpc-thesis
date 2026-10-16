# E3 CHPC candidate archive (read-only)

Curated, read-only packages of authentic Morphorm example workflows. Each package holds the shipped input files of one
example plus a `README.md`, a machine-readable `problem_card.yaml` (scientific role, classification, included files,
omitted result categories, hashes) and a `provenance.yaml` (logical source identifier and checksum of every file).

| Package | Example | Classification | Content |
|---|---|---|---|
| `example_01/` | 1 | general example | bracket deck, journal, geometry figure |
| `example_07/` | 7 | distinct workflow | full Helmholtz-filter cantilever deck, journal, geometry figure |
| `example_13/` | 13 | general example (2-D) | 2-D L-bracket Helmholtz-filter deck, journal, geometry figure |
| `example_16_restart/` | 16 | restart-specific workflow | stage-1 deck, restart deck, journal |

None of these packages contains completed results (Exodus outputs, renders, histories, logs, accepted summaries).
Whether, and how, any of them is useful for a given task is for the reader to judge from the packages themselves.
`MANIFEST.sha256` lists every file in the archive; verify with `sha256sum -c MANIFEST.sha256` from this directory.

Source identifiers such as `MORPHORM-CANDIDATE-EX07` are logical identifiers. They are not filesystem paths and they are
not the original locations of the files; original locations are kept in researcher-side provenance records only.
