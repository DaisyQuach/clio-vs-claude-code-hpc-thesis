"""Verify the Exodus mesh against the locked specification (FROZEN-EX16-v1, section 3)."""
import sys, json, hashlib, datetime
import numpy as np
from netCDF4 import Dataset

path = sys.argv[1]
out = sys.argv[2]
ds = Dataset(path, "r")
def names(var):
    arr = ds.variables[var][:]
    res = []
    for row in arr:
        if hasattr(row, "filled"):
            row = row.filled(b"")
        res.append(b"".join(x if isinstance(x, bytes) else x.encode() for x in row).decode().strip("\x00").strip())
    return res

x = np.array(ds.variables["coordx"][:]); y = np.array(ds.variables["coordy"][:]); z = np.array(ds.variables["coordz"][:])
n_nodes = len(x)
n_elem = int(ds.dimensions["num_elem"].size)
n_blk = int(ds.dimensions["num_el_blk"].size)
n_ns = int(ds.dimensions["num_node_sets"].size)
n_ss = int(ds.dimensions["num_side_sets"].size) if "num_side_sets" in ds.dimensions else 0
ndim = int(ds.dimensions["num_dim"].size)
blk_names = names("eb_names") if "eb_names" in ds.variables else []
ns_names = names("ns_names") if "ns_names" in ds.variables else []
blocks = []
for b in range(1, n_blk + 1):
    conn = ds.variables[f"connect{b}"]
    blocks.append({"id": int(ds.variables["eb_prop1"][b-1]), "name": blk_names[b-1] if blk_names else "",
                   "elem_type": conn.getncattr("elem_type"), "num_elem": int(conn.shape[0]), "nodes_per_elem": int(conn.shape[1])})
nodesets = {}
for s in range(1, n_ns + 1):
    ids = np.array(ds.variables[f"node_ns{s}"][:]) - 1
    nm = ns_names[s-1] if ns_names else f"ns{s}"
    nodesets[nm] = {"id": int(ds.variables["ns_prop1"][s-1]), "num_nodes": int(len(ids)),
                    "x_min": float(x[ids].min()), "x_max": float(x[ids].max()),
                    "y_min": float(y[ids].min()), "y_max": float(y[ids].max()),
                    "z_min": float(z[ids].min()), "z_max": float(z[ids].max())}
# element size check (block 1, HEX8): edge lengths of every element
conn = np.array(ds.variables["connect1"][:]) - 1
P = np.stack([x, y, z], axis=1)
edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
el = np.concatenate([np.linalg.norm(P[conn[:,a]] - P[conn[:,b]], axis=1) for a, b in edges])
tol = 1e-9
h = 1.0/24.0
checks_raw = {
  "num_elements == 27648": n_elem == 27648,
  "num_nodes == 30625": n_nodes == 30625,
  "num_dim == 3": ndim == 3,
  "one element block": n_blk == 1,
  "block name == block_1": (blocks[0]["name"] == "block_1"),
  "block elem_type is HEX8": blocks[0]["elem_type"].upper().startswith("HEX") and blocks[0]["nodes_per_elem"] == 8,
  "block_1 contains every element": blocks[0]["num_elem"] == n_elem,
  "bounding box x in [0,2]": abs(x.min()) < tol and abs(x.max() - 2.0) < tol,
  "bounding box y in [0,1]": abs(y.min()) < tol and abs(y.max() - 1.0) < tol,
  "bounding box z in [0,1]": abs(z.min()) < tol and abs(z.max() - 1.0) < tol,
  "uniform element edge length h = 1/24": bool(np.all(np.abs(el - h) < 1e-9)),
  "structured 48 x 24 x 24 grid (unique coords)": (len(np.unique(np.round(x, 9))) == 49 and len(np.unique(np.round(y, 9))) == 25 and len(np.unique(np.round(z, 9))) == 25),
  "nodeset ns_fix exists with 625 nodes": ("ns_fix" in nodesets and nodesets["ns_fix"]["num_nodes"] == 625),
  "ns_fix nodes all on x = 0": ("ns_fix" in nodesets and abs(nodesets["ns_fix"]["x_min"]) < tol and abs(nodesets["ns_fix"]["x_max"]) < tol),
  "ns_fix is the complete x=0 face": ("ns_fix" in nodesets and int(np.sum(np.abs(x) < tol)) == 625),
  "nodeset ns_load exists with 25 nodes": ("ns_load" in nodesets and nodesets["ns_load"]["num_nodes"] == 25),
  "ns_load nodes all on x = 2, y = 0, spanning z in [0,1]": ("ns_load" in nodesets and abs(nodesets["ns_load"]["x_min"]-2) < tol and abs(nodesets["ns_load"]["x_max"]-2) < tol and abs(nodesets["ns_load"]["y_min"]) < tol and abs(nodesets["ns_load"]["y_max"]) < tol and abs(nodesets["ns_load"]["z_min"]) < tol and abs(nodesets["ns_load"]["z_max"]-1) < tol),
  "ns_load is the complete x=2,y=0 edge": int(np.sum((np.abs(x-2) < tol) & (np.abs(y) < tol))) == 25,
  "no sidesets (none required)": n_ss == 0,
  "exactly two nodesets": n_ns == 2,
}
checks = {k: bool(v) for k, v in checks_raw.items()}
sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
record = {
  "frozen_configuration_id": "FROZEN-EX16-v1",
  "verified_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
  "mesh_file": path, "mesh_sha256": sha,
  "num_dim": ndim, "num_nodes": n_nodes, "num_elements": n_elem,
  "bounding_box": {"x": [float(x.min()), float(x.max())], "y": [float(y.min()), float(y.max())], "z": [float(z.min()), float(z.max())]},
  "element_edge_length": {"min": float(el.min()), "max": float(el.max()), "target": h},
  "blocks": blocks, "nodesets": nodesets, "num_sidesets": n_ss,
  "checks": checks, "all_checks_pass": all(checks.values()),
}
json.dump(record, open(out, "w"), indent=2)
print(json.dumps(record, indent=2))
sys.exit(0 if record["all_checks_pass"] else 1)
