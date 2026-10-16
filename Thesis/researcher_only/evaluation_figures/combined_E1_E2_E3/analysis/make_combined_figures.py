#!/usr/bin/env python3
"""Combined E1 / E2 / E3 baseline figures (researcher-only). Same palette and style as thesis_prelim.
Reads ../data/*.csv (build_combined.py) and ../renders/*.png; writes ../figures/*.png and *.pdf.
Usage: python3 make_combined_figures.py"""
import csv, os
from collections import defaultdict
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
NON_SLURM = [c for c in CATS if c != "Slurm submit & wait"]
EXPS = [("E1", "E1 (Example 8, uninterrupted)"), ("E2", "E2 (Example 16, interrupted + recovery)"), ("E3", "E3 (Example 8, distributed storage)")]
ECOL = {"E1": SLOTS[0], "E2": SLOTS[1], "E3": SLOTS[2]}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
                     "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlecolor": INK, "legend.frameon": False})

def rows(n):
    return list(csv.DictReader(open(os.path.join(D, n))))

def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(F, f"{name}.{ext}"), dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig); print("wrote", name)

# ---------- Fig 1: time breakdown WITHOUT Slurm submit & wait; Slurm time annotated at the right ----------
B = rows("time_breakdown_by_session.csv")
groups = [(e, t, [b for b in B if b["experiment"] == e]) for e, t in EXPS]
fig, axes = plt.subplots(3, 1, figsize=(7.8, 9.6), sharex=True, gridspec_kw={"height_ratios": [len(g) for _, _, g in groups], "hspace": 0.35})
xmax = max(float(b["non_slurm_s"]) for b in B) / 60
for ax, (exp, title, bs) in zip(axes, groups):
    y = list(range(len(bs)))[::-1]
    for yi, b in zip(y, bs):
        left = 0.0
        for c in NON_SLURM:
            w = float(b[c]) / 60
            if w > 0:
                ax.barh(yi, w, left=left, height=0.62, color=COL[c], edgecolor="white", linewidth=0.8)
            left += w
        s, tot = float(b["slurm_submit_wait_s"]) / 60, float(b["wall_s"]) / 60
        ax.text(xmax * 1.03, yi, f"{left:4.1f} + {s:4.1f} Slurm = {tot:4.1f} min", va="center", fontsize=7.5, color=INK2, family="DejaVu Sans Mono")
    ax.set_yticks(y); ax.set_yticklabels([f"{b['trial']}" + (f" · {b['session']}" if b["session"] else "") for b in bs], fontsize=8)
    ax.grid(axis="y", visible=False); ax.set_title(title, loc="left")
    ax.set_xlim(0, xmax * 1.02)
axes[0].text(xmax * 1.03, len(groups[0][2]) - 0.2, "without Slurm + Slurm submit & wait = session", fontsize=7.5, color=INK, va="bottom", fontweight="bold")
axes[-1].set_xlabel("Minutes of agent session time, excluding 'Slurm submit & wait' (agent submitting and waiting for its Morphorm job)")
h = [plt.Rectangle((0, 0), 1, 1, color=COL[c]) for c in NON_SLURM]
fig.legend(h, NON_SLURM, ncol=3, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.45, 0.06))
fig.suptitle("Baseline agent session time by activity, Slurm submit & wait removed (E2: A = Stage-1 session, B = recovery session)",
             x=0.01, ha="left", fontsize=9.5, color=INK, y=0.955)
fig.subplots_adjust(top=0.91)
save(fig, "figC1_time_breakdown_without_slurm_E1_E2_E3")

# ---------- Fig 2: mean shares of the non-Slurm time ----------
S = rows("summary_by_experiment_session.csv")
fig, ax = plt.subplots(figsize=(7.8, 2.6))
labs = [f"{s['experiment']}" + ("" if s["session"] == "single" else f" · {s['session']}") for s in S]
y = list(range(len(S)))[::-1]
for yi, s in zip(y, S):
    left = 0.0
    for c in NON_SLURM:
        w = float(s[f"share_of_non_slurm_{c}"]) * 100
        if w > 0:
            ax.barh(yi, w, left=left, height=0.6, color=COL[c], edgecolor="white", linewidth=0.8)
            if w >= 6:
                ax.text(left + w / 2, yi, f"{w:.0f}%", ha="center", va="center", fontsize=7, color="white")
        left += w
    ax.text(101.5, yi, f"{s['mean_without_slurm_min']} + {s['mean_slurm_submit_wait_min']} Slurm = {s['mean_wall_min']} min  (n={s['n']})",
            va="center", fontsize=7.5, color=INK2, family="DejaVu Sans Mono")
ax.set_yticks(y); ax.set_yticklabels(labs); ax.set_xlim(0, 100); ax.grid(axis="y", visible=False)
ax.set_xlabel("Share of agent session time excluding Slurm submit & wait (%)")
ax.set_title("Mean composition of the non-Slurm session time, counted trials", loc="left")
fig.legend([plt.Rectangle((0, 0), 1, 1, color=COL[c]) for c in NON_SLURM], NON_SLURM, ncol=4, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.45, -0.02))
save(fig, "figC2_mean_share_without_slurm_E1_E2_E3")

# ---------- Fig 3: compliance histories, three panels ----------
H = rows("compliance_histories.csv")
fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.5))
for ax, (exp, title) in zip(axes, EXPS):
    ref = sorted((int(r["iteration"]), float(r["compliance"])) for r in H if r["experiment"] == exp and r["series"] == "reference")
    ax.plot([i for i, _ in ref], [c for _, c in ref], color=INK2, lw=2.0, label="Reference", zorder=2)
    for k, s in enumerate(sorted({r["series"] for r in H if r["experiment"] == exp and r["series"] != "reference"})):
        pts = sorted((int(r["iteration"]), float(r["compliance"])) for r in H if r["experiment"] == exp and r["series"] == s)
        ax.plot([i for i, _ in pts], [c for _, c in pts], ls="none", marker="o", ms=6.5 - 1.0 * k, mfc="none", mec=SLOTS[k], mew=1.1, label=f"Trial {s}", zorder=3)
    if exp == "E2":
        ax.axvline(20, color=MUTED, ls="--", lw=1)
    ax.set_yscale("log"); ax.set_xlabel("Optimization iteration (global)"); ax.set_title(title, loc="left", fontsize=9)
    ax.legend(fontsize=7, loc="upper right")
axes[0].set_ylabel("Compliance F (log scale)")
fig.suptitle("Compliance history of every counted trial vs its reference (all final differences 0.0; E3 reference = E1 symmetry-honored variant)",
             x=0.01, ha="left", fontsize=9.5, color=INK)
fig.tight_layout(); save(fig, "figC3_compliance_histories_E1_E2_E3")

# ---------- Fig 4: descriptive telemetry ----------
T = rows("trial_telemetry.csv")
metrics = [("agent_wall_s", "Agent wall time (min)", 1 / 60), ("agent_api_s", "Model API time (min)", 1 / 60), ("turns", "Agent turns", 1),
           ("output_tokens", "Output tokens (thousands)", 1 / 1000), ("reported_cost_usd", "Reported cost (USD, API-equiv.)", 1)]
fig, axes = plt.subplots(1, 5, figsize=(11.4, 2.9))
for ax, (k, lab, sc) in zip(axes, metrics):
    for xi, (exp, _) in enumerate(EXPS):
        vals = [float(t[k]) * sc for t in T if t["experiment"] == exp and t[k]]
        ax.plot([xi + (j - 2) * 0.07 for j in range(len(vals))], vals, ls="none", marker="o", ms=7, mfc=ECOL[exp], mec="white", mew=1.3)
        ax.hlines(sum(vals) / len(vals), xi - 0.27, xi + 0.27, color=INK2, lw=1.2)
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["E1", "E2\n(A+B)", "E3"]); ax.set_xlim(-0.6, 2.6); ax.set_ylim(bottom=0)
    ax.set_title(lab, fontsize=8.5, loc="left"); ax.grid(axis="x", visible=False)
fig.suptitle("Descriptive telemetry per counted trial (dots) and mean (bar); not a performance score", x=0.01, ha="left", fontsize=9, color=INK)
fig.tight_layout(); save(fig, "figC4_telemetry_E1_E2_E3")

# ---------- Fig 5: topology grid, 3 rows x 6 ----------
rows_ids = [("E1", ["reference", "01", "02", "03", "04R2", "05"]), ("E2", ["reference", "01", "02R", "03", "04R", "05"]),
            ("E3", ["reference", "01", "02R", "03", "04", "05"])]
fig, axes = plt.subplots(3, 6, figsize=(13.0, 6.9))
for r, (exp, ids) in enumerate(rows_ids):
    for c, i in enumerate(ids):
        ax = axes[r, c]; ax.axis("off")
        img = os.path.join(R, f"{exp}_{i}.png")
        if os.path.isfile(img):
            ax.imshow(mpimg.imread(img)[60:-20, 40:-2])
        ax.set_title(f"{exp} reference" if i == "reference" else f"{exp} trial {i}", fontsize=8.5, color=INK)
fig.suptitle("Final topology (density ≥ 0.5, colored by displacement magnitude): reference and every counted trial, E1 / E2 / E3",
             x=0.01, ha="left", fontsize=10, color=INK)
fig.tight_layout(); save(fig, "figC5_topology_grid_E1_E2_E3")
