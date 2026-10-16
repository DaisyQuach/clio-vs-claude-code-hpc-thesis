#!/usr/bin/env python3
"""Verify the EX8 run reached 50 iterations and produced the required fields.
Usage: python3 -I verify_result.py <run_dir> <out.txt>"""
import sys, os, re, datetime
import numpy as np, netCDF4
run, out = sys.argv[1], sys.argv[2]
checks = []
def chk(n, g, e): checks.append((n, g, e, g == e))
def names(ds, var):
    arr = ds.variables[var][:]
    if np.ma.isMaskedArray(arr): arr = arr.filled(b"")
    return [b"".join(bytes(c) if not isinstance(c, bytes) else c for c in row).split(b"\x00")[0].decode().strip() for row in arr]
diag = open(os.path.join(run, "morphorm_oc_optimizer_diagnostics.txt")).read()
rows = [l for l in diag.splitlines() if re.match(r"^\s*\d+\s+\d+\s", l)]
iters = [int(l.split()[0]) for l in rows]
chk("diagnostics: iteration rows 0..50", (min(iters), max(iters), len(iters)), (0, 50, 51))
chk("diagnostics: max iteration reached == 50", max(iters), 50)
stop = [l.strip() for l in diag.splitlines() if l.strip().startswith("******")]
chk("diagnostics: stopping message", stop, ["****** Optimization stopping due to exceeding maximum number of iterations. ******"])
last = rows[-1].split()
chk("diagnostics: final objective finite", np.isfinite(float(last[2])), True)
chk("diagnostics: final constraint H1 <= 1e-6 (feasible)", float(last[4]) <= 1e-6, True)
hist = open(os.path.join(run, "opt_criteria_history.csv")).read().strip().splitlines()
# runtime layout: one row per criterion: "<name>, v0, v1, ..., v50,"
objrow = [l for l in hist if l.startswith("My Objective")]
chk("opt_criteria_history: objective row present", len(objrow) >= 1, True)
nvals = len([v for v in objrow[0].split(",")[1:] if v.strip()]) if objrow else 0
chk("opt_criteria_history: 51 objective values (iterations 0..50)", nvals, 51)
eo = netCDF4.Dataset(os.path.join(run, "engine_output.exo"))
nvars = names(eo, "name_nod_var")
chk("engine_output: nodal fields include control and topology", all(v in nvars for v in ["control", "topology"]), True)
tsteps = len(eo.dimensions["time_step"])
times = eo.variables["time_whole"][:]
chk("engine_output: 51 time steps (iterations 0..50)", tsteps, 51)
chk("engine_output: time values 1..51 (one per iteration 0..50)", [float(t) for t in times], [float(i) for i in range(1, 52)])
chk("engine_output: nodes 15925", len(eo.dimensions["num_nodes"]), 15925)
# final design: volume fraction of filtered topology (nodal average) ~ 0.15
topo_idx = nvars.index("topology") + 1
topo = eo.variables[f"vals_nod_var{topo_idx}"][-1, :]
chk("engine_output: final topology in [0,1]", bool(topo.min() >= -1e-9 and topo.max() <= 1 + 1e-9), True)
fa = os.path.join(run, "analyze_id_2_output_scenario_id_1", "iteration50.exo")
chk("final analyze output iteration50.exo exists", os.path.isfile(fa), True)
if os.path.isfile(fa):
    ds = netCDF4.Dataset(fa)
    nv = names(ds, "name_nod_var")
    ev = names(ds, "name_elem_var") if "name_elem_var" in ds.variables else []
    chk("iteration50.exo: nodes 15925", len(ds.dimensions["num_nodes"]), 15925)
    chk("iteration50.exo: elements 13824", len(ds.dimensions["num_elem"]), 13824)
    chk("iteration50.exo: has displacement x/y/z nodal fields", all(any(re.fullmatch(r"displacement[ _]?"+c, v.lower()) for v in nv) for c in "xyz"), True)
    chk("iteration50.exo: has a density/topology field", any(("density" in v.lower() or "topology" in v.lower() or "control" in v.lower()) for v in nv + ev), True)
    chk("iteration50.exo: nodal var names (info)", nv, nv)
    chk("iteration50.exo: elem var names (info)", ev, ev)
    for v in nv:
        if v.lower().startswith("displacement"):
            arr = ds.variables[f"vals_nod_var{nv.index(v)+1}"][-1, :]
            chk(f"iteration50.exo: {v} finite", bool(np.all(np.isfinite(arr))), True)
n_iter_files = len([f for f in os.listdir(os.path.join(run, "analyze_id_2_output_scenario_id_1")) if re.match(r"iteration\d+\.exo$", f)])
chk("analyze per-iteration exo files (0..50)", n_iter_files, 51)
allok = all(c[3] for c in checks)
lines = ["EX8 result verification record (FROZEN-EX8-v1)",
         f"utc_timestamp: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}", f"run_dir: {run}",
         f"engine_output time steps: {tsteps}, time values: {[float(t) for t in times]}", ""]
for n, g, e, ok in checks:
    lines.append(f"{n:58s} {str(g)[:60]:>60s} {'PASS' if ok else 'FAIL'}")
lines += ["", f"OVERALL: {'PASS' if allok else 'FAIL'} ({sum(c[3] for c in checks)}/{len(checks)} checks passed)"]
open(out, "w").write("\n".join(lines) + "\n"); print("\n".join(lines)); sys.exit(0 if allok else 1)
