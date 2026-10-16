"""Mesh verification for FROZEN-EX8-v1 (run with the approved runtime python3 -I)."""
import sys, json, datetime
import numpy as np
import netCDF4 as nc

path = sys.argv[1]
d = nc.Dataset(path)
def names(var):
    arr = d.variables[var][:]
    out = []
    for row in arr:
        s = b"".join([bytes([c]) if isinstance(c, int) else (c if isinstance(c, bytes) else str(c).encode()) for c in row.filled(b"") if c not in (b"", 0, "")]).decode(errors="ignore")
        out.append(s.strip("\x00"))
    return out

num_nodes = d.dimensions["num_nodes"].size
num_elem = d.dimensions["num_elem"].size
num_dim = d.dimensions["num_dim"].size
num_el_blk = d.dimensions["num_el_blk"].size
num_ns = d.dimensions["num_node_sets"].size if "num_node_sets" in d.dimensions else 0
num_ss = d.dimensions["num_side_sets"].size if "num_side_sets" in d.dimensions else 0

x = np.array(d.variables["coordx"][:]); y = np.array(d.variables["coordy"][:]); z = np.array(d.variables["coordz"][:])
bbox = {"xmin": float(x.min()), "xmax": float(x.max()), "ymin": float(y.min()), "ymax": float(y.max()), "zmin": float(z.min()), "zmax": float(z.max())}

blk_names = names("eb_names") if "eb_names" in d.variables else []
ns_names = names("ns_names") if "ns_names" in d.variables else []
ss_names = names("ss_names") if "ss_names" in d.variables else []
blocks = []
for b in range(1, num_el_blk + 1):
    conn = d.variables[f"connect{b}"]
    blocks.append({"id": int(d.variables["eb_prop1"][b-1]), "name": blk_names[b-1] if blk_names else "", "elem_type": conn.getncattr("elem_type"), "num_elem": conn.shape[0], "nodes_per_elem": conn.shape[1]})
nodesets = []
for s in range(1, num_ns + 1):
    nn = np.array(d.variables[f"node_ns{s}"][:]) - 1
    nodesets.append({"id": int(d.variables["ns_prop1"][s-1]), "name": ns_names[s-1] if ns_names else "", "num_nodes": int(nn.size),
                     "x_range": [float(x[nn].min()), float(x[nn].max())], "y_range": [float(y[nn].min()), float(y[nn].max())], "z_range": [float(z[nn].min()), float(z[nn].max())]})
sidesets = []
conn1 = np.array(d.variables["connect1"][:]) - 1
for s in range(1, num_ss + 1):
    el = np.array(d.variables[f"elem_ss{s}"][:]) - 1
    sd = np.array(d.variables[f"side_ss{s}"][:])
    # HEX8 Exodus side->local node map
    face_nodes = {1:[0,1,5,4],2:[1,2,6,5],3:[2,3,7,6],4:[0,4,7,3],5:[0,3,2,1],6:[4,5,6,7]}
    zf = []
    for e, sdi in zip(el, sd):
        nodes = conn1[e][face_nodes[int(sdi)]]
        zf.extend(z[nodes].tolist())
    sidesets.append({"id": int(d.variables["ss_prop1"][s-1]), "name": ss_names[s-1] if ss_names else "", "num_faces": int(el.size),
                     "face_node_z_range": [float(min(zf)), float(max(zf))]})

# element size uniformity check (edge lengths along x for element 0)
h = 1.0/24.0
ux = np.unique(np.round(x, 9)); uy = np.unique(np.round(y, 9)); uz = np.unique(np.round(z, 9))
rec = {
  "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
  "mesh_file": path, "num_dim": num_dim, "num_nodes": num_nodes, "num_elem": num_elem,
  "bounding_box": bbox, "blocks": blocks, "nodesets": nodesets, "sidesets": sidesets,
  "unique_coords": {"nx": int(ux.size), "ny": int(uy.size), "nz": int(uz.size)},
  "spacing": {"dx_max_dev": float(np.abs(np.diff(ux) - h).max()), "dy_max_dev": float(np.abs(np.diff(uy) - h).max()), "dz_max_dev": float(np.abs(np.diff(uz) - h).max())},
}
checks = {
  "num_elem == 13824": num_elem == 13824,
  "num_nodes == 15925": num_nodes == 15925,
  "num_dim == 3": num_dim == 3,
  "bbox == [0,2]x[0,1]x[0,0.5]": all(abs(bbox[k]-v) < 1e-9 for k, v in dict(xmin=0, xmax=2, ymin=0, ymax=1, zmin=0, zmax=0.5).items()),
  "one block named block_1 with all elements, HEX8": len(blocks) == 1 and blocks[0]["name"] == "block_1" and blocks[0]["num_elem"] == 13824 and blocks[0]["elem_type"].upper().startswith("HEX") and blocks[0]["nodes_per_elem"] == 8,
  "uniform h=1/24 grid 49x25x13 nodes": (ux.size, uy.size, uz.size) == (49, 25, 13) and rec["spacing"]["dx_max_dev"] < 1e-9 and rec["spacing"]["dy_max_dev"] < 1e-9 and rec["spacing"]["dz_max_dev"] < 1e-9,
  "ns_fix: 325 nodes all at x=0": any(n["name"] == "ns_fix" and n["num_nodes"] == 325 and abs(n["x_range"][1]) < 1e-9 for n in nodesets),
  "ns_load: 13 nodes at x=2,y=0 spanning z in [0,0.5]": any(n["name"] == "ns_load" and n["num_nodes"] == 13 and abs(n["x_range"][0]-2) < 1e-9 and abs(n["y_range"][1]) < 1e-9 and abs(n["z_range"][0]) < 1e-9 and abs(n["z_range"][1]-0.5) < 1e-9 for n in nodesets),
  "ss_sym: 1152 faces all on z=0.5": any(s["name"] == "ss_sym" and s["num_faces"] == 1152 and abs(s["face_node_z_range"][0]-0.5) < 1e-9 and abs(s["face_node_z_range"][1]-0.5) < 1e-9 for s in sidesets),
}
rec["checks"] = checks
rec["ALL_CHECKS_PASS"] = all(checks.values())
print(json.dumps(rec, indent=2))
