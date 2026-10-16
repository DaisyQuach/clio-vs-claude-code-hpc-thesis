#!/usr/bin/env python3
"""Extract scalar results from one executed Morphorm run directory.

Writes <out_prefix>_criterion_history.csv (from morphorm_oc_optimizer_diagnostics.txt)
and <out_prefix>_summary.json (final scalars from the diagnostics and from the
final analyze Exodus file).  Run with the approved runtime's python3.

Usage: summarize_run.py <run_dir> <out_prefix> [--expect-iterations N]
Exit 0 on success; 2 if the diagnostics show fewer iterations than expected or
no stop message.
"""
import csv, glob, json, os, re, sys
import numpy as np
from netCDF4 import Dataset

run, out = sys.argv[1], sys.argv[2]
expect = None
if "--expect-iterations" in sys.argv:
    expect = int(sys.argv[sys.argv.index("--expect-iterations") + 1])


def names(ds, var):
    return [b"".join(r.compressed()).decode() for r in ds.variables[var][:]] if var in ds.variables else []


def nodal(ds, name, step=-1):
    i = names(ds, "name_nod_var").index(name) + 1
    return np.asarray(ds.variables[f"vals_nod_var{i}"][step, :], dtype=float)


diag = os.path.join(run, "morphorm_oc_optimizer_diagnostics.txt")
rows, stop_msg = [], None
with open(diag) as fh:
    fh.readline()
    for line in fh:
        parts = line.split()
        if parts and re.fullmatch(r"\d+", parts[0]):
            rows.append([int(parts[0]), int(parts[1])] + [float(p) for p in parts[2:7]])
        elif "Optimization stopping" in line:
            stop_msg = line.strip().strip("*").strip()
cols = ["iteration", "f_count", "compliance_F", "norm_grad_F", "volume_constraint_H1", "abs_dX", "abs_dF"]
with open(f"{out}_criterion_history.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(cols)
    w.writerows(rows)

outs = glob.glob(os.path.join(run, "analyze_id_2_output_scenario_id_1", "iteration*.exo"))
final = max(outs, key=lambda p: int(re.search(r"iteration(\d+)\.exo$", p).group(1)))
with Dataset(final) as ds:
    rho = nodal(ds, "Topology")
    u = np.stack([nodal(ds, f"displacement {c}") for c in "XYZ"], axis=1)
    conn = np.asarray(ds.variables["connect1"][:]) - 1
    xyz = np.stack([np.asarray(ds.variables[c][:]) for c in ("coordx", "coordy", "coordz")], axis=1)
ext = xyz[conn].max(axis=1) - xyz[conn].min(axis=1)
vol = ext.prod(axis=1)
rho_e = rho[conn].mean(axis=1)
umag = np.linalg.norm(u, axis=1)
solid_nodes = np.unique(conn[rho_e >= 0.5])

eng = os.path.join(run, "engine_output.exo")
with Dataset(eng) as ds:
    n_steps = len(ds.dimensions["time_step"])
    eng_vars = names(ds, "name_nod_var")
    times = np.asarray(ds.variables["time_whole"][:], dtype=float).tolist()

summary = {
    "run_dir": os.path.basename(os.path.abspath(run)),
    "iterations_logged": len(rows),
    "first_iteration": rows[0][0], "last_iteration": rows[-1][0],
    "stop_message": stop_msg,
    "initial_compliance": rows[0][2], "final_compliance": rows[-1][2],
    "final_volume_constraint_H1": rows[-1][4],
    "final_abs_dX": rows[-1][5], "final_abs_dF": rows[-1][6],
    "final_analyze_exodus": os.path.relpath(final, run),
    "num_elements": int(len(conn)), "num_nodes": int(len(rho)),
    "volume_fraction_mean_density": float((rho_e * vol).sum() / vol.sum()),
    "volume_fraction_solid_rho_ge_0.5": float(vol[rho_e >= 0.5].sum() / vol.sum()),
    "density_min": float(rho.min()), "density_max": float(rho.max()),
    "fraction_gray_elements_0.1_to_0.9": float(((rho_e > 0.1) & (rho_e < 0.9)).mean()),
    "max_displacement_magnitude_all_nodes": float(umag.max()),
    "max_displacement_magnitude_solid_nodes": float(umag[solid_nodes].max()) if solid_nodes.size else None,
    "engine_output_steps": n_steps, "engine_output_nodal_fields": eng_vars,
    "engine_output_time_values_first_last": [times[0], times[-1]],
    "expected_last_iteration": expect,
    "reached_expected_iterations": (expect is None) or (rows[-1][0] == expect),
}
with open(f"{out}_summary.json", "w") as fh:
    json.dump(summary, fh, indent=2)
print(json.dumps(summary, indent=2))
ok = summary["reached_expected_iterations"] and stop_msg is not None
sys.exit(0 if ok else 2)
