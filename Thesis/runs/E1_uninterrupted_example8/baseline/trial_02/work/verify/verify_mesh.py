#!/usr/bin/env python3
"""Mesh verification for frozen workflow EX8 (FROZEN-EX8-v1).
Usage: python3 -I verify_mesh.py <mesh.exo>
Checks element/node counts, element type, bounding box, block name, nodeset and sideset
names/sizes and the geometric location of every set entity against the locked specification.
Exit code 0 only if every check passes."""
import sys, json, datetime
import numpy as np
import netCDF4

path = sys.argv[1]
ds = netCDF4.Dataset(path, 'r')
TOL = 1e-9

def names(var):
    if var not in ds.variables:
        return []
    out = []
    for row in ds.variables[var][:]:
        s = b''.join([b if isinstance(b, bytes) else bytes(b) for b in row.compressed()]) if hasattr(row, 'compressed') else row.tobytes()
        out.append(s.decode('utf-8', 'ignore').strip('\x00').strip())
    return out

checks = []
def check(name, actual, expected):
    ok = (actual == expected)
    checks.append({"check": name, "expected": expected, "actual": actual, "pass": bool(ok)})
    return ok

num_nodes = len(ds.dimensions['num_nodes'])
num_elem = len(ds.dimensions['num_elem'])
num_el_blk = len(ds.dimensions['num_el_blk'])
num_dim = len(ds.dimensions['num_dim'])
check("num_dim", num_dim, 3)
check("num_elem", num_elem, 13824)
check("num_nodes", num_nodes, 15925)
check("num_el_blk", num_el_blk, 1)

x = ds.variables['coordx'][:]; y = ds.variables['coordy'][:]; z = ds.variables['coordz'][:]
bbox = [float(x.min()), float(x.max()), float(y.min()), float(y.max()), float(z.min()), float(z.max())]
bbox_exp = [0.0, 2.0, 0.0, 1.0, 0.0, 0.5]
check("bounding_box_xmin_xmax_ymin_ymax_zmin_zmax", [round(v, 9) for v in bbox], bbox_exp)

# element block
conn = ds.variables['connect1']
check("block1_elem_type", str(conn.getncattr('elem_type')).upper(), 'HEX8')
check("block1_num_elem", len(ds.dimensions['num_el_in_blk1']), 13824)
check("block1_nodes_per_elem", len(ds.dimensions['num_nod_per_el1']), 8)
eb_names = names('eb_names')
check("block_names", eb_names, ['block_1'])
eb_ids = [int(v) for v in ds.variables['eb_prop1'][:]]
checks.append({"check": "block_ids(info)", "expected": None, "actual": eb_ids, "pass": True})

# uniform element size check: edge lengths of a few elements
c = np.array(conn[:]) - 1
X = np.column_stack([x, y, z])
e = X[c[:, 1]] - X[c[:, 0]]
edge = np.linalg.norm(e, axis=1)
h = 1.0 / 24.0
check("uniform_edge_length_h=1/24 (max abs dev < 1e-9)", bool(np.max(np.abs(edge - h)) < 1e-9), True)
check("unique_x_coordinates", len(np.unique(np.round(x, 9))), 49)
check("unique_y_coordinates", len(np.unique(np.round(y, 9))), 25)
check("unique_z_coordinates", len(np.unique(np.round(z, 9))), 13)

# nodesets
ns_names = names('ns_names')
ns_ids = [int(v) for v in ds.variables['ns_prop1'][:]]
ns = {}
for i, nm in enumerate(ns_names, start=1):
    nodes = np.array(ds.variables['node_ns%d' % i][:]) - 1
    ns[nm] = nodes
check("nodeset_names", sorted(ns_names), sorted(['ns_fix', 'ns_load']))
checks.append({"check": "nodeset_ids(info)", "expected": None, "actual": dict(zip(ns_names, ns_ids)), "pass": True})
if 'ns_fix' in ns:
    n = ns['ns_fix']
    check("ns_fix_size", int(len(n)), 325)
    check("ns_fix_all_on_x=0", bool(np.all(np.abs(x[n]) < TOL)), True)
    # every node with x=0 is in the set
    check("ns_fix_contains_every_x=0_node", int(np.sum(np.abs(x) < TOL)), int(len(n)))
if 'ns_load' in ns:
    n = ns['ns_load']
    check("ns_load_size", int(len(n)), 13)
    check("ns_load_all_on_x=2_y=0", bool(np.all(np.abs(x[n] - 2.0) < TOL) and np.all(np.abs(y[n]) < TOL)), True)
    check("ns_load_spans_z_0_to_0.5", [round(float(z[n].min()), 9), round(float(z[n].max()), 9)], [0.0, 0.5])

# sidesets
ss_names = names('ss_names')
ss_ids = [int(v) for v in ds.variables['ss_prop1'][:]]
check("sideset_names", ss_names, ['ss_sym'])
checks.append({"check": "sideset_ids(info)", "expected": None, "actual": dict(zip(ss_names, ss_ids)), "pass": True})
# Exodus HEX8 side -> local node indices (0-based)
HEX8_SIDES = {1: [0, 1, 5, 4], 2: [1, 2, 6, 5], 3: [2, 3, 7, 6], 4: [0, 3, 7, 4], 5: [0, 1, 2, 3], 6: [4, 5, 6, 7]}
for i, nm in enumerate(ss_names, start=1):
    el = np.array(ds.variables['elem_ss%d' % i][:]) - 1
    sd = np.array(ds.variables['side_ss%d' % i][:])
    check("%s_size" % nm, int(len(el)), 1152)
    allz = True
    for ee, ss in zip(el, sd):
        nodes = c[ee][HEX8_SIDES[int(ss)]]
        if not np.all(np.abs(z[nodes] - 0.5) < TOL):
            allz = False
            break
    check("%s_all_faces_on_z=0.5" % nm, allz, True)
    check("%s_unique_faces" % nm, int(len(set(zip(el.tolist(), sd.tolist())))), int(len(el)))

# Exodus metadata
info = {"title": getattr(ds, 'title', ''), "api_version": float(getattr(ds, 'api_version', 0)), "version": float(getattr(ds, 'version', 0)),
        "num_dim": num_dim, "num_nodes": num_nodes, "num_elem": num_elem, "num_el_blk": num_el_blk,
        "num_node_sets": len(ds.dimensions['num_node_sets']) if 'num_node_sets' in ds.dimensions else 0,
        "num_side_sets": len(ds.dimensions['num_side_sets']) if 'num_side_sets' in ds.dimensions else 0}
ds.close()

all_pass = all(cc["pass"] for cc in checks)
result = {"trial_id": "E1-example8-baseline-02", "frozen_configuration_id": "FROZEN-EX8-v1",
          "mesh_file": path, "verification_utc": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
          "exodus_info": info, "checks": checks, "all_checks_pass": all_pass}
print(json.dumps(result, indent=2, default=str))
sys.exit(0 if all_pass else 1)
