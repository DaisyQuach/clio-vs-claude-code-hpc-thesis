import sys, json, numpy as np, netCDF4, hashlib, datetime
f = sys.argv[1]
d = netCDF4.Dataset(f)
def s(v): return b''.join(d.variables[v][:].filled(b'') if hasattr(d.variables[v][:], 'filled') else d.variables[v][:]).decode().strip('\x00')
def names(v):
    arr = d.variables[v][:]
    out=[]
    for row in arr:
        row = row.filled(b'') if hasattr(row,'filled') else row
        out.append(b''.join(x if isinstance(x,bytes) else bytes([x]) for x in row).decode().strip('\x00').strip())
    return out
x=d.variables['coordx'][:]; y=d.variables['coordy'][:]; z=d.variables['coordz'][:]
nn=len(x); ne=int(d.dimensions['num_elem'].size); nb=int(d.dimensions['num_el_blk'].size)
blk_names=names('eb_names'); ns_names=names('ns_names'); ss_names=names('ss_names')
rec={'file':f,'utc':datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
 'sha256':hashlib.sha256(open(f,'rb').read()).hexdigest(),
 'num_dim':int(d.dimensions['num_dim'].size),'num_nodes':nn,'num_elem':ne,'num_el_blk':nb,
 'bbox':{'x':[float(x.min()),float(x.max())],'y':[float(y.min()),float(y.max())],'z':[float(z.min()),float(z.max())]}}
blocks=[]
for i in range(1,nb+1):
    c=d.variables['connect%d'%i]; blocks.append({'id':int(d.variables['eb_prop1'][i-1]),'name':blk_names[i-1],'elem_type':getattr(c,'elem_type'),'num_elem':int(c.shape[0]),'nodes_per_elem':int(c.shape[1])})
rec['blocks']=blocks
tol=1e-6; h=1/24.
nsets=[]
for i in range(1,int(d.dimensions['num_node_sets'].size)+1):
    nodes=d.variables['node_ns%d'%i][:]-1
    e={'id':int(d.variables['ns_prop1'][i-1]),'name':ns_names[i-1],'num_nodes':int(len(nodes))}
    if ns_names[i-1]=='ns_fix': e['all_on_x0']=bool(np.all(np.abs(x[nodes])<tol)); e['expected']=325
    if ns_names[i-1]=='ns_load': e['all_on_edge_x2_y0']=bool(np.all(np.abs(x[nodes]-2.0)<tol) and np.all(np.abs(y[nodes])<tol)); e['z_range']=[float(z[nodes].min()),float(z[nodes].max())]; e['expected']=13
    nsets.append(e)
rec['nodesets']=nsets
ssets=[]
for i in range(1,int(d.dimensions['num_side_sets'].size)+1):
    el=d.variables['elem_ss%d'%i][:]-1; sd=d.variables['side_ss%d'%i][:]
    conn=d.variables['connect1'][:]-1
    # HEX8 face local node ordering (Exodus)
    faces={1:[0,1,5,4],2:[1,2,6,5],3:[2,3,7,6],4:[0,4,7,3],5:[0,3,2,1],6:[4,5,6,7]}
    ok=True
    for e_,s_ in zip(el,sd):
        fn=conn[e_][faces[int(s_)]]
        if not np.all(np.abs(z[fn]-0.5)<tol): ok=False; break
    ssets.append({'id':int(d.variables['ss_prop1'][i-1]),'name':ss_names[i-1],'num_faces':int(len(el)),'all_faces_on_z0p5':ok,'expected':1152})
rec['sidesets']=ssets
# uniform spacing check
ux=np.unique(np.round(x,6)); uy=np.unique(np.round(y,6)); uz=np.unique(np.round(z,6))
rec['grid']={'nx_nodes':len(ux),'ny_nodes':len(uy),'nz_nodes':len(uz),'dx':float(np.diff(ux).mean()),'dy':float(np.diff(uy).mean()),'dz':float(np.diff(uz).mean()),'dx_spread':float(np.diff(ux).max()-np.diff(ux).min()),'dy_spread':float(np.diff(uy).max()-np.diff(uy).min()),'dz_spread':float(np.diff(uz).max()-np.diff(uz).min())}
checks={
 'num_elem==13824':ne==13824,'num_nodes==15925':nn==15925,'one_block_named_block_1':nb==1 and blk_names==['block_1'],
 'block_is_HEX8':blocks[0]['elem_type'].upper().startswith('HEX') and blocks[0]['nodes_per_elem']==8,'block_has_all_elements':blocks[0]['num_elem']==ne,
 'bbox_x_0_2':abs(x.min())<tol and abs(x.max()-2)<tol,'bbox_y_0_1':abs(y.min())<tol and abs(y.max()-1)<tol,'bbox_z_0_0.5':abs(z.min())<tol and abs(z.max()-0.5)<tol,
 'grid_49x25x13_nodes':(len(ux),len(uy),len(uz))==(49,25,13),'uniform_h_1/24':all(abs(rec['grid'][k]-h)<1e-5 for k in ('dx','dy','dz')),
 'ns_fix_325_on_x0':any(e['name']=='ns_fix' and e['num_nodes']==325 and e.get('all_on_x0') for e in nsets),
 'ns_load_13_on_edge':any(e['name']=='ns_load' and e['num_nodes']==13 and e.get('all_on_edge_x2_y0') for e in nsets),
 'ss_sym_1152_on_z0p5':any(e['name']=='ss_sym' and e['num_faces']==1152 and e['all_faces_on_z0p5'] for e in ssets),
 'nodeset_names':sorted(ns_names)==['ns_fix','ns_load'],'sideset_names':ss_names==['ss_sym'],'num_dim==3':rec['num_dim']==3}
rec['checks']={k:bool(v) for k,v in checks.items()}; rec['ALL_CHECKS_PASS']=all(checks.values())
print(json.dumps(rec,indent=1))
