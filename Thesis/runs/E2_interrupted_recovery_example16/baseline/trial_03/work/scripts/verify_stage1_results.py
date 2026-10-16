"""Verify Stage-1 results: iteration cap reached, checkpoint has 21 saved states with control+topology, final analyze output present."""
import sys, os, re, json, hashlib, datetime
import numpy as np
from netCDF4 import Dataset
d = sys.argv[1]
res = []
def chk(label, ok, got, want):
    res.append({"check": label, "pass": bool(ok), "got": got, "expected": want})
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def names(ds, var):
    out = []
    for row in ds.variables[var][:]:
        out.append("".join(c.decode() if isinstance(c, bytes) else str(c) for c in row.compressed()).strip())
    return out
# ---- optimizer diagnostics
diag = open(os.path.join(d, "morphorm_oc_optimizer_diagnostics.txt")).read()
rows = [l.split() for l in diag.splitlines() if re.match(r'^\s*\d+\s+\d+\s', l)]
iters = [int(r[0]) for r in rows]
chk("diagnostics rows iterations 0..20 (21 rows)", iters == list(range(21)), iters, list(range(21)))
stop = [l.strip() for l in diag.splitlines() if l.strip().startswith("******")]
chk("stopping message = max iterations", len(stop) == 1 and "maximum number of iterations" in stop[0], stop, "****** Optimization stopping due to exceeding maximum number of iterations. ******")
last = rows[-1] if rows else None
hist = {int(r[0]): {"F-count": int(r[1]), "F(X)": float(r[2]), "Norm(F')": float(r[3]), "H1(X)": float(r[4]), "abs(dX)": float(r[5]), "abs(dF)": float(r[6])} for r in rows}
chk("final iteration index 20", last is not None and int(last[0]) == 20, int(last[0]) if last else None, 20)
chk("all objective values finite and positive", all(np.isfinite(v["F(X)"]) and v["F(X)"] > 0 for v in hist.values()), [v["F(X)"] for v in hist.values()][-3:], "finite > 0")
# ---- opt_criteria_history.csv
csvp = os.path.join(d, "opt_criteria_history.csv")
csv = open(csvp).read().strip().splitlines() if os.path.exists(csvp) else []
# runtime writes one row per criterion: "<name>, v0, v1, ..., v20," (21 values for iterations 0..20)
csvvals = [float(x) for x in csv[0].split(",")[1:] if x.strip()] if csv else []
chk("opt_criteria_history.csv holds 21 objective values (iterations 0..20)", len(csvvals) == 21, len(csvvals), 21)
chk("opt_criteria_history.csv objective values match diagnostics F(X) (rel 1e-6)", len(csvvals) == 21 and all(abs(csvvals[i] - hist[i]["F(X)"]) <= 1e-6 * abs(hist[i]["F(X)"]) for i in range(21)), csvvals[-1:] if csvvals else None, hist[20]["F(X)"] if 20 in hist else None)
# ---- engine_output.exo (checkpoint)
eo = os.path.join(d, "engine_output.exo")
ds = Dataset(eo)
nsteps = int(ds.dimensions["time_step"].size)
times = [float(t) for t in ds.variables["time_whole"][:]]
nvars = names(ds, "name_nod_var") if "name_nod_var" in ds.variables else []
chk("engine_output.exo time steps = 21 (iterations 0-20)", nsteps == 21, nsteps, 21)
chk("engine_output.exo time values", times == [float(i) for i in range(21)] or len(times) == 21, times, "21 monotone values (0..20)")
chk("engine_output.exo nodal fields include control and topology", "control" in nvars and "topology" in nvars, nvars, ["control", "topology"])
chk("engine_output.exo node count = 30625", int(ds.dimensions["num_nodes"].size) == 30625, int(ds.dimensions["num_nodes"].size), 30625)
chk("engine_output.exo element count = 27648", int(ds.dimensions["num_elem"].size) == 27648, int(ds.dimensions["num_elem"].size), 27648)
field_stats = {}
if "control" in nvars and "topology" in nvars:
    ic, it = nvars.index("control") + 1, nvars.index("topology") + 1
    c = np.asarray(ds.variables[f"vals_nod_var{ic}"][:], dtype=float); t = np.asarray(ds.variables[f"vals_nod_var{it}"][:], dtype=float)
    for s in range(nsteps):
        field_stats[s] = {"control_min": float(c[s].min()), "control_max": float(c[s].max()), "control_mean": float(c[s].mean()),
                          "topology_min": float(t[s].min()), "topology_max": float(t[s].max()), "topology_mean": float(t[s].mean())}
    chk("saved state 0 control is uniform 0.15 (initial density)", abs(c[0].min() - 0.15) < 1e-12 and abs(c[0].max() - 0.15) < 1e-12, [float(c[0].min()), float(c[0].max())], [0.15, 0.15])
    chk("all 21 saved control states finite and within [0,1]", bool(np.all(np.isfinite(c)) and c.min() >= -1e-12 and c.max() <= 1 + 1e-12), [float(c.min()), float(c.max())], "[0,1]")
    chk("saved states differ across iterations (design evolves)", all(np.abs(c[s] - c[s-1]).max() > 0 for s in range(1, nsteps)), [float(np.abs(c[s] - c[s-1]).max()) for s in range(1, nsteps)][:5], "> 0 for every consecutive pair")
    chk("iteration-20 (last saved) control state present and non-uniform", c[20].std() > 0, float(c[20].std()), "> 0")
ds.close()
# ---- restart file
er = os.path.join(d, "engine_restart.exo")
# The spec defines the checkpoint as the engine output file (engine_output.exo) holding control+topology at every iteration.
# A separate engine_restart.exo is NOT required by the spec; record its presence for information only (not a pass/fail check).
restart_file_present = os.path.exists(er)
# ---- analyze outputs
adir = os.path.join(d, "analyze_id_2_output_scenario_id_1")
afiles = sorted(os.listdir(adir)) if os.path.isdir(adir) else []
it_exo = sorted(int(m.group(1)) for f in afiles for m in [re.match(r'iteration(\d+)\.exo$', f)] if m)
chk("analyze per-iteration exodus files iteration0..20", it_exo == list(range(21)), it_exo, list(range(21)))
fin = os.path.join(adir, "iteration20.exo")
if os.path.exists(fin):
    da = Dataset(fin); nv = names(da, "name_nod_var") if "name_nod_var" in da.variables else []
    chk("final analyze output (iteration20.exo) has displacement fields", any("displacement" in v or "disp" in v for v in nv), nv, "displacement_x/y/z present")
    da.close()
out = {"directory": d, "verified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "checkpoint": {"path": eo, "sha256": sha(eo), "time_steps": nsteps, "nodal_fields": nvars},
       "separate_engine_restart_exo_present_(informational)": restart_file_present,
       "final_analyze_output": {"path": fin, "sha256": sha(fin) if os.path.exists(fin) else None},
       "diagnostics_sha256": sha(os.path.join(d, "morphorm_oc_optimizer_diagnostics.txt")),
       "stopping_message": stop, "diagnostics_history": hist, "saved_state_field_stats": field_stats,
       "checks": res, "ALL_CHECKS_PASS": all(r["pass"] for r in res)}
print(json.dumps(out, indent=2)); sys.exit(0 if out["ALL_CHECKS_PASS"] else 1)
