"""Verify Stage-1 results of FROZEN-EX16-v1: iteration count, stopping message,
checkpoint (engine_output.exo) with 21 saved states holding control and topology, final analyze output."""
import sys, os, re, json, hashlib, datetime, glob
import numpy as np
import netCDF4

run = sys.argv[1]
C = {}
def chk(name, cond, observed): C[name] = {"pass": bool(cond), "observed": observed}
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def strs(ds, var):
    if var not in ds.variables: return []
    out=[]
    for row in ds.variables[var][:]:
        if np.ma.isMaskedArray(row): row=row.filled(b"")
        out.append(b"".join(x for x in row.tolist() if x).decode(errors="replace"))
    return out

# ---- optimizer diagnostics
diag = os.path.join(run,"morphorm_oc_optimizer_diagnostics.txt")
chk("diagnostics file exists", os.path.exists(diag), diag)
iters=[]; stop_msg=None; rows=[]
if os.path.exists(diag):
    for line in open(diag):
        m = re.match(r"\s*(\d+)\s+(\d+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)", line)
        if m:
            iters.append(int(m.group(1))); rows.append({"iter":int(m.group(1)),"fcount":int(m.group(2)),"objective":float(m.group(3)),"grad_norm":float(m.group(4)),"H1":float(m.group(5)),"abs_dX":float(m.group(6)),"abs_dF":float(m.group(7))})
        if "******" in line: stop_msg = line.strip()
chk("diagnostics: last iteration == 20", bool(iters) and iters[-1]==20, iters[-1] if iters else None)
chk("diagnostics: iterations 0..20 all present (21 rows)", iters==list(range(21)), (len(iters), iters[:3], iters[-3:]))
chk("diagnostics: stopping message = maximum number of iterations", stop_msg is not None and "maximum number of iterations" in stop_msg, stop_msg)
chk("diagnostics: all objective values finite", all(np.isfinite(r["objective"]) for r in rows), [r["objective"] for r in rows[-3:]])

# ---- checkpoint engine_output.exo
eo = os.path.join(run,"engine_output.exo")
chk("checkpoint engine_output.exo exists", os.path.exists(eo), eo)
eo_info={}
if os.path.exists(eo):
    ds = netCDF4.Dataset(eo,"r")
    nts = ds.dimensions["time_step"].size if "time_step" in ds.dimensions else 0
    times = [float(t) for t in ds.variables["time_whole"][:]] if "time_whole" in ds.variables else []
    nod = strs(ds,"name_nod_var")
    nn = ds.dimensions["num_nodes"].size; ne = ds.dimensions["num_elem"].size
    eo_info={"time_steps":nts,"time_values":times,"nodal_vars":nod,"num_nodes":nn,"num_elem":ne}
    chk("checkpoint: 21 saved states (time steps)", nts==21, nts)
    chk("checkpoint: nodal field 'control' present", "control" in nod, nod)
    chk("checkpoint: nodal field 'topology' present", "topology" in nod, nod)
    chk("checkpoint: mesh size matches (30625 nodes, 27648 elems)", nn==30625 and ne==27648, (nn,ne))
    # per-state field statistics
    stats=[]
    if "control" in nod and "topology" in nod:
        ic = nod.index("control")+1; itp = nod.index("topology")+1
        for s in range(nts):
            c = np.asarray(ds.variables[f"vals_nod_var{ic}"][s,:]); t = np.asarray(ds.variables[f"vals_nod_var{itp}"][s,:])
            stats.append({"state":s+1,"time":times[s] if times else None,"control_min":float(c.min()),"control_max":float(c.max()),"control_mean":float(c.mean()),
                          "topology_min":float(t.min()),"topology_max":float(t.max()),"topology_mean":float(t.mean()),"control_all_finite":bool(np.isfinite(c).all()),"topology_all_finite":bool(np.isfinite(t).all())})
        chk("checkpoint: state 1 control is uniform 0.15 (initial design)", abs(stats[0]["control_min"]-0.15)<1e-12 and abs(stats[0]["control_max"]-0.15)<1e-12, (stats[0]["control_min"],stats[0]["control_max"]))
        chk("checkpoint: all saved fields finite", all(s["control_all_finite"] and s["topology_all_finite"] for s in stats), len(stats))
        chk("checkpoint: saved states are distinct designs (control differs between consecutive states)", all(stats[i]["control_mean"]!=stats[i+1]["control_mean"] or stats[i]["control_max"]!=stats[i+1]["control_max"] for i in range(len(stats)-1)), [round(s["control_mean"],6) for s in stats])
    eo_info["state_stats"]=stats
    ds.close()

# ---- restart file
er = os.path.join(run,"engine_restart.exo")
# informational only: the locked checkpoint is engine_output.exo (spec section 7); a separately named
# engine_restart.exo is mentioned by the manual but its presence is not a locked requirement.
INFO_engine_restart_present = os.path.exists(er)

# ---- final analyze output
vizdirs = sorted(glob.glob(os.path.join(run,"analyze_id_2_output*")))
chk("analyze visualization directory exists", bool(vizdirs), vizdirs)
final=None
if vizdirs:
    files = sorted(glob.glob(os.path.join(vizdirs[0],"iteration*.exo")), key=lambda p:int(re.search(r"iteration(\d+)",p).group(1)))
    nums = [int(re.search(r"iteration(\d+)",p).group(1)) for p in files]
    chk("analyze: iteration0..iteration20 outputs present", nums==list(range(21)), (len(nums), nums[:3], nums[-3:]))
    cand = os.path.join(vizdirs[0],"iteration20.exo")
    chk("analyze: iteration20.exo exists", os.path.exists(cand), cand)
    if os.path.exists(cand):
        final=cand
        ds=netCDF4.Dataset(cand,"r"); nod=strs(ds,"name_nod_var")
        chk("analyze: iteration20.exo has displacement nodal fields", any("displacement" in n or n.startswith("disp") for n in nod), nod)
        ds.close()

hist = os.path.join(run,"opt_criteria_history.csv")
chk("opt_criteria_history.csv exists", os.path.exists(hist), hist if os.path.exists(hist) else "absent")
rec={"frozen_configuration_id":"FROZEN-EX16-v1","stage":"stage1","run_dir":os.path.abspath(run),
     "verified_utc":datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
     "diagnostics_rows":rows,"stopping_message":stop_msg,"checkpoint":eo_info,"final_analyze_output":final,"info_engine_restart_exo_present":INFO_engine_restart_present,
     "sha256":{os.path.basename(p):sha(p) for p in [diag,eo,er,hist,final] if p and os.path.exists(p)},
     "checks":C,"n_checks":len(C),"n_pass":sum(1 for v in C.values() if v["pass"]),"all_checks_pass":all(v["pass"] for v in C.values())}
print(json.dumps(rec,indent=2))
sys.exit(0 if rec["all_checks_pass"] else 1)
