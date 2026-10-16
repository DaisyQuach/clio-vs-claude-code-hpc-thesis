"""Verify the Stage-1 Exodus mesh against FROZEN-EX16-v1 section 3 (locked mesh)."""
import sys, json, hashlib, datetime
import numpy as np
import netCDF4

path = sys.argv[1]
ds = netCDF4.Dataset(path, "r")
def names(var):
    if var not in ds.variables: return []
    return [b"".join(c for c in row if c != b"").decode().rstrip("\x00") for row in ds.variables[var][:].data if True]
def strs(var):
    if var not in ds.variables: return []
    arr = ds.variables[var][:]
    out=[]
    for row in arr:
        if np.ma.isMaskedArray(row): row = row.filled(b"")
        out.append(b"".join(x for x in row.tolist() if x not in (b"", None)).decode(errors="replace"))
    return out

num_dim = ds.dimensions["num_dim"].size
num_nodes = ds.dimensions["num_nodes"].size
num_elem = ds.dimensions["num_elem"].size
num_el_blk = ds.dimensions["num_el_blk"].size
num_ns = ds.dimensions["num_node_sets"].size if "num_node_sets" in ds.dimensions else 0
num_ss = ds.dimensions["num_side_sets"].size if "num_side_sets" in ds.dimensions else 0
x = ds.variables["coordx"][:] if "coordx" in ds.variables else ds.variables["coord"][0,:]
y = ds.variables["coordy"][:] if "coordy" in ds.variables else ds.variables["coord"][1,:]
z = ds.variables["coordz"][:] if "coordz" in ds.variables else ds.variables["coord"][2,:]
x,y,z = np.asarray(x),np.asarray(y),np.asarray(z)
bbox = [[float(x.min()),float(x.max())],[float(y.min()),float(y.max())],[float(z.min()),float(z.max())]]
eb_names = strs("eb_names"); ns_names = strs("ns_names"); ss_names = strs("ss_names")
eb_ids = [int(v) for v in ds.variables["eb_prop1"][:]]
blocks=[]
for i in range(1,num_el_blk+1):
    v = ds.variables[f"connect{i}"]
    blocks.append({"id":eb_ids[i-1],"name":eb_names[i-1] if eb_names else None,"elem_type":getattr(v,"elem_type",None),
                   "num_elem":ds.dimensions[f"num_el_in_blk{i}"].size,"nodes_per_elem":ds.dimensions[f"num_nod_per_el{i}"].size})
ns_ids = [int(v) for v in ds.variables["ns_prop1"][:]] if num_ns else []
nodesets=[]
h=1.0/24.0
for i in range(1,num_ns+1):
    nn = np.asarray(ds.variables[f"node_ns{i}"][:]).astype(int)-1
    d={"id":ns_ids[i-1],"name":ns_names[i-1] if ns_names else None,"num_nodes":int(len(nn)),
       "x_range":[float(x[nn].min()),float(x[nn].max())],"y_range":[float(y[nn].min()),float(y[nn].max())],"z_range":[float(z[nn].min()),float(z[nn].max())]}
    nodesets.append(d)
# uniform spacing check: unique coordinates along each axis
ux,uy,uz = np.unique(np.round(x,10)),np.unique(np.round(y,10)),np.unique(np.round(z,10))
spacing = {"nx_unique":int(len(ux)),"ny_unique":int(len(uy)),"nz_unique":int(len(uz)),
           "dx_min":float(np.diff(ux).min()),"dx_max":float(np.diff(ux).max()),
           "dy_min":float(np.diff(uy).min()),"dy_max":float(np.diff(uy).max()),
           "dz_min":float(np.diff(uz).min()),"dz_max":float(np.diff(uz).max())}
# element volume check from connectivity of block 1 (hex8, axis aligned -> bbox volume)
conn = np.asarray(ds.variables["connect1"][:]).astype(int)-1
ex = x[conn]; ey=y[conn]; ez=z[conn]
vol = (ex.max(1)-ex.min(1))*(ey.max(1)-ey.min(1))*(ez.max(1)-ez.min(1))
elem = {"min_elem_bbox_volume":float(vol.min()),"max_elem_bbox_volume":float(vol.max()),"total_volume":float(vol.sum()),"expected_elem_volume":h**3}
sha = hashlib.sha256(open(path,"rb").read()).hexdigest()

checks = {
 "num_dim == 3": num_dim==3,
 "num_elem == 27648": num_elem==27648,
 "num_nodes == 30625": num_nodes==30625,
 "one element block": num_el_blk==1,
 "block name == block_1": bool(blocks and blocks[0]["name"]=="block_1"),
 "block elem type HEX8": bool(blocks and str(blocks[0]["elem_type"]).upper().startswith("HEX") and blocks[0]["nodes_per_elem"]==8),
 "block contains every element": bool(blocks and blocks[0]["num_elem"]==num_elem),
 "bounding box [0,2]x[0,1]x[0,1]": bool(np.allclose(bbox,[[0,2],[0,1],[0,1]],atol=1e-9)),
 "uniform h=1/24 in x,y,z (49x25x25 coordinate planes)": spacing["nx_unique"]==49 and spacing["ny_unique"]==25 and spacing["nz_unique"]==25 and all(abs(spacing[k]-h)<1e-9 for k in ("dx_min","dx_max","dy_min","dy_max","dz_min","dz_max")),
 "total volume == 2.0": abs(elem["total_volume"]-2.0)<1e-9,
 "nodeset ns_fix exists with 625 nodes on x=0": any(n["name"]=="ns_fix" and n["num_nodes"]==625 and abs(n["x_range"][0])<1e-12 and abs(n["x_range"][1])<1e-12 for n in nodesets),
 "nodeset ns_load exists with 25 nodes on x=2,y=0,z in [0,1]": any(n["name"]=="ns_load" and n["num_nodes"]==25 and abs(n["x_range"][0]-2)<1e-12 and abs(n["x_range"][1]-2)<1e-12 and abs(n["y_range"][0])<1e-12 and abs(n["y_range"][1])<1e-12 and abs(n["z_range"][0])<1e-12 and abs(n["z_range"][1]-1)<1e-12 for n in nodesets),
 "no sidesets required (count recorded)": True,
}
rec = {"frozen_configuration_id":"FROZEN-EX16-v1","mesh_file":path,"mesh_sha256":sha,
       "verified_utc":datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "num_dim":num_dim,"num_nodes":num_nodes,"num_elem":num_elem,"num_element_blocks":num_el_blk,
       "num_nodesets":num_ns,"num_sidesets":num_ss,"bounding_box":bbox,"blocks":blocks,"nodesets":nodesets,
       "sidesets":ss_names,"spacing":spacing,"element_volume":elem,"checks":checks,"all_checks_pass":all(checks.values())}
print(json.dumps(rec,indent=2))
sys.exit(0 if rec["all_checks_pass"] else 1)
