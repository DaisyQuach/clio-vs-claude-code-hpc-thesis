# researcher_only/ — never agent-visible

Nothing under this directory may be copied, staged, cloned, listed or read by any E3 baseline or CLIO trial process,
by the GitHub control repository, or by the Globus source tree. Automation refuses any source path under here
(`automation/lib/e3_common.sh: e3_guard_source`) and the post-trial boundary audit flags any reference to it.

| Path | Content |
|---|---|
| `example8_reference/` | inventory and provenance records for the completed Example 8 materials (hashes and pointers only; no copies) |
| `evaluation/` | reserved for future scoring sheets and validation records (empty; nothing fabricated) |

Permissions: directories here are mode 700 (owner only). Because the trial agents run under the same Unix account as the
researcher, mode bits do **not** prevent a trial process from reading this area; see `../setup/permissions_audit.md`.
