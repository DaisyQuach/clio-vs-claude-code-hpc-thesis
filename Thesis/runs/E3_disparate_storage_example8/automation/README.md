# E3 automation (researcher-side, non-destructive)

Nothing here launches a trial by itself, submits a Slurm job, or runs Morphorm. Every script refuses to overwrite trial content,
never deletes or edits a source collection, and checks source paths against the permitted collections.

| Script | Does |
|---|---|
| `init_trial_workspace.sh --system S --trial-dir D [--dry-run]` | create/verify a fresh trial workspace and its manifest fields |
| `init_node_local_staging.sh --system S --trial-dir D` | create fresh `$SLURM_TMPDIR/e3/<system>/<trial_id>`; record node-local placement |
| `record_source_versions.sh --trial-dir D --control-dir C` | record control commit, control checksums, collection manifests |
| `record_staging_snapshot.sh --trial-dir D --staging S` | list files, bytes and hashes left in node-local staging |
| `record_output_provenance.sh --trial-dir D` | hash every trial output/record; check `outputs/SHA256SUMS.txt` |
| `audit_boundary.sh --system S --trial-dir D --since M` | classify every path used in agent tool calls and in job scripts/job logs (FORBIDDEN → FAIL); detect writes outside the trial, changes to collections or `researcher_only/` |
| `verify_readonly_sources.sh [--with-originals]` | verify collections, archive write protection, and (researcher-side) the original sources |
| `baseline/` | headless Claude Code baseline trial automation (see `baseline/README.md`) |
| `environment/` | E3 approved software loader, modulefiles and E3-local runtime copies (see `environment/README.md`) |
| `sandbox/` | optional bubblewrap prototype: development safeguard and login-node visibility check, **not** the E3 runtime boundary and not used by the runner (see `sandbox/README.md`) |
| `lib/e3_common.sh` | roots, permitted collections, forbidden roots, guards, record helpers |
| `lib/classify_tool_paths.py` | path classifier used by the audit |
| `templates/trial_manifest.yaml` | E3 manifest fields |

Agent-side record keeping (sources searched, artifact selections, staged/returned files, placement) is done with the helpers in the
control repository (`scripts/non_destructive_preflight_helpers/`), which write the same TSV formats the automation verifies.
Validation performed at setup: `bash -n` on every script; dry runs on the real tree (write nothing); full offline plumbing runs on a
scratch copy of the tree with a test double instead of Claude Code (see `../setup/E3_SETUP_REPORT.md` §8).

Access model (2026-10-10, same as E1/E2): researcher-only material is excluded from the agent-visible task packet and
agents are instructed and audited not to access it. Because experimental agents and Slurm jobs run under the
researcher's account, this separation is procedural rather than a technically enforced filesystem security boundary.
The automation enforces it where it can: guarded source paths, a clean `agent-inputs/`, and the prompt and protocol
prohibition. It then detects violations after the trial with `audit_boundary.sh`.
