# Thesis: Claude Code baseline vs CLIO on HPC topology-optimization workflows (official results)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23408965.svg)](https://doi.org/10.5281/zenodo.23408965)

**How to cite:** Quach, D. (2026). *CLIO vs. Claude Code on HPC topology-optimization workflows: official thesis experiments
E1–E3 (data and automation)* (Version 1.0.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23408965
(this version; all versions: https://doi.org/10.5281/zenodo.23408964). Machine-readable: `CITATION.cff`.
**License:** code (`*.sh`, `*.py`) under MIT (`LICENSE`); data, documents, figures and slides under CC BY 4.0
(`LICENSE-DATA`). Third-party software, manuals and example files are not included (`PUBLIC_EXCLUSIONS.md`).

Counted (official) trials of experiments E1–E3 on CHPC notchpeak, Morphorm manual examples 8 and 16.
Baseline: Claude Code 2.1.295, run 2026-10-09/10. CLIO: clio-agent 0.9.5b5.post2 + iowarp-core 2.2.1 with the
factorio-flat 0.5.0 blueprint, driving the same Claude Code CLI, run 2026-10-13. Model `claude-fable-5-1` in both arms,
n = 5 counted trials per arm per experiment.

## Results at a glance

| | E1 (uninterrupted, ex. 8) | E2 (interrupted recovery, ex. 16) | E3 (disparate storage, ex. 8) |
|---|---|---|---|
| Accepted (CLIO / baseline) | 5/5 vs 5/5 | 5/5 vs 5/5 | 5/5 vs 5/5 |
| Cost, CLIO ÷ baseline | **0.72×** (p = 0.008) | **0.78×** (p = 0.008) | **0.83×** (p = 0.008) |
| Wall time | **1.22×** (Slurm node speed) | 0.85× (n.s.) | 0.91× (n.s.) |
| Time outside Slurm | 0.82× (n.s.) | **0.77×** | 0.94× (n.s.) |
| Output tokens | **0.68×** | **0.67×** | **0.70×** |

Full tables, excluded attempts, caveats and threats to validity: `THESIS_NOTES_methods_and_evaluation.md` (Part C).

## Layout

| Path | Content |
|---|---|
| `REPRODUCE.md` | **How to set up and run the experiments**: setup used (cluster, software, pins, agent systems), one-time preparation, commands for both arms, replacements, scoring and analysis |
| `setup/clio_deployment_config/` | CLIO deployment config used in every counted CLIO session (`config.yaml`, `mcp.yaml`, installed blueprint list) |
| `THESIS_NOTES_methods_and_evaluation.md` | Methods, evaluation and official results for E1–E3, both arms |
| `slides/CLIO_vs_Claude_Code_official_thesis.pptx` | Official results deck (built by `make_official_slides.py`) |
| `analysis/official_thesis_clio/` | `official_aggregate.py`, `official_compare.py`, `data/*.csv`, `figures/H1–H6`, batch wrappers and logs, baseline integrity snapshot |
| `Thesis/` | Copy of the experiment tree: design, automation (baseline and CLIO), frozen packets, every trial's workspace, logs and transcripts, scores, ground-truth scorer tools, evaluation figures |
| `PUBLIC_EXCLUSIONS.md` | What this public copy leaves out (copyrighted Morphorm material, raw transcripts) and what was redacted |
| `CITATION.cff`, `.zenodo.json`, `LICENSE`, `LICENSE-DATA` | Citation metadata and licenses |
| `EXCLUDED_FILES.md` | What was left out (software copies, Exodus binaries, runtime state, manuals, files > 50 MB) |

Paths inside the documents refer to the original CHPC locations
(`/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis` and `.../clioSessions/CLIO_E1_API_pilots`).
This repository is a public, filtered copy (2026-10-15) of the study record taken 2026-10-13; the CHPC tree remains the
primary record and the unfiltered copy is available on request.
It contains the official study only. The non-counted pilots and the clio-core engine tests are kept on CHPC
(`clioSessions/CLIO_E1_API_pilots`, `clioSessions/CLIO_engine_pilots`) and are not included; the notes and deck mention
the engine pilots only as future work.
