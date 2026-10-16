#!/usr/bin/env python3
"""Combine the E1/E2 (thesis_prelim) and E3 (E3_baseline_prelim) baseline datasets into one dataset (researcher-only).

Reads only ../../thesis_prelim/data/*.csv and ../../E3_baseline_prelim/data/*.csv (both produced by the same E1/E2 method);
writes ../data/*.csv. Counted trials only: E1/E2 counted (accepted) trials and E3 valid/accepted trials; E3 attempt 02
(audit_failed) is excluded, as excluded E1/E2 attempts are.
Usage: python3 -I build_combined.py
"""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
EF = os.path.abspath(os.path.join(HERE, "..", ".."))
E12, E3D, OUT = os.path.join(EF, "thesis_prelim", "data"), os.path.join(EF, "E3_baseline_prelim", "data"), os.path.join(HERE, "..", "data")
os.makedirs(OUT, exist_ok=True)
CATS = ["Model reasoning & writing", "Reading inputs & manuals", "Authoring files", "Meshing (Cubit)",
        "Deck translation (XMLGenerator)", "Verification scripts", "Slurm submit & wait", "Records, copies & hashing"]
NON_SLURM = [c for c in CATS if c != "Slurm submit & wait"]
SESSION_LABEL = {"session_main": "", "session_a": "A", "session_b": "B"}

def rows(p):
    return list(csv.DictReader(open(p)))

def f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def short(rid):
    return rid.split("-")[-1]

# ---- time breakdown per session -------------------------------------------------------------------------------------
tb = []
for b in rows(os.path.join(E12, "time_breakdown_by_session.csv")):
    tb.append({"experiment": b["experiment"], "trial": short(b["run_id"]), "session": SESSION_LABEL.get(b["session"], b["session"]),
               "wall_s": f(b["wall_s"]), "api_s_reported": f(b["api_s_reported"]), **{c: f(b[c]) or 0.0 for c in CATS},
               "slurm_queue_s": f(b.get("slurm_queue_s")) or 0.0, "slurm_run_s": f(b.get("slurm_run_s")) or 0.0})
e3t = {t["trial"]: t for t in rows(os.path.join(E3D, "trials.csv"))}
for b in rows(os.path.join(E3D, "time_breakdown_by_trial.csv")):
    if b["terminal_state"] != "valid":
        continue
    tb.append({"experiment": "E3", "trial": e3t[b["trial"]].get("attempt") or b["trial"], "session": "",
               "wall_s": f(b["wall_s"]), "api_s_reported": f(b["api_s_reported"]), **{c: f(b[c]) or 0.0 for c in CATS},
               "slurm_queue_s": f(b.get("slurm_queue_s")) or 0.0, "slurm_run_s": f(b.get("slurm_run_s")) or 0.0})
for r in tb:
    r["non_slurm_s"] = round(sum(r[c] for c in NON_SLURM), 1)
    r["slurm_submit_wait_s"] = r["Slurm submit & wait"]

# ---- per-trial telemetry ------------------------------------------------------------------------------------------------
tel = []
for t in rows(os.path.join(E12, "trials.csv")):
    if t["counted"] != "True":
        continue
    tel.append({"experiment": t["experiment"], "trial": short(t["run_id"]), "agent_wall_s": f(t["agent_wall_s_total"]),
                "agent_api_s": f(t["agent_api_s_total"]), "turns": f(t["agent_turns_total"]), "output_tokens": f(t["output_tokens_total"]),
                "reported_cost_usd": f(t["reported_cost_usd_total"]), "final_compliance_rel_diff_vs_ref": f(t["final_compliance_rel_diff_vs_ref"]),
                "final_density_max_abs_diff_vs_ref": f(t["final_density_max_abs_diff_vs_ref"]), "sessions": 2 if t["experiment"] == "E2" else 1})
for t in e3t.values():
    if t["terminal_state"] != "valid":
        continue
    tel.append({"experiment": "E3", "trial": t.get("attempt") or t["trial"], "agent_wall_s": f(t["session_wall_s"]), "agent_api_s": f(t["session_api_s"]),
                "turns": f(t["turns"]), "output_tokens": f(t["output_tokens"]), "reported_cost_usd": f(t["reported_cost_usd"]),
                "final_compliance_rel_diff_vs_ref": 0.0, "final_density_max_abs_diff_vs_ref": 0.0, "sessions": 1,
                "files_staged": f(t["files_staged"]), "globus_transfers": f(t["globus_transfers"])})
# E3 reference differences come from the score records (all 0.0, accepted; Thesis/researcher_only/scores/E3-baseline-*/score.json)

# ---- compliance histories -------------------------------------------------------------------------------------------------
hist = [{"experiment": h["experiment"], "series": "reference" if h["series"] == "reference" else short(h["series"]),
         "iteration": int(h["global_iteration"]), "compliance": f(h["compliance"])} for h in rows(os.path.join(E12, "compliance_histories.csv"))]
for h in rows(os.path.join(E3D, "compliance_histories.csv")):
    ref = h["series"].startswith("E1 reference")
    hist.append({"experiment": "E3", "series": "reference" if ref else (h.get("attempt") or h["series"].replace("trial_", "")),
                 "iteration": int(h["iteration"]), "compliance": f(h["compliance"])})

def write(name, rs):
    keys = []
    for r in rs:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(os.path.join(OUT, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rs)
    print(f"wrote {name}: {len(rs)} rows")

write("time_breakdown_by_session.csv", tb); write("trial_telemetry.csv", tel); write("compliance_histories.csv", hist)

# ---- summary (means per experiment/session) ---------------------------------------------------------------------------------
summ = []
for exp, ses in (("E1", ""), ("E2", "A"), ("E2", "B"), ("E3", "")):
    g = [r for r in tb if r["experiment"] == exp and r["session"] == ses]
    tot = sum(r["wall_s"] for r in g)
    s = {"experiment": exp, "session": ses or "single", "n": len(g), "mean_wall_min": round(tot / len(g) / 60, 1),
         "mean_without_slurm_min": round(sum(r["non_slurm_s"] for r in g) / len(g) / 60, 1),
         "mean_slurm_submit_wait_min": round(sum(r["slurm_submit_wait_s"] for r in g) / len(g) / 60, 1),
         "mean_morphorm_run_min": round(sum(r["slurm_run_s"] for r in g) / len(g) / 60, 1)}
    non = sum(r["non_slurm_s"] for r in g)
    s.update({f"share_of_non_slurm_{c}": round(sum(r[c] for r in g) / non, 3) for c in NON_SLURM})
    summ.append(s)
write("summary_by_experiment_session.csv", summ)
