# researcher_only — never agent-visible

`ground_truth/example_8` and `ground_truth/example_16`: source audits (`SOURCE_AUDIT.md`), immutable canonical input copies
(`source_inputs/`), manual extracts (`manual_reference/`), rebuilt reference packages (`reference_case/`, with
`GROUND_TRUTH_CONSTRUCTION_REPORT.md`, `ACCEPTANCE_SPEC.md`, `REFERENCE_VALIDATION.md`, `acceptance_spec.json`, `SHA256SUMS.txt`).
`ground_truth/tools`: validation, summary, restart-evidence, generated-config, scoring and rendering tools.
`session_evidence/`: staged per-session launch records/transcripts during a run. `scores/`: scoring records. `evaluation_figures/`: figures.
No path under this directory may appear in any agent-visible document (checked by `automation/preflight.sh`).
