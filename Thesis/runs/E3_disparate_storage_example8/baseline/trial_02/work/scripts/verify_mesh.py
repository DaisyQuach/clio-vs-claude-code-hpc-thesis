"""Verify an Exodus II mesh against the locked E3-SPC-v1 mesh specification (section 3)."""
import sys, json, datetime
import numpy as np
import netCDF4

path = sys.argv[1]
ds = netCDF4.Dataset(path, "r")
def names(var):
    out = []
    for row in ds.variables[var][:]:
        row = np.ma.filled(row, b"") if np.ma.isMaskedArray(row) else row
        out.append("".join(c.decode() if isinstance(c, bytes) else str(c) for c in row).strip("\x00").strip())
    return out
res = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "file": path, "checks": {}}
def check(name, ok, got, expected):
    res["checks"][name] = {"pass": bool(ok), "got": got, "expected": expected}

num_dim = ds.dimensions["num_dim"].size
num_nodes = ds.dimensions["num_nodes"].size
num_elem = ds.dimensions["num_elem"].size
num_blk = ds.dimensions["num_el_blk"].size
check("num_dim", num_dim == 3, num_dim, 3)
check("num_nodes", num_nodes == 15925, num_nodes, 15925)
check("num_elem", num_elem == 13824, num_elem, 13824)
check("num_el_blk", num_blk == 1, num_blk, 1)
x = ds.variables["coordx"][:]; y = ds.variables["coordy"][:]; z = ds.variables["coordz"][:]
bbox = [[float(x.min()), float(x.max())], [float(y.min()), float(y.max())], [float(z.min()), float(z.max())]]
exp_bbox = [[0.0, 2.0], [0.0, 1.0], [0.0, 0.5]]
check("bounding_box", np.allclose(np.array(bbox), np.array(exp_bbox), atol=1e-6), bbox, exp_bbox)
# unique coordinate counts -> structured 48 x 24 x 12
nx, ny, nz = [len(np.unique(np.round(c, 6))) for c in (x, y, z)]
check("grid_divisions", (nx, ny, nz) == (49, 25, 13), [nx, ny, nz], [49, 25, 13])
hx = float(np.diff(np.unique(np.round(x, 6))).mean()); hy = float(np.diff(np.unique(np.round(y, 6))).mean()); hz = float(np.diff(np.unique(np.round(z, 6))).mean())
check("element_size_h", all(abs(h - 1/24) < 1e-5 for h in (hx, hy, hz)), [hx, hy, hz], 1/24)
# block
blk_names = names("eb_names") if "eb_names" in ds.variables else []
check("block_name", blk_names == ["block_1"], blk_names, ["block_1"])
conn = ds.variables["connect1"]
elem_type = getattr(conn, "elem_type", "")
check("elem_type", elem_type.upper().startswith("HEX") and conn.shape[1] == 8, [elem_type, int(conn.shape[1])], ["HEX8", 8])
check("block1_num_elem", conn.shape[0] == 13824, int(conn.shape[0]), 13824)
# nodesets
ns_names = names("ns_names"); ns = {}
for i, n in enumerate(ns_names, start=1):
    ns[n] = ds.variables["node_ns%d" % i][:]
check("nodeset_names", sorted(ns_names) == ["ns_fix", "ns_load"], ns_names, ["ns_fix", "ns_load"])
fix = ns.get("ns_fix", np.array([], dtype=int)); load = ns.get("ns_load", np.array([], dtype=int))
check("ns_fix_size", len(fix) == 325, int(len(fix)), 325)
check("ns_fix_on_x0", len(fix) > 0 and np.allclose(x[fix - 1], 0.0, atol=1e-6), float(np.abs(x[fix - 1]).max()) if len(fix) else None, "x = 0")
check("ns_load_size", len(load) == 13, int(len(load)), 13)
check("ns_load_on_edge", len(load) > 0 and np.allclose(x[load - 1], 2.0, atol=1e-6) and np.allclose(y[load - 1], 0.0, atol=1e-6)
      and abs(z[load - 1].min()) < 1e-6 and abs(z[load - 1].max() - 0.5) < 1e-6,
      [float(x[load - 1].min()), float(x[load - 1].max()), float(y[load - 1].min()), float(y[load - 1].max()), float(z[load - 1].min()), float(z[load - 1].max())] if len(load) else None,
      "x = 2, y = 0, z spans [0, 0.5]")
# sidesets
ss_names = names("ss_names")
check("sideset_names", ss_names == ["ss_sym"], ss_names, ["ss_sym"])
if ss_names:
    el = ds.variables["elem_ss1"][:]; sd = ds.variables["side_ss1"][:]
    check("ss_sym_size", len(el) == 1152, int(len(el)), 1152)
    # Exodus HEX8 face node tables (sides 1..6)
    faces = {1: [0, 1, 5, 4], 2: [1, 2, 6, 5], 3: [2, 3, 7, 6], 4: [0, 4, 7, 3], 5: [0, 3, 2, 1], 6: [4, 5, 6, 7]}
    c = conn[:]
    zmax = []
    for e, s in zip(el, sd):
        nodes = c[e - 1][faces[int(s)]]
        zmax.append(float(np.abs(z[nodes - 1] - 0.5).max()))
    check("ss_sym_faces_on_z0.5", max(zmax) < 1e-6, max(zmax), "all face nodes at z = 0.5")
res["all_pass"] = all(v["pass"] for v in res["checks"].values())
print(json.dumps(res, indent=2))
sys.exit(0 if res["all_pass"] else 1)
