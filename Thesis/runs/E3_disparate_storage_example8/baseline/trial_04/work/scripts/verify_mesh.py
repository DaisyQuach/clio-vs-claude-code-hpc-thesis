#!/usr/bin/env python3
"""Mesh verification for E3-SPC-v1 (reads an Exodus II file with netCDF4; writes a JSON record)."""
import sys, json, datetime
import numpy as np
from netCDF4 import Dataset
path = sys.argv[1]; out = sys.argv[2]
ds = Dataset(path, "r")
def names(var):
    v = ds.variables[var][:]
    return ["".join(c.decode() if isinstance(c, bytes) else str(c) for c in row).strip("\x00 ") for row in np.asarray(v).astype("S1").astype(str)] if False else [b"".join(np.asarray(row).astype("S1")).decode().strip("\x00 ") for row in v]
x = ds.variables["coordx"][:]; y = ds.variables["coordy"][:]; z = ds.variables["coordz"][:]
nn = ds.dimensions["num_nodes"].size; ne = ds.dimensions["num_elem"].size
nblk = ds.dimensions["num_el_blk"].size
blk_names = names("eb_names") if "eb_names" in ds.variables else []
blocks = []
for i in range(1, nblk + 1):
    conn = ds.variables[f"connect{i}"]
    blocks.append({"id": int(ds.variables["eb_prop1"][i-1]), "name": blk_names[i-1] if blk_names else "", "elem_type": conn.elem_type, "num_elem": conn.shape[0], "nodes_per_elem": conn.shape[1]})
ns = []
nns = ds.dimensions["num_node_sets"].size if "num_node_sets" in ds.dimensions else 0
ns_names = names("ns_names") if "ns_names" in ds.variables else []
h = 1.0/24.0; tol = 1e-6
checks = {}
for i in range(1, nns + 1):
    nodes = ds.variables[f"node_ns{i}"][:] - 1
    name = ns_names[i-1] if ns_names else ""
    d = {"id": int(ds.variables["ns_prop1"][i-1]), "name": name, "num_nodes": int(len(nodes)),
         "x_range": [float(x[nodes].min()), float(x[nodes].max())], "y_range": [float(y[nodes].min()), float(y[nodes].max())], "z_range": [float(z[nodes].min()), float(z[nodes].max())]}
    ns.append(d)
    if name == "ns_fix":
        checks["ns_fix_all_on_x0"] = bool(np.all(np.abs(x[nodes]) < tol)); checks["ns_fix_count_equals_x0_nodes"] = bool(len(nodes) == int(np.sum(np.abs(x) < tol)))
    if name == "ns_load":
        checks["ns_load_all_on_edge_x2_y0"] = bool(np.all(np.abs(x[nodes]-2.0) < tol) and np.all(np.abs(y[nodes]) < tol)); checks["ns_load_count_equals_edge_nodes"] = bool(len(nodes) == int(np.sum((np.abs(x-2.0) < tol) & (np.abs(y) < tol))))
ss = []
nss = ds.dimensions["num_side_sets"].size if "num_side_sets" in ds.dimensions else 0
ss_names = names("ss_names") if "ss_names" in ds.variables else []
# HEX8 face-local node indices (Exodus convention, 1-based sides)
HEX_FACES = {1:[0,1,5,4],2:[1,2,6,5],3:[2,3,7,6],4:[0,4,7,3],5:[0,3,2,1],6:[4,5,6,7]}
conn1 = ds.variables["connect1"][:] - 1
for i in range(1, nss + 1):
    el = ds.variables[f"elem_ss{i}"][:] - 1; sd = ds.variables[f"side_ss{i}"][:]
    name = ss_names[i-1] if ss_names else ""
    allz = True
    for e, s in zip(el, sd):
        fn = conn1[e][HEX_FACES[int(s)]]
        if not np.all(np.abs(z[fn]-0.5) < tol): allz = False; break
    ss.append({"id": int(ds.variables["ss_prop1"][i-1]), "name": name, "num_faces": int(len(el)), "all_faces_on_z0.5": allz})
    if name == "ss_sym": checks["ss_sym_all_faces_on_cut_plane"] = allz
bbox = {"x": [float(x.min()), float(x.max())], "y": [float(y.min()), float(y.max())], "z": [float(z.min()), float(z.max())]}
ux, uy, uz = (len(np.unique(np.round(c, 8))) for c in (x, y, z))
rec = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "file": path, "num_dim": ds.dimensions["num_dim"].size,
       "num_nodes": nn, "num_elem": ne, "num_el_blk": nblk, "blocks": blocks, "nodesets": ns, "sidesets": ss, "bounding_box": bbox,
       "unique_coordinate_planes": {"x": ux, "y": uy, "z": uz}, "element_size_h": {"x": (bbox["x"][1]-bbox["x"][0])/(ux-1), "y": (bbox["y"][1]-bbox["y"][0])/(uy-1), "z": (bbox["z"][1]-bbox["z"][0])/(uz-1)}}
exp = {"num_dim": 3, "num_nodes": 15925, "num_elem": 13824, "num_el_blk": 1, "block_name": "block_1", "block_elem_type": "HEX8", "block_num_elem": 13824,
       "ns_fix": 325, "ns_load": 13, "ss_sym": 1152, "bbox": {"x": [0.0, 2.0], "y": [0.0, 1.0], "z": [0.0, 0.5]}, "planes": {"x": 49, "y": 25, "z": 13}}
checks.update({
  "num_dim": rec["num_dim"] == 3, "num_nodes": nn == 15925, "num_elem": ne == 13824, "single_block": nblk == 1,
  "block_name_block_1": blocks[0]["name"] == "block_1", "block_HEX8": blocks[0]["elem_type"].upper().startswith("HEX") and blocks[0]["nodes_per_elem"] == 8,
  "block_contains_all_elements": blocks[0]["num_elem"] == ne,
  "ns_fix_325": any(d["name"] == "ns_fix" and d["num_nodes"] == 325 for d in ns), "ns_load_13": any(d["name"] == "ns_load" and d["num_nodes"] == 13 for d in ns),
  "ss_sym_1152": any(d["name"] == "ss_sym" and d["num_faces"] == 1152 for d in ss),
  "bbox": all(abs(bbox[k][j]-exp["bbox"][k][j]) < tol for k in "xyz" for j in (0,1)),
  "structured_48x24x12": (ux, uy, uz) == (49, 25, 13), "uniform_h_1_over_24": all(abs(rec["element_size_h"][k]-h) < 1e-6 for k in "xyz"),
  "exactly_two_nodesets_one_sideset": (nns, nss) == (2, 1)})
rec["expected"] = exp; rec["checks"] = checks; rec["result"] = "PASS" if all(checks.values()) else "FAIL"
json.dump(rec, open(out, "w"), indent=2); print(json.dumps(rec, indent=2)); sys.exit(0 if rec["result"] == "PASS" else 1)
