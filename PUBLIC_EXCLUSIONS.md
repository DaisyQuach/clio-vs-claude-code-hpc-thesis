# What the public copy leaves out

This public repository is a filtered copy of the private study record
(`DaisyQuach/clio-thesis-official-results`, available on request). Everything in it is unchanged except as listed here.

## Withheld because it is third-party copyrighted material (Morphorm LLC, all rights reserved)
- Text the agents extracted from the Morphorm User and Theory Manuals (`work/manual_text/`, `work/manuals/` and similar).
- Examples Manual excerpts and page images (`researcher_only/ground_truth/*/manual_reference/`), the Morphorm example
  sources (`ground_truth/*/source_inputs/`, `reference_case/inputs/`), the Morphorm example decks and Cubit journals
  `topology_mech_ex*` (including the researcher's edited reference variants), and the Morphorm driver `runmorphorm.py`.
- E3 source materials taken from Morphorm examples (`chpc_candidate_archive/*/selected_source_materials/`,
  `globus_source_root/.../permitted_starting_materials/`, `geometry_and_loading_figure.png`).
- The manual PDFs and other items already left out of the private copy (`EXCLUDED_FILES.md`).

## Withheld because it quotes that material
Raw agent transcripts and session exports, which contain manual text the agents read:
`transcript_*.jsonl`, `stream.jsonl`, `tool_inputs.jsonl`, CLIO `export*.json`, `messages.json`, `trace.json`,
`provenance_execution.json`, `stream_audit*.jsonl`, `sdk_transcripts/`, and the per-session `claude_config/` folders
copied with the session evidence. Per-call usage, results, session records, launch plans, run summaries, job records,
scores and all derived tables (`analysis/official_thesis_clio/data/`) are included, so every reported number can be
checked against the per-trial records; rebuilding the tables from raw transcripts needs the private copy.

## Redacted
`auth_status_isolated_config.json` (78 files): the account `email`, `orgId` and `orgName` values are replaced by
`<redacted>`. These files therefore no longer match their entries in the trial's `evidence_SHA256SUMS.txt`.

## Exact exclusion list used
```
work/manual_text/
work/manuals/
work/manual/
work/manual_txt/
work/manuals_txt/
researcher_only/ground_truth/example_8/manual_reference/
researcher_only/ground_truth/example_16/manual_reference/
researcher_only/ground_truth/example_8/source_inputs/
researcher_only/ground_truth/example_16/source_inputs/
researcher_only/ground_truth/example_8/reference_case/inputs/
researcher_only/ground_truth/example_16/reference_case/inputs/
chpc_candidate_archive/*/selected_source_materials/
permitted_starting_materials/
geometry_and_loading_figure.png
transcript_*.jsonl
stream.jsonl
tool_inputs.jsonl
sdk_transcripts/
export_transcript.json
export_full.json
export.json
messages.json
trace.json
provenance_execution.json
stream_audit*.jsonl
session_export*.json
session_messages.json
session_trace.json
claude_config/
runmorphorm.py
.claude.json
topology_mech_ex*
```
