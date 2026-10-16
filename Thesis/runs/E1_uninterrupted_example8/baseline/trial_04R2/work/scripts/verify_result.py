#!/usr/bin/env python3
"""Verify the finished FROZEN-EX8-v1 run reached 50 iterations and inspect the final outputs (read-only)."""
import sys, os, re, json, datetime
import numpy as np
import netCDF4
rd = sys.argv[1]
rec = {"run_dir": rd, "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
checks = []
def chk(name, ok, got, want): checks.append({"check": name, "pass": bool(ok), "got": got, "expected": want})
# optimizer diagnostics
dg = open(os.path.join(rd, "morphorm_oc_optimizer_diagnostics.txt")).read()
rows = [l for l in dg.splitlines() if re.match(r"^\s*\d+\s+\d+\s", l)]
iters = [int(l.split()[0]) for l in rows]
chk("diagnostics_last_iteration_50", iters and iters[-1] == 50, iters[-1] if iters else None, 50)
chk("diagnostics_rows_0..50", iters == list(range(0, 51)), [len(iters), iters[:3], iters[-3:]], [51, [0, 1, 2], [48, 49, 50]])
msg = [l.strip() for l in dg.splitlines() if "******" in l]
rec["stopping_message"] = msg
chk("stopping_message_is_max_iterations", any("maximum number of iterations" in m for m in msg), msg, "exceeding maximum number of iterations")
chk("no_early_convergence_message", not any("converged" in m.lower() for m in msg), msg, "no 'converged' message")
last = rows[-1].split() if rows else []
rec["final_diagnostics_row"] = rows[-1] if rows else None
if last:
    rec["final_objective"] = float(last[2]); rec["final_constraint_H1"] = float(last[4])
    chk("final_constraint_feasible_H1<=1e-6", float(last[4]) <= 1e-6, float(last[4]), "<= 1e-6")
# opt_criteria_history.csv
# opt_criteria_history.csv is written as one row per criterion: "<name>, v0, v1, ..., v50,"
hist = [l for l in open(os.path.join(rd, "opt_criteria_history.csv")).read().strip().splitlines() if l.strip()]
hvals = [v.strip() for v in hist[0].split(",")[1:] if v.strip()] if hist else []
chk("criteria_history_has_51_objective_values(iter0..50)", len(hvals) == 51, len(hvals), 51)
rec["criteria_history"] = {"rows": len(hist), "criterion": hist[0].split(",")[0] if hist else None, "n_values": len(hvals), "first": hvals[0] if hvals else None, "last": hvals[-1] if hvals else None}
# engine_output.exo
eo = netCDF4.Dataset(os.path.join(rd, "engine_output.exo"))
nsteps = eo.dimensions["time_step"].size
evars = [b"".join(c for c in r.tolist() if c and c != b"\x00").decode().strip() for r in eo.variables["name_nod_var"][:]] if "name_nod_var" in eo.variables else []
times = eo.variables["time_whole"][:].tolist() if "time_whole" in eo.variables else []
chk("engine_output_has_control_and_topology", "control" in evars and "topology" in evars, evars, ["control", "topology"])
rec["engine_output"] = {"time_steps": int(nsteps), "nodal_vars": evars, "times": times, "num_nodes": int(eo.dimensions["num_nodes"].size), "num_elem": int(eo.dimensions["num_elem"].size)}
# engine_output.exo stores iterations 0..50 as time steps 1..51
chk("engine_output_51_time_steps(iter0..50)", nsteps == 51 and times and abs(times[-1] - 51) < 1e-9, [int(nsteps), times[-1] if times else None], [51, 51.0])
if "topology" in evars and nsteps:
    iv = evars.index("topology") + 1
    topo = eo.variables[f"vals_nod_var{iv}"][-1, :]
    rec["engine_output_final_topology_stats"] = {"min": float(topo.min()), "max": float(topo.max()), "mean": float(topo.mean())}
if "control" in evars and nsteps:
    iv = evars.index("control") + 1
    ctl = eo.variables[f"vals_nod_var{iv}"][-1, :]
    rec["engine_output_final_control_stats"] = {"min": float(ctl.min()), "max": float(ctl.max()), "mean": float(ctl.mean())}
# final analyze output file
vd = os.path.join(rd, "analyze_id_2_output_scenario_id_1")
files = sorted(os.listdir(vd)) if os.path.isdir(vd) else []
itfiles = sorted((int(re.match(r"iteration(\d+)\.exo", f).group(1)), f) for f in files if re.match(r"iteration\d+\.exo$", f))
rec["analyze_iteration_files"] = {"count": len(itfiles), "first": itfiles[0][1] if itfiles else None, "last": itfiles[-1][1] if itfiles else None}
chk("analyze_iteration50_exo_exists", any(i == 50 for i, _ in itfiles), itfiles[-1][1] if itfiles else None, "iteration50.exo")
if any(i == 50 for i, _ in itfiles):
    fa = netCDF4.Dataset(os.path.join(vd, "iteration50.exo"))
    nv = [b"".join(c for c in r.tolist() if c and c != b"\x00").decode().strip() for r in fa.variables["name_nod_var"][:]] if "name_nod_var" in fa.variables else []
    ev = [b"".join(c for c in r.tolist() if c and c != b"\x00").decode().strip() for r in fa.variables["name_elem_var"][:]] if "name_elem_var" in fa.variables else []
    rec["iteration50_exo"] = {"nodal_vars": nv, "elem_vars": ev, "time_steps": int(fa.dimensions["time_step"].size), "num_nodes": int(fa.dimensions["num_nodes"].size), "num_elem": int(fa.dimensions["num_elem"].size)}
    norm = [re.sub(r"[\s_]", "", v.lower()) for v in nv]
    has_disp = all(d in norm for d in ("displacementx", "displacementy", "displacementz")) or all(d in norm for d in ("dispx", "dispy", "dispz"))
    chk("iteration50_has_displacements_xyz", has_disp, nv, "displacement X/Y/Z")
    has_dens = any("topolog" in v.lower() or "density" in v.lower() or "control" in v.lower() for v in nv + ev)
    chk("iteration50_has_density_field", has_dens, nv + ev, "a topology/density field")
    for v in nv:
        iv = nv.index(v) + 1
        arr = fa.variables[f"vals_nod_var{iv}"][-1, :]
        rec["iteration50_exo"][f"stat_{v}"] = {"min": float(arr.min()), "max": float(arr.max())}
    chk("iteration50_finite", all(np.isfinite(fa.variables[f"vals_nod_var{i+1}"][-1, :]).all() for i in range(len(nv))), "finite", "finite")
rec["checks"] = checks; rec["all_pass"] = all(c["pass"] for c in checks)
print(json.dumps(rec, indent=2))
sys.exit(0 if rec["all_pass"] else 1)
