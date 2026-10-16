#!/usr/bin/env python3
"""Preliminary thesis figures for the controlled E1/E2 baseline trials (researcher-only).
Reads ../data/*.csv (from build_dataset.py) and ../renders/*.png; writes ../figures/*.png and *.pdf.
Palette: validated 8-slot categorical order (dataviz reference palette, light mode, adjacent pairs pass;
three slots < 3:1 contrast on white -> every figure carries a legend and a CSV table view)."""
import csv, os
from collections import defaultdict
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

HERE = os.path.dirname(os.path.abspath(__file__))
D, R, F = (os.path.join(HERE, "..", x) for x in ("data", "renders", "figures"))
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
    return list(csv.DictReader(open(os.path.join(D, name))))

def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(F, f"{name}.{ext}"), dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig); print("wrote", name)

def short(rid):
    return rid.split("-")[-1]

trials = rows("trials.csv")
counted = {e: [t for t in trials if t["experiment"] == e and t["counted"] == "True"] for e in ("E1", "E2")}

# ---------- Fig 1 / 2: compliance histories vs reference ----------
H = rows("compliance_histories.csv")
for exp, fname, title in (("E1", "fig1_E1_compliance_vs_reference", "E1 (Example 8): compliance history, 5 counted trials vs reference"),
                          ("E2", "fig2_E2_compliance_vs_reference", "E2 (Example 16): compliance across the interruption, 5 counted trials vs reference")):
    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    ref = sorted([(int(r["global_iteration"]), float(r["compliance"])) for r in H if r["experiment"] == exp and r["series"] == "reference"])
    ax.plot([i for i, _ in ref], [c for _, c in ref], color=INK2, lw=2.0, label="Reference (rebuilt ground truth)", zorder=2)
    series = sorted({r["series"] for r in H if r["experiment"] == exp and r["series"] != "reference"})
    for k, s in enumerate(series):
        pts = sorted([(int(r["global_iteration"]), float(r["compliance"])) for r in H if r["series"] == s])
        ax.plot([i for i, _ in pts], [c for _, c in pts], ls="none", marker="o", ms=8 - 1.2 * k, mfc="none",
                mec=SLOTS[k], mew=1.2, label=f"Trial {short(s)}", zorder=3)
    ax.set_yscale("log"); ax.set_xlabel("Optimization iteration (global)"); ax.set_ylabel("Compliance F (log scale)")
    if exp == "E2":
        ax.axvline(20, color=MUTED, ls="--", lw=1)
        ax.text(20.6, ax.get_ylim()[1] * 0.55, "Session A stops (Stage 1, iter 20)\nfresh Session B resumes", color=INK2, fontsize=8, va="top")
    md = max(abs(float(t.get("final_compliance_rel_diff_vs_ref") or 0)) for t in counted[exp])
    ax.text(0.99, 0.97, f"max |final compliance diff| vs reference = {md:.1e} (all trials)", transform=ax.transAxes, ha="right", va="top", fontsize=8, color=INK2)
    ax.set_title(title, loc="left")
    ax.legend(loc="center right", fontsize=8, title="Markers overlap exactly", title_fontsize=7.5)
    save(fig, fname)

# ---------- Fig 3: time breakdown stacked bars ----------
B = rows("time_breakdown_by_session.csv")
fig, axes = plt.subplots(2, 1, figsize=(7.2, 6.4), gridspec_kw={"height_ratios": [5, 10]}, sharex=True)
for ax, exp in zip(axes, ("E1", "E2")):
    bs = [b for b in B if b["experiment"] == exp]
    labels = [f"{short(b['run_id'])}" + ("" if exp == "E1" else f" · {'A' if b['session']=='session_a' else 'B'}") for b in bs]
    y = list(range(len(bs)))[::-1]
    for yi, b in zip(y, bs):
        left = 0.0
        for c in CATS:
            w = float(b[c]) / 60
            if w > 0:
                ax.barh(yi, w, left=left, height=0.52, color=COL[c], edgecolor="white", linewidth=1.0)
            left += w
        q, r_ = float(b.get("slurm_queue_s") or 0) / 60, float(b.get("slurm_run_s") or 0) / 60
        sub = sorted(b for b in [])  # placeholder to keep linters quiet
        ax.barh(yi - 0.40, q, left=0, height=0.16, color="#c9c8c3", edgecolor="white", linewidth=0.6)
        ax.barh(yi - 0.40, r_, left=q, height=0.16, color=MUTED, edgecolor="white", linewidth=0.6)
        ax.text(left + 0.3, yi, f"{left:.0f} min", va="center", fontsize=7.5, color=INK2)
    ax.set_yticks(y); ax.set_yticklabels(labels); ax.grid(axis="y", visible=False)
    ax.set_title(f"{exp}: where the agent session time goes" + (" (A = Stage 1 session, B = fresh recovery session)" if exp == "E2" else ""), loc="left")
axes[-1].set_xlabel("Minutes of agent session wall time")
h = [plt.Rectangle((0, 0), 1, 1, color=COL[c]) for c in CATS] + [plt.Rectangle((0, 0), 1, 1, color="#c9c8c3"), plt.Rectangle((0, 0), 1, 1, color=MUTED)]
fig.legend(h, CATS + ["Slurm queue (thin lane)", "Slurm Morphorm run (thin lane, overlaps 'Slurm submit & wait')"], ncol=2, fontsize=7.5,
           loc="lower center", bbox_to_anchor=(0.5, -0.11))
save(fig, "fig3_time_breakdown_by_session")

# ---------- Fig 4: Gantt (one representative trial per experiment) ----------
G = rows("gantt_segments.csv")
def p(s): return datetime.fromisoformat(s)
lanes = CATS + ["Slurm queue", "Slurm run"]
lc = dict(COL, **{"Slurm queue": "#c9c8c3", "Slurm run": MUTED})
fig, axes = plt.subplots(2, 1, figsize=(7.2, 6.8), sharex=False, gridspec_kw={"hspace": 0.45})
for ax, (exp, rid) in zip(axes, (("E1", "E1-example8-baseline-01"), ("E2", "E2-example16-baseline-03"))):
    seg = [g for g in G if g["run_id"] == rid]
    t0 = min(p(g["start_utc"]) for g in seg)
    for g in seg:
        yi = len(lanes) - 1 - lanes.index(g["category"])
        a = (p(g["start_utc"]) - t0).total_seconds() / 60; w = (p(g["end_utc"]) - p(g["start_utc"])).total_seconds() / 60
        ax.barh(yi, max(w, 0.08), left=a, height=0.62, color=lc[g["category"]], linewidth=0)
    if exp == "E2":
        ends = {}
        for g in seg:
            ends.setdefault(g["session"], [p(g["start_utc"]), p(g["end_utc"])])
            ends[g["session"]][0] = min(ends[g["session"]][0], p(g["start_utc"])); ends[g["session"]][1] = max(ends[g["session"]][1], p(g["end_utc"]))
        a_end = (ends["session_a"][1] - t0).total_seconds() / 60; b_start = (ends["session_b"][0] - t0).total_seconds() / 60
        ax.axvspan(a_end, b_start, color="#f1f0ec", zorder=0)
        ax.annotate(f"interruption + boundary check ({(b_start - a_end) * 60:.0f} s)", xy=((a_end + b_start) / 2, len(lanes) - 0.6),
                    xytext=((a_end + b_start) / 2, len(lanes) + 0.5), ha="center", fontsize=7.5, color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
        ax.text(0.5, len(lanes) - 0.25, "Session A", fontsize=7.5, color=INK2); ax.text(b_start + 6, len(lanes) - 0.25, "Session B (fresh process)", fontsize=7.5, color=INK2)
    ax.set_yticks(range(len(lanes))); ax.set_yticklabels(lanes[::-1], fontsize=7.5); ax.grid(axis="y", visible=False)
    ax.set_xlabel("Minutes from trial start"); ax.set_ylim(-0.6, len(lanes) + (1.2 if exp == "E2" else 0.2))
    ax.set_title(f"{exp} timeline, trial {short(rid)}", loc="left")
save(fig, "fig4_gantt_representative_trials")

# ---------- Fig 5: descriptive telemetry small multiples ----------
metrics = [("agent_wall_s_total", "Agent wall time (min)", 1 / 60), ("agent_turns_total", "Agent turns", 1),
           ("output_tokens_total", "Output tokens (thousands)", 1 / 1000), ("reported_cost_usd_total", "Reported cost (USD, API-equivalent)", 1)]
fig, axes = plt.subplots(1, 4, figsize=(8.4, 2.8))
for ax, (k, lab, sc) in zip(axes, metrics):
    for xi, exp in enumerate(("E1", "E2")):
        vals = [float(t[k]) * sc for t in counted[exp]]
        ax.plot([xi + (j - 2) * 0.06 for j in range(len(vals))], vals, ls="none", marker="o", ms=8, mfc=SLOTS[xi], mec="white", mew=1.5)
        ax.hlines(sum(vals) / len(vals), xi - 0.25, xi + 0.25, color=INK2, lw=1.2)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["E1", "E2\n(A+B)"]); ax.set_xlim(-0.6, 1.6); ax.set_title(lab, fontsize=8.5, loc="left")
    ax.grid(axis="x", visible=False); ax.set_ylim(bottom=0)
fig.suptitle("Descriptive audit telemetry per counted trial (dots) and mean (bar); not a performance score", x=0.01, ha="left", fontsize=9, color=INK)
fig.tight_layout(); save(fig, "fig5_telemetry_descriptive")

# ---------- Fig 6: topology grid ----------
for exp, ids in (("E1", ["reference", "01", "02", "03", "04R2", "05"]), ("E2", ["reference", "01", "02R", "03", "04R", "05"])):
    fig, axes = plt.subplots(2, 3, figsize=(8.4, 4.6))
    for ax, i in zip(axes.flat, ids):
        img = os.path.join(R, f"{exp}_{i}.png")
        ax.axis("off")
        if os.path.isfile(img):
            ax.imshow(mpimg.imread(img)[60:-20, 40:-2])
        ax.set_title("Reference" if i == "reference" else f"Trial {i}", fontsize=9, color=INK)
    fig.suptitle(f"{exp}: final topology (density ≥ 0.5, colored by displacement magnitude), reference vs counted trials", x=0.01, ha="left", fontsize=9.5, color=INK)
    fig.tight_layout(); save(fig, f"fig6_{exp}_topology_grid")

# ---------- summary table of mean shares ----------
with open(os.path.join(D, "time_share_summary.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["experiment", "session", "n", "mean_wall_min"] + [f"share_{c}" for c in CATS])
    groups = defaultdict(list)
    for b in B:
        groups[(b["experiment"], b["session"])].append(b)
    for (e, s), bs in sorted(groups.items()):
        tot = sum(float(b["wall_s"]) for b in bs)
        w.writerow([e, s, len(bs), round(tot / len(bs) / 60, 1)] + [round(sum(float(b[c]) for b in bs) / tot, 3) for c in CATS])
print("wrote time_share_summary.csv")
