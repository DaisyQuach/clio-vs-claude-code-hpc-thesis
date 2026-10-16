# E3 scientific scoring scope (frozen at remediation, 2026-10-10 UTC)

Researcher-only. This file must never be copied into agent-visible storage (trial directories, `chpc_candidate_archive/`,
`globus_source_root/`, the control repository or any staging area).

## 1. Scientific requirements and rubric
- E3 uses the **same frozen Symmetry-Plane Cantilever scientific requirements as E1**. The E3 task specification
  `E3-SPC-v1` reproduces §1–§7 of `FROZEN-EX8-v1` verbatim (derivation: `researcher_only/example8_reference/frozen_spec_derivation.md`).
- E3 uses the **same compliance rubric as E1**, applied by reference to the E1 researcher records
  (`Thesis/researcher_only/RESEARCHER_DECISIONS.md`, `Thesis/researcher_only/ground_truth/example_8/`). The rubric is not
  copied here and is not changed for E3. Any change to it is a new researcher decision that must be recorded before scoring.

## 2. Status of the historical Example 8 package
- E3 does **not** treat the historical completed Example 8 package (the run in the example-test collection or the
  ground-truth package) as an exact ground-truth solution. A trial is not scored by byte- or number-matching that package.
- The historical package remains a researcher-side reference for checking that a configuration is scientifically
  compliant (consistent with the E1 decision `reference_policy: symmetry_honored_variant`); it is not a target answer.

## 3. What E3 evaluates
1. Scientific/configuration compliance with `E3-SPC-v1` §1–§7 (geometry, mesh, blocks, nodesets/sidesets, material, SIMP,
   objective, constraint, filter, optimizer, iteration settings, outputs).
2. Correct symmetry treatment (half domain, symmetry boundary condition on the symmetry plane, and the filter/mesh
   consequences of modelling a half domain — not reuse of a full-domain example unchanged).
3. Valid execution with the approved runtime through the E3 loader and the frozen Slurm resources.
4. Presence and integrity of the required outputs and deliverables (`task/required_deliverables.md`).
5. Artifact selection: which catalogued artifacts the agent consulted, staged and used, and whether it recognised that the
   related examples (in particular the full-domain Helmholtz cantilever) differ from the target.
6. Provenance: completeness and correctness of the trial's source, version, command and output records.
7. Transfer/staging records: what was staged from which collection, by which mechanism, with hashes and timing.

## 4. Claims E3 does not make yet
- **No staging-performance claim** (speed, efficiency or reliability of distributed staging versus local access) is made
  until the Globus collection, the Globus transfer path and the node-local staging mechanism have been configured and
  verified (see `setup/GLOBUS_ACTION_REQUIRED.md`, `setup/COMPUTE_NODE_QUALIFICATION_ACTION_REQUIRED.md`). Until then,
  staging records are evaluated for completeness and correctness only.
- Trials run under the `posix_readonly_fallback` decision are recorded as deviations and are not evidence about Globus.

## 5. Visibility rule
Access model (added 2026-10-10, procedural-access update; same as E1/E2): researcher-only material is excluded from the agent-visible task packet and agents are instructed and audited not to access it. Because experimental agents and Slurm jobs run under the researcher's account, this separation is procedural rather than a technically enforced filesystem security boundary.
The audit outcome of a trial (`provenance/boundary_audit.txt`, including job scripts and job logs) is part of its record
and is reviewed before scoring. A trial with evidence of access to researcher-only material is disqualified, as in E1/E2.

No scoring values, target numeric outcomes (objective, compliance, volume fraction, iteration counts as targets, histories),
or acceptance tolerances are placed in agent-visible storage. They exist only in researcher-only locations and are applied
after a trial has finished.
