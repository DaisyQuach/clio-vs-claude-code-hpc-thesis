import sys, json, datetime
import numpy as np, netCDF4
path = sys.argv[1]
ds = netCDF4.Dataset(path)
def names(var):
    arr = ds.variables[var][:]
    out = []
    for row in arr:
        out.append(b''.join(c for c in row.compressed().tolist() if c != b'\x00').decode().strip() if hasattr(row,'compressed') else ''.join(x.decode() for x in row if x).strip())
    return out
x = ds.variables['coordx'][:]; y = ds.variables['coordy'][:]; z = ds.variables['coordz'][:]
nn = len(x); ne = int(ds.dimensions['num_elem'].size); nb = int(ds.dimensions['num_el_blk'].size)
blk_names = names('eb_names'); ns_names = names('ns_names') if 'ns_names' in ds.variables else []; ss_names = names('ss_names') if 'ss_names' in ds.variables else []
ns_ids = ds.variables['ns_prop1'][:].tolist(); ss_ids = ds.variables['ss_prop1'][:].tolist()
blk_sizes = [int(ds.dimensions['num_el_in_blk%d'%(i+1)].size) for i in range(nb)]
blk_types = [ds.variables['connect%d'%(i+1)].elem_type for i in range(nb)]
ns = {}
for i,n in enumerate(ns_names):
    nodes = ds.variables['node_ns%d'%(i+1)][:]-1
    ns[n] = dict(count=len(nodes), x=[float(x[nodes].min()),float(x[nodes].max())], y=[float(y[nodes].min()),float(y[nodes].max())], z=[float(z[nodes].min()),float(z[nodes].max())])
ss = {}
conn = ds.variables['connect1'][:]-1
for i,n in enumerate(ss_names):
    el = ds.variables['elem_ss%d'%(i+1)][:]-1; sd = ds.variables['side_ss%d'%(i+1)][:]
    zs = []
    hexfaces = {1:[0,1,5,4],2:[1,2,6,5],3:[2,3,7,6],4:[0,3,7,4],5:[0,1,2,3],6:[4,5,6,7]}
    for e,s in zip(el,sd):
        fn = conn[e][hexfaces[int(s)]]; zs.append(z[fn])
    zs = np.array(zs)
    ss[n] = dict(count=len(el), face_z_min=float(zs.min()), face_z_max=float(zs.max()), sides_used=sorted(set(int(s) for s in sd)))
h = 1.0/24.0
dx = np.unique(np.round(x,6)); 
rep = dict(
  utc=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), file=path,
  num_nodes=nn, num_elements=ne, num_blocks=nb, block_names=blk_names, block_sizes=blk_sizes, block_elem_types=blk_types,
  bbox=dict(x=[float(x.min()),float(x.max())], y=[float(y.min()),float(y.max())], z=[float(z.min()),float(z.max())]),
  unique_x=len(dx), unique_y=len(np.unique(np.round(y,6))), unique_z=len(np.unique(np.round(z,6))),
  element_size_x=float(np.diff(np.sort(dx)).mean()), element_size_x_max_dev=float(np.abs(np.diff(np.sort(dx))-h).max()),
  nodesets=dict(ids=ns_ids, names=ns_names, detail=ns), sidesets=dict(ids=ss_ids, names=ss_names, detail=ss))
tol=1e-6
checks = {}
checks_raw = {
 'num_elements == 13824': ne==13824, 'num_nodes == 15925': nn==15925,
 'one block named block_1 with all elements': nb==1 and blk_names==['block_1'] and blk_sizes==[ne],
 'element type HEX8': all(t.upper().startswith('HEX') for t in blk_types) and ds.dimensions['num_nod_per_el1'].size==8,
 'bbox x [0,2] y [0,1] z [0,0.5]': abs(x.min())<tol and abs(x.max()-2)<tol and abs(y.min())<tol and abs(y.max()-1)<tol and abs(z.min())<tol and abs(z.max()-0.5)<tol,
 'structured 49 x 25 x 13 node planes (h=1/24)': rep['unique_x']==49 and rep['unique_y']==25 and rep['unique_z']==13,
 'ns_fix: 325 nodes, all at x=0': 'ns_fix' in ns and ns['ns_fix']['count']==325 and ns['ns_fix']['x'][1]<tol,
 'ns_load: 13 nodes at x=2,y=0 spanning z in [0,0.5]': 'ns_load' in ns and ns['ns_load']['count']==13 and abs(ns['ns_load']['x'][0]-2)<tol and ns['ns_load']['y'][1]<tol and abs(ns['ns_load']['z'][0])<tol and abs(ns['ns_load']['z'][1]-0.5)<tol,
 'ss_sym: 1152 faces, all on z=0.5': 'ss_sym' in ss and ss['ss_sym']['count']==1152 and abs(ss['ss_sym']['face_z_min']-0.5)<tol and abs(ss['ss_sym']['face_z_max']-0.5)<tol,
}
checks = {k: bool(v) for k,v in checks_raw.items()}
rep["checks"]=checks; rep["ALL_PASS"]=all(checks.values())
print(json.dumps(rep, indent=2, default=lambda o: bool(o) if isinstance(o, np.bool_) else (int(o) if isinstance(o, np.integer) else float(o))))
sys.exit(0 if rep['ALL_PASS'] else 2)
