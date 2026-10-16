#!/usr/bin/env python3
"""Mesh verification for FROZEN-EX8-v1 (half cantilever). Reads an Exodus II file with netCDF4."""
import sys, json, datetime
import numpy as np
import netCDF4

path = sys.argv[1]
ds = netCDF4.Dataset(path, "r")
def names(var):
    arr = ds.variables[var][:]
    out = []
    for row in arr:
        out.append("".join(c.decode() if isinstance(c, bytes) else str(c) for c in row.compressed() if c != b'').strip())
    return out

exp = {"num_elem": 13824, "num_nodes": 15925, "num_el_blk": 1, "num_node_sets": 2, "num_side_sets": 1,
       "block_name": "block_1", "elem_type": "HEX8", "ns_fix": 325, "ns_load": 13, "ss_sym": 1152,
       "bbox": [[0.0, 2.0], [0.0, 1.0], [0.0, 0.5]], "h": 1.0/24.0}
res = {"file": path, "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "checks": []}
def check(name, got, want, ok=None):
    if ok is None: ok = (got == want)
    res["checks"].append({"check": name, "got": got, "expected": want, "pass": bool(ok)})

dims = {k: len(v) for k, v in ds.dimensions.items()}
check("num_dim", dims["num_dim"], 3)
check("num_elem", dims["num_elem"], exp["num_elem"])
check("num_nodes", dims["num_nodes"], exp["num_nodes"])
check("num_el_blk", dims["num_el_blk"], exp["num_el_blk"])
check("num_node_sets", dims["num_node_sets"], exp["num_node_sets"])
check("num_side_sets", dims["num_side_sets"], exp["num_side_sets"])

x = ds.variables["coordx"][:] if "coordx" in ds.variables else ds.variables["coord"][0,:]
y = ds.variables["coordy"][:] if "coordy" in ds.variables else ds.variables["coord"][1,:]
z = ds.variables["coordz"][:] if "coordz" in ds.variables else ds.variables["coord"][2,:]
bbox = [[float(x.min()), float(x.max())], [float(y.min()), float(y.max())], [float(z.min()), float(z.max())]]
check("bounding_box", bbox, exp["bbox"], np.allclose(np.array(bbox), np.array(exp["bbox"]), atol=1e-9))

# block
blk_names = names("eb_names") if "eb_names" in ds.variables else []
check("block_names", blk_names, [exp["block_name"]])
conn = ds.variables["connect1"]
check("elem_type_block1", conn.elem_type.upper(), exp["elem_type"])
check("num_el_in_blk1", dims["num_el_in_blk1"], exp["num_elem"])
check("num_nod_per_el1", dims["num_nod_per_el1"], 8)
check("block_ids", [int(v) for v in ds.variables["eb_prop1"][:]], [1])

# uniform element size: check unique coordinate levels
ux, uy, uz = np.unique(np.round(x, 9)), np.unique(np.round(y, 9)), np.unique(np.round(z, 9))
check("unique_x_levels(49)", int(len(ux)), 49)
check("unique_y_levels(25)", int(len(uy)), 25)
check("unique_z_levels(13)", int(len(uz)), 13)
hx, hy, hz = np.diff(ux), np.diff(uy), np.diff(uz)
check("uniform_h_x", [float(hx.min()), float(hx.max())], exp["h"], np.allclose(hx, exp["h"], atol=1e-9))
check("uniform_h_y", [float(hy.min()), float(hy.max())], exp["h"], np.allclose(hy, exp["h"], atol=1e-9))
check("uniform_h_z", [float(hz.min()), float(hz.max())], exp["h"], np.allclose(hz, exp["h"], atol=1e-9))
# structured check: every element is an axis-aligned hex with edge h
c = conn[:] - 1
ex = x[c]; ey = y[c]; ez = z[c]
check("elem_extent_x", [float((ex.max(1)-ex.min(1)).min()), float((ex.max(1)-ex.min(1)).max())], exp["h"], np.allclose(ex.max(1)-ex.min(1), exp["h"], atol=1e-9))
check("elem_extent_y", [float((ey.max(1)-ey.min(1)).min()), float((ey.max(1)-ey.min(1)).max())], exp["h"], np.allclose(ey.max(1)-ey.min(1), exp["h"], atol=1e-9))
check("elem_extent_z", [float((ez.max(1)-ez.min(1)).min()), float((ez.max(1)-ez.min(1)).max())], exp["h"], np.allclose(ez.max(1)-ez.min(1), exp["h"], atol=1e-9))

# nodesets
ns_names = names("ns_names"); ns_ids = [int(v) for v in ds.variables["ns_prop1"][:]]
check("nodeset_names", ns_names, ["ns_fix", "ns_load"])
check("nodeset_ids", ns_ids, [1, 2])
for i, nm in enumerate(ns_names, start=1):
    nodes = ds.variables[f"node_ns{i}"][:] - 1
    check(f"{nm}_size", int(len(nodes)), exp[nm])
    if nm == "ns_fix":
        check("ns_fix_all_on_x=0", float(np.abs(x[nodes]).max()), 0.0, np.allclose(x[nodes], 0.0, atol=1e-9))
        allx0 = np.where(np.abs(x) < 1e-9)[0]
        check("ns_fix_contains_every_x=0_node", int(len(allx0)), int(len(nodes)), set(allx0.tolist()) == set(nodes.tolist()))
    if nm == "ns_load":
        check("ns_load_all_on_x=2_y=0", [float(np.abs(x[nodes]-2.0).max()), float(np.abs(y[nodes]).max())], 0.0,
              np.allclose(x[nodes], 2.0, atol=1e-9) and np.allclose(y[nodes], 0.0, atol=1e-9))
        alle = np.where((np.abs(x-2.0) < 1e-9) & (np.abs(y) < 1e-9))[0]
        check("ns_load_contains_every_edge_node", int(len(alle)), int(len(nodes)), set(alle.tolist()) == set(nodes.tolist()))
        check("ns_load_z_range", [float(z[nodes].min()), float(z[nodes].max())], [0.0, 0.5], np.isclose(z[nodes].min(), 0.0) and np.isclose(z[nodes].max(), 0.5))

# sidesets
ss_names = names("ss_names"); ss_ids = [int(v) for v in ds.variables["ss_prop1"][:]]
check("sideset_names", ss_names, ["ss_sym"])
check("sideset_ids", ss_ids, [1])
elems = ds.variables["elem_ss1"][:] - 1; sides = ds.variables["side_ss1"][:]
check("ss_sym_size", int(len(elems)), exp["ss_sym"])
# exodus hex8 side -> local node indices (1-based sides)
hex_sides = {1:[0,1,5,4], 2:[1,2,6,5], 3:[2,3,7,6], 4:[0,4,7,3], 5:[0,3,2,1], 6:[4,5,6,7]}
zs = np.array([z[c[e][hex_sides[int(s)]]] for e, s in zip(elems, sides)])
check("ss_sym_all_faces_on_z=0.5", [float(zs.min()), float(zs.max())], 0.5, np.allclose(zs, 0.5, atol=1e-9))
check("ss_sym_unique_elements", int(len(np.unique(elems))), exp["ss_sym"])
check("num_side_ss1_dim", dims["num_side_ss1"], exp["ss_sym"])

res["all_pass"] = all(ch["pass"] for ch in res["checks"])
print(json.dumps(res, indent=1))
sys.exit(0 if res["all_pass"] else 1)
