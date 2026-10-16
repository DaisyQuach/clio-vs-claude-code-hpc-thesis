#!/usr/bin/env python3
"""CLIO-side supplement to the shared E3 boundary audit (researcher decision 2026-10-13).

The shared audit (runs/E3_disparate_storage_example8/automation/audit_boundary.sh, unchanged) treats every path under the
E3 .agent_runtime/ tree as FORBIDDEN, including the agent's own runtime. A CLIO agent reaches its own runtime by design:
its blueprint skills (SKILL.md, scripts such as hpc-batch-jobs/scripts/wait_job.sh) live in the session's CLIO home, and
CLIO stores long shell outputs as files the agent reads back. This supplement re-labels exactly those paths as
OWN_RUNTIME and nothing else:
  <own clio_home>/config/agent-blueprints/<blueprint id>/...                 (this trial's frozen blueprint)
  <own clio_home>/state/workspaces/<ws>/tool-output/<this session id>/...    (this session's own tool output)
Every other FORBIDDEN / ANCESTOR / CHANGED / FAIL line stays, and the verdict is recomputed with the shared audit's
exact rules. The shared audit's own output is kept unchanged next to it.

Usage: e3_own_runtime_audit.py --trial-dir TD --clio-home H --session-id S --blueprint-id B [--report-only OUT]
  default: provenance/boundary_audit.txt -> provenance/boundary_audit.shared.txt (moved, unchanged), and a new
           provenance/boundary_audit.txt with the supplement applied. Exit 0 unless the new verdict is FAIL (exit 1).
  --report-only OUT: write the supplemented report to OUT and change nothing in the trial.
"""
import argparse, os, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("--trial-dir", required=True); ap.add_argument("--clio-home", required=True)
ap.add_argument("--session-id", required=True); ap.add_argument("--blueprint-id", required=True)
ap.add_argument("--report-only")
a = ap.parse_args()
td = os.path.realpath(a.trial_dir); home = os.path.normpath(a.clio_home)
src = f"{td}/provenance/boundary_audit.txt"; shared = f"{td}/provenance/boundary_audit.shared.txt"
if not a.session_id or not re.fullmatch(r"sess_[0-9a-f]+", a.session_id):
    sys.exit(f"bad --session-id {a.session_id!r}")
raw = open(shared if (os.path.exists(shared) and not a.report_only) else src).read().splitlines()

bp_root = f"{home}/config/agent-blueprints/{a.blueprint_id}"
tool_out = re.compile(re.escape(f"{home}/state/workspaces/") + r"[^/]+/tool-output/" + re.escape(a.session_id) + r"(/|$)")


def under(p, r):
    return p == r or p.startswith(r.rstrip("/") + "/")


def own(p):
    p = os.path.normpath(p)
    return under(p, bp_root) or bool(tool_out.match(p + ("/" if not p.endswith("/") else "")))


body, n_own, section = [], 0, ""
for line in raw:
    if line.startswith("verdict: "):
        continue                                          # recomputed below
    if line.startswith("## "):
        section = line
    f = line.split("\t")
    if section.startswith("## 1.") and line.startswith("  FORBIDDEN\t") and len(f) == 4 and own(f[3]):
        line = "  OWN_RUNTIME\t" + "\t".join(f[1:]); n_own += 1
    body.append(line)
text = "\n".join(body)
# the shared audit's verdict rules (audit_boundary.sh, last lines), applied to the supplemented body
fail = re.search(r"^  FORBIDDEN|CHANGED | FAIL", text, re.M) is not None
review = re.search(r"^  ANCESTOR|NO_TOOL_RECORD|^  JOB_RECORD_MENTION|^  REVIEW_GLOBUS", text, re.M) is not None
v = "FAIL" if fail else ("REVIEW" if review else "PASS")
shared_v = next((l[9:] for l in raw if l.startswith("verdict: ")), "missing")
hdr = [f"clio_supplement: Thesis/automation/clio/lib/e3_own_runtime_audit.py (researcher decision 2026-10-13); "
       f"shared audit output kept unchanged in provenance/boundary_audit.shared.txt (shared result {shared_v})",
       f"clio_own_runtime_roots: {bp_root} ; {home}/state/workspaces/*/tool-output/{a.session_id}",
       f"clio_own_runtime_lines: {n_own}"]
out = "\n".join(hdr + body + [f"verdict: {v}"]) + "\n"
if a.report_only:
    open(a.report_only, "w").write(out)
else:
    if not os.path.exists(shared):
        os.rename(src, shared)
    open(src, "w").write(out)
print(f"own_runtime_lines={n_own} shared={shared_v} supplemented={v}")
sys.exit(1 if v == "FAIL" else 0)
