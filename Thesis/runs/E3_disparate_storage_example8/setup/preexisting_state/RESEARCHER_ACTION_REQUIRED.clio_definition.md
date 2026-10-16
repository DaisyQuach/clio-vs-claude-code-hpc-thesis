# RESEARCHER ACTION REQUIRED — define the CLIO deployment (E3 readiness stopped at Phase 5)

Date: 2026-10-10 UTC. E3 is **NO-GO**. Full status: `setup/E3_READINESS_AFTER_PILOT.md` and `setup/E3_BLOCKER_STATUS.yaml`.
Earlier action records: `setup/preexisting_state/RESEARCHER_ACTION_REQUIRED.*.md`.

Everything except CLIO is resolved or decided: Globus, GitHub at the pin, compute-node qualification, Claude 2.1.295,
Cubit licensing, the baseline runner and the account name. You chose to assume **local CLIO Desktop connected to CHPC**
and to clarify it with Experiments 1 and 2 (`setup/CLIO_DEPLOYMENT_ASSUMPTION.md`).

## Your action (when ready; nothing urgent)
Document the actual CLIO deployment. It should cover:
- which machine runs the CLIO session and how it connects to CHPC;
- which machine reads GitHub and Globus;
- which machine writes E3 trial files, and how artifacts reach CHPC;
- how the session record (tool calls, transcript) is captured for the audit.

## Verify (safe)
None needed. The document is the deliverable.

## Then send
> CLIO deployment is defined (see <document>). Resume E3 readiness at Phase 5.

Next steps after that:
1. The CLIO runbook and runner.
2. `clio/trial_02..05`.
3. A harmless CLIO access-path test.
4. Phase 7: fresh packets for all ten trials, the freeze, and the final integrity checks.
