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
