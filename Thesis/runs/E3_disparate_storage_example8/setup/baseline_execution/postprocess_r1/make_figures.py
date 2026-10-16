#!/usr/bin/env python3
"""Preliminary E3 baseline-only figures (researcher-side). Same style and palette as the E1/E2 thesis_prelim figures.
Reads <out>/data/*.csv (build_dataset.py) and <out>/renders/*.png; writes <out>/figures/*.png and *.pdf.
r1: all six attempts appear in every operational figure (trial_06 = 02R); scientific figures use valid trials only (exclusions labelled).
Usage: python3 make_figures.py --out <out>"""
import argparse, csv, os
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.dates as mdates

ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
D, R, F = (os.path.join(a.out, x) for x in ("data", "renders", "figures"))
os.makedirs(F, exist_ok=True)
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
CATS = ["Model reasoning & writing", "Reading inputs & manuals", "Authoring files", "Meshing (Cubit)",
        "Deck translation (XMLGenerator)", "Verification scripts", "Slurm submit & wait", "Records, copies & hashing"]
COL = dict(zip(CATS, SLOTS))
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
                     "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlecolor": INK, "legend.frameon": False})

def rows(name):
    p = os.path.join(D, name)
    return list(csv.DictReader(open(p))) if os.path.isfile(p) else []

def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(F, f"{name}.{ext}"), dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig); print("wrote", name)

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def p(s):
    return datetime.fromisoformat(s)

T = rows("trials.csv")
state = {t["trial"]: t["terminal_state"] for t in T}
LAB = {t["trial"]: t.get("attempt") or t["trial"] for t in T}  # r1: 06 -> 02R
valid = [t["trial"] for t in T if t["terminal_state"] == "valid"]
excl = [f"{LAB[t['trial']]} ({t['terminal_state']})" for t in T if t["terminal_state"] != "valid"]
excl_txt = ("excluded: " + ", ".join(excl)) if excl else "no exclusions"

# ---------- Fig 1: compliance history, valid trials vs E1 reference ----------
H = rows("compliance_histories.csv")
fig, ax = plt.subplots(figsize=(6.6, 3.6))
ref = sorted((int(r["iteration"]), float(r["compliance"])) for r in H if r["series"].startswith("E1 reference"))
if ref:
    ax.plot([i for i, _ in ref], [c for _, c in ref], color=INK2, lw=2.0, label="E1 reference (symmetry-honored variant)", zorder=2)
for k, n in enumerate(valid):
    pts = sorted((int(r["iteration"]), float(r["compliance"])) for r in H if r["series"] == f"trial_{n}")
    if pts:
        ax.plot([i for i, _ in pts], [c for _, c in pts], ls="none", marker="o", ms=8 - 1.2 * k, mfc="none", mec=SLOTS[k], mew=1.2, label=f"Trial {LAB[n]}", zorder=3)
ax.set_yscale("log"); ax.set_xlabel("Optimization iteration"); ax.set_ylabel("Compliance F (log scale)")
ax.set_title(f"E3 baseline (Symmetry-Plane Cantilever): compliance history, {len(valid)} valid of 6 attempts", loc="left")
ax.text(0.99, 0.97, excl_txt, transform=ax.transAxes, ha="right", va="top", fontsize=7.5, color=INK2)
if not valid:
    ax.text(0.5, 0.5, "No valid trial: no scientific series shown", transform=ax.transAxes, ha="center", color=INK2)
ax.legend(loc="center right", fontsize=8)
save(fig, "fig1_E3_compliance_history_valid_trials")

# ---------- Fig 2: execution timeline of all five trials (absolute UTC) ----------
L = rows("timeline_lanes.csv")
lane_col = {"Slurm queue / dependency wait": "#c9c8c3", "Job setup + preparation (pin clone, packet, checks)": SLOTS[3],
            "Agent session": SLOTS[0], "Records, audit, verification": SLOTS[6], "Job (no agent session)": SLOTS[7]}
fig, ax = plt.subplots(figsize=(7.6, 3.9))
ys = {n: 5 - i for i, n in enumerate(["01", "02", "03", "04", "05", "06"])}
for l in L:
    y = ys[l["trial"]]; a0, a1 = p(l["start_utc"]), p(l["end_utc"])
    if l["lane"].startswith("Workflow job") and l["lane"].endswith("(run)"):
        ax.barh(y - 0.33, (a1 - a0).total_seconds() / 86400, left=mdates.date2num(a0), height=0.14, color=MUTED, linewidth=0)
    elif l["lane"].startswith("Workflow job"):
        ax.barh(y - 0.33, (a1 - a0).total_seconds() / 86400, left=mdates.date2num(a0), height=0.14, color="#e4e3df", linewidth=0)
    else:
        ax.barh(y, (a1 - a0).total_seconds() / 86400, left=mdates.date2num(a0), height=0.46, color=lane_col.get(l["lane"], MUTED), edgecolor="white", linewidth=0.6)
for t in T:
    ends = [p(l["end_utc"]) for l in L if l["trial"] == t["trial"]]
    if ends:
        ax.text(mdates.date2num(max(ends)), ys[t["trial"]], f"  {t['terminal_state']}", va="center", fontsize=7.5, color=INK2)
ax.set_yticks(list(ys.values())); ax.set_yticklabels([f"Trial {LAB.get(n, n)}" for n in ys]); ax.grid(axis="y", visible=False)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=None)); ax.set_xlabel("UTC (trials ran one at a time; afterany chain)")
ax.set_title("E3 baseline execution timeline, all six attempts (02R = replacement for 02, run later)", loc="left")
h = [plt.Rectangle((0, 0), 1, 1, color=c) for c in lane_col.values()] + [plt.Rectangle((0, 0), 1, 1, color=MUTED)]
fig.legend(h, list(lane_col) + ["Agent-submitted Morphorm job (thin lane; light = queue)"], ncol=2, fontsize=7, loc="lower center", bbox_to_anchor=(0.5, -0.2))
save(fig, "fig2_E3_execution_timeline")

# ---------- Fig 3: where the agent session time goes (E1/E2 method), all trials with a session ----------
B = rows("time_breakdown_by_trial.csv")
if B:
    fig, ax = plt.subplots(figsize=(7.2, 0.6 + 0.55 * len(B)))
    y = list(range(len(B)))[::-1]
    for yi, b in zip(y, B):
        left = 0.0
        for c in CATS:
            w = float(b[c]) / 60
            if w > 0:
                ax.barh(yi, w, left=left, height=0.52, color=COL[c], edgecolor="white", linewidth=1.0)
            left += w
        q, r_ = float(b.get("slurm_queue_s") or 0) / 60, float(b.get("slurm_run_s") or 0) / 60
        ax.barh(yi - 0.40, q, left=0, height=0.16, color="#c9c8c3", edgecolor="white", linewidth=0.6)
        ax.barh(yi - 0.40, r_, left=q, height=0.16, color=MUTED, edgecolor="white", linewidth=0.6)
        ax.text(left + 0.3, yi, f"{left:.0f} min · {b['terminal_state']}", va="center", fontsize=7.5, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels([f"Trial {LAB[b['trial']]}" for b in B]); ax.grid(axis="y", visible=False)
    ax.set_xlabel("Minutes of agent session wall time"); ax.set_title("E3 baseline: where the agent session time goes", loc="left")
    hh = [plt.Rectangle((0, 0), 1, 1, color=COL[c]) for c in CATS] + [plt.Rectangle((0, 0), 1, 1, color="#c9c8c3"), plt.Rectangle((0, 0), 1, 1, color=MUTED)]
    fig.legend(hh, CATS + ["Slurm queue (thin lane)", "Slurm Morphorm run (thin lane, overlaps 'Slurm submit & wait')"], ncol=2, fontsize=7.5,
               loc="upper center", bbox_to_anchor=(0.5, -0.02))
    fig.subplots_adjust(bottom=0.24)
    save(fig, "fig3_E3_time_breakdown_by_trial")

# ---------- Fig 4: activity Gantt, representative trial (rule: lowest-numbered valid trial, else lowest with a session) ----------
G = rows("gantt_segments.csv")
have = sorted({g["trial"] for g in G})
rep = next((n for n in sorted(valid) if n in have), have[0] if have else None)
if rep:
    lanes = CATS + ["Slurm queue", "Slurm run"]; lc = dict(COL, **{"Slurm queue": "#c9c8c3", "Slurm run": MUTED})
    seg = [g for g in G if g["trial"] == rep]; t0 = min(p(g["start_utc"]) for g in seg)
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    for g in seg:
        yi = len(lanes) - 1 - lanes.index(g["category"])
        x0 = (p(g["start_utc"]) - t0).total_seconds() / 60; w = (p(g["end_utc"]) - p(g["start_utc"])).total_seconds() / 60
        ax.barh(yi, max(w, 0.08), left=x0, height=0.62, color=lc[g["category"]], linewidth=0)
    ax.set_yticks(range(len(lanes))); ax.set_yticklabels(lanes[::-1], fontsize=7.5); ax.grid(axis="y", visible=False)
    ax.set_xlabel("Minutes from session start")
    ax.set_title(f"E3 activity timeline, trial {LAB[rep]} ({state.get(rep)}; selection rule: lowest-numbered valid trial)", loc="left")
    save(fig, "fig4_E3_gantt_representative_trial")

# ---------- Fig 5: resource / telemetry comparison across all five trials ----------
metrics = [("job_elapsed_s", "Job wall time (min)", 1 / 60), ("queue_wait_after_eligible_s", "Queue wait after eligible (min)", 1 / 60),
           ("job_total_cpu_s", "Job CPU time (min)", 1 / 60), ("job_peak_rss_mb", "Agent-job peak RSS (GB)", 1 / 1024),
           ("bytes_staged", "Bytes staged (MB)", 1 / 1e6), ("globus_transfer_wall_s", "Globus transfer wall (s)", 1),
           ("turns", "Agent turns", 1), ("output_tokens", "Output tokens (thousands)", 1 / 1000), ("reported_cost_usd", "Reported cost (USD, API-equiv.)", 1),
           ("workflow_run_s", "Morphorm job run time (min)", 1 / 60)]
fig, axes = plt.subplots(2, 5, figsize=(10.4, 4.6))
for ax, (k, lab, sc) in zip(axes.flat, metrics):
    for t in T:
        v = num(t.get(k)); x = int(t["trial"])
        if v is None:
            ax.text(x, 0, "–", ha="center", va="bottom", color=MUTED, fontsize=8); continue
        ok = t["terminal_state"] == "valid"
        ax.plot([x], [v * sc], ls="none", marker="o", ms=7, mfc=SLOTS[0] if ok else "white", mec=SLOTS[0] if ok else SLOTS[7], mew=1.4)
    ax.margins(y=0.12); ax.set_xticks([1, 2, 3, 4, 5, 6]); ax.set_xticklabels([LAB.get(f"{i:02d}", f"{i:02d}") for i in range(1, 7)], fontsize=7); ax.set_xlim(0.4, 6.6); ax.set_ylim(bottom=0); ax.set_title(lab, fontsize=8, loc="left"); ax.grid(axis="x", visible=False)
for ax in axes[-1]:
    ax.set_xlabel("Attempt", fontsize=8)
hh = [plt.Line2D([], [], ls="none", marker="o", ms=7, mfc=SLOTS[0], mec=SLOTS[0]), plt.Line2D([], [], ls="none", marker="o", ms=7, mfc="white", mec=SLOTS[7], mew=1.4)]
fig.legend(hh, ["valid", "not valid (" + (", ".join(excl) if excl else "none") + ")"], loc="lower center", ncol=2, fontsize=8, bbox_to_anchor=(0.5, -0.06))
fig.suptitle("E3 baseline resource and telemetry comparison, all six attempts (descriptive only; not a performance score)", x=0.01, ha="left", fontsize=9, color=INK)
fig.tight_layout(); save(fig, "fig5_E3_resource_telemetry")

# ---------- Fig 6: topology grid (reference + valid trials only) ----------
ids = ["reference"] + valid
if os.path.isdir(R):
    cols = 3; rws = (len(ids) + cols - 1) // cols
    fig, axes = plt.subplots(rws, cols, figsize=(8.4, 2.4 * rws + 0.4), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for ax, i in zip(axes.flat, ids):
        img = os.path.join(R, f"E3_{i}.png")
        if os.path.isfile(img):
            im = mpimg.imread(img); nz = (im[..., :3].min(axis=2) < 0.97).nonzero()
            if len(nz[0]):
                im = im[max(nz[0].min() - 8, 0):nz[0].max() + 8, max(nz[1].min() - 8, 0):nz[1].max() + 8]
            ax.imshow(im)
        ax.set_title("E1 reference (symmetry-honored variant)" if i == "reference" else f"Trial {LAB.get(i, i)}", fontsize=9, color=INK)
    fig.suptitle(f"E3: final topology (density ≥ 0.5, colored by displacement magnitude), valid trials only; {excl_txt}", x=0.01, ha="left", fontsize=9, color=INK)
    fig.tight_layout(); save(fig, "fig6_E3_topology_grid")
