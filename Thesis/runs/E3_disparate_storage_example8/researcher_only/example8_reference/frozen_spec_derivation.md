# Derivation of the E3 frozen task specification (researcher-only)

| Item | Value |
|---|---|
| E3 specification | `github_control_repo_worktree/task/frozen_task_specification.md` (`E3-SPC-v1`), commit `333edab8ebcaeaef96b8b2b2243c6e0da155853b` |
| Source of locked values | `Thesis/common/frozen_example8/scientific_problem_specification.md` (FROZEN-EX8-v1) |
| Verbatim block | E3 §1–§7 are the FROZEN-EX8-v1 lines from `## 1. Problem statement` up to (not including) `## 8.`; SHA-256 of the block in both files: `12c500e181c673cc6780e3ba58254f7ec53e885372977857fb7d8a7eb303c30e` |
| E3 changes | new title and ID (no "EX8"/"Example 8" in agent-visible text); header resolving `software_contract.md`/`compute_resources.md` to the private source collection; §8 scientific deliverables identical to FROZEN-EX8-v1 §8 except `work/run_summary.md` points to `protocol/provenance_requirements.md`; new §8.2 distributed-context deliverables; new §9 distributed-context conditions |
| Not changed | geometry, mesh, sets, material, BCs, load, objective, constraint, SIMP, optimizer, iteration count, filter incl. symmetry-plane requirement, generated-configuration requirement, execution |

Check: `awk '/^## 1\. Problem statement/{p=1} /^## 8\. /{p=0} p' <file> | sha256sum` on both files.
