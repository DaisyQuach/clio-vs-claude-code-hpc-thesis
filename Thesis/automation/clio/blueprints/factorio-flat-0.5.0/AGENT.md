---
id: factorio-flat
title: Factorio Flat
display_name: Factorio Flat
version: 0.5.0
description: Factorio Flat tuned for non-interactive HPC simulation work (bounded Slurm waits with a helper, simulation skills on the root expert, packet mode, bundled Morphorm/Exodus checks, tool-call hygiene). A scientist-facing research partner spanning research framing, evidence coordination, simulation, and adversarial review, extended with materials science, manufacturing, characterization, mechanical testing, fatigue/failure, and data analysis specialists.
root_expert: main
# A2UI catalogs are a per-agent allowlist: from clio-agent 0.9.4.17 this
# agent may produce surfaces only against the catalogs listed here, in this
# preference order (nothing is implicit, the builtins included). clio-workspace
# stays the default for tables, charts, and metrics; the pack's own
# abaqus-topology catalog carries the before/after topology comparison, whose
# TopologyViewport aliases the clio.mesh-viewport.v1 kernel.
a2ui_catalogs:
  - clio-workspace
  - abaqus-topology: catalogs/abaqus-topology
# Floor: 0.9.4.17 is the first release that reads the list form above (an
# older runtime would drop the pack catalog). Raised to 0.9.4.19 (#78
# follow-up): TopologyViewport (clio.mesh-viewport.v1) and ParameterSlider
# (clio.slider.v1) need clio-schemas>=0.4.0, which 0.9.4.18 does not pin
# (0.3.3) and 0.9.4.19 does.
# Raised again (#1533): ConvergencePlot now aliases clio.chart.v1 instead of
# the removed clio.time-series.v1, which needs clio-schemas>=0.5.1; clio-agent
# 0.9.4.23 is the first release that pins it (checked against its
# pyproject.toml). Below this floor, load_catalog_directory refuses the abaqus-topology
# catalog with a typed a2ui_component_unimplemented reason and the server
# drops it from the producible set, but main/abaqus_engineer's prompts and the
# visualize-topology-optimization skill still tell the model the views
# exist -- raising the floor makes the default-registry installer skip the
# whole pack update on an old server (typed
# blueprint_requires_newer_clio_agent) instead of shipping a pack that
# promises a view it cannot produce.
requires:
  clio_agent: ">=0.9.4.23"
blueprint:
  format: agent-blueprint-v1
# Provider selection belongs to deployment configuration. Factorio Flat's
# evidence researchers use the installed web MCP, which can point at a
# self-hosted clio-search/SearXNG deployment without paid-provider credentials.
# clio-kit is provisioned once via `uv tool install clio-kit==2.10.6` (see clio-agent install/doctor).
# Installed-tool launchers replace `uvx clio-kit@...`: concurrent uvx spawns raced on a cold
# uv cache (truncated pyvenv.cfg -> dead transport -> _UnsupportedSessionAgent), and
# `uv cache prune/clean` deletes ephemeral envs under RUNNING servers (astral-sh/uv#11694).
mcp_servers:
  web: clio-kit mcp-server web
experts:
  - experts/main.md
  - experts/research_methodologist.md
  - experts/virtual_lab.md
  - experts/evidence_researcher.md
  - experts/evidence_leaf.md
  - experts/evidence_critic.md
  - experts/simulation_methodologist.md
  - experts/abaqus_engineer.md
  - experts/independent_reviewer.md
  - experts/materials_scientist.md
  - experts/manufacturing_expert.md
  - experts/characterization_expert.md
  - experts/mechanical_testing_expert.md
  - experts/fatigue_failure_expert.md
  - experts/data_analysis_expert.md
defaults:
  prompt_profile: heavy
---

# Factorio Flat

Factorio Flat keeps the scientist-facing identity and scientific integrity of
its original design while adding materials-science specialists as siblings
rather than replacements. `main` remains the root: it decides whether to
answer directly, ask a consequential clarification, load a skill itself, or
consult a specialist.

The original nine experts are unchanged in role: `research_methodologist`
(framing), `virtual_lab` (feasibility), `evidence_researcher` with its
`evidence_leaf`/`evidence_critic` children (literature evidence fan-out and
criticism), `simulation_methodologist` and `abaqus_engineer` (simulation
formulation and Abaqus/Tosca/Morphorm implementation), and
`independent_reviewer` (adversarial review).

Six materials-science specialists sit alongside them, also as direct children
of `main`, covering ground the original nine did not: `materials_scientist`
(processing-structure-property reasoning), `manufacturing_expert`
(design-to-part manufacturing route), `characterization_expert` (turning
measurements into evidence), `mechanical_testing_expert` (physical test
design and interpretation), `fatigue_failure_expert` (fatigue life prediction
and failure analysis), and `data_analysis_expert` (statistics, uncertainty,
and figures). Where a new specialist's skill set would have duplicated an
original expert's role too closely, the skill went to the original expert
instead of a new one — `simulation_methodologist` and `abaqus_engineer` carry
the FEA/topology-optimization and Abaqus/Tosca/Morphorm skills, and
`evidence_researcher` carries the literature-search/synthesis skills.

**HPC variant (0.4.0-hpc.1).** Same experts and science rules as Factorio Flat 0.4.0.
Pilot traces showed that `main` does simulation packets alone and never delegates. It never saw the Morphorm,
topology-optimization or meshing skills, because those sit on its children. It also had no Slurm guidance.
This variant makes three changes:
- `main` carries `hpc-batch-jobs`, `morphorm`, `topology_optimization` and `meshing` directly.
- `main` has a non-interactive packet mode.
- `morphorm` describes the general Cubit → input deck → XMLGenerator → Slurm workflow.

Skills are the reusable procedures each expert loads on demand; a skill can be
shared by more than one expert (for example `heat_treatment` is used by both
`materials_scientist` and `manufacturing_expert`).

**HPC variant 0.4.0-hpc.2.** Changes after the hpc.1 pilots (`pilot_program_20261012_bpv2/STUDY.md`). Model output
is about 70 tokens/s, so output tokens set model time. In hpc.1 they went to:
- 27–39 % run reports: written once, rejected for length (16,000-character command limit), then written again in parts;
- 12–31 % one-off verification scripts;
- 3–11 % tool-call blocks that did not parse (raw line breaks inside JSON strings in heredocs);
- one wasted call per `load_skill` with null optional arguments;
- translation and restart retries that every pilot repeated.

hpc.2 changes:
- `main`: tool-call formatting rules (JSON escaping, the command-length limit, patch instead of re-send);
  `load_skill` with `skill_id` only; a facts log plus reports written once; bundled checks before new scripts.
- `morphorm`: bundled `scripts/exo_summary.py`, `xml_params.py` and `diag_summary.py`; guidance to re-translate once
  with the manual's equivalent keyword form when a setting is missing from the generated XML; restart-state
  counting, with a first-objective check right after submitting a continuation.
- `hpc-batch-jobs`: bundled `scripts/wait_job.sh` (one status line per bounded wait) and low-output wait steps.

No task parameters, reference values or packet-specific paths are included.

