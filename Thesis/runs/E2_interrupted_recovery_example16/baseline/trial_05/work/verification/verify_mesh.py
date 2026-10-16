"""Mesh verification against FROZEN-EX16-v1 Section 3 (locked mesh)."""
import sys, json, hashlib, datetime
import numpy as np
import netCDF4

path = sys.argv[1]
ds = netCDF4.Dataset(path, "r")
def names(var):
    arr = ds.variables[var][:]
    out = []
    for row in arr:
        out.append(b"".join([c for c in row.tobytes().split(b"\x00")[0:1]]).decode().strip())
    return out
res = {}
res["file"] = path
res["sha256"] = hashlib.sha256(open(path, "rb").read()).hexdigest()
res["utc"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
res["num_dim"] = int(ds.dimensions["num_dim"].size)
res["num_nodes"] = int(ds.dimensions["num_nodes"].size)
res["num_elem"] = int(ds.dimensions["num_elem"].size)
res["num_el_blk"] = int(ds.dimensions["num_el_blk"].size)
res["num_node_sets"] = int(ds.dimensions["num_node_sets"].size) if "num_node_sets" in ds.dimensions else 0
res["num_side_sets"] = int(ds.dimensions["num_side_sets"].size) if "num_side_sets" in ds.dimensions else 0
x = ds.variables["coordx"][:]; y = ds.variables["coordy"][:]; z = ds.variables["coordz"][:]
res["bbox"] = {"x": [float(x.min()), float(x.max())], "y": [float(y.min()), float(y.max())], "z": [float(z.min()), float(z.max())]}
res["unique_x"] = int(len(np.unique(np.round(x, 9)))); res["unique_y"] = int(len(np.unique(np.round(y, 9)))); res["unique_z"] = int(len(np.unique(np.round(z, 9))))
res["h_x"] = float(np.diff(np.unique(np.round(x, 9))).mean()); res["h_y"] = float(np.diff(np.unique(np.round(y, 9))).mean()); res["h_z"] = float(np.diff(np.unique(np.round(z, 9))).mean())
res["h_x_minmax"] = [float(np.diff(np.unique(np.round(x, 9))).min()), float(np.diff(np.unique(np.round(x, 9))).max())]
# blocks
blk_names = names("eb_names") if "eb_names" in ds.variables else []
res["blocks"] = []
for i in range(res["num_el_blk"]):
    conn = ds.variables["connect%d" % (i + 1)]
    res["blocks"].append({"id": int(ds.variables["eb_prop1"][i]), "name": blk_names[i] if blk_names else None,
                          "elem_type": getattr(conn, "elem_type", None), "num_elem": int(conn.shape[0]), "nodes_per_elem": int(conn.shape[1])})
# nodesets
ns_names = names("ns_names") if "ns_names" in ds.variables else []
res["nodesets"] = []
for i in range(res["num_node_sets"]):
    nodes = ds.variables["node_ns%d" % (i + 1)][:] - 1
    d = {"id": int(ds.variables["ns_prop1"][i]), "name": ns_names[i] if ns_names else None, "num_nodes": int(len(nodes)),
         "x_range": [float(x[nodes].min()), float(x[nodes].max())], "y_range": [float(y[nodes].min()), float(y[nodes].max())],
         "z_range": [float(z[nodes].min()), float(z[nodes].max())]}
    res["nodesets"].append(d)
# independent recount from coordinates
tol = 1e-9
res["count_nodes_x0"] = int(np.sum(np.abs(x - 0.0) < tol))
res["count_nodes_x2_y0"] = int(np.sum((np.abs(x - 2.0) < tol) & (np.abs(y - 0.0) < tol)))
# element volume check (all HEX8 equal volume h^3)
conn = ds.variables["connect1"][:] - 1
pts = np.stack([x[conn], y[conn], z[conn]], axis=-1)
ext = pts.max(axis=1) - pts.min(axis=1)
res["elem_extent_min"] = [float(v) for v in ext.min(axis=0)]; res["elem_extent_max"] = [float(v) for v in ext.max(axis=0)]
res["total_volume_from_extents"] = float(np.prod(ext, axis=1).sum())
# checks
chk = {}
chk["num_elem==27648"] = res["num_elem"] == 27648
chk["num_nodes==30625"] = res["num_nodes"] == 30625
chk["num_dim==3"] = res["num_dim"] == 3
chk["one block named block_1 with all elements, HEX8"] = (res["num_el_blk"] == 1 and res["blocks"][0]["name"] == "block_1" and res["blocks"][0]["num_elem"] == 27648 and res["blocks"][0]["nodes_per_elem"] == 8 and str(res["blocks"][0]["elem_type"]).upper().startswith("HEX"))
chk["bbox == [0,2]x[0,1]x[0,1]"] = all(abs(a - b) < 1e-9 for a, b in zip(res["bbox"]["x"] + res["bbox"]["y"] + res["bbox"]["z"], [0, 2, 0, 1, 0, 1]))
chk["grid 49x25x25 nodes, uniform h=1/24"] = (res["unique_x"] == 49 and res["unique_y"] == 25 and res["unique_z"] == 25 and abs(res["h_x"] - 1/24) < 1e-9 and abs(res["h_y"] - 1/24) < 1e-9 and abs(res["h_z"] - 1/24) < 1e-9 and abs(res["h_x_minmax"][0] - 1/24) < 1e-9 and abs(res["h_x_minmax"][1] - 1/24) < 1e-9)
nsd = {n["name"]: n for n in res["nodesets"]}
chk["ns_fix: 625 nodes, all at x=0"] = ("ns_fix" in nsd and nsd["ns_fix"]["num_nodes"] == 625 and abs(nsd["ns_fix"]["x_range"][0]) < 1e-9 and abs(nsd["ns_fix"]["x_range"][1]) < 1e-9 and nsd["ns_fix"]["num_nodes"] == res["count_nodes_x0"])
chk["ns_load: 25 nodes, all at x=2,y=0, z spans [0,1]"] = ("ns_load" in nsd and nsd["ns_load"]["num_nodes"] == 25 and abs(nsd["ns_load"]["x_range"][0] - 2) < 1e-9 and abs(nsd["ns_load"]["x_range"][1] - 2) < 1e-9 and abs(nsd["ns_load"]["y_range"][0]) < 1e-9 and abs(nsd["ns_load"]["y_range"][1]) < 1e-9 and abs(nsd["ns_load"]["z_range"][0]) < 1e-9 and abs(nsd["ns_load"]["z_range"][1] - 1) < 1e-9 and nsd["ns_load"]["num_nodes"] == res["count_nodes_x2_y0"])
chk["no sidesets"] = res["num_side_sets"] == 0
chk["elements uniform cubes of edge 1/24"] = all(abs(v - 1/24) < 1e-9 for v in res["elem_extent_min"] + res["elem_extent_max"]) and abs(res["total_volume_from_extents"] - 2.0) < 1e-9
res["checks"] = chk
res["ALL_CHECKS_PASS"] = all(chk.values())
print(json.dumps(res, indent=2))
sys.exit(0 if res["ALL_CHECKS_PASS"] else 1)
