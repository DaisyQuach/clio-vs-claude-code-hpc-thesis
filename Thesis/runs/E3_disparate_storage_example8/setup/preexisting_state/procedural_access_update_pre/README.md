# E3 — distributed-context study (Symmetry-Plane Cantilever, based on Morphorm Example 8)

Set up 2026-10-09/10 UTC; remediated 2026-10-10 UTC. **No trial has been run; nothing here is a result.** Start with
`setup/E3_SETUP_REPORT.md`, then `setup/E3_REMEDIATION_REPORT.md`. **E3 is not ready for a counted trial** (blockers in the
remediation report §12).

| Path | Content | Visibility |
|---|---|---|
| `setup/` | setup and remediation reports, source inventories (CSV + SHA-256), exclusions, permissions audits, access-qualification plan, ACTION_REQUIRED files, pre-existing state (incl. archived legacy packet and withdrawn Example 2) | researcher |
| `github_control_repo_worktree/` | worktree of the private repo `DaisyQuach/daisy-e3-distributed-context-control` (task, frozen spec `E3-SPC-v1`, catalog, protocol, helpers) | agent-visible (via clone at pinned commit) |
| `globus_source_root/` | private Globus-ready collection: manuals, curated documentation, target specification + figure (owner-only, 700/600) | agent-visible, private |
| `chpc_candidate_archive/` | read-only curated packages of Examples 1, 7, 13, 16 (no results; logical source identifiers only) | agent-visible |
| `researcher_only/` | Example 8 reference records (hashes only), `provenance/` (canonical source map), `evaluation/E3_SCORING_SCOPE.md` | **never agent-visible** |
| `baseline/trial_01/`, `clio/trial_01/` | fresh E3 trial workspaces (`agent-inputs work staging-manifest jobs logs outputs provenance manifest.yaml`) | agent-visible during a trial |
| `automation/` | non-destructive workspace/staging/provenance/audit scripts, the baseline headless automation, `sandbox/` (filesystem-sandbox prototype) | researcher |
| `automation/environment/` | E3 approved software loader `load_morphorm_e3.sh`, E3 modulefiles and byte-identical runtime copies (loader, modulefiles, runtime are agent-usable) | agent-usable (read/execute) |

Pre-existing content: `baseline/trial_02..05/agent_inputs/` and `manifest.yaml` legacy keys from the 2026-10-09 thesis build
(E1-identical frozen Example 8 packets) are kept unchanged; `baseline/trial_01/agent_inputs/` was moved at remediation to
`setup/preexisting_state/legacy_baseline_trial01_agent_inputs/` (the only valid packet for trial_01 is `agent-inputs/`);
`clio/README.md` unchanged. The previous version of this README is
`setup/preexisting_state/E3_README.md.pre_e3_setup`.
