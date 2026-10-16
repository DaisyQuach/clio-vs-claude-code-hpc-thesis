#!/usr/bin/env python3
"""Runtime evidence that the essential BCs were enforced: read an analyze iteration output and test
u=0 on x=0 nodes and u_z=0 on z=0.5 nodes (sideset ss_sym), and that u_y<0 at the loaded edge."""
import sys, re, json, numpy as np, netCDF4
f = sys.argv[1]
ds = netCDF4.Dataset(f)
nv = ["".join(c.decode() for c in row.compressed()).strip() for row in ds.variables["name_nod_var"][:]]
ev = ["".join(c.decode() for c in row.compressed()).strip() for row in ds.variables["name_elem_var"][:]] if "name_elem_var" in ds.variables else []
x = ds.variables["coordx"][:]; y = ds.variables["coordy"][:]; z = ds.variables["coordz"][:]
def nodal(name, step=-1):
    # match e.g. 'displacement_x', 'dispx', 'Displacement X', 'disp_x'
    comp = name[-1]
    cands = [n for n in nv if "disp" in n.lower() and re.sub(r"[^a-z]", "", n.lower()).endswith(comp)]
    if not cands: raise SystemExit(f"no nodal variable for {name}; available: {nv}")
    i = nv.index(cands[0]) + 1
    return np.array(ds.variables[f"vals_nod_var{i}"][step, :])
out = {"file": f, "nodal_vars": nv, "elem_vars": ev, "time_steps": [float(t) for t in ds.variables["time_whole"][:]]}
ux, uy, uz = (nodal(n) for n in ("displacement_x", "displacement_y", "displacement_z"))
fix = np.abs(x) < 1e-9; sym = np.abs(z - 0.5) < 1e-9; load = (np.abs(x - 2.0) < 1e-9) & (np.abs(y) < 1e-9)
free_z0 = (np.abs(z) < 1e-9) & ~fix
out["n_fix_nodes"] = int(fix.sum()); out["n_sym_nodes"] = int(sym.sum()); out["n_load_nodes"] = int(load.sum())
out["max_abs_u_on_x0"] = float(np.max(np.abs(np.stack([ux[fix], uy[fix], uz[fix]]))))
out["max_abs_uz_on_z0.5 (ss_sym)"] = float(np.max(np.abs(uz[sym])))
out["max_abs_uz_on_z0 (free face, for contrast)"] = float(np.max(np.abs(uz[free_z0])))
out["max_abs_uz_overall"] = float(np.max(np.abs(uz)))
out["max_abs_ux_uy_on_z0.5 (should be nonzero: only uz fixed)"] = float(np.max(np.abs(np.stack([ux[sym], uy[sym]]))))
out["uy_on_load_edge_min_max"] = [float(uy[load].min()), float(uy[load].max())]
out["pass_fix"] = out["max_abs_u_on_x0"] < 1e-12
out["pass_sym_uz0"] = out["max_abs_uz_on_z0.5 (ss_sym)"] < 1e-12
out["pass_load_dir_negative_y"] = bool(uy[load].max() < 0)
out["all_pass"] = out["pass_fix"] and out["pass_sym_uz0"] and out["pass_load_dir_negative_y"]
print(json.dumps(out, indent=1))
