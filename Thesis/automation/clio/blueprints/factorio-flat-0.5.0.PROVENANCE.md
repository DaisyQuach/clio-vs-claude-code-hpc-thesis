# factorio-flat 0.5.0 as used in the counted thesis CLIO trials

Researcher decision (2026-10-13): the counted CLIO trials use the blueprint validated in the non-counted pilots
(factorio-flat-hpc 0.4.0-hpc.2, pilot program 20261012_bpv2, 15/15 counted pilot runs passed) and refer to it by its
official name, **factorio-flat 0.5.0**.

- Source: `clioSessions/CLIO_E1_API_pilots/pilot_program_20261012_bpv2/blueprint_variant/factorio-flat-hpc/`, copied
  2026-10-13T02:52:54Z.
- Only change: the AGENT.md front matter (`id: factorio-flat`, `title` / `display_name: Factorio Flat`,
  `version: 0.5.0`). Every other file is byte-identical to the pilot variant (`diff -r` showed only these four lines).
  Comments inside AGENT.md still describe the change history as "hpc.1 / hpc.2"; they were left unchanged on purpose.
- `.clio-install.md` replaced: the stock one recorded marketplace commit 740b986 of factorio-flat 0.4.0, which is not this
  content. The new one keeps the marketplace source URL (a different source made CLIO see two `factorio-flat` packs and
  refuse with `ambiguous_blueprint`, found in the 2026-10-13 deployment check), with `ref: main` (CLIO hashes source URL + ref into the source id), a `note:` line naming this frozen copy,
  `commit: none` and CLIO's own tree checksum of this directory: `6076c0269adaed32e216fb8ef423ea4cf189daf2ebd9d8675e26b84eabe56075`.
- Relation to the published 0.5.0 (iowarp/clio-agent-marketplace PR #96, commit 8e913d8): same skills, scripts and
  packet-mode guidance, but not byte-identical (the PR made main.md's first packet step toolchain-generic, states the
  "16,000 characters in current CLIO releases" limit, adds UNPARSABLE handling to xml_params.py, stricter final-state
  handling in wait_job.sh, tests and a CHANGELOG). Thesis text should cite this directory's checksum as the exact
  configuration used.
- Deployed per session by `launch_clio_session.sh` (CLIO_BLUEPRINT_SOURCE_DIR) into that deployment's own config only;
  the installed CLIO and its stock factorio-flat 0.4.0 are not changed.
