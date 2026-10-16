# daisy-e3-distributed-context-control

Private control repository for Experiment 3 (E3, distributed context) of a topology-optimization thesis. It defines the
task, the permitted storage collections, and the protocol a trial must follow. It contains no credentials, manuals,
completed examples, ground truth or reference outputs.

| Path | Content |
|---|---|
| `task/task_prompt.md` | the task prompt given to the agent |
| `task/frozen_task_specification.md` | frozen scientific specification `E3-SPC-v1` (Symmetry-Plane Cantilever) and required deliverables |
| `task/required_deliverables.md` | checklist of deliverables |
| `catalog/permitted_storage_catalog.yaml` | the only storage collections a trial may read, with access methods |
| `catalog/artifact_cards/` | one card per catalogued package |
| `catalog/checksums.sha256` | SHA-256 of every file in this repository except itself |
| `protocol/` | access rules, staging rules, cache policy, provenance requirements |
| `scripts/non_destructive_preflight_helpers/` | record-keeping and staging helpers (read-only on sources) |

Verify: `sha256sum -c catalog/checksums.sha256` from the repository root.

Access model (same as Experiments 1 and 2): researcher-only material is excluded from the agent-visible task packet and
agents are instructed and audited not to access it. Because experimental agents and Slurm jobs run under the
researcher's account, this separation is procedural rather than a technically enforced filesystem security boundary.
See `protocol/access_rules.md`.

Revision (E3 remediation, 2026-10-10 UTC): catalog version 2 — the incomplete Example 2 package was withdrawn, a
self-contained Example 13 package was added, cards carry logical source identifiers instead of original locations, and
collection manifest checksums and the approved software interface were updated.

Revision (procedural-access update, 2026-10-10 UTC): catalog version 3 — the access model is stated explicitly in the
task prompt, the protocol, the catalog and each artifact card. Scientific task, specification and packages unchanged.

Revision (Globus configuration, 2026-10-10 UTC): catalog version 4 — the private source collection is the Globus guest
collection `6dcea62e-130d-47a9-8b77-80fba6f58693` (read-only). Globus is its only permitted access method.

Revision (staging procedure, 2026-10-10 UTC): catalog version 5. Files from the private source collection are staged only
by Globus: a transfer into the trial's `staging-inbox/` through the catalogued destination collection, then a
manifest-checked copy into the node-local `$E3_STAGING_DIR`, which lives under the Slurm per-job `$TMPDIR`. The helper is
`scripts/non_destructive_preflight_helpers/globus_stage_file.sh`.
