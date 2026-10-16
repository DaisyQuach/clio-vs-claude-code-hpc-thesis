#!/usr/bin/env python3
"""Post-run verification for FROZEN-EX8-v1: iteration count, engine output history, final analyze output.
Usage: verify_results.py <run_dir> <final_analyze_output.exo>"""
import sys, os, json, datetime, re
import numpy as np, netCDF4

d, final_exo = sys.argv[1], sys.argv[2]
res = {"run_dir": os.path.abspath(d), "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "checks": []}
def check(name, got, want, ok=None):
    if ok is None: ok = (got == want)
    res["checks"].append({"check": name, "got": got, "expected": want, "pass": bool(ok)})

# optimizer diagnostics
diag = os.path.join(d, "morphorm_oc_optimizer_diagnostics.txt")
check("diagnostics_exists", os.path.exists(diag), True)
rows = []
if os.path.exists(diag):
    for line in open(diag):
        parts = line.split()
        if parts and parts[0].isdigit(): rows.append(parts)
    iters = [int(r[0]) for r in rows]
    check("diagnostics_last_iteration", max(iters) if iters else None, 50)
    check("diagnostics_iterations_0_to_50_contiguous", iters, "0..50", iters == list(range(0, 51)))
    res["final_row"] = dict(zip(["Iter", "F-count", "F(X)", "Norm(F')", "H1(X)", "abs(dX)", "abs(dF)"], rows[-1])) if rows else None
    res["initial_row"] = dict(zip(["Iter", "F-count", "F(X)", "Norm(F')", "H1(X)", "abs(dX)", "abs(dF)"], rows[0])) if rows else None

# run log stopping message
log = os.path.join(d, "morphorm_run.log")
if os.path.exists(log):
    txt = open(log, errors="replace").read()
    msgs = [l.strip() for l in txt.splitlines() if re.search(r"(?i)(converg|stop|max.*iter|iteration.*reached|tolerance|complete|finish|terminat)", l)]
    res["stopping_messages"] = msgs[-10:]
    check("run_log_has_no_error", not re.search(r"(?i)\b(error|fatal|abort|segfault|exception)\b", txt), True)

# engine output
eo = os.path.join(d, "engine_output.exo")
check("engine_output_exists", os.path.exists(eo), True)
if os.path.exists(eo):
    ds = netCDF4.Dataset(eo)
    t = ds.variables["time_whole"][:] if "time_whole" in ds.variables else []
    nv = [ "".join(c.decode() for c in row.compressed()).strip() for row in ds.variables["name_nod_var"][:]] if "name_nod_var" in ds.variables else []
    res["engine_output_time_steps"] = [float(v) for v in t]
    res["engine_output_nodal_vars"] = nv
    check("engine_output_has_control_and_topology", all(any(n.lower().startswith(k) for n in nv) for k in ("control", "topology")), True)
    # engine writes one state per optimizer iteration 0..50 (time stamps 1..51): 51 design states expected
    check("engine_output_num_design_states (iterations 0..50)", len(t), 51)
    check("engine_output_time_steps_contiguous", [float(v) for v in t] == [float(i) for i in range(1, 52)], True)
    check("engine_output_num_nodes", len(ds.dimensions["num_nodes"]), 15925)
    ds.close()

# final analyze output
check("final_analyze_output_exists", os.path.exists(final_exo), True)
if os.path.exists(final_exo):
    ds = netCDF4.Dataset(final_exo)
    nv = ["".join(c.decode() for c in row.compressed()).strip() for row in ds.variables["name_nod_var"][:]] if "name_nod_var" in ds.variables else []
    ev = ["".join(c.decode() for c in row.compressed()).strip() for row in ds.variables["name_elem_var"][:]] if "name_elem_var" in ds.variables else []
    res["final_analyze_nodal_vars"] = nv; res["final_analyze_elem_vars"] = ev
    res["final_analyze_time_steps"] = [float(v) for v in ds.variables["time_whole"][:]] if "time_whole" in ds.variables else []
    norm = [re.sub(r"[^a-z]", "", n.lower()) for n in nv]
    check("final_analyze_has_displacements (dispx, dispy, dispz)", sorted(n for n in norm if "disp" in n), ["displacementx", "displacementy", "displacementz"])
    check("final_analyze_time_step_is_iteration_50", [float(v) for v in ds.variables["time_whole"][:]], [50.0])
    check("final_analyze_has_density_field", any(("topolog" in n.lower() or "densit" in n.lower() or "control" in n.lower()) for n in nv + ev), True)
    check("final_analyze_num_nodes", len(ds.dimensions["num_nodes"]), 15925)
    check("final_analyze_num_elem", len(ds.dimensions["num_elem"]), 13824)
    ds.close()

res["all_pass"] = all(c["pass"] for c in res["checks"])
print(json.dumps(res, indent=1))
sys.exit(0 if res["all_pass"] else 1)
