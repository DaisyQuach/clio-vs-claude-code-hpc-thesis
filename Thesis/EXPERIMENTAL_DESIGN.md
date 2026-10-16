# Experimental Design

## Status of earlier work
The earlier pilot E1/E2 trials in `/uufs/chpc.utah.edu/common/home/chet/Daisy/ThesisExperiments` (three baseline trials per
experiment, agent-chosen meshes, interactive Claude Code sessions) are **retained unchanged as preliminary evidence**. They were
read only during this build and are not part of the controlled study below.

## Controlled study

| Experiment | Workflow (frozen) | Question | Sessions per trial |
|---|---|---|---|
| **E1** uninterrupted | Morphorm Examples Manual §7.2.8 **Example 8** (half cantilever, Helmholtz filter with a symmetry plane, 48 × 24 × 12 HEX8, OC, 50 iterations) | Can an agent construct and complete the frozen workflow from the specification alone, headlessly? | 1 |
| **E2** interrupted recovery | Morphorm Examples Manual §7.2.16 **Example 16** (full cantilever, 48 × 24 × 24 HEX8, Stage 1 = 20 iterations with restart file, Stage 2 = 40 further iterations from the saved `control` design) | Can a completely fresh process recover the workflow state from persistent workspace artifacts and continue it correctly? Session A builds and runs Stage 1 only; Session B (new process, no resume/continue/fork/session reuse) continues from the trial root. | 2 |
| **E3** disparate storage (future) | Example 8, same frozen formulation as E1 | Does a disparate-storage deployment change workflow construction/completion? Only documentation, frozen specification and planned packets exist in this build; no automation, storage distribution or execution. | — |

- **Baseline system:** fully headless Claude Code pinned to **2.1.295** (researcher decision 2026-10-09; 2.1.292 was not installed) with model **`claude-fable-5-1`**, one new process per session, autoupdater disabled, isolated per-session configuration directory.
- **Replicates:** five planned baseline trials for E1 and five for E2 (paired blocks `E1-01..05`, `E2-01..05`); five planned-but-not-executable packets for E3. The CLIO arm is not implemented in this build; `runs/*/clio/` is reserved.
- **Scientific references:** rebuilt from the canonical manual sources under `researcher_only/ground_truth/` (Example 8 for E1 and E3, which share one reference because their frozen scientific inputs are byte-identical, `FROZEN-EX8-v1`; an independent Example 16 reference for E2, `FROZEN-EX16-v1`).
- **Primary outcome:** researcher-only scientific scoring of each trial against the predeclared acceptance specification: `accepted`, `rejected` or `needs_review`, with reasons and measured values. A process that exits is never a success by itself; artifact verification and scoring are required.
- **Token, cost and tool-call data** (from the stream/transcripts) are **descriptive audit metadata**, not primary performance measures.
- **Scope of inference:** five trials per experiment characterize this configuration on these two workflows. The study does **not** establish broad model superiority or population-level reliability.

## Controls and frozen variables
Mesh resolution, set names, symmetry treatment, load placement, SIMP floor/exponent, filter, optimizer, iteration counts, deliverable
names, software interface, Slurm resources, model, harness version, prompts and network policy are locked in the frozen configurations
(`common/frozen_example8`, `common/frozen_example16`) whose SHA-256 is recorded in every packet manifest.

## Known formulation issues carried into the design (see `BUILD_REPORT.md`)
1. Example 8: the shipped deck's filter-block symmetry keyword is dropped by XMLGenerator; the frozen specification requires the symmetry plane
   to be present in the generated configuration, and the reference package holds both the canonical-as-executed and the symmetry-honored result.
   The accepted variant is a researcher decision (`acceptance_spec.json: reference_policy`).
2. Example 16: the shipped restart deck resumes from iteration 19; the frozen specification requires resumption from the iteration-20 design and
   the reference package holds both restart results. The accepted semantics is a researcher decision (`reference_policy`).
