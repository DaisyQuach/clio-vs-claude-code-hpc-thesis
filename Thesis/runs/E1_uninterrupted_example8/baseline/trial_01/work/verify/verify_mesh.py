import sys, json, numpy as np, netCDF4, hashlib, datetime
path = sys.argv[1]
ds = netCDF4.Dataset(path, 'r')
def names(var):
    if var not in ds.variables: return []
    out=[]
    for row in ds.variables[var][:]:
        out.append(b''.join(c for c in row.data.tolist() if c not in (b'', b'\x00')).decode() if hasattr(row,'data') else ''.join(row))
    return out
def cname(v):
    arr = ds.variables[v][:]
    res=[]
    for row in arr:
        if np.ma.is_masked(row): row = row.filled(b'')
        res.append(b''.join(x if isinstance(x,bytes) else x.encode() for x in row.tolist() if x not in (b'', b'\x00', '')).decode())
    return res
x = ds.variables['coordx'][:]; y = ds.variables['coordy'][:]; z = ds.variables['coordz'][:]
nn = ds.dimensions['num_nodes'].size; ne = ds.dimensions['num_elem'].size
nblk = ds.dimensions['num_el_blk'].size
blk_names = cname('eb_names') if 'eb_names' in ds.variables else []
ns_names = cname('ns_names') if 'ns_names' in ds.variables else []
ss_names = cname('ss_names') if 'ss_names' in ds.variables else []
rec = {}
rec['file'] = path
rec['sha256'] = hashlib.sha256(open(path,'rb').read()).hexdigest()
rec['utc'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
rec['num_dim'] = ds.dimensions['num_dim'].size
rec['num_nodes'] = nn; rec['num_elem'] = ne
rec['bbox'] = {'x':[float(x.min()),float(x.max())],'y':[float(y.min()),float(y.max())],'z':[float(z.min()),float(z.max())]}
rec['num_el_blk'] = nblk
blocks=[]
for i in range(nblk):
    c = ds.variables[f'connect{i+1}']
    blocks.append({'id': int(ds.variables['eb_prop1'][i]), 'name': blk_names[i] if blk_names else None,
                   'elem_type': getattr(c,'elem_type',None), 'num_elem': c.shape[0], 'nodes_per_elem': c.shape[1]})
rec['blocks'] = blocks
# element edge length check (block 1): all edges of hex should be h
h = 1.0/24.0
c = ds.variables['connect1'][:] - 1
xyz = np.stack([x,y,z],axis=1)
edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
L = np.concatenate([np.linalg.norm(xyz[c[:,a]]-xyz[c[:,b]],axis=1) for a,b in edges])
rec['edge_length'] = {'min':float(L.min()),'max':float(L.max()),'target_h':h,'max_abs_dev':float(np.abs(L-h).max())}
# unique coords -> structured grid counts
rec['unique_coords'] = {'nx':int(len(np.unique(np.round(x,8)))),'ny':int(len(np.unique(np.round(y,8)))),'nz':int(len(np.unique(np.round(z,8))))}
nsets=[]
for i in range(ds.dimensions['num_node_sets'].size):
    nodes = ds.variables[f'node_ns{i+1}'][:] - 1
    nsets.append({'id': int(ds.variables['ns_prop1'][i]), 'name': ns_names[i] if ns_names else None, 'num_nodes': int(len(nodes)),
                  'x_range':[float(x[nodes].min()),float(x[nodes].max())],'y_range':[float(y[nodes].min()),float(y[nodes].max())],'z_range':[float(z[nodes].min()),float(z[nodes].max())]})
rec['nodesets'] = nsets
ssets=[]
hex_faces = {1:(0,1,5,4),2:(1,2,6,5),3:(2,3,7,6),4:(0,3,7,4),5:(0,1,2,3),6:(4,5,6,7)}  # Exodus HEX8 side numbering (1-based sides)
for i in range(ds.dimensions['num_side_sets'].size):
    el = ds.variables[f'elem_ss{i+1}'][:] - 1; sd = ds.variables[f'side_ss{i+1}'][:]
    zc=[]
    for e,s in zip(el,sd):
        fn = c[e][list(hex_faces[int(s)])]
        zc.append(z[fn])
    zc=np.array(zc)
    ssets.append({'id': int(ds.variables['ss_prop1'][i]), 'name': ss_names[i] if ss_names else None, 'num_faces': int(len(el)),
                  'face_node_z_min': float(zc.min()), 'face_node_z_max': float(zc.max())})
rec['sidesets'] = ssets
# expected values (locked)
tol=1e-6
checks = {
 'num_dim==3': rec['num_dim']==3,
 'num_elem==13824': ne==13824,
 'num_nodes==15925': nn==15925,
 'bbox x[0,2] y[0,1] z[0,0.5]': all(abs(a-b)<tol for a,b in zip(rec['bbox']['x']+rec['bbox']['y']+rec['bbox']['z'],[0,2,0,1,0,0.5])),
 'one block named block_1 with all elements, HEX8': nblk==1 and blocks[0]['name']=='block_1' and blocks[0]['num_elem']==ne and blocks[0]['nodes_per_elem']==8 and (blocks[0]['elem_type'] or '').upper().startswith('HEX'),
 'uniform edge length h=1/24': rec['edge_length']['max_abs_dev']<1e-9,
 'structured 49x25x13 node grid': (rec['unique_coords']['nx'],rec['unique_coords']['ny'],rec['unique_coords']['nz'])==(49,25,13),
 'nodeset ns_fix: 325 nodes all at x=0': any(n['name']=='ns_fix' and n['num_nodes']==325 and abs(n['x_range'][0])<tol and abs(n['x_range'][1])<tol for n in nsets),
 'nodeset ns_load: 13 nodes at x=2,y=0, z spans [0,0.5]': any(n['name']=='ns_load' and n['num_nodes']==13 and abs(n['x_range'][0]-2)<tol and abs(n['x_range'][1]-2)<tol and abs(n['y_range'][0])<tol and abs(n['y_range'][1])<tol and abs(n['z_range'][0])<tol and abs(n['z_range'][1]-0.5)<tol for n in nsets),
 'sideset ss_sym: 1152 faces all on z=0.5': any(s['name']=='ss_sym' and s['num_faces']==1152 and abs(s['face_node_z_min']-0.5)<tol and abs(s['face_node_z_max']-0.5)<tol for s in ssets),
 'exactly 2 nodesets and 1 sideset': len(nsets)==2 and len(ssets)==1,
}
rec['checks'] = checks
rec['ALL_CHECKS_PASS'] = all(checks.values())
print(json.dumps(rec, indent=2))
sys.exit(0 if rec['ALL_CHECKS_PASS'] else 1)
