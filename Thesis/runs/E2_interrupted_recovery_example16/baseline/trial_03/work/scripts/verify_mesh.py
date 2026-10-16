"""Verify the FROZEN-EX16-v1 mesh against the locked specification (section 3)."""
import sys, json, hashlib, datetime
import numpy as np
from netCDF4 import Dataset

path = sys.argv[1]
H = 1.0 / 24.0
def names(ds, var):
    if var not in ds.variables: return []
    arr = ds.variables[var][:]
    out = []
    for row in arr:
        out.append("".join(c.decode() if isinstance(c, bytes) else str(c) for c in row.compressed() if c != b'' ).strip())
    return out

ds = Dataset(path)
x = np.asarray(ds.variables['coordx'][:], dtype=float); y = np.asarray(ds.variables['coordy'][:], dtype=float); z = np.asarray(ds.variables['coordz'][:], dtype=float)
nn = len(x); ne = int(ds.dimensions['num_elem'].size); nb = int(ds.dimensions['num_el_blk'].size)
nns = int(ds.dimensions['num_node_sets'].size) if 'num_node_sets' in ds.dimensions else 0
nss = int(ds.dimensions['num_side_sets'].size) if 'num_side_sets' in ds.dimensions else 0
bnames = names(ds, 'eb_names'); nsnames = names(ds, 'ns_names')
checks = []
def chk(label, ok, got, want):
    checks.append({"check": label, "pass": bool(ok), "got": got, "expected": want})

chk("num_dim", int(ds.dimensions['num_dim'].size) == 3, int(ds.dimensions['num_dim'].size), 3)
chk("num_elem", ne == 27648, ne, 27648)
chk("num_nodes", nn == 30625, nn, 30625)
chk("num_el_blk", nb == 1, nb, 1)
chk("num_node_sets", nns == 2, nns, 2)
chk("num_side_sets", nss == 0, nss, 0)
tol = 1e-9
bbox = [float(x.min()), float(x.max()), float(y.min()), float(y.max()), float(z.min()), float(z.max())]
chk("bounding_box", all(abs(a-b) < tol for a, b in zip(bbox, [0,2,0,1,0,1])), bbox, [0,2,0,1,0,1])
# block 1
conn = ds.variables['connect1']
etype = conn.getncattr('elem_type')
chk("block1_elem_type", etype.upper().startswith("HEX8") or etype.upper()=="HEX", etype, "HEX8")
chk("block1_num_elem", conn.shape[0] == 27648, int(conn.shape[0]), 27648)
chk("block1_nodes_per_elem", conn.shape[1] == 8, int(conn.shape[1]), 8)
chk("block1_name", (bnames[0] if bnames else None) == "block_1", bnames[0] if bnames else None, "block_1")
# uniform element size: check all unique coordinate values are multiples of h and count 49/25/25
ix, iy, iz = np.round(x/H), np.round(y/H), np.round(z/H)
snap = max(float(np.abs(x-ix*H).max()), float(np.abs(y-iy*H).max()), float(np.abs(z-iz*H).max()))
chk("all_nodes_on_h_lattice", snap < 1e-9, {"max_snap_error": snap}, "every coordinate is an integer multiple of h (tol 1e-9)")
ux, uy, uz = np.unique(ix), np.unique(iy), np.unique(iz)
chk("unique_x_planes", len(ux) == 49 and ux.min() == 0 and ux.max() == 48, int(len(ux)), 49)
chk("unique_y_planes", len(uy) == 25 and uy.min() == 0 and uy.max() == 24, int(len(uy)), 25)
chk("unique_z_planes", len(uz) == 25 and uz.min() == 0 and uz.max() == 24, int(len(uz)), 25)
# element edge lengths all == h (check first node-to-second node edge for every element and the element volumes)
c = np.asarray(conn[:], dtype=int) - 1
p = np.stack([x, y, z], axis=1)
edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
maxdev = 0.0
for a, b in edges:
    L = np.linalg.norm(p[c[:, a]] - p[c[:, b]], axis=1)
    maxdev = max(maxdev, float(np.abs(L - H).max()))
chk("all_hex_edges_equal_h", maxdev < 1e-9, {"max_abs_dev_from_h": maxdev, "h": H}, "all 12 edges of every element = 1/24")
# nodesets
ns = {}
for i in range(1, nns+1):
    nodes = np.asarray(ds.variables[f'node_ns{i}'][:], dtype=int) - 1
    nm = nsnames[i-1] if nsnames else f"ns{i}"
    ns[nm] = nodes
chk("nodeset_names", set(ns.keys()) == {"ns_fix", "ns_load"}, sorted(ns.keys()), ["ns_fix", "ns_load"])
if "ns_fix" in ns:
    f = ns["ns_fix"]
    chk("ns_fix_count", len(f) == 625, int(len(f)), 625)
    chk("ns_fix_all_on_x0", bool(np.all(np.abs(x[f]) < tol)), float(np.abs(x[f]).max()), "x = 0 for every node")
    allx0 = np.where(np.abs(x) < tol)[0]
    chk("ns_fix_contains_every_x0_node", set(f.tolist()) == set(allx0.tolist()), int(len(allx0)), 625)
if "ns_load" in ns:
    l = ns["ns_load"]
    chk("ns_load_count", len(l) == 25, int(len(l)), 25)
    chk("ns_load_all_on_x2_y0", bool(np.all(np.abs(x[l]-2.0) < tol) and np.all(np.abs(y[l]) < tol)),
        {"max|x-2|": float(np.abs(x[l]-2).max()), "max|y|": float(np.abs(y[l]).max())}, "x = 2 and y = 0 for every node")
    chk("ns_load_z_spans_0_to_1", abs(z[l].min()) < tol and abs(z[l].max()-1) < tol and len(np.unique(np.round(z[l]/H))) == 25,
        [float(z[l].min()), float(z[l].max())], [0.0, 1.0])
    alledge = np.where((np.abs(x-2.0) < tol) & (np.abs(y) < tol))[0]
    chk("ns_load_contains_every_edge_node", set(l.tolist()) == set(alledge.tolist()), int(len(alledge)), 25)
vol = 2.0*1.0*1.0
chk("domain_volume_from_counts", abs(ne*H**3 - vol) < 1e-9, ne*H**3, vol)
sha = hashlib.sha256(open(path, 'rb').read()).hexdigest()
allpass = all(c["pass"] for c in checks)
rec = {"trial": "E2-example16-baseline-03", "frozen_configuration_id": "FROZEN-EX16-v1",
       "mesh_file": path, "mesh_sha256": sha, "verified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "mesher": "Coreform Cubit 2026.8 (cubit-edu/2026.8) batch, journal mesh.jou",
       "summary": {"num_elem": ne, "num_nodes": nn, "num_el_blk": nb, "block_names": bnames, "elem_type": etype,
                   "num_node_sets": nns, "nodeset_names": nsnames, "nodeset_sizes": {k: int(len(v)) for k, v in ns.items()},
                   "num_side_sets": nss, "bounding_box_xmin_xmax_ymin_ymax_zmin_zmax": bbox, "h": H},
       "checks": checks, "ALL_CHECKS_PASS": allpass}
print(json.dumps(rec, indent=2))
sys.exit(0 if allpass else 1)
