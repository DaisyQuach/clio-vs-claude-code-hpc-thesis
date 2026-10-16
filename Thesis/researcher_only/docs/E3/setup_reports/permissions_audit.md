# Permissions audit (E3 setup, 2026-10-10 UTC)

## Changes made (only newly created E3 paths)
| Path | Mode set | Purpose |
|---|---|---|
| `researcher_only/`, `researcher_only/example8_reference/`, `researcher_only/evaluation/` | `700` (drwx------) | owner-only researcher area |
| `chpc_candidate_archive/` (recursive) | `a-w` (dirs `dr-xr-xr-x`, files `-r--r--r--`) | read-only candidate archive; verified: 0 entries with a write bit |
| `.agent_runtime/` (created only at trial time) | `700` | per-session Claude config, outside every trial workspace |
| trial `agent-inputs/` (at preparation time, not at setup) | `a-w` | frozen control packet read-only for the agent |

No permission was changed on any original: `Morphorm_Full_Examples_Tests/`, `Morphorm_ground_truth/`, `Morphorm/docs/`,
`morphorm_manuals/`, E1, E2, `ThesisExperiments/`, or the pre-existing E3 packets (`baseline/trial_0[1-5]/agent_inputs/` keep `dr-xr-xr-x`).

## Observed state
| Path | Mode | Owner:group |
|---|---|---|
| E3 root | `drwxr-xr-x` | u-account:hochhalter |
| `researcher_only/` | `drwx------` | same |
| `chpc_candidate_archive/` | `dr-xr-xr-x` | same |
| `globus_source_root/` (+ manuals `-rw-r--r--`) | `drwxr-xr-x` | same |
| `github_control_repo_worktree/` | `drwxr-xr-x` | same |
| originals `Morphorm_Full_Examples_Tests/`, `Morphorm_ground_truth/`, `morphorm_manuals/` | `drwxr-xr-x` | same account |
| `Morphorm/docs/` | `drwxr-sr-x` | another account:hochhalter (not writable by this account) |

## Limits that matter for E3 (researcher attention)
1. **Same Unix identity.** Trials run as the researcher's own account. Mode bits (including `700` on `researcher_only/`) and the
   read-only archive do not stop a process running as the owner: it can read `researcher_only/` and could `chmod` the archive back.
   The protection is procedural (prompt, access rules, staging helpers that refuse non-catalog sources) plus detection
   (`automation/audit_boundary.sh` classifies every path used in tool calls, job scripts and job logs; a forbidden path is a FAIL).
   *Update 2026-10-10 (procedural-access update):* this is the adopted E3 model, the same as E1/E2. Researcher-only material is
   excluded from the agent-visible task packet and agents are instructed and audited not to access it. Because experimental agents
   and Slurm jobs run under the researcher's account, this separation is procedural rather than a technically enforced filesystem
   security boundary. A separate trial identity or OS sandbox is not adopted (`setup/E3_PROCEDURAL_ACCESS_UPDATE.md`).
2. **Original sources are owner-writable.** `Morphorm_Full_Examples_Tests/`, `Morphorm_ground_truth/` and `morphorm_manuals/` are
   owned by the same account with `rwx`; a trial process could modify them. They are hashed in `source_inventory.sha256` so any change is
   detectable (`automation/verify_readonly_sources.sh --with-originals`). Not changed here, per instructions.
3. **World-readable private material.** `globus_source_root/manuals/` (licensed manuals) and the parent directories are readable by
   all CHPC users (`o+r`), as are the originals. Recommended researcher action: `chmod -R o-rwx globus_source_root` (not done: the
   instructions limit restrictive permission changes to researcher-only directories).
4. **Group readability.** E3 trees are group-readable by `hochhalter` (41 members listed by `getent`), except `researcher_only/`.
5. ACL tools (`getfacl`, `nfs4_getfacl`) exist; no ACLs were set.
