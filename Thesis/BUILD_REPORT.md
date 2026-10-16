# BUILD REPORT — Thesis controlled experiment suite

> **Addendum 2026-10-09 (after researcher review):** baseline repinned to Claude Code **2.1.295**; Example 8 policy = `symmetry_honored_variant`;
> Example 16 policy = `manual_semantics_iteration_20` (`researcher_only/RESEARCHER_DECISIONS.md`). Frozen hashes became
> FROZEN-EX8-v1 `cf15ac52f018defeba40afbedc910d757c08609c6a9adaa4a1b0e0428a570b4d`, FROZEN-EX16-v1 `a67d6cba7f0ce35ae6dc227f33b39056514be9494d6e15bc8e58524dfba1a86b`;
> the 15 planned packets were regenerated and re-verified; preflight and all dry runs pass without any override. Items 1–3 of §1 are resolved; §4 hashes below are the pre-decision values.

Build window: 2026-10-09T06:42:48Z → 2026-10-09T07:40Z (UTC), on CHPC notchpeak (agent host notch351, allocation 16154145).
Write boundary respected: nothing outside `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis` was created, modified or deleted
(`find <protected trees> -newermt <build start>` returns nothing; manual SHA-256 unchanged `7fc32762…c23d`). No counted trial was run; **no model call
was made**; the only Slurm submissions were the seven researcher-controlled reference-build jobs listed in §3. All 15 packets remain `status: planned`.

## 1. Headline status and approval items

| # | Item | Status |
|---|---|---|
| 1 | **BLOCKER — pinned Claude Code 2.1.292 is not installed** (`$HOME/.local/share/claude/versions/` holds 2.1.293, 2.1.294, 2.1.295). Preflight is BLOCKED; every counted entry point refuses to run. Installing it is a researcher action outside this tree (e.g. `claude install 2.1.292`), after which `preflight.sh` re-verifies the headless flags against its own `--help`. | **requires researcher action** |
| 2 | **DECISION — Example 8 accepted reference** (`researcher_only/ground_truth/example_8/reference_case/acceptance_spec.json: reference_policy`): `symmetry_honored_variant` (recommended; matches the frozen specification and the manual's described behaviour) or `canonical_shipped_deck` (manual listing as executed by the frozen software, which drops the filter symmetry plane). Until set, every E1 trial scores `needs_review`. | **requires researcher decision** |
| 3 | **DECISION — Example 16 accepted restart semantics** (`…/example_16/reference_case/acceptance_spec.json: reference_policy`): `manual_semantics_iteration_20` (recommended; resume from the iteration-20 design, as the manual states and as authorized 2026-10-06) or `shipped_listing_iteration_19`. Until set, every E2 trial scores `needs_review`. | **requires researcher decision** |
| 4 | Config-dir isolation (`CLAUDE_CONFIG_DIR` per session with a copied credential) is verified only with `claude auth status --json`, not with a live model call. First counted session is the first end-to-end test; fallback documented in `automation/AUTOMATION_LIMITATIONS.md` §2. | uncertainty |
| 5 | Both reference packages complete, validated and hashed; all dry runs pass; 15 planned packets verified. | done |

## 2. Source audit results (details: `researcher_only/ground_truth/example_*/SOURCE_AUDIT.md`)

| Example | Canonical sources (all under `Morphorm/docs/examples/input_decks/topology_optimization/mech/`, driver `Morphorm/engine/python/runmorphorm.py`) | SHA-256 | Manual |
|---|---|---|---|
| 8 | `topology_mech_ex8.jou` | `cd852856c747047fe57988f68d31d585cd0800bfc72468b53813cbe2c9ec46a6` | §7.2.8, PDF pp. 506–510 (printed 500–504) |
| 8 | `topology_mech_ex8.i` | `01a76bf2fcbbd34ba919c0aa7e023c409224a000b2b41c2a6ec48f932986a5ff` | Listing 7.2.10 |
| 16 | `topology_mech_ex16.jou` | `b02676b90e219b460a1e4a5b9a5910438fea46198cfac4dbdeffa4a3c947fca5` | §7.2.16, PDF pp. 551–558 (printed 545–552) |
| 16 | `topology_mech_ex16.i` | `4193f3b3981691499f13359369f6f419ea69c9a908f8c5285945ba51ca29112d` | Listing 7.2.18 |
| 16 | `topology_mech_ex16_restart.i` | `951941cc684b444bd3c268c192eb7269ec964eb8b2579b6b8087b86575a32da6` | Listing 7.2.19 |
| both | `runmorphorm.py` | `70bd98cebb38bb77b3509b15d178bedd14bace8c775c004771b0217df782ae35` | execution command |
| evidence only | `topology_mech_ex7.jou` (differs from the Example 16 journal only in the export file name; not executed) | `2e5d0201ac23aea4533c007d44dd593713aae9533d73f800ec921034c70409ae` | §7.2.7 |
| manual | `morphorm_manuals/examplesmanual.pdf` | `7fc32762247845fb89045c9eac9b422e57d49d4a68b1bdc0ed04864c9271c23d` | Release 1.0.0, 716 pages |

Both audits establish an unambiguous canonical source; no parameter had to be invented. Two formulation discrepancies were found and carried forward
openly (items 2 and 3 above): the Example 8 filter-block symmetry keyword is dropped by XMLGenerator (verified by host-side translation; a study-level
variant deck adds exactly `Symmetry Plane Sides {ss_sym}` and nothing else), and the Example 16 shipped `restart_iteration 20` reads the iteration-19 state.

## 3. Reference builds (researcher-controlled; frozen contract `--account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00`)

| Job | Package / run | State | Elapsed | Key result |
|---|---|---|---|---|
| 16154328 | ex8 mesh | COMPLETED 0:0 | 0:11 | 13,824 HEX8, 8/8 checks; coordinates identical to 2026-10-07 mesh |
| 16154329 | ex8 `run_canonical` | COMPLETED 0:0 | 9:54 | F₅₀ = 1.468985e5; diagnostics and final fields **identical** to the 2026-10-07 and 2026-10-04 runs; no `Symmetry Plane Sides` |
| 16154330 | ex8 `run_symmetry_honored_variant` | COMPLETED 0:0 | 9:52 | F₅₀ = 1.044701e5; `Symmetry Plane Sides {ss_sym}` applied; material on the cut plane (mean density 0.506 vs 0.0137) |
| 16154331 | ex16 mesh | COMPLETED 0:0 | 0:11 | 27,648 HEX8, 7/7 checks; coordinates identical to 2026-10-07 mesh |
| 16154332 | ex16 `stage1` | COMPLETED 0:0 | 18:30 | F₂₀ = 2.360040e5; checkpoint 21 states; `engine_output.exo` byte-identical to 2026-10-07 |
| 16154333 | ex16 `restart_corrected_21` | COMPLETED 0:0 | 21:02 | resumes from iteration 20 (diff 0); F₄₀ = 2.135584e5 at overall 60; identical to 2026-10-07 corrected restart |
| 16154334 | ex16 `restart_shipped_20` | COMPLETED 0:0 | 20:52 | resumes from iteration 19; F₄₀ = 2.136843e5 at overall 59; identical to 2026-10-07 superseded run |

Validation verdicts (`REFERENCE_VALIDATION.md` in each package): exact source identity and bit-for-bit agreement with historical executions; exact manual
agreement **cannot** be claimed for the canonical Example 8 run (symmetry claim not realized) nor for the shipped Example 16 restart (wrong resume state);
it holds for the symmetry-honored variant qualitatively and for the corrected restart exactly. Package manifests: example_8 `SHA256SUMS.txt` 342 files,
example_16 407 files, both verify.

## 4. Frozen configurations and packets

| Frozen configuration | ID | SHA-256 (sorted per-file hash list) | Used by |
|---|---|---|---|
| `common/frozen_example8/` | FROZEN-EX8-v1 | `28d909c5a5c32320e69438564d30a1876f94277138416fcd6f6a6d71ba14b248` | E1 and E3 (agent inputs byte-identical; E3 adds only `E3_PLANNED_NOT_EXECUTABLE.md`, excluded from the hash) |
| `common/frozen_example16/` | FROZEN-EX16-v1 | `ac0375cca7a0f663bd8a05fa4349c7c604a55df37d07ebe49feca883a156ab9f` | E2 |

Prompt hashes: E1 `task_prompt.md` `9d3d620a…8556`; E2 `session_a_prompt.md` `82874a8e…9361`, `recovery_prompt.md` `7b0bae25…4105`.
Planned packets (all `status: planned`, null curation/scoring fields, `agent_inputs/` = frozen documents + User/Theory manuals, empty `work/ jobs/ logs/ outputs/`):
`E1-example8-baseline-01..05` (`runs/E1_uninterrupted_example8/baseline/trial_01..05`), `E2-example16-baseline-01..05`, `E3-example8-baseline-01..05`
(non-executable). `verify_trial_packet.sh --planned`: 15/15 verified.

## 5. Dry-run results (no model call, no Slurm, no manifest change; `THESIS_CLAUDE_BIN_OVERRIDE=…/2.1.295` used to render plans)

| Test | Result |
|---|---|
| `preflight.sh --experiment e1-example8 --dry-run` | BLOCKED on `pinned_binary` only; all other checks PASS (help flags, stream-json, auth status logged in, credentials file, Slurm commands and partition, approved software with runtime inventory hash `fa0d97b9…e4e4d2`, frozen hashes, no CLAUDE.md in ancestors, no researcher-only references) |
| `run_e1_baseline.sh --trial 1 --dry-run` | rc 0; launch plan + exact argv written under `researcher_only/session_evidence/E1-example8-baseline-01/dryrun_*/session_main/`; manifest unchanged |
| `run_e2_baseline.sh --trial 1 --dry-run` | rc 0; two independent plans (session_a, session_b) with distinct UUIDs and config dirs; interlock listed; manifest unchanged |
| `run_all_planned_baselines.sh --experiment e1-example8 --dry-run` / `e2-example16 --dry-run` | 5/5 trials processed each; no status change |
| Guards | no selector → refused; `e3-example8` → refused; counted without `--execute-counted` → refused; counted without pinned binary → rc 3; direct counted launch → refused |
| Offline plumbing (scratch copy of a packet, synthetic session record) | collector copies evidence and refuses a second time; completed verification passes; boundary audit catches a restricted path; scorer: `needs_review` (undecided) / `accepted` (policy set, reference-built packet) / `rejected` (wrong variant) for both Example 8 and Example 16 synthetic packets |

## 6. Verified headless syntax (from 2.1.295 `--help`; re-verified against 2.1.292 by preflight once installed)
```
claude --print --verbose --output-format stream-json --model claude-fable-5-1 --dangerously-skip-permissions --session-id <uuid> --disable-slash-commands --no-chrome -- "<prompt>"
```
with `DISABLE_AUTOUPDATER=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 CLAUDE_CONFIG_DIR=<per-session> THESIS_TRIAL_ID=<run id>`,
cwd = trial root, inherited `CLAUDE*` variables removed, 1 h 50 min timeout, run inside an `sbatch --wait` agent-host job on the frozen contract.
Details: `docs/HEADLESS_CLAUDE_SYNTAX.md`, `docs/E2_FRESH_SESSION_ENFORCEMENT.md`.

## 7. Created files
Complete inventory: `docs/CREATED_FILES.txt` (639 listed paths plus counted reference outputs). Top level: `README.md`, `EXPERIMENTAL_DESIGN.md`,
`BUILD_REPORT.md`; `common/` (two frozen configurations with manuals, `scripts/`); `automation/` (12 scripts/docs + `lib/common.sh`); `docs/` (5 files);
`runs/` (15 packets, READMEs); `researcher_only/` (audits, source copies, manual extracts, two reference packages, tools, scores dir, figures dir, dry-run evidence).

## 8. Assumptions and uncertainties
1. Slurm contract taken verbatim from the pilot's frozen `compute_resources.md` (no `--qos`/`--constraint`); agent-host jobs use the same contract.
2. Agent-visible packets include the User and Theory manuals (as in the pilot), never the Examples Manual.
3. The frozen Example 8 specification requires the filter symmetry plane in the *generated* configuration (manual intent); it does not name the keyword form.
4. The frozen Example 16 specification requires resumption from the iteration-20 design with seamless compliance; it does not name `restart_iteration 21`.
5. Floating-point reproducibility across hochhalter-np nodes: all reference runs reproduced earlier runs bit for bit across notch272/274/351 and across
   runtimes; accept tolerance 1e-6 relative nevertheless.
6. Compute nodes have model-provider egress in batch jobs (true interactively in the pilot). Fallback: `--local` inside an interactive allocation.
7. Same Unix user: researcher-only protection is procedural plus post-hoc transcript audit.
8. Not implemented by design: CLIO automation, E3 execution, installation of Claude Code.

## 9. Researcher checklist (exact commands)
```bash
cd /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/automation
# 0. prerequisites (outside this tree): install Claude Code 2.1.292, e.g.  claude install 2.1.292 ; then set reference_policy in both acceptance_spec.json files
# 1. E1 dry run
./run_e1_baseline.sh --trial 1 --dry-run
# 2. E2 dry run
./run_e2_baseline.sh --trial 1 --dry-run
# 3. first counted E1 baseline trial (then researcher-only scoring)
./preflight.sh --experiment e1-example8 && ./run_e1_baseline.sh --trial 1 --execute-counted
./score_researcher_only.sh --trial-dir ../runs/E1_uninterrupted_example8/baseline/trial_01 --figures
# 4. first counted E2 baseline trial (then researcher-only scoring)
./preflight.sh --experiment e2-example16 && ./run_e2_baseline.sh --trial 1 --execute-counted
./score_researcher_only.sh --trial-dir ../runs/E2_interrupted_recovery_example16/baseline/trial_01 --figures
```
