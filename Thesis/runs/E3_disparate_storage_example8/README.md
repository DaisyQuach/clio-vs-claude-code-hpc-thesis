> **Status 2026-10-10 (baseline executed):** E3 baseline is complete: 5 valid trials (01, 03, 04, 05, 02R = `baseline/trial_06`), all accepted
> under the E1 rubric; attempt 02 is retained as excluded (audit_failed). CLIO has not been run, so the baseline-versus-CLIO comparison is
> incomplete. See `Thesis/researcher_only/docs/E3/E3_BASELINE_EXECUTION_REPORT.md` (E3 reports now in `Thesis/researcher_only/docs/E3/`) and `Thesis/researcher_only/evaluation_figures/E3_baseline_prelim/E3_BASELINE_EVALUATION.md` (results live in `Thesis/researcher_only/`).
> The text below is the pre-execution README (kept unchanged; copy in `setup/preexisting_state/E3_README.md.pre_baseline_execution`).

# E3 — distributed-context study (Symmetry-Plane Cantilever, based on Morphorm Example 8)

Set up 2026-10-09/10 UTC; remediated 2026-10-10 UTC; procedural-access update 2026-10-10 UTC. **No trial has been run;
nothing here is a result.** Start with `setup/E3_PROCEDURAL_ACCESS_UPDATE.md` (current status), then
`setup/E3_SETUP_REPORT.md` and `setup/E3_REMEDIATION_REPORT.md`. **E3 is not ready for a counted trial** (operational
blockers in `setup/E3_PROCEDURAL_ACCESS_UPDATE.md` §5).

Access model (same as E1 and E2): researcher-only material is excluded from the agent-visible task packet and agents are
instructed and audited not to access it. Because experimental agents and Slurm jobs run under the researcher's account,
this separation is procedural rather than a technically enforced filesystem security boundary. No E3 document claims
that researcher-only material is technically inaccessible.

| Path | Content | Visibility |
|---|---|---|
| `setup/` | setup and remediation reports, source inventories (CSV + SHA-256), exclusions, permissions audits, access-qualification plan, ACTION_REQUIRED files, pre-existing state (incl. archived legacy packet and withdrawn Example 2) | researcher |
| `github_control_repo_worktree/` | worktree of the private repo `DaisyQuach/daisy-e3-distributed-context-control` (task, frozen spec `E3-SPC-v1`, catalog, protocol, helpers) | agent-visible (via clone at pinned commit) |
| `globus_source_root/` | private Globus-ready collection: manuals, curated documentation, target specification + figure (owner-only, 700/600) | agent-visible, private |
| `chpc_candidate_archive/` | read-only curated packages of Examples 1, 7, 13, 16 (no results; logical source identifiers only) | agent-visible |
| `researcher_only/` | Example 8 reference records (hashes only), `provenance/` (canonical source map), `evaluation/E3_SCORING_SCOPE.md` | researcher-only: excluded from every agent packet; access prohibited and audited (procedural) |
| `baseline/trial_01..05/`, `clio/trial_01/` | fresh E3 trial workspaces (`agent-inputs work staging-manifest jobs logs outputs provenance manifest.yaml README.md`) | agent-visible during a trial |
| `automation/` | non-destructive workspace/staging/provenance/audit scripts, the baseline headless automation, `sandbox/` (optional development safeguard; not the E3 runtime boundary) | researcher |
| `automation/environment/` | E3 approved software loader `load_morphorm_e3.sh`, E3 modulefiles and byte-identical runtime copies (loader, modulefiles, runtime are agent-usable) | agent-usable (read/execute) |

Pre-existing content: the legacy `agent_inputs/` packets from the 2026-10-09 thesis build (E1-identical frozen Example 8
packets) were moved out of every trial: trial_01 at remediation, trial_02..05 at the procedural-access update, to
`setup/preexisting_state/legacy_baseline_trial0N_agent_inputs/` (hash lists alongside). The only valid packet of each trial
is `agent-inputs/`. Legacy `manifest.yaml` keys are kept unchanged; E3 fields are appended. The previous version of this README is
`setup/preexisting_state/E3_README.md.pre_e3_setup`.
