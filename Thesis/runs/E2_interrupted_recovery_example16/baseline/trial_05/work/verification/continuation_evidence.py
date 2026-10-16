"""Continuation evidence for FROZEN-EX16-v1 (spec section 7): Stage 2 must start from the iteration-20 design of Stage 1.
Usage: python3 -I continuation_evidence.py <stage1_run_dir> <stage2_run_dir> <stage2_deck> <restart_iteration_used>
Compares (a) Stage-2 first evaluated compliance (local iteration 0) with every Stage-1 compliance, and
(b) the Stage-2 engine-output state 1 'control' field with every saved 'control' state of the Stage-1 checkpoint.
"""
import sys, os, re, json, hashlib, datetime
import numpy as np, netCDF4
s1, s2, deck, riter = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def rows(path):
    out = []
    for line in open(path):
        m = re.match(r"^\s*(\d+)\s+(\d+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)", line)
        if m: out.append((int(m.group(1)), float(m.group(3))))
    return out
r1 = rows(os.path.join(s1, "morphorm_oc_optimizer_diagnostics.txt")); r2 = rows(os.path.join(s2, "morphorm_oc_optimizer_diagnostics.txt"))
F1 = dict(r1); F2 = dict(r2)
hist1 = [float(x) for x in open(os.path.join(s1, "opt_criteria_history.csv")).read().split(",")[1:] if x.strip()]
hist2 = [float(x) for x in open(os.path.join(s2, "opt_criteria_history.csv")).read().split(",")[1:] if x.strip()] if os.path.exists(os.path.join(s2, "opt_criteria_history.csv")) else []
res = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "stage1_run_dir": s1, "stage2_run_dir": s2, "checks": {}}
C = res["checks"]
res["restart_settings_in_stage2_deck"] = {k: re.search(r"^\s*%s\s+(\S+)" % k, open(deck).read(), re.M).group(1) for k in ["initial_guess_file_name", "initial_guess_field_name", "restart_iteration", "max_iterations"]}
res["restart_iteration_used"] = riter
res["restart_input_sha256"] = sha(os.path.join(s2, "restart_input.exo")); res["stage1_checkpoint_sha256"] = sha(os.path.join(s1, "engine_output.exo"))
C["restart_input.exo is an exact copy of the Stage-1 checkpoint engine_output.exo"] = res["restart_input_sha256"] == res["stage1_checkpoint_sha256"]
res["stage1_compliance_iter19"] = F1.get(19); res["stage1_compliance_iter20"] = F1.get(20)
res["stage1_criteria_history_last"] = hist1[-1] if hist1 else None
res["stage2_first_compliance_local_iter0"] = F2.get(0)
res["stage2_criteria_history_first"] = hist2[0] if hist2 else None
# (a) diagnostics comparison: which Stage-1 iteration does Stage-2's first compliance match?
match = [i for i, f in F1.items() if F2.get(0) is not None and abs(f - F2[0]) <= 1e-6 * max(1.0, abs(f))]
res["stage1_iterations_matching_stage2_first_compliance (6-digit diagnostics)"] = match
C["Stage-2 first compliance == Stage-1 iteration-20 compliance (diagnostics, 7 significant digits)"] = match == [20]
if hist1 and hist2:
    res["criteria_history_rel_diff_iter20_vs_stage2_first"] = abs(hist1[-1] - hist2[0]) / abs(hist1[-1])
    C["Stage-2 first compliance == Stage-1 iteration-20 compliance (opt_criteria_history.csv, rel diff < 1e-10)"] = res["criteria_history_rel_diff_iter20_vs_stage2_first"] < 1e-10
# (b) saved fields: Stage-2 engine output state 1 (local iteration 0) control vs Stage-1 checkpoint states
def nod(ds, name):
    nv = [row.tobytes().split(b"\x00")[0].decode().strip() for row in ds.variables["name_nod_var"][:]]
    return "vals_nod_var%d" % (nv.index(name) + 1)
d1 = netCDF4.Dataset(os.path.join(s1, "engine_output.exo")); d2 = netCDF4.Dataset(os.path.join(s2, "engine_output.exo"))
c2 = d2.variables[nod(d2, "control")][0, :]; t2 = d2.variables[nod(d2, "topology")][0, :]
n1 = len(d1.variables["time_whole"][:])
diffs = []
for k in range(n1):
    c1 = d1.variables[nod(d1, "control")][k, :]; t1 = d1.variables[nod(d1, "topology")][k, :]
    diffs.append({"stage1_exodus_step": k + 1, "stage1_iteration": k, "max_abs_diff_control": float(np.max(np.abs(c1 - c2))), "max_abs_diff_topology": float(np.max(np.abs(t1 - t2)))})
res["stage2_state1_vs_stage1_states"] = diffs
exact = [d["stage1_iteration"] for d in diffs if d["max_abs_diff_control"] == 0.0]
res["stage1_iterations_whose_control_field_equals_stage2_initial_control"] = exact
C["Stage-2 initial control field is bit-identical to the Stage-1 iteration-20 (Exodus step 21) control field"] = exact == [20]
C["Stage-2 initial topology (filtered) field equals Stage-1 iteration-20 topology (max abs diff < 1e-10)"] = diffs[20]["max_abs_diff_topology"] < 1e-10 if len(diffs) > 20 else False
res["stage2_num_saved_states"] = len(d2.variables["time_whole"][:])
d1.close(); d2.close()
res["ALL_CHECKS_PASS"] = all(C.values())
print(json.dumps(res, indent=2))
sys.exit(0 if res["ALL_CHECKS_PASS"] else 1)
