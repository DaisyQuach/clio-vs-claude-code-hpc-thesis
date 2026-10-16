#!/usr/bin/env python3
"""Verify the EX8 mesh (FROZEN-EX8-v1) against every locked mesh setting.
Usage: python3 -I verify_mesh.py <mesh.exo> <out.txt>"""
import sys, json, hashlib, datetime
import numpy as np
import netCDF4

mesh_path, out_path = sys.argv[1], sys.argv[2]
ds = netCDF4.Dataset(mesh_path, "r")
d = ds.dimensions
def names(var):
    arr = ds.variables[var][:]
    if np.ma.isMaskedArray(arr):
        arr = arr.filled(b"")
    out = []
    for row in arr:
        s = b"".join(bytes(c) if not isinstance(c, bytes) else c for c in row)
        out.append(s.split(b"\x00")[0].decode("utf-8", "replace").strip())
    return out

h = 1.0 / 24.0
tol = 1e-6
checks = []
def chk(name, got, exp):
    ok = (got == exp)
    checks.append((name, got, exp, ok))

num_dim = len(d["num_dim"]); num_nodes = len(d["num_nodes"]); num_elem = len(d["num_elem"])
num_blk = len(d["num_el_blk"]); num_ns = len(d["num_node_sets"]) if "num_node_sets" in d else 0
num_ss = len(d["num_side_sets"]) if "num_side_sets" in d else 0
chk("num_dim", num_dim, 3)
chk("num_nodes", num_nodes, 15925)
chk("num_elem", num_elem, 13824)
chk("num_el_blk", num_blk, 1)
chk("num_node_sets", num_ns, 2)
chk("num_side_sets", num_ss, 1)

x = ds.variables["coordx"][:]; y = ds.variables["coordy"][:]; z = ds.variables["coordz"][:]
bbox = [float(x.min()), float(x.max()), float(y.min()), float(y.max()), float(z.min()), float(z.max())]
chk("bbox_xmin~0", abs(bbox[0]-0.0) < tol, True)
chk("bbox_xmax~2", abs(bbox[1]-2.0) < tol, True)
chk("bbox_ymin~0", abs(bbox[2]-0.0) < tol, True)
chk("bbox_ymax~1", abs(bbox[3]-1.0) < tol, True)
chk("bbox_zmin~0", abs(bbox[4]-0.0) < tol, True)
chk("bbox_zmax~0.5", abs(bbox[5]-0.5) < tol, True)
# structured grid: unique coordinates per axis
ux, uy, uz = np.unique(np.round(x, 9)), np.unique(np.round(y, 9)), np.unique(np.round(z, 9))
chk("unique_x_count(49)", len(ux), 49); chk("unique_y_count(25)", len(uy), 25); chk("unique_z_count(13)", len(uz), 13)
chk("uniform_spacing_x", bool(np.allclose(np.diff(ux), h, atol=1e-8)), True)
chk("uniform_spacing_y", bool(np.allclose(np.diff(uy), h, atol=1e-8)), True)
chk("uniform_spacing_z", bool(np.allclose(np.diff(uz), h, atol=1e-8)), True)

blk_names = names("eb_names") if "eb_names" in ds.variables else []
chk("block_names", blk_names, ["block_1"])
elem_type = ds.variables["connect1"].elem_type if "connect1" in ds.variables else None
chk("block1_elem_type_HEX8", str(elem_type).upper().startswith("HEX"), True)
nel_blk1 = len(d["num_el_in_blk1"]); npe = len(d["num_nod_per_el1"])
chk("block1_num_elem", nel_blk1, 13824); chk("block1_nodes_per_elem", npe, 8)

ns_names = names("ns_names") if "ns_names" in ds.variables else []
ns = {}
for i, nm in enumerate(ns_names, start=1):
    ids = ds.variables[f"node_ns{i}"][:].astype(int) - 1
    ns[nm] = ids
chk("nodeset_names", sorted(ns_names), ["ns_fix", "ns_load"])
if "ns_fix" in ns:
    ids = ns["ns_fix"]
    chk("ns_fix_count", len(ids), 325)
    chk("ns_fix_all_x0", bool(np.all(np.abs(x[ids]) < tol)), True)
    chk("ns_fix_complete(all x=0 nodes)", int(np.sum(np.abs(x) < tol)), len(ids))
if "ns_load" in ns:
    ids = ns["ns_load"]
    chk("ns_load_count", len(ids), 13)
    chk("ns_load_all_x2_y0", bool(np.all((np.abs(x[ids]-2.0) < tol) & (np.abs(y[ids]) < tol))), True)
    chk("ns_load_complete(all x=2,y=0 nodes)", int(np.sum((np.abs(x-2.0) < tol) & (np.abs(y) < tol))), len(ids))
    chk("ns_load_z_span", [round(float(z[ids].min()),6), round(float(z[ids].max()),6)], [0.0, 0.5])

ss_names = names("ss_names") if "ss_names" in ds.variables else []
chk("sideset_names", ss_names, ["ss_sym"])
conn = ds.variables["connect1"][:].astype(int) - 1
# Exodus HEX8 side -> local node ordering
hex_sides = {1:[0,1,5,4],2:[1,2,6,5],3:[2,3,7,6],4:[0,4,7,3],5:[0,3,2,1],6:[4,5,6,7]}
if ss_names:
    el = ds.variables["elem_ss1"][:].astype(int) - 1
    sd = ds.variables["side_ss1"][:].astype(int)
    chk("ss_sym_face_count", len(el), 1152)
    allz = True
    for e, s in zip(el, sd):
        nodes = conn[e][hex_sides[int(s)]]
        if not np.all(np.abs(z[nodes]-0.5) < tol):
            allz = False; break
    chk("ss_sym_all_faces_on_z0.5", allz, True)
    chk("ss_sym_unique_elements", len(np.unique(el)), 1152)
    # completeness: number of elements touching z=0.5 with a face
    top_elems = int(np.sum(np.sum(np.abs(z[conn]-0.5) < tol, axis=1) == 4))
    chk("ss_sym_complete(elements with a face on z=0.5)", top_elems, len(el))
# element volume check (all hexes h^3)
def hex_vol(c):
    p = np.stack([x[c], y[c], z[c]], axis=-1)
    return float(np.prod(p.max(axis=0)-p.min(axis=0)))
vols = np.array([hex_vol(c) for c in conn])
chk("all_elem_volumes_h^3", bool(np.allclose(vols, h**3, rtol=1e-6)), True)
chk("total_volume_1.0", bool(abs(vols.sum()-1.0) < 1e-8), True)

sha = hashlib.sha256(open(mesh_path, "rb").read()).hexdigest()
allok = all(c[3] for c in checks)
lines = []
lines.append(f"EX8 mesh verification record (FROZEN-EX8-v1)")
lines.append(f"utc_timestamp: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
lines.append(f"mesh_file: {mesh_path}")
lines.append(f"mesh_sha256: {sha}")
lines.append(f"bounding_box: x[{bbox[0]:.9f},{bbox[1]:.9f}] y[{bbox[2]:.9f},{bbox[3]:.9f}] z[{bbox[4]:.9f},{bbox[5]:.9f}]")
lines.append(f"element_type: {elem_type}; blocks: {blk_names}; nodesets: {ns_names} sizes {[len(ns[n]) for n in ns_names]}; sidesets: {ss_names}")
lines.append("")
lines.append(f"{'check':48s} {'got':>28s} {'expected':>28s} result")
for n, g, e, ok in checks:
    lines.append(f"{n:48s} {str(g):>28s} {str(e):>28s} {'PASS' if ok else 'FAIL'}")
lines.append("")
lines.append(f"OVERALL: {'PASS' if allok else 'FAIL'} ({sum(c[3] for c in checks)}/{len(checks)} checks passed)")
open(out_path, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(0 if allok else 1)
