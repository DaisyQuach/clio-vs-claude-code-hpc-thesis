#!/usr/bin/env python3
"""Verify the FROZEN-EX8-v1 mesh against every locked mesh setting (read-only)."""
import sys, json, datetime
import numpy as np
import netCDF4

path = sys.argv[1]
ds = netCDF4.Dataset(path, "r")
tol = 1e-9
rec = {"file": path, "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
checks = []
def chk(name, ok, got, want):
    checks.append({"check": name, "pass": bool(ok), "got": got, "expected": want})

def names(var):
    if var not in ds.variables: return []
    out = []
    for row in ds.variables[var][:]:
        s = b"".join(c for c in row.tolist() if c and c != b"\x00").decode() if hasattr(row,"tolist") else str(row)
        out.append(s.strip())
    return out

ndim = ds.dimensions["num_dim"].size
nn = ds.dimensions["num_nodes"].size
ne = ds.dimensions["num_elem"].size
nblk = ds.dimensions["num_el_blk"].size
chk("num_dim", ndim == 3, ndim, 3)
chk("num_nodes", nn == 15925, nn, 15925)
chk("num_elem", ne == 13824, ne, 13824)
chk("num_el_blk", nblk == 1, nblk, 1)

x = ds.variables["coordx"][:]; y = ds.variables["coordy"][:]; z = ds.variables["coordz"][:]
bbox = [float(x.min()), float(x.max()), float(y.min()), float(y.max()), float(z.min()), float(z.max())]
want_bbox = [0.0, 2.0, 0.0, 1.0, 0.0, 0.5]
chk("bounding_box", all(abs(a-b) < 1e-9 for a, b in zip(bbox, want_bbox)), bbox, want_bbox)
# uniform spacing h = 1/24 on each axis
h = 1.0/24.0
for lbl, c, n in (("x", x, 49), ("y", y, 25), ("z", z, 13)):
    u = np.unique(np.round(c, 9))
    chk(f"unique_{lbl}_coords", len(u) == n and np.allclose(np.diff(u), h, atol=1e-9), [int(len(u)), float(np.diff(u).min()), float(np.diff(u).max())], [n, h, h])

# block
blk_names = names("eb_names")
chk("block_names", blk_names == ["block_1"], blk_names, ["block_1"])
conn = ds.variables["connect1"]
elem_type = getattr(conn, "elem_type", "")
chk("block1_elem_type", elem_type.upper().startswith("HEX") and conn.shape[1] == 8, [elem_type, int(conn.shape[1])], ["HEX8", 8])
chk("block1_num_elem", conn.shape[0] == 13824, int(conn.shape[0]), 13824)
# element edge lengths (uniform cubes h)
c = conn[:] - 1
p0 = np.c_[x[c[:,0]], y[c[:,0]], z[c[:,0]]]; p1 = np.c_[x[c[:,1]], y[c[:,1]], z[c[:,1]]]
p3 = np.c_[x[c[:,3]], y[c[:,3]], z[c[:,3]]]; p4 = np.c_[x[c[:,4]], y[c[:,4]], z[c[:,4]]]
e01 = np.linalg.norm(p1-p0, axis=1); e03 = np.linalg.norm(p3-p0, axis=1); e04 = np.linalg.norm(p4-p0, axis=1)
chk("element_edge_lengths_h", np.allclose(e01, h, atol=1e-9) and np.allclose(e03, h, atol=1e-9) and np.allclose(e04, h, atol=1e-9),
    [float(min(e01.min(), e03.min(), e04.min())), float(max(e01.max(), e03.max(), e04.max()))], [h, h])
# node sets
ns_names = names("ns_names")
chk("nodeset_names", sorted(ns_names) == ["ns_fix", "ns_load"], ns_names, ["ns_fix", "ns_load"])
for i, nm in enumerate(ns_names, start=1):
    ids = ds.variables[f"node_ns{i}"][:] - 1
    if nm == "ns_fix":
        chk("ns_fix_count", len(ids) == 325, int(len(ids)), 325)
        chk("ns_fix_on_x0", np.all(np.abs(x[ids]) < tol), float(np.abs(x[ids]).max()), 0.0)
        allx0 = np.where(np.abs(x) < tol)[0]
        chk("ns_fix_complete", set(ids.tolist()) == set(allx0.tolist()), int(len(allx0)), int(len(ids)))
    if nm == "ns_load":
        chk("ns_load_count", len(ids) == 13, int(len(ids)), 13)
        chk("ns_load_on_edge", np.all(np.abs(x[ids]-2.0) < tol) and np.all(np.abs(y[ids]) < tol), [float(np.abs(x[ids]-2).max()), float(np.abs(y[ids]).max())], [0.0, 0.0])
        chk("ns_load_z_span", abs(z[ids].min()) < tol and abs(z[ids].max()-0.5) < tol, [float(z[ids].min()), float(z[ids].max())], [0.0, 0.5])
        alledge = np.where((np.abs(x-2.0) < tol) & (np.abs(y) < tol))[0]
        chk("ns_load_complete", set(ids.tolist()) == set(alledge.tolist()), int(len(alledge)), int(len(ids)))
# side sets
ss_names = names("ss_names")
chk("sideset_names", ss_names == ["ss_sym"], ss_names, ["ss_sym"])
if "elem_ss1" in ds.variables:
    el = ds.variables["elem_ss1"][:] - 1; sd = ds.variables["side_ss1"][:]
    chk("ss_sym_count", len(el) == 1152, int(len(el)), 1152)
    # Exodus HEX8 local face node ordering
    faces = {1:(0,1,5,4), 2:(1,2,6,5), 3:(2,3,7,6), 4:(0,4,7,3), 5:(0,3,2,1), 6:(4,5,6,7)}
    zmax_ok = True; zbad = 0.0
    for e, s in zip(el, sd):
        nodes = c[e, list(faces[int(s)])]
        zz = z[nodes]
        if not np.all(np.abs(zz-0.5) < tol):
            zmax_ok = False; zbad = max(zbad, float(np.abs(zz-0.5).max()))
    chk("ss_sym_faces_on_z0.5", zmax_ok, zbad, 0.0)
    nfaces_expected = 48*24
    chk("ss_sym_covers_plane", len(set(el.tolist())) == nfaces_expected, int(len(set(el.tolist()))), nfaces_expected)
rec["checks"] = checks
rec["all_pass"] = all(cc["pass"] for cc in checks)
rec["summary"] = {"num_dim": ndim, "num_nodes": nn, "num_elem": ne, "num_el_blk": nblk, "block_names": blk_names,
                  "elem_type": elem_type, "bounding_box_xmin_xmax_ymin_ymax_zmin_zmax": bbox,
                  "nodesets": {nm: int(ds.dimensions[f"num_nod_ns{i}"].size) for i, nm in enumerate(ns_names, start=1)},
                  "sidesets": {nm: int(ds.dimensions[f"num_side_ss{i}"].size) for i, nm in enumerate(ss_names, start=1)}}
print(json.dumps(rec, indent=2))
sys.exit(0 if rec["all_pass"] else 1)
