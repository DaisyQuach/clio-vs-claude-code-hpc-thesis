#!/usr/bin/env python3
"""Runtime evidence for the Helmholtz symmetry plane: at a given step, the filtered 'topology' field near the
real outer boundaries is pulled down by the sticking penalty (Robin condition), while nodes on the symmetry
plane z=0.5 (excluded from the surface integral) should look like interior nodes."""
import sys, json, numpy as np, netCDF4
f = sys.argv[1]; step = int(sys.argv[2]) if len(sys.argv) > 2 else 0
ds = netCDF4.Dataset(f)
nv = ["".join(c.decode() for c in row.compressed()).strip() for row in ds.variables["name_nod_var"][:]]
t = [float(v) for v in ds.variables["time_whole"][:]]
x = ds.variables["coordx"][:]; y = ds.variables["coordy"][:]; z = ds.variables["coordz"][:]
def nodal(name):
    i = [n.lower() for n in nv].index(name) + 1
    return np.array(ds.variables[f"vals_nod_var{i}"][step, :])
topo = nodal("topology"); ctrl = nodal("control")
tol = 1e-9
on_x0 = np.abs(x) < tol; on_x2 = np.abs(x-2) < tol; on_y0 = np.abs(y) < tol; on_y1 = np.abs(y-1) < tol
on_z0 = np.abs(z) < tol; on_z05 = np.abs(z-0.5) < tol
outer = on_x0 | on_x2 | on_y0 | on_y1 | on_z0
interior = ~(outer | on_z05)
sym_only = on_z05 & ~outer          # symmetry plane nodes not touching any real boundary
z0_only = on_z0 & ~(on_x0 | on_x2 | on_y0 | on_y1)  # z=0 face nodes not touching other faces
# compare like with like: z0_only vs sym_only (both are 'face-only' node sets); also deep interior (>=0.15 from any real boundary)
deep = (x > 0.15) & (x < 1.85) & (y > 0.15) & (y < 0.85) & (z > 0.15)
deep_int = deep & ~on_z05; deep_sym = deep & on_z05
out = {"file": f, "step_index": step, "time": t[step], "nodal_vars": nv,
       "control_min_max": [float(ctrl.min()), float(ctrl.max())],
       "topology_mean_deep_interior": float(topo[deep_int].mean()),
       "topology_mean_deep_symmetry_plane_nodes": float(topo[deep_sym].mean()),
       "topology_mean_z0_face_only_nodes": float(topo[z0_only].mean()),
       "topology_mean_x0_face_nodes": float(topo[on_x0].mean()),
       "topology_mean_sym_face_only_nodes": float(topo[sym_only].mean()),
       "n_deep_int": int(deep_int.sum()), "n_deep_sym": int(deep_sym.sum()), "n_z0_only": int(z0_only.sum()), "n_sym_only": int(sym_only.sum())}
# expectation: sym-plane nodes ~ interior; real boundary faces noticeably lower than interior
ratio_sym = out["topology_mean_deep_symmetry_plane_nodes"] / out["topology_mean_deep_interior"]
ratio_z0 = out["topology_mean_z0_face_only_nodes"] / out["topology_mean_deep_interior"]
out["ratio_sym_plane_to_interior"] = ratio_sym; out["ratio_z0_face_to_interior"] = ratio_z0
out["pass_symmetry_plane_not_penalized"] = bool(abs(ratio_sym - 1.0) < 0.02)
out["pass_real_boundary_penalized"] = bool(ratio_z0 < 0.9)
print(json.dumps(out, indent=1))
