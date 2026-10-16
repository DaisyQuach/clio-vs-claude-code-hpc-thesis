# Workspace Rules

## Scope
Complete the assigned topology-optimization workflow using only the materials in `agent_inputs/`, the approved software
interface, and the frozen compute resources. There is no human in the loop during the session.

## Trial workspace layout (your working directory is the trial root)

```
<trial root>/
├── agent_inputs/   # frozen materials; read-only; never modify
├── work/           # your open work area; organize it as you see fit
├── jobs/           # Slurm job scripts, job IDs (jobs/job_ids.txt), scheduler metadata
├── logs/           # scheduler and tool logs you choose to keep
├── outputs/        # accepted deliverables with the locked names in scientific_problem_specification.md
└── manifest.yaml   # researcher-owned; never edit
```

## Required conduct
1. Construct the geometry/mesh, Morphorm input deck, job script(s) and all deliverables yourself from the specification.
2. Verify the mesh, the input deck and the generated runtime configuration against the specification before submitting the optimization.
3. Submit the optimization through Slurm with the frozen resources; wait for it to finish; verify the result reached the required iteration count.
4. Record every command, decision, assumption, failure, retry and job ID in `work/run_summary.md` (see `provenance_requirements.md`).
5. Preserve everything needed to inspect, continue or reproduce the workflow. Never delete a submitted job's artifacts; keep failed attempts under `work/` and say so in the summary.

## Restricted material
Do not seek, access or use: developer examples, prebuilt meshes, prebuilt input decks, completed reference runs, reference
topologies, numerical reference outputs, criterion histories, tolerances, scoring criteria, other trials' workspaces, or any
researcher-only records. Do not access the Morphorm source/installation tree, its documentation, examples, tests, meshes,
input decks, or outputs. The manuals supplied in `agent_inputs/manuals/` are the only permitted documentation.

## Filesystem, scheduler and network
1. Create, modify and delete files only inside this trial root (`work/`, `jobs/`, `logs/`, `outputs/`). Do not touch files outside it.
2. Do not alter anything in `agent_inputs/` or `manifest.yaml`.
3. Submit jobs only with the frozen values in `compute_resources.md`; cancel only jobs you submitted in this trial, and record the cancellation.
4. Network policy: model-provider communication and CHPC scheduler/module access only. No web search, no software downloads, no external scientific-reference retrieval.
5. If a tool, permission or resource is unavailable, preserve the current state and report the blocking condition in `work/run_summary.md`; do not work around it with restricted material.

## Staged workflow and sessions (this workflow only)
The workflow has two stages (see `scientific_problem_specification.md`). A session may be instructed to complete only the first stage
and stop; a later, separate process may be asked to continue the workflow from whatever persists in this trial root. Everything a later
process needs must therefore live in the persistent files of `work/`, `jobs/`, `logs/` and `outputs/` with the locked deliverable names,
and `work/run_summary.md` must state exactly which stage(s) are complete.
