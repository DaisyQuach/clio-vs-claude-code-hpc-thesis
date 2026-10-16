import sys, netCDF4, numpy as np
def names(d,v):
    out=[]
    for row in d.variables[v][:]:
        row=row.filled(b'') if hasattr(row,'filled') else row
        out.append(b''.join(x if isinstance(x,bytes) else bytes([x]) for x in row).decode().strip('\x00').strip())
    return out
for f in sys.argv[1:]:
    d=netCDF4.Dataset(f); t=d.variables['time_whole'][:] if 'time_whole' in d.variables else []
    nv=names(d,'name_nod_var') if 'name_nod_var' in d.variables else []
    ev=names(d,'name_elem_var') if 'name_elem_var' in d.variables else []
    print(f"{f}: nodes={d.dimensions['num_nodes'].size} elems={d.dimensions['num_elem'].size} time_steps={len(t)} last_time={t[-1] if len(t) else None}")
    print("  nodal vars:", nv); print("  elem vars:", ev)
    for i,n in enumerate(nv):
        a=d.variables['vals_nod_var%d'%(i+1)][-1,:]; print(f"  {n}: min={a.min():.4e} max={a.max():.4e} mean={a.mean():.4e}")
