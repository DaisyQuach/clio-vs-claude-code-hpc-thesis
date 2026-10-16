#!/usr/bin/env python3
"""Verify the completed optimization reached the required iteration count and that the
required output files exist with the expected contents.
Usage: python3 -I verify_results.py <run_dir>
Exit 0 only if every check passes."""
import sys, os, re, json, datetime, glob
import numpy as np
import netCDF4

run = sys.argv[1]
checks = []
def check(name, actual, expected):
    ok = (actual == expected)
    checks.append({"check": name, "expected": expected, "actual": actual, "pass": bool(ok)})
    return ok

def exo_names(ds, var):
    out = []
    if var not in ds.variables: return out
    for row in ds.variables[var][:]:
        s = b''.join([b if isinstance(b, bytes) else bytes(b) for b in row.compressed()]) if hasattr(row, 'compressed') else row.tobytes()
        out.append(s.decode('utf-8', 'ignore').strip('\x00').strip())
    return out

# ---- optimizer diagnostics ----
diag = os.path.join(run, 'morphorm_oc_optimizer_diagnostics.txt')
check("diagnostics_file_exists", os.path.exists(diag), True)
txt = open(diag).read() if os.path.exists(diag) else ''
lines = [l for l in txt.splitlines() if l.strip()]
iters = []
rows = {}
for l in lines:
    m = re.match(r'^\s*(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', l)
    if m:
        it = int(m.group(1)); iters.append(it)
        rows[it] = {"F-count": int(m.group(2)), "F(X)": float(m.group(3)), "Norm(F')": float(m.group(4)),
                    "H1(X)": float(m.group(5)), "abs(dX)": float(m.group(6)), "abs(dF)": float(m.group(7))}
check("diagnostics_max_iteration_index", max(iters) if iters else None, 50)
check("diagnostics_iterations_0_to_50_all_present", sorted(set(iters)), list(range(0, 51)))
term = [l.strip() for l in lines if l.strip().startswith('******')]
checks.append({"check": "optimizer_termination_message(info)", "expected": None, "actual": term, "pass": True})
check("terminated_by_reaching_max_iterations", any('maximum number of iterations' in t for t in term), True)
check("not_terminated_by_convergence_before_cap", any('converged' in t.lower() for t in term), False)
check("no_simulation_failure_message", any('failed' in t.lower() for t in term), False)
checks.append({"check": "iteration_0_row(info)", "expected": None, "actual": rows.get(0), "pass": True})
checks.append({"check": "iteration_50_row(info)", "expected": None, "actual": rows.get(50), "pass": True})
if 50 in rows:
    check("final_volume_constraint_H1_<=_1e-3", bool(rows[50]["H1(X)"] <= 1e-3), True)
    check("final_objective_finite_positive", bool(np.isfinite(rows[50]["F(X)"]) and rows[50]["F(X)"] > 0), True)

# ---- opt_criteria_history.csv ----
hist = os.path.join(run, 'opt_criteria_history.csv')
checks.append({"check": "opt_criteria_history_exists(info)", "expected": None, "actual": os.path.exists(hist), "pass": True})
if os.path.exists(hist):
    hl = [l for l in open(hist).read().splitlines() if l.strip()]
    checks.append({"check": "opt_criteria_history_rows(info)", "expected": None, "actual": len(hl) - 1, "pass": True})
    checks.append({"check": "opt_criteria_history_last(info)", "expected": None, "actual": hl[-1] if hl else None, "pass": True})

# ---- engine_output.exo ----
eo = os.path.join(run, 'engine_output.exo')
check("engine_output_exists", os.path.exists(eo), True)
if os.path.exists(eo):
    ds = netCDF4.Dataset(eo)
    nsteps = len(ds.dimensions['time_step']) if 'time_step' in ds.dimensions else 0
    nodal = exo_names(ds, 'name_nod_var')
    checks.append({"check": "engine_output_time_steps(info)", "expected": None, "actual": nsteps, "pass": True})
    checks.append({"check": "engine_output_time_values(info)", "expected": None, "actual": [float(v) for v in ds.variables['time_whole'][:]] if 'time_whole' in ds.variables else None, "pass": True})
    check("engine_output_has_control_and_topology", all(n in nodal for n in ['control', 'topology']), True)
    checks.append({"check": "engine_output_nodal_vars(info)", "expected": None, "actual": nodal, "pass": True})
    check("engine_output_num_nodes", len(ds.dimensions['num_nodes']), 15925)
    check("engine_output_num_elem", len(ds.dimensions['num_elem']), 13824)
    if nsteps and 'topology' in nodal:
        iv = nodal.index('topology') + 1
        topo = np.array(ds.variables['vals_nod_var%d' % iv][nsteps - 1, :])
        checks.append({"check": "engine_output_final_topology_stats(info)", "expected": None,
                       "actual": {"min": float(topo.min()), "max": float(topo.max()), "mean": float(topo.mean())}, "pass": True})
        check("engine_output_final_topology_in_[0,1]", bool(topo.min() >= -1e-9 and topo.max() <= 1 + 1e-9), True)
    ds.close()

# ---- final analyze output (iteration 50) ----
cands = sorted(glob.glob(os.path.join(run, 'analyze_id_2_output*', 'iteration50.exo')))
check("final_analyze_output_iteration50_exists", len(cands) >= 1, True)
checks.append({"check": "final_analyze_output_path(info)", "expected": None, "actual": cands, "pass": True})
if cands:
    ds = netCDF4.Dataset(cands[0])
    nodal = exo_names(ds, 'name_nod_var'); elem = exo_names(ds, 'name_elem_var')
    checks.append({"check": "iteration50_nodal_vars(info)", "expected": None, "actual": nodal, "pass": True})
    checks.append({"check": "iteration50_elem_vars(info)", "expected": None, "actual": elem, "pass": True})
    norm = [n.lower().replace(' ', '_') for n in nodal]
    check("iteration50_has_displacements_x_y_z", all(any(n.startswith(p) for n in norm) for p in ['displacement_x', 'displacement_y', 'displacement_z']) or all(n in norm for n in ['dispx', 'dispy', 'dispz']), True)
    check("iteration50_has_density_field", any('topology' in n.lower() or 'density' in n.lower() or 'control' in n.lower() for n in nodal + elem), True)
    check("iteration50_num_nodes", len(ds.dimensions['num_nodes']), 15925)
    for n in nodal:
        if n.lower().replace(' ', '_') in ('displacement_y', 'dispy'):
            iv = nodal.index(n) + 1
            uy = np.array(ds.variables['vals_nod_var%d' % iv][-1, :])
            checks.append({"check": "iteration50_uy_range(info)", "expected": None, "actual": [float(uy.min()), float(uy.max())], "pass": True})
            check("iteration50_uy_finite", bool(np.all(np.isfinite(uy))), True)
    ds.close()
    allit = sorted(glob.glob(os.path.join(os.path.dirname(cands[0]), 'iteration*.exo')))
    checks.append({"check": "analyze_iteration_files_count(info)", "expected": None, "actual": len(allit), "pass": True})

# ---- run log ----
rl = os.path.join(run, 'morphorm_run.log')
check("morphorm_run_log_exists", os.path.exists(rl), True)
if os.path.exists(rl):
    rtxt = open(rl, errors='ignore').read()
    errs = [l for l in rtxt.splitlines() if re.search(r'\b(error|exception|abort|segfault|nan)\b', l, re.I)]
    checks.append({"check": "run_log_error_like_lines(info)", "expected": None, "actual": errs[:20], "pass": True})

all_pass = all(c["pass"] for c in checks)
print(json.dumps({"trial_id": "E1-example8-baseline-02", "frozen_configuration_id": "FROZEN-EX8-v1", "run_dir": os.path.abspath(run),
                  "verification_utc": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                  "checks": checks, "all_checks_pass": all_pass}, indent=2, default=str))
sys.exit(0 if all_pass else 1)
