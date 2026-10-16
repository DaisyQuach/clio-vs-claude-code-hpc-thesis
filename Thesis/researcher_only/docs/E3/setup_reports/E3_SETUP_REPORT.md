# E3 setup report — distributed-context study (Symmetry-Plane Cantilever)

> **Update 2026-10-10 UTC (procedural-access update; `setup/E3_PROCEDURAL_ACCESS_UPDATE.md`).** E3 now uses the same
> procedural researcher-only access model as E1 and E2. Researcher-only material is excluded from the agent-visible task
> packet and agents are instructed and audited not to access it. Because experimental agents and Slurm jobs run under the
> researcher's account, this separation is procedural rather than a technically enforced filesystem security boundary.
> Technical ground-truth isolation is no longer a prerequisite for a counted trial. The `automation/sandbox/` prototype
> is kept as an optional development safeguard and is not the runtime boundary. Legacy packets in `baseline/trial_02..05`
> were archived. E3 is still **not ready** for a counted trial; the current blockers are listed in that update's §5.
> The text below is unchanged history except where marked *superseded*, *resolved* or *decided*.

Setup window: 2026-10-09T23:54Z → 2026-10-10T00:16Z (UTC), login node notchpeak1, no allocation.
**No scored trial was run, no model was called for a trial, no Slurm job was submitted, Morphorm was not run, and no result was
created.** Validation used `--version`/`--help` of the pinned Claude Code binary and a test double (no model call).

## 1. Status

| Item | Status |
|---|---|
| Source inventory and curation | done — 13 files curated (SHA-256 verified), 17 researcher-only records; originals verify unchanged |
| Researcher-only Example 8 reference area | done — hash records only (304 files hashed), mode 700, nothing copied |
| CHPC candidate archive (Examples 1, 2, 7, 16) | done — 4 packages, no results, read-only (0 write bits) |
| Private Globus-ready source tree | tree ready and hashed; **collection NOT configured — action required** (`GLOBUS_ACTION_REQUIRED.md`) |
| Private GitHub control repository | **created, private, pushed** — commit `333edab8ebcaeaef96b8b2b2243c6e0da155853b` |
| Automation (E) and baseline headless automation (F) | done — syntax-checked, real-tree dry runs (write nothing), offline plumbing tests on a scratch copy |
| Access qualification | plan only (`access_qualification_plan.md`); needs an allocation |
| E1/E2/ThesisExperiments/originals untouched | verified (§9) |
| Counted baseline trial possible now? | **no** — blocked by Globus configuration and the legacy `agent_inputs/` decision (§10) (at setup time; current blockers: `E3_PROCEDURAL_ACCESS_UPDATE.md` §5) |

## 2. New E3 paths

Complete list: `setup/E3_CREATED_PATHS.txt` (every path that did not exist before setup, plus the two modified pre-existing files).
Top level (all new unless noted):
```
README.md                         (modified; previous version in setup/preexisting_state/)
setup/                            E3_SETUP_REPORT.md source_inventory.csv source_inventory.sha256 permissions_audit.md
                                  access_qualification_plan.md source_exclusions.md GLOBUS_ACTION_REQUIRED.md
                                  E3_CREATED_PATHS.txt E3_SETUP_SHA256SUMS.txt curate_sources.py generate_candidate_cards.py preexisting_state/
github_control_repo_worktree/     git worktree of the private repository (24 tracked files + .git)
globus_source_root/               manuals/ documentation/ target_materials/symmetry_plane_cantilever/ README.md MANIFEST.sha256 MANIFEST.tsv
chpc_candidate_archive/           example_01/ example_02/ example_07/ example_16_restart/ README.md MANIFEST.sha256   (read-only)
researcher_only/                  README.md example8_reference/ evaluation/   (mode 700)
baseline/trial_01/                agent-inputs/ staging-manifest/ provenance/ (new, empty); work/ jobs/ logs/ outputs/ (pre-existing, empty);
                                  manifest.yaml (pre-existing; E3 e3dc_* fields appended, legacy keys unchanged); agent_inputs/ (pre-existing, untouched)
clio/trial_01/                    agent-inputs/ work/ staging-manifest/ jobs/ logs/ outputs/ provenance/ manifest.yaml
automation/                       README.md init_trial_workspace.sh init_node_local_staging.sh record_source_versions.sh
                                  record_staging_snapshot.sh record_output_provenance.sh audit_boundary.sh verify_readonly_sources.sh
                                  lib/e3_common.sh lib/classify_tool_paths.py templates/trial_manifest.yaml
automation/baseline/              run_baseline_e3_trial.sh prepare_baseline_trial.sh verify_baseline_trial.sh collect_baseline_metrics.sh
                                  baseline_e3_prompt.md baseline_e3_config.env.example baseline_e3_config.env README.md
```

## 3. Source-to-destination map (every curated file; verified identical by SHA-256)

D = `/uufs/chpc.utah.edu/common/home/chet/Daisy`, E3 = this directory.

| Original | E3 destination | SHA-256 (original = copy) |
|---|---|---|
| `D/Morphorm_Full_Examples_Tests/topology_mech_ex1.i` ¹ | `chpc_candidate_archive/example_01/selected_source_materials/topology_mech_ex1.i` | `b96faf4ec2b0187edc32b5cf8e873a0ae36e41d7dac8084383ef6db925d21b34` |
| `D/Morphorm/docs/examples/input_decks/topology_optimization/mech/topology_mech_ex1.jou` | `chpc_candidate_archive/example_01/selected_source_materials/topology_mech_ex1.jou` | `30ceb2ae66411de86d01707c521bc70fc407b8538ed703d970f7340e1ab05746` |
| `D/Morphorm/docs/examples/figs/topology_optimization/mech/topology_original_geom_mech_ex1.png` | `chpc_candidate_archive/example_01/selected_source_materials/problem_geometry_figure.png` | `234f8a9cfa440268e89be4ed9bac4157f0ce3952a2a0a4f385c7d63af274bfd1` |
| `D/Morphorm/docs/examples/input_decks/topology_optimization/mech/topology_mech_ex2.i` | `chpc_candidate_archive/example_02/selected_source_materials/topology_mech_ex2.i` | `d060e336bf540d8e2dbe3f524f75c5f7bd48e5449eee06713edf2c0882bcc14a` |
| `D/Morphorm_Full_Examples_Tests/Example7_Helmholtz/topology_mech_ex7.i` ¹ | `chpc_candidate_archive/example_07/selected_source_materials/topology_mech_ex7.i` | `3ed36cc28ba7773a9cd7b7f4aece6e927f70ede4dddec72ea07222d24ffddf46` |
| `D/Morphorm_Full_Examples_Tests/Example7_Helmholtz/topology_mech_ex7.jou` ¹ | `chpc_candidate_archive/example_07/selected_source_materials/topology_mech_ex7.jou` | `2e5d0201ac23aea4533c007d44dd593713aae9533d73f800ec921034c70409ae` |
| `D/Morphorm/docs/examples/figs/topology_optimization/mech/topology_original_geom_mech_ex7.png` | `chpc_candidate_archive/example_07/selected_source_materials/problem_geometry_figure.png` | `cf38e2f0eaadd07ecee27762e25679afdb59306d9f744ff8ac835c04e71b812a` |
| `D/Morphorm_Full_Examples_Tests/Example16_Restart/topology_mech_ex16.i` ¹ | `chpc_candidate_archive/example_16_restart/selected_source_materials/topology_mech_ex16.i` | `4193f3b3981691499f13359369f6f419ea69c9a908f8c5285945ba51ca29112d` |
| `D/Morphorm_Full_Examples_Tests/Example16_Restart/topology_mech_ex16_restart.i` ¹ | `chpc_candidate_archive/example_16_restart/selected_source_materials/topology_mech_ex16_restart.i` | `951941cc684b444bd3c268c192eb7269ec964eb8b2579b6b8087b86575a32da6` |
| `D/Morphorm_Full_Examples_Tests/Example16_Restart/topology_mech_ex16.jou` ¹ | `chpc_candidate_archive/example_16_restart/selected_source_materials/topology_mech_ex16.jou` | `b02676b90e219b460a1e4a5b9a5910438fea46198cfac4dbdeffa4a3c947fca5` |
| `D/morphorm_manuals/usermanual.pdf` | `globus_source_root/manuals/Morphorm_User_Manual.pdf` | `46c0b655c9bccd535e197f560181e84333c2d165a1d50a0d47398fe27a19dae5` |
| `D/morphorm_manuals/theorymanual.pdf` | `globus_source_root/manuals/Morphorm_Theory_Manual.pdf` | `e60bf7f2cc9d70c5ebc2ded40520c06b1f06e07498ede6842ec9be621473039f` |
| `D/Morphorm/docs/examples/figs/topology_optimization/mech/topology_original_geom_mech_ex8.png` ² | `globus_source_root/target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png` | `2cc53d2243e7fc8435d8413a5bc89f73a194df4c38164310004354c11432563d` |

¹ byte-identical to the shipped original in `D/Morphorm/docs/examples/input_decks/topology_optimization/mech/` (verified).
² problem-statement figure only (half domain, mesh, red fixed face, blue load edge, green symmetry plane); also identical to
`D/Morphorm_ground_truth/Example_08/original_inputs/manual_figures/topology_original_geom_mech_ex8.png`.
Full hashes, sizes, types, roles and visibility: `setup/source_inventory.csv`. Derived (non-copied) E3 files: the frozen
specification (§1–§7 verbatim from FROZEN-EX8-v1, `researcher_only/example8_reference/frozen_spec_derivation.md`), `software_contract.md`
and `compute_resources.md` (FROZEN-EX8-v1 text with documentation location adapted), and all READMEs/cards/protocol written for E3.

## 4. Material intentionally excluded from agent-visible storage
Full list with paths: `setup/source_exclusions.md`. In short: every completed Example 8 artifact (deck, journal, mesh, job script,
logs, run directory, renders, histories, ground-truth package, thesis reference package and acceptance spec, docs-tree deck/journal/page/
result figure, Examples Manual); all result/evidence material of Examples 1, 2, 7, 16 (meshes, run directories, Exodus outputs,
histories, renders, logs, run READMEs, sbatch/env scripts); researcher-made variant decks (`topology_mech_ex7_conventional.i`,
`topology_mech_ex16_restart_from_topology.i`); Abaqus/Tosca material; Example 13; the Examples Manual `.inc` pages; the full Morphorm
documentation source tree; manuals from GitHub.

## 5. Hash manifests
| Scope | File |
|---|---|
| Original sources of all curated/recorded files (30) | `setup/source_inventory.sha256` (+ `source_inventory.csv`) |
| Example 8 reference records | `researcher_only/example8_reference/morphorm_full_examples_tests_example8.sha256` (126), `morphorm_ground_truth_example_08.sha256` (178) |
| Private source collection | `globus_source_root/MANIFEST.sha256` (SHA-256 `44735ea762399004a7975a895c25ac28bc7dada8cd7e92d6d96f6aaa293a465c`), `MANIFEST.tsv` |
| Candidate archive | `chpc_candidate_archive/MANIFEST.sha256` (SHA-256 `a17ef59bc95725f60fc409f8918fd7e59ba9e4e6ba92facf57623004640adb79`); per-package hashes in each `problem_card.yaml` |
| Control repository | `github_control_repo_worktree/catalog/checksums.sha256` (all tracked files except itself and `.gitignore`) |
| Every file created by setup | `setup/E3_SETUP_SHA256SUMS.txt` |

## 6. GitHub
Private repository created and pushed with the already-authenticated GitHub CLI (`gh` 2.0.0 module, token with `repo` scope; created via
`gh api user/repos -F private=true`, pushed over SSH).
- URL: https://github.com/DaisyQuach/daisy-e3-distributed-context-control (SSH `git@github.com:DaisyQuach/daisy-e3-distributed-context-control.git`)
- Commits: `c200e4cb0717ab4e11ef679a76e7b1ddc1c9c087` (initial), `333edab8ebcaeaef96b8b2b2243c6e0da155853b` (catalog checksum update) — **pinned**
- Privacy confirmed: API `private: true`, `visibility: private`; unauthenticated `GET api.github.com/repos/...` → HTTP 404.
- Content: only the required structure plus a `.gitignore` (blocks PDFs, Exodus files, credential/token files). Pre-push scan: no secrets, no
  account-name paths, no binaries. No `GITHUB_ACTION_REQUIRED.md` was needed.

## 7. Globus
**Not configured — action required.** No Globus CLI/SDK/credentials exist here; creating a collection needs interactive login and an endpoint
action, which were not attempted or bypassed. `globus_source_root/` is ready; exact steps and the directory to register are in
`setup/GLOBUS_ACTION_REQUIRED.md`. The baseline automation refuses counted runs until a collection ID is configured, or the researcher sets
`E3_GLOBUS_MODE=posix_readonly_fallback` (recorded as a deviation).

## 8. Validation performed (non-destructive)
- `bash -n` on all 19 shell scripts; `py_compile` on the classifier; 22 YAML files parse (the manifest template parses after substitution).
- Real tree, read-only: `verify_readonly_sources.sh --with-originals` PASS; `verify_baseline_trial.sh --planned` on `baseline/trial_01` PASS;
  `run_baseline_e3_trial.sh --dry-run` on `baseline/trial_01`: pinned binary 2.1.295 PASS, headless flags PASS, private repo readable
  noninteractively PASS, stops at `globus_not_configured` (exit 3); confirmed it wrote nothing.
- Scratch copy of the tree (`E3_ROOT_OVERRIDE`, test double for Claude Code, fake `SLURM_JOB_ID`/`SLURM_TMPDIR`; no model call):
  full counted path ran (clone at pin → read-only `agent-inputs/` → node-local staging → session → records): 2 files / 2,143,420 bytes staged,
  1 returned, hashes consistent, audit PASS, sources unchanged, metrics written; completed-verification correctly FAILs for missing
  scientific deliverables. Negative tests: agent read of `researcher_only/` → audit FAIL; read of `setup/` → FAIL; staging a non-catalog file →
  refused; rerun on a used trial → refused (exit 4); no allocation → `ACTION_REQUIRED_slurm_allocation` (exit 3); Globus unset →
  `ACTION_REQUIRED_globus_not_configured`; unreadable repo → `ACTION_REQUIRED_control_repo_unreadable`; trial dir outside E3 → refused (exit 2).
- Two defects found and fixed during testing: guard failures inside command substitution did not stop scripts; staging-record ordering made a
  fresh workspace look used.

## 9. Filesystem check: E1, E2, ThesisExperiments, originals
Method: full `find -printf '%p %y %s %m %T@ %C@'` snapshots taken before any write (23:54Z) and after setup, compared line by line.

| Tree | Entries before / after | Differences |
|---|---|---|
| `Thesis/runs/E1_uninterrupted_example8` | 1757 / 1757 | **0** |
| `ThesisExperiments` (stat only; never opened) | 39897 / 39897 | **0** |
| `Morphorm_Full_Examples_Tests` | 1255 / 1255 | **0** |
| `Morphorm_ground_truth` | 1073 / 1073 | **0** |
| `Thesis/runs/E2_interrupted_recovery_example16` | 2161 / 2341 | 202 lines, all under `baseline/trial_04R` and `trial_05` |
| Thesis outside E3 | 5732 / 5963 | E2 session evidence, `.agent_runtime/E2-…`, `researcher_only/{batch_logs,scores,session_evidence,evaluation_figures}` for E2 04R/05 |

The E2 and Thesis-level changes were made by the researcher's **concurrently running E2 batch chain** (`batch_logs/e2_04R_05_chain_20261009T223854Z`,
started before this setup; agent-host job 16168659 `agent_E2-example16-baseline-05_session_a` was running throughout). This setup wrote only
under the E3 root, the session scratchpad, and the GitHub remote. Originals additionally verify by content (`source_inventory.sha256`: 30/30).

## 10. Ambiguities, gaps and decisions for the researcher
1. **Legacy E3 packets.** `baseline/trial_01..05/` already held 2026-10-09 "planned, non-executable" packets (`agent_inputs/` with the E1 frozen
   Example 8 configuration and both manuals). They were left untouched. In `trial_01` an agent would see both `agent_inputs/` (which names
   "Frozen Workflow EX8") and the new `agent-inputs/`. The automation refuses a counted run until you either move `agent_inputs/` out of the
   trial or pass `--accept-legacy-agent-inputs`. `trial_02..05` were not converted (only `trial_01` was requested).
   *Resolved:* trial_01 at remediation; trial_02..05 at the procedural-access update (archived under `setup/preexisting_state/`).
2. **Approved software interface depends on the obsolete tree.** `Thesis/common/scripts/load_approved_software.sh` (used by E1/E2 and named in
   the E3 software contract) sources `Daisy/ThesisExperiments/common/scripts/load_approved_software.sh`. Not inspected or changed. E3 trials will
   transitively use the obsolete tree unless you provide another loader.
3. **Example 2 is not in either named source root.** It was taken from the Morphorm documentation tree (`Morphorm/docs/.../topology_mech_ex2.i`),
   recorded as such. Example 2 ships no journal and needs Example 1's mesh and engine output (not provided), so it cannot run on its own.
4. **Closeness of Example 7 to the target.** The shipped Example 8 deck equals the Example 7 deck plus one symmetry BC block, one filter keyword and a
   mesh name; the Example 8 journal is the Example 7 journal at half width. E3 places Example 7 in the candidate archive as instructed. This makes
   adaptation easy, which you may want to state in the design.
5. **Provenance paths disclose source roots.** `problem_card.yaml` must state original locations, so agents can read paths such as
   `Morphorm_Full_Examples_Tests/Example7_Helmholtz/…` whose sibling is `Example8_SymmetryPlane/`. Access rules forbid opening them and the audit
   flags any use; redact if you prefer.
6. **Same Unix identity.** `researcher_only/` (700) and the read-only archive do not stop processes running as the owner; access-qualification
   item 7 is expected to FAIL. Enforcement needs a separate trial account or sandbox. The originals are also owner-writable (hashed for detection).
   *Superseded 2026-10-10:* technical enforcement is not adopted. E3 uses the procedural E1/E2 policy (prohibited and audited), and item 7 was redefined accordingly.
7. **Private material is world-readable.** Manuals in `globus_source_root/manuals/` (and the originals) are `o+r`. Recommend
   `chmod -R o-rwx globus_source_root` (not done; restricted to researcher-only dirs by the instructions).
8. **E3 scoring reference.** E3 §1–§7 equal FROZEN-EX8-v1, so the E1 reference (`reference_policy: symmetry_honored_variant`) may apply, but
   that is your decision; nothing was written to `researcher_only/evaluation/`.
9. **Node-local storage.** Whether CHPC sets `$SLURM_TMPDIR`, and whether it contains the account name (forbidden in records unless accepted
   with `E3_ALLOW_ACCOUNT_NAME_IN_TMPDIR=1`), must be checked in qualification step 4.
10. **Claude config location.** The isolated session config (credential copy, transcript) is under `E3/.agent_runtime/`, outside the trial
    directory; the transcript is copied into the trial `logs/session/` and the credential copy is removed after the session.
11. **Agent-visible names.** The mandated directory name `E3_disparate_storage_example8` appears in catalog paths; the agent-visible documents
    otherwise avoid "Example 8".
12. **Examples Manual pages.** The `.inc` pages for Examples 1, 2, 7, 16 were excluded (results sections; thesis rule "never the Examples
    Manual"); packages carry factual READMEs instead.
13. **Harness version.** `~/.local/bin/claude` now points to 2.1.296; E3 pins 2.1.295 by explicit path, as in E1/E2.
