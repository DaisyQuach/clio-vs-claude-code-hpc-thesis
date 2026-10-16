#!/usr/bin/env python3
"""Report and check an Exodus mesh against the structured grid its Cubit journal
declares.  Run with the approved runtime's python3 (numpy, netCDF4).

Usage: validate_mesh.py mesh.exo NX NY NZ LX LY LZ [sideset ...]
Exit 0 if every check passes, 1 otherwise.  JSON report on stdout.
"""
import json, sys
import numpy as np
from netCDF4 import Dataset

path, nx, ny, nz = sys.argv[1], *map(int, sys.argv[2:5])
lx, ly, lz = map(float, sys.argv[5:8])
want_ss = sys.argv[8:]


def names(ds, var):
    if var not in ds.variables:
        return []
    return [b"".join(r.compressed()).decode() for r in ds.variables[var][:]]


with Dataset(path) as ds:
    x, y, z = (np.asarray(ds.variables[c][:]) for c in ("coordx", "coordy", "coordz"))
    rep = {
        "file": path,
        "num_nodes": len(ds.dimensions["num_nodes"]),
        "num_elem": len(ds.dimensions["num_elem"]),
        "num_el_blk": len(ds.dimensions["num_el_blk"]),
        "block_names": names(ds, "eb_names"),
        "element_type": ds.variables["connect1"].getncattr("elem_type"),
        "bbox": {"x": [float(x.min()), float(x.max())], "y": [float(y.min()), float(y.max())],
                 "z": [float(z.min()), float(z.max())]},
        "nodesets": {}, "sidesets": {},
    }
    for i, n in enumerate(names(ds, "ns_names"), 1):
        idx = np.asarray(ds.variables[f"node_ns{i}"][:]) - 1
        rep["nodesets"][n] = {"size": int(idx.size),
                              "x": [float(x[idx].min()), float(x[idx].max())],
                              "y": [float(y[idx].min()), float(y[idx].max())],
                              "z": [float(z[idx].min()), float(z[idx].max())]}
    for i, n in enumerate(names(ds, "ss_names"), 1):
        rep["sidesets"][n] = {"size": len(ds.dimensions[f"num_side_ss{i}"])}

tol = 1e-6
checks = {
    "num_elem == NX*NY*NZ": rep["num_elem"] == nx * ny * nz,
    "num_nodes == (NX+1)(NY+1)(NZ+1)": rep["num_nodes"] == (nx + 1) * (ny + 1) * (nz + 1),
    "single block 'block_1'": rep["block_names"] == ["block_1"],
    "element type HEX8": rep["element_type"].upper().startswith("HEX8"),
    "bbox == [0,LX]x[0,LY]x[0,LZ]": all(abs(a - b) < tol for a, b in zip(
        rep["bbox"]["x"] + rep["bbox"]["y"] + rep["bbox"]["z"], [0, lx, 0, ly, 0, lz])),
    "ns_fix: (NY+1)(NZ+1) nodes on x=0": rep["nodesets"].get("ns_fix", {}).get("size") == (ny + 1) * (nz + 1)
        and rep["nodesets"]["ns_fix"]["x"][1] < tol,
    "ns_load: NZ+1 nodes on x=LX, y=0": rep["nodesets"].get("ns_load", {}).get("size") == nz + 1
        and rep["nodesets"]["ns_load"]["x"][0] > lx - tol and rep["nodesets"]["ns_load"]["y"][1] < tol,
}
for s in want_ss:
    checks[f"sideset {s}: NX*NY faces"] = rep["sidesets"].get(s, {}).get("size") == nx * ny
rep["expected"] = {"NX": nx, "NY": ny, "NZ": nz, "LX": lx, "LY": ly, "LZ": lz, "sidesets": want_ss}
rep["checks"] = {k: bool(v) for k, v in checks.items()}
rep["all_checks_pass"] = all(checks.values())
print(json.dumps(rep, indent=2))
sys.exit(0 if rep["all_checks_pass"] else 1)
