# Researcher decisions (recorded 2026-10-09 UTC, after review of BUILD_REPORT.md)

| Item | Decision | Effect |
|---|---|---|
| Baseline harness version | Use Claude Code **2.1.295** (2.1.292 is not installed) | `automation/lib/common.sh: CLAUDE_PIN_VERSION=2.1.295`; frozen `formal_configuration.md` updated in both configurations, so FROZEN-EX8-v1 / FROZEN-EX16-v1 hashes were recomputed and the 15 planned packets regenerated before any trial |
| Example 8 accepted reference | `symmetry_honored_variant` | `ground_truth/example_8/reference_case/acceptance_spec.json: reference_policy` |
| Example 16 accepted restart semantics | `manual_semantics_iteration_20` | `ground_truth/example_16/reference_case/acceptance_spec.json: reference_policy` |

Pre-decision state is preserved in `BUILD_REPORT.md` §1 and in the acceptance-spec `_reference_policy_note` fields.
| Example 16 acceptance spec amendment | v1.1: Stage-2 WriteRestart no longer checked (output-only setting not locked by the frozen spec) | `ground_truth/example_16/reference_case/ACCEPTANCE_SPEC.md` amendment log |
| E1-example8-baseline-04R2 | Counted (accepted by researcher override of needs_review) | provider limit hit after the final successful tool call; exact match; `scores/E1-example8-baseline-04R2/score_with_override.json` |
