#!/usr/bin/env python3
"""E3-SPC-v1 mesh verification: counts, bounding box, block name, nodeset/sideset sizes (Exodus II via netCDF4)."""
import sys, json, datetime
import numpy as np
import netCDF4
path = sys.argv[1]
ds = netCDF4.Dataset(path, "r")
def names(var):
    if var not in ds.variables: return []
    v = ds.variables[var]; v.set_auto_mask(False)
    return [bytes(row).decode("ascii", "ignore").strip("\x00 ") for row in v[:]]
num_nodes = ds.dimensions["num_nodes"].size
num_elem = ds.dimensions["num_elem"].size
num_blk = ds.dimensions["num_el_blk"].size
x = ds.variables["coordx"][:]; y = ds.variables["coordy"][:]; z = ds.variables["coordz"][:]
blk_names = names("eb_names"); ns_names = names("ns_names"); ss_names = names("ss_names")
blk_sizes = [ds.dimensions[f"num_el_in_blk{i+1}"].size for i in range(num_blk)]
blk_types = [ds.variables[f"connect{i+1}"].elem_type for i in range(num_blk)]
ns = {}
for i, n in enumerate(ns_names):
    idx = ds.variables[f"node_ns{i+1}"][:] - 1
    ns[n] = dict(count=int(len(idx)), x=[float(x[idx].min()), float(x[idx].max())], y=[float(y[idx].min()), float(y[idx].max())], z=[float(z[idx].min()), float(z[idx].max())])
ss = {}
conn = ds.variables["connect1"][:] - 1
for i, n in enumerate(ss_names):
    el = ds.variables[f"elem_ss{i+1}"][:] - 1; sd = ds.variables[f"side_ss{i+1}"][:]
    zf = []
    for e, s in zip(el, sd):
        # HEX8 face node ordering (Exodus): sides 1..6
        faces = {1:[0,1,5,4],2:[1,2,6,5],3:[2,3,7,6],4:[0,4,7,3],5:[0,3,2,1],6:[4,5,6,7]}
        zf.append([float(z[conn[e][k]]) for k in faces[int(s)]])
    zf = np.array(zf)
    ss[n] = dict(count=int(len(el)), sides_used=sorted(set(int(v) for v in sd)), face_z_min=float(zf.min()) if len(zf) else None, face_z_max=float(zf.max()) if len(zf) else None)
h = 1.0/24.0
expected = dict(num_elem=13824, num_nodes=15925, blocks=["block_1"], elem_type="HEX8",
                bbox=dict(x=[0.0,2.0], y=[0.0,1.0], z=[0.0,0.5]), ns_fix=325, ns_load=13, ss_sym=1152)
rec = dict(utc=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), file=path, spec="E3-SPC-v1 section 3",
           num_nodes=num_nodes, num_elem=num_elem, num_blocks=num_blk, block_names=blk_names, block_sizes=blk_sizes, block_elem_types=blk_types,
           bbox=dict(x=[float(x.min()), float(x.max())], y=[float(y.min()), float(y.max())], z=[float(z.min()), float(z.max())]),
           nodesets=ns, sidesets=ss, expected=expected)
tol = 1e-6
checks = {
 "num_elem == 13824": num_elem == 13824,
 "num_nodes == 15925": num_nodes == 15925,
 "exactly one block named block_1": blk_names == ["block_1"],
 "block_1 contains every element": blk_sizes == [num_elem],
 "element type HEX8": all(t.upper().startswith("HEX") for t in blk_types),
 "bounding box [0,2]x[0,1]x[0,0.5]": all(abs(rec["bbox"][k][i]-expected["bbox"][k][i]) < tol for k in "xyz" for i in (0,1)),
 "ns_fix has 325 nodes": ns.get("ns_fix",{}).get("count") == 325,
 "ns_fix all on x=0": "ns_fix" in ns and abs(ns["ns_fix"]["x"][1]) < tol,
 "ns_load has 13 nodes": ns.get("ns_load",{}).get("count") == 13,
 "ns_load on x=2,y=0 spanning z in [0,0.5]": "ns_load" in ns and abs(ns["ns_load"]["x"][0]-2)<tol and abs(ns["ns_load"]["y"][1])<tol and abs(ns["ns_load"]["z"][0])<tol and abs(ns["ns_load"]["z"][1]-0.5)<tol,
 "ss_sym has 1152 faces": ss.get("ss_sym",{}).get("count") == 1152,
 "ss_sym faces all on z=0.5": "ss_sym" in ss and ss["ss_sym"]["face_z_min"] is not None and abs(ss["ss_sym"]["face_z_min"]-0.5)<tol and abs(ss["ss_sym"]["face_z_max"]-0.5)<tol,
 "uniform element size h=1/24 (unique x coords = 49)": len(np.unique(np.round(x,6))) == 49 and len(np.unique(np.round(y,6))) == 25 and len(np.unique(np.round(z,6))) == 13,
}
rec["checks"] = checks; rec["result"] = "PASS" if all(checks.values()) else "FAIL"
print(json.dumps(rec, indent=2))
sys.exit(0 if rec["result"] == "PASS" else 1)
