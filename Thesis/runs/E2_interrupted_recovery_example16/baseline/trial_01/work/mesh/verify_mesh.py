#!/usr/bin/env python3
"""Verify the FROZEN-EX16-v1 mesh against the locked specification (section 3)."""
import sys, json, hashlib
import numpy as np
import netCDF4

path = sys.argv[1]
ds = netCDF4.Dataset(path, "r")
def names(var):
    arr = ds.variables[var][:]
    out = []
    for row in arr:
        s = b"".join(x for x in row.tobytes().split(b"\x00")[:1]).decode()
        out.append(s)
    return out

x = ds.variables["coordx"][:]; y = ds.variables["coordy"][:]; z = ds.variables["coordz"][:]
nn = ds.dimensions["num_nodes"].size
ne = ds.dimensions["num_elem"].size
nblk = ds.dimensions["num_el_blk"].size
nns = ds.dimensions["num_node_sets"].size
nss = ds.dimensions["num_side_sets"].size if "num_side_sets" in ds.dimensions else 0
ndim = ds.dimensions["num_dim"].size
blk_names = names("eb_names") if "eb_names" in ds.variables else []
ns_names = names("ns_names") if "ns_names" in ds.variables else []
blk_ids = ds.variables["eb_prop1"][:].tolist()
ns_ids = ds.variables["ns_prop1"][:].tolist()
rec = {"file": path, "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest()}
rec["num_dim"] = ndim
rec["num_nodes"] = int(nn); rec["num_elem"] = int(ne)
rec["bounding_box"] = {"x": [float(x.min()), float(x.max())], "y": [float(y.min()), float(y.max())], "z": [float(z.min()), float(z.max())]}
rec["num_el_blk"] = int(nblk); rec["num_node_sets"] = int(nns); rec["num_side_sets"] = int(nss)
blocks = []
for i, bid in enumerate(blk_ids, 1):
    conn = ds.variables[f"connect{i}"]
    blocks.append({"id": int(bid), "name": blk_names[i-1] if blk_names else None,
                   "elem_type": getattr(conn, "elem_type", None),
                   "num_elem": conn.shape[0], "nodes_per_elem": conn.shape[1]})
rec["blocks"] = blocks
nsets = []
for i, nid in enumerate(ns_ids, 1):
    nodes = ds.variables[f"node_ns{i}"][:] - 1
    nsets.append({"id": int(nid), "name": ns_names[i-1] if ns_names else None, "num_nodes": int(len(nodes)),
                  "x_range": [float(x[nodes].min()), float(x[nodes].max())],
                  "y_range": [float(y[nodes].min()), float(y[nodes].max())],
                  "z_range": [float(z[nodes].min()), float(z[nodes].max())]})
rec["nodesets"] = nsets
# uniform element size check: unique coordinate values
ux, uy, uz = np.unique(np.round(x, 9)), np.unique(np.round(y, 9)), np.unique(np.round(z, 9))
rec["unique_coords"] = {"x": len(ux), "y": len(uy), "z": len(uz)}
rec["spacing"] = {"x": [float(np.diff(ux).min()), float(np.diff(ux).max())],
                  "y": [float(np.diff(uy).min()), float(np.diff(uy).max())],
                  "z": [float(np.diff(uz).min()), float(np.diff(uz).max())]}
# element volume check for the single HEX8 block (structured, axis-aligned)
conn = ds.variables["connect1"][:] - 1
ex = x[conn]; ey = y[conn]; ez = z[conn]
evol = (ex.max(1)-ex.min(1))*(ey.max(1)-ey.min(1))*(ez.max(1)-ez.min(1))
rec["elem_volume"] = {"min": float(evol.min()), "max": float(evol.max()), "total": float(evol.sum())}
# independent node-based set checks
tol = 1e-9
rec["nodes_on_x0_face"] = int(np.sum(np.abs(x) < tol))
rec["nodes_on_x2_y0_edge"] = int(np.sum((np.abs(x-2.0) < tol) & (np.abs(y) < tol)))
ns_fix = [n for n in nsets if n["name"] == "ns_fix"]
ns_load = [n for n in nsets if n["name"] == "ns_load"]
checks = {
 "num_dim == 3": ndim == 3,
 "num_elem == 27648": ne == 27648,
 "num_nodes == 30625": nn == 30625,
 "bbox == [0,2]x[0,1]x[0,1]": all(abs(a-b) < 1e-9 for a, b in zip([x.min(), x.max(), y.min(), y.max(), z.min(), z.max()], [0, 2, 0, 1, 0, 1])),
 "exactly one block named block_1 with all elements, HEX8": nblk == 1 and blocks[0]["name"] == "block_1" and blocks[0]["num_elem"] == 27648 and blocks[0]["nodes_per_elem"] == 8 and str(blocks[0]["elem_type"]).upper().startswith("HEX"),
 "structured 48x24x24 (49x25x25 unique coords)": (len(ux), len(uy), len(uz)) == (49, 25, 25),
 "uniform h = 1/24": all(abs(v - 1/24) < 1e-7 for v in rec["spacing"]["x"] + rec["spacing"]["y"] + rec["spacing"]["z"]),
 "ns_fix exists with 625 nodes, all at x = 0": bool(ns_fix) and ns_fix[0]["num_nodes"] == 625 and abs(ns_fix[0]["x_range"][1]) < tol and rec["nodes_on_x0_face"] == 625,
 "ns_load exists with 25 nodes, all at x = 2, y = 0, z in [0,1]": bool(ns_load) and ns_load[0]["num_nodes"] == 25 and abs(ns_load[0]["x_range"][0]-2) < tol and abs(ns_load[0]["x_range"][1]-2) < tol and abs(ns_load[0]["y_range"][1]) < tol and abs(ns_load[0]["z_range"][0]) < tol and abs(ns_load[0]["z_range"][1]-1) < tol and rec["nodes_on_x2_y0_edge"] == 25,
 "no sidesets required (count)": True,
}
rec["checks"] = checks
rec["ALL_CHECKS_PASS"] = all(checks.values())
print(json.dumps(rec, indent=2))
sys.exit(0 if rec["ALL_CHECKS_PASS"] else 1)
