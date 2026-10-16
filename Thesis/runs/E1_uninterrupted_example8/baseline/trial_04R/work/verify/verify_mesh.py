#!/usr/bin/env python3
"""Verify the FROZEN-EX8-v1 mesh against every locked mesh setting."""
import sys, json, datetime
import numpy as np
import netCDF4 as nc

path = sys.argv[1]
ds = nc.Dataset(path)
def names(var):
    arr = ds.variables[var][:]
    out = []
    for row in arr:
        out.append("".join(c.decode() if isinstance(c, bytes) else str(c) for c in row.compressed() if c != b'' and c != '').strip())
    return out

ndim = len(ds.dimensions['num_dim']); nnode = len(ds.dimensions['num_nodes']); nelem = len(ds.dimensions['num_elem'])
x = ds.variables['coordx'][:]; y = ds.variables['coordy'][:]; z = ds.variables['coordz'][:]
bbox = [float(x.min()), float(x.max()), float(y.min()), float(y.max()), float(z.min()), float(z.max())]
nblk = len(ds.dimensions['num_el_blk']); blk_names = names('eb_names'); blk_ids = [int(i) for i in ds.variables['eb_prop1'][:]]
blk_info = []
for b in range(1, nblk+1):
    v = ds.variables[f'connect{b}']
    blk_info.append({'id': blk_ids[b-1], 'name': blk_names[b-1], 'elem_type': getattr(v, 'elem_type'), 'num_elem': v.shape[0], 'nodes_per_elem': v.shape[1]})
ns_names = names('ns_names'); ns_ids = [int(i) for i in ds.variables['ns_prop1'][:]]
ns = {}
for i, nm in enumerate(ns_names, start=1):
    nodes = ds.variables[f'node_ns{i}'][:] - 1
    ns[nm] = {'id': ns_ids[i-1], 'count': int(len(nodes)),
              'x_range': [float(x[nodes].min()), float(x[nodes].max())],
              'y_range': [float(y[nodes].min()), float(y[nodes].max())],
              'z_range': [float(z[nodes].min()), float(z[nodes].max())]}
ss_names = names('ss_names'); ss_ids = [int(i) for i in ds.variables['ss_prop1'][:]]
ss = {}
conn = ds.variables['connect1'][:] - 1
# Exodus HEX8 side -> local node ordering
HEX_SIDES = {1:[0,1,5,4],2:[1,2,6,5],3:[2,3,7,6],4:[0,4,7,3],5:[0,3,2,1],6:[4,5,6,7]}
for i, nm in enumerate(ss_names, start=1):
    el = ds.variables[f'elem_ss{i}'][:] - 1; sd = ds.variables[f'side_ss{i}'][:]
    zs = []
    for e, s in zip(el, sd):
        zs.extend(z[conn[e][HEX_SIDES[int(s)]]].tolist())
    ss[nm] = {'id': ss_ids[i-1], 'count': int(len(el)), 'face_node_z_range': [float(min(zs)), float(max(zs))]}

# uniform spacing check
ux, uy, uz = np.unique(np.round(x, 9)), np.unique(np.round(y, 9)), np.unique(np.round(z, 9))
spacing = {'nx_unique': int(len(ux)), 'ny_unique': int(len(uy)), 'nz_unique': int(len(uz)),
           'dx_min_max': [float(np.diff(ux).min()), float(np.diff(ux).max())],
           'dy_min_max': [float(np.diff(uy).min()), float(np.diff(uy).max())],
           'dz_min_max': [float(np.diff(uz).min()), float(np.diff(uz).max())]}
h = 1.0/24.0; tol = 1e-9
checks = {
 'num_dim == 3': ndim == 3,
 'num_elem == 13824': nelem == 13824,
 'num_nodes == 15925': nnode == 15925,
 'bbox == [0,2]x[0,1]x[0,0.5]': np.allclose(bbox, [0,2,0,1,0,0.5], atol=tol),
 'exactly one element block': nblk == 1,
 "block name == 'block_1'": blk_names == ['block_1'],
 'block elem type HEX8': blk_info[0]['elem_type'].upper().startswith('HEX') and blk_info[0]['nodes_per_elem'] == 8,
 'block contains every element': blk_info[0]['num_elem'] == nelem,
 'uniform h=1/24 in x,y,z (48x24x12)': (len(ux),len(uy),len(uz)) == (49,25,13) and all(abs(v-h) < 1e-9 for v in spacing['dx_min_max']+spacing['dy_min_max']+spacing['dz_min_max']),
 "nodeset 'ns_fix' exists with 325 nodes": ns.get('ns_fix', {}).get('count') == 325,
 "ns_fix all on x=0": 'ns_fix' in ns and abs(ns['ns_fix']['x_range'][1]) < tol,
 "nodeset 'ns_load' exists with 13 nodes": ns.get('ns_load', {}).get('count') == 13,
 "ns_load all on x=2,y=0 spanning z in [0,0.5]": 'ns_load' in ns and abs(ns['ns_load']['x_range'][0]-2)<tol and abs(ns['ns_load']['y_range'][1])<tol and abs(ns['ns_load']['z_range'][0])<tol and abs(ns['ns_load']['z_range'][1]-0.5)<tol,
 "sideset 'ss_sym' exists with 1152 faces": ss.get('ss_sym', {}).get('count') == 1152,
 "ss_sym faces all on z=0.5": 'ss_sym' in ss and abs(ss['ss_sym']['face_node_z_range'][0]-0.5)<tol and abs(ss['ss_sym']['face_node_z_range'][1]-0.5)<tol,
 'exactly two nodesets': len(ns_names) == 2,
 'exactly one sideset': len(ss_names) == 1,
}
rec = {'file': path, 'verified_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
       'num_dim': ndim, 'num_nodes': nnode, 'num_elem': nelem, 'bounding_box_xmin_xmax_ymin_ymax_zmin_zmax': bbox,
       'element_blocks': blk_info, 'nodesets': ns, 'sidesets': ss, 'node_spacing': spacing,
       'checks': {k: bool(v) for k, v in checks.items()}, 'ALL_CHECKS_PASS': all(checks.values())}
print(json.dumps(rec, indent=2))
sys.exit(0 if rec['ALL_CHECKS_PASS'] else 1)
