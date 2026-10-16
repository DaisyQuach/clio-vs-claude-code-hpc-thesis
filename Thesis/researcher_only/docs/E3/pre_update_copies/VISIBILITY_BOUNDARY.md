# Agent-visible versus researcher-only

| Agent-visible (inside a trial packet) | Researcher-only (never referenced in agent-visible text) |
|---|---|
| `agent_inputs/*.md` (frozen configuration, prompts), `agent_inputs/manuals/` (User and Theory manuals only), `FROZEN_CONFIG_*` | `researcher_only/ground_truth/**` (source audits, canonical journals/decks copies, rebuilt references, histories, final Exodus files, acceptance specs and tolerances, scorer tools, figures) |
| `work/`, `jobs/`, `logs/`, `outputs/` written by the agent itself | `researcher_only/session_evidence/**` (launch records, streams, transcripts; copied into `<trial>/logs/agent_sessions/` only after the last session of the trial) |
| the approved software interface `common/scripts/load_approved_software.sh` and the read-only approved runtime it loads | `researcher_only/scores/**`, `researcher_only/evaluation_figures/**`, `BUILD_REPORT.md`, `docs/`, `automation/` |
| `manifest.yaml` (read-only for the agent; researcher-owned) | the Examples Manual, the Morphorm source/docs tree, pilot trials, prior ground-truth packages |

Enforcement: (1) no agent-visible document names any researcher-only path (`preflight.sh: agent_visible_leak`); (2) permitted
starting files are limited to the frozen documents and two manuals; no mesh, deck, output or history is supplied; (3) after a trial,
`verify_trial_packet.sh --completed` greps every transcript/stream for restricted paths (`boundary_audit`) and a hit fails the packet;
(4) scoring writes only the decision word into the manifest; tolerances, measured values and references stay in `researcher_only/`.
Residual limitation: same Unix user, so this is procedural plus audit, not permission-enforced (see `automation/AUTOMATION_LIMITATIONS.md`).
