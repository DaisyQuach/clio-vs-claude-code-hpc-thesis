#!/usr/bin/env python3
"""Verify the EX16 mesh against the frozen specification (FROZEN-EX16-v1 section 3)."""
import sys, json, datetime, hashlib
import numpy as np
from netCDF4 import Dataset

path = sys.argv[1]
h = 1.0/24.0
tol = 1e-6
d = Dataset(path, 'r')
def s(v):
    import numpy.ma as ma
    out = []
    for c in v:
        if ma.is_masked(c):
            continue
        out.append(c.decode() if isinstance(c, bytes) else str(c))
    return ''.join(out).strip('\x00').strip()
rec = {}
rec['file'] = path
rec['sha256'] = hashlib.sha256(open(path,'rb').read()).hexdigest()
rec['verified_utc'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
rec['num_dim'] = int(d.dimensions['num_dim'].size)
rec['num_nodes'] = int(d.dimensions['num_nodes'].size)
rec['num_elem'] = int(d.dimensions['num_elem'].size)
rec['num_el_blk'] = int(d.dimensions['num_el_blk'].size)
rec['num_node_sets'] = int(d.dimensions['num_node_sets'].size) if 'num_node_sets' in d.dimensions else 0
rec['num_side_sets'] = int(d.dimensions['num_side_sets'].size) if 'num_side_sets' in d.dimensions else 0
x = np.array(d.variables['coordx'][:]); y = np.array(d.variables['coordy'][:]); z = np.array(d.variables['coordz'][:])
rec['bbox'] = {'xmin': float(x.min()), 'xmax': float(x.max()), 'ymin': float(y.min()), 'ymax': float(y.max()), 'zmin': float(z.min()), 'zmax': float(z.max())}
# unique coordinate planes -> structured grid check
ux, uy, uz = np.unique(np.round(x, 9)), np.unique(np.round(y, 9)), np.unique(np.round(z, 9))
rec['unique_coord_planes'] = {'x': int(ux.size), 'y': int(uy.size), 'z': int(uz.size)}
rec['max_spacing_deviation_from_h'] = float(max(np.abs(np.diff(ux)-h).max(), np.abs(np.diff(uy)-h).max(), np.abs(np.diff(uz)-h).max()))
# blocks
blk_names = [s(n) for n in d.variables['eb_names'][:]] if 'eb_names' in d.variables else []
blk_ids = [int(i) for i in d.variables['eb_prop1'][:]]
blocks = []
for k, bid in enumerate(blk_ids, start=1):
    conn = d.variables[f'connect{k}']
    blocks.append({'id': bid, 'name': blk_names[k-1] if blk_names else '', 'elem_type': getattr(conn, 'elem_type', ''), 'num_elem': int(conn.shape[0]), 'nodes_per_elem': int(conn.shape[1])})
rec['blocks'] = blocks
# nodesets
ns_names = [s(n) for n in d.variables['ns_names'][:]] if 'ns_names' in d.variables else []
ns_ids = [int(i) for i in d.variables['ns_prop1'][:]] if 'ns_prop1' in d.variables else []
nsets = []
for k, nid in enumerate(ns_ids, start=1):
    nodes = np.array(d.variables[f'node_ns{k}'][:]) - 1
    e = {'id': nid, 'name': ns_names[k-1] if ns_names else '', 'num_nodes': int(nodes.size),
         'x_range': [float(x[nodes].min()), float(x[nodes].max())],
         'y_range': [float(y[nodes].min()), float(y[nodes].max())],
         'z_range': [float(z[nodes].min()), float(z[nodes].max())]}
    nsets.append(e)
rec['nodesets'] = nsets
# independent recount of expected sets from coordinates
rec['coord_count_x_eq_0'] = int(np.sum(np.abs(x) < tol))
rec['coord_count_x_eq_2_and_y_eq_0'] = int(np.sum((np.abs(x-2.0) < tol) & (np.abs(y) < tol)))
# element volume check (all hex volumes == h^3) via hex8 decomposition using trilinear formula on structured grid: check bbox of each element
conn = np.array(d.variables['connect1'][:]) - 1
ex = x[conn]; ey = y[conn]; ez = z[conn]
edges = np.stack([(ex.max(1)-ex.min(1)), (ey.max(1)-ey.min(1)), (ez.max(1)-ez.min(1))], axis=1)
rec['element_extent_min'] = float(edges.min()); rec['element_extent_max'] = float(edges.max())

checks = {
 'num_dim == 3': rec['num_dim'] == 3,
 'num_elem == 27648': rec['num_elem'] == 27648,
 'num_nodes == 30625': rec['num_nodes'] == 30625,
 'exactly one element block': rec['num_el_blk'] == 1,
 'block name == block_1': len(blocks) == 1 and blocks[0]['name'] == 'block_1',
 'block elem_type HEX8 (8 nodes/elem)': len(blocks) == 1 and blocks[0]['nodes_per_elem'] == 8 and blocks[0]['elem_type'].upper().startswith('HEX'),
 'block contains every element': len(blocks) == 1 and blocks[0]['num_elem'] == rec['num_elem'],
 'bbox == [0,2]x[0,1]x[0,1]': all(abs(rec['bbox'][k]-v) < tol for k, v in dict(xmin=0, xmax=2, ymin=0, ymax=1, zmin=0, zmax=1).items()),
 'structured 49x25x25 coordinate planes': (ux.size, uy.size, uz.size) == (49, 25, 25),
 'uniform spacing h=1/24': rec['max_spacing_deviation_from_h'] < 1e-9,
 'all element extents == h': abs(rec['element_extent_min']-h) < 1e-9 and abs(rec['element_extent_max']-h) < 1e-9,
 'two nodesets': rec['num_node_sets'] == 2,
 'ns_fix: 625 nodes all at x=0': any(n['name']=='ns_fix' and n['num_nodes']==625 and abs(n['x_range'][0])<tol and abs(n['x_range'][1])<tol for n in nsets),
 'ns_load: 25 nodes at x=2,y=0 spanning z in [0,1]': any(n['name']=='ns_load' and n['num_nodes']==25 and abs(n['x_range'][0]-2)<tol and abs(n['x_range'][1]-2)<tol and abs(n['y_range'][0])<tol and abs(n['y_range'][1])<tol and abs(n['z_range'][0])<tol and abs(n['z_range'][1]-1)<tol for n in nsets),
 'coordinate recount x=0 == 625': rec['coord_count_x_eq_0'] == 625,
 'coordinate recount x=2,y=0 == 25': rec['coord_count_x_eq_2_and_y_eq_0'] == 25,
 'no sidesets': rec['num_side_sets'] == 0,
}
rec['checks'] = checks
rec['ALL_CHECKS_PASS'] = all(checks.values())
print(json.dumps(rec, indent=2))
sys.exit(0 if rec['ALL_CHECKS_PASS'] else 1)
