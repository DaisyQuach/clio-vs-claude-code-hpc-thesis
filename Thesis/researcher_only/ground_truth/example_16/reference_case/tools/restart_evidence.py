#!/usr/bin/env python3
"""Evidence that a restart run continued from a specific saved Stage-1 state.

Usage: restart_evidence.py <stage1_dir> <restart_dir> <restart_deck> <out_json> [intended_iteration=20]

Checks (all recorded, pass/fail summarized in "resumed_from_intended_iteration"):
  1. <restart_dir>/initialguess.exo is byte-identical to <stage1_dir>/engine_output.exo.
  2. Which checkpoint step the restart's initial `control` field matches exactly
     (searched over all steps, never assumed).  Morphorm reads `restart_iteration`
     as a 1-based Exodus state; state s holds Stage-1 iteration s-1.
  3. The restart's first compliance equals Stage-1's compliance at the matched
     iteration, and whether that iteration is the intended one.
"""
import hashlib, json, re, sys
import numpy as np
from netCDF4 import Dataset

s1, rs, deck, out = sys.argv[1:5]
want = int(sys.argv[5]) if len(sys.argv) > 5 else 20


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def diag(path):
    rows = {}
    for line in open(path):
        p = line.split()
        if p and p[0].isdigit():
            rows[int(p[0])] = {"F": float(p[2]), "H1": float(p[4])}
    return rows


def allsteps(path, name):
    with Dataset(path) as ds:
        names = [b"".join(r.compressed()).decode() for r in ds.variables["name_nod_var"][:]]
        v = np.asarray(ds.variables[f"vals_nod_var{names.index(name) + 1}"][:], float)
        t = np.asarray(ds.variables["time_whole"][:], float)
    return v, t


txt = open(deck).read()
it = int(re.search(r"^\s*restart_iteration\s+(\d+)", txt, re.M).group(1))
fname = re.search(r"^\s*initial_guess_field_name\s+(\S+)", txt, re.M).group(1)
ck, ig = f"{s1}/engine_output.exo", f"{rs}/initialguess.exo"
d1, d2 = diag(f"{s1}/morphorm_oc_optimizer_diagnostics.txt"), diag(f"{rs}/morphorm_oc_optimizer_diagnostics.txt")
allc, times = allsteps(ck, fname)
allt, _ = allsteps(ck, "topology")
rsc, _ = allsteps(f"{rs}/engine_output.exo", "control")
rst, _ = allsteps(f"{rs}/engine_output.exo", "topology")
match = [float(np.abs(allc[k] - rsc[0]).max()) for k in range(len(times))]
km = int(np.argmin(match))
F0r = d2[min(d2)]["F"]
ev = {
    "restart_deck": deck.split("/")[-1],
    "restart_iteration_in_deck": it,
    "initial_guess_field_name_in_deck": fname,
    "deck_state_read_1based": it,
    "deck_state_holds_stage1_iteration": it - 1,
    "intended_resume_iteration": want,
    "sha256_stage1_engine_output": sha(ck),
    "sha256_restart_initialguess": sha(ig),
    "checkpoint_byte_identical": sha(ck) == sha(ig),
    "checkpoint_steps": int(len(times)),
    "checkpoint_time_values_first_last": [float(times[0]), float(times[-1])],
    "stage1_last_iteration": max(d1),
    "stage1_cold_start_compliance_iteration_0": d1[0]["F"],
    "restart_initial_control_vs_each_checkpoint_step_max_abs_diff": match,
    "restart_initial_control_best_matching_checkpoint_step_0based": km,
    "restart_initial_control_best_match_max_abs_diff": match[km],
    "restart_resumes_from_stage1_iteration": km,
    "restart_initial_topology_vs_checkpoint_topology_at_matched_step_max_abs_diff": float(np.abs(allt[km] - rst[0]).max()),
    "stage1_compliance_at_matched_iteration": d1[km]["F"],
    "restart_first_compliance": F0r,
    "restart_first_compliance_vs_matched_iteration_abs_diff": abs(F0r - d1[km]["F"]),
    f"stage1_compliance_at_intended_iteration_{want}": d1[want]["F"],
    "restart_first_compliance_vs_intended_iteration_abs_diff": abs(F0r - d1[want]["F"]),
    "restart_first_compliance_vs_intended_iteration_rel_diff": abs(F0r - d1[want]["F"]) / abs(d1[want]["F"]),
    f"stage1_H1_at_intended_iteration_{want}": d1[want]["H1"],
    "restart_first_H1": d2[min(d2)]["H1"],
    "restart_iterations_logged": len(d2),
    "restart_last_local_iteration": max(d2),
    "restart_final_compliance": d2[max(d2)]["F"],
    "overall_final_iteration_equivalent": km + max(d2),
    "restart_engine_output_steps": int(len(rsc)),
}
ev["resumed_from_intended_iteration"] = bool(km == want and match[km] == 0.0 and abs(F0r - d1[want]["F"]) == 0.0)
json.dump(ev, open(out, "w"), indent=2)
print(json.dumps({k: v for k, v in ev.items() if "each_checkpoint" not in k}, indent=2))
sys.exit(0 if ev["resumed_from_intended_iteration"] else 3)
