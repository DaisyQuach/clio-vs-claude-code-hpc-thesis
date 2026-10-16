#!/usr/bin/env python3
"""COUNTED thesis study: CLIO (factorio-flat 0.5.0) vs the Claude Code baseline, n = 5 counted trials per experiment.

Inputs : data/*.csv from official_aggregate.py (both arms read-only from Thesis/, same meter and rules).
Outputs: data/per_run.csv, data/stats.csv, data/morphorm_jobs.csv, figures/H1–H6 (PNG 300 dpi + PDF).
Derived from hpc2_vs_baseline/compare.py (the pilot comparison); statistics unchanged:
mean ± SD per system, ratio of means (CLIO / baseline) with a percentile bootstrap 95 % CI (20,000 resamples, seed 1),
an exact two-sided permutation test on the difference in means (all C(10,5) = 252 splits) and an exact Mann-Whitney U
p-value. Verdict "lower"/"higher" only when the permutation p < 0.05 AND the CI excludes 1, otherwise "no detectable
difference". With n = 5 a non-significant result is not evidence of equality.
"""
import collections
import csv
import glob
import itertools
import json
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.dirname(HERE)
D = f"{HERE}/data"
TH = "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs"
ARM = "clio"
os.makedirs(f"{HERE}/data", exist_ok=True)
os.makedirs(f"{HERE}/figures", exist_ok=True)
EXPS = ("E1", "E2", "E3")
BASE_TRIALS = {"E1": ["01", "02", "03", "05", "04R2"], "E2": ["01", "02R", "03", "04R", "05"], "E3": ["01", "02R", "03", "04", "05"]}
TRIAL_DIR = {("E3", "02R"): "06"}  # E3 replacement 02R ran in baseline/trial_06

SLOT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
C_BASE, C_CLIO = SLOT[0], SLOT[6]
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "savefig.facecolor": SURF, "axes.titleweight": "bold", "axes.titlesize": 10})
FOOT = ("COUNTED THESIS TRIALS · CLIO = clio-agent 0.9.5b5.post2 + factorio-flat 0.5.0, runtime-tuned, default effort · "
        "baseline = Claude Code 2.1.295 · claude-fable-5-1 list prices")


def rows(name):
    return [r for r in csv.DictReader(l for l in open(f"{D}/{name}") if not l.startswith("#"))]


def save(fig, name, y=-0.04):
    fig.text(0.01, y, FOOT, fontsize=6.5, color=INK2, transform=fig.transFigure)
    fig.savefig(f"{HERE}/figures/{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(f"{HERE}/figures/{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def sysname(r):
    return "baseline" if r["arm"] == "baseline" else ("clio" if r["arm"] == ARM else None)


# ------------------------------------------------------------------ per-run table
U, T, O = rows("usage_by_run_session.csv"), rows("time_breakdown_by_run_session.csv"), rows("outcomes_by_run.csv")
runs = collections.OrderedDict()
for r in U:
    s = sysname(r)
    if not s or (s == "baseline" and r["run"] not in BASE_TRIALS[r["experiment"]]):
        continue
    k = (r["experiment"], s, r["run"])
    d = runs.setdefault(k, collections.Counter())
    for c in ("cost", "cost_output", "cost_cache_read", "cost_cache_write", "cost_input", "api_calls", "output", "cache_write",
              "cache_read", "resend_calls", "resend_cache_write"):
        d[c] += float(r[c])
for r in T:
    s = sysname(r)
    k = (r["experiment"], s, r["run"])
    if k not in runs:
        continue
    d = runs[k]
    d["wall_min"] += float(r["wall_s"]) / 60
    d["model_min"] += float(r["Model reasoning & writing"]) / 60
    d["slurm_min"] += float(r["Slurm submit & wait"]) / 60
    d["non_slurm_min"] += float(r["non_slurm_s"]) / 60
    for c in ("Reading inputs & manuals", "Authoring files", "Meshing (Cubit)", "Deck translation (XMLGenerator)",
              "Verification scripts", "Records, copies & hashing"):
        d["tools_min"] += float(r[c]) / 60
    d[f"sess_{r['session']}_wall_min"] += float(r["wall_s"]) / 60
    for c in ("Model reasoning & writing", "Slurm submit & wait"):
        d[f"sess_{r['session']}_{c}"] += float(r[c]) / 60
    d[f"sess_{r['session']}_tools"] += (float(r["non_slurm_s"]) - float(r["Model reasoning & writing"])) / 60
outc = {(o["experiment"], "clio" if o["arm"] == ARM else o["arm"], o["run"]): o["outcome"] for o in O}
for (e, s, run), d in runs.items():
    d["outcome"] = outc.get((e, s, run), "?")

# Morphorm jobs (node speed and contention matter for wall time): both arms from the trials' own sacct records
mj = [{"experiment": m["experiment"], "system": "clio" if m["arm"] == ARM else "baseline", "run": m["run"], "job": m["job"], "name": m["name"],
       "state": m["state"], "elapsed_min": int(m["elapsed_s"]) / 60, "node": m["node"]}
      for m in rows("agent_morphorm_jobs.csv") if any(k[0] == m["experiment"] and k[1] == ("clio" if m["arm"] == ARM else "baseline") and k[2] == m["run"] for k in runs)]
with open(f"{HERE}/data/morphorm_jobs.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(mj[0])); w.writeheader(); w.writerows(mj)
for (e, s, run), d in runs.items():
    js = [m for m in mj if m["experiment"] == e and m["system"] == s and m["run"] == run]
    d["morphorm_jobs"] = len(js)
    d["cancelled_jobs"] = sum(1 for m in js if m["state"].startswith("CANCELLED"))
    d["morphorm_min"] = sum(m["elapsed_min"] for m in js if m["state"] == "COMPLETED")
    d["nodes"] = "+".join(sorted({m["node"] for m in js}))

for (e, s_, run), d in runs.items():  # nudges = extra user messages the pilot runner sent after an early stop (baseline: none)
    d["nudges"] = 0
    if s_ == "clio":
        for f_ in glob.glob(f"{TH}/{ {'E1': 'E1_uninterrupted_example8', 'E2': 'E2_interrupted_recovery_example16', 'E3': 'E3_disparate_storage_example8'}[e]}/clio/trial_{run}/logs/**/clio/runner_events.jsonl", recursive=True):
            d["nudges"] += sum(1 for l in open(f_) if '"kind": "nudge"' in l and '"message_posted"' in l)
METRICS = [("cost", "Cost per run (USD)"), ("wall_min", "Session wall time (min)"), ("model_min", "Model reasoning & writing (min)"),
           ("non_slurm_min", "Time outside Slurm (min)"), ("tools_min", "Tool time (min)"), ("slurm_min", "Slurm submit & wait (min)"),
           ("morphorm_min", "Morphorm job run time (min)"), ("api_calls", "API calls"), ("output", "Output tokens"),
           ("cache_write", "Cache-write tokens"), ("cache_read", "Cache-read tokens"), ("cancelled_jobs", "Cancelled Morphorm jobs"), ("nudges", "Nudges (extra user messages)")]
cols = ["experiment", "system", "run", "outcome", "nodes"] + [m for m, _ in METRICS] + ["resend_calls", "morphorm_jobs"]
with open(f"{HERE}/data/per_run.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(cols)
    for (e, s, run), d in runs.items():
        w.writerow([e, s, run, d["outcome"], d["nodes"]] + [round(d[m], 4) for m, _ in METRICS] + [d["resend_calls"], d["morphorm_jobs"]])


# ------------------------------------------------------------------ statistics
def vals(e, s, m):
    return np.array([d[m] for (ee, ss, _), d in runs.items() if ee == e and ss == s], float)


def perm_p(a, b):
    x = np.concatenate([a, b]); n = len(a); obs = abs(a.mean() - b.mean()); cnt = tot = 0
    for idx in itertools.combinations(range(len(x)), n):
        m = np.zeros(len(x), bool); m[list(idx)] = True
        cnt += abs(x[m].mean() - x[~m].mean()) >= obs - 1e-12; tot += 1
    return cnt / tot


def mwu_p(a, b):
    x = np.concatenate([a, b]); n = len(a)
    ranks = np.argsort(np.argsort(x, kind="mergesort"), kind="mergesort").astype(float) + 1
    for v in np.unique(x):  # average ranks for ties
        ranks[x == v] = ranks[x == v].mean()
    u = lambda r: r[:n].sum() - n * (n + 1) / 2
    obs = u(ranks); mu = n * len(b) / 2; dist = []
    for idx in itertools.combinations(range(len(x)), n):
        m = np.zeros(len(x), bool); m[list(idx)] = True
        dist.append(ranks[m].sum() - n * (n + 1) / 2)
    dist = np.array(dist)
    return float(np.mean(np.abs(dist - mu) >= abs(obs - mu) - 1e-12))


rng = np.random.default_rng(1)


def boot_ratio(a, b, n=20000):
    if b.mean() == 0:
        return (np.nan, np.nan)
    ia = rng.integers(0, len(a), (n, len(a))); ib = rng.integers(0, len(b), (n, len(b)))
    bm = b[ib].mean(1); ok = bm > 0
    r = a[ia].mean(1)[ok] / bm[ok]
    return tuple(np.percentile(r, [2.5, 97.5]))


stats = []
for e in EXPS:
    for m, lab in METRICS:
        a, b = vals(e, "clio", m), vals(e, "baseline", m)
        if len(a) == 0 or len(b) == 0:
            continue
        ratio = a.mean() / b.mean() if b.mean() else np.nan
        lo, hi = boot_ratio(a, b) if len(a) > 1 and len(b) > 1 else (np.nan, np.nan)
        p = perm_p(a, b) if len(a) > 1 and len(b) > 1 else np.nan
        pu = mwu_p(a, b) if len(a) > 1 and len(b) > 1 else np.nan
        verdict = "no detectable difference" if min(len(a), len(b)) >= 3 else "too few runs (n < 3)"
        if min(len(a), len(b)) >= 3 and p < 0.05 and not (lo <= 1 <= hi):
            verdict = "lower" if ratio < 1 else "higher"
        stats.append({"experiment": e, "metric": m, "label": lab, "n_clio": len(a), "n_baseline": len(b),
                      "clio_mean": a.mean(), "clio_sd": a.std(ddof=1) if len(a) > 1 else np.nan,
                      "baseline_mean": b.mean(), "baseline_sd": b.std(ddof=1), "ratio": ratio, "ratio_ci_lo": lo, "ratio_ci_hi": hi,
                      "perm_p": p, "mwu_p": pu, "verdict": verdict})
with open(f"{HERE}/data/stats.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(stats[0])); w.writeheader()
    for s in stats:
        w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()})
ST = {(s["experiment"], s["metric"]): s for s in stats}
json.dump({"n": {e: {s: len(vals(e, s, "cost")) for s in ("baseline", "clio")} for e in EXPS},
           "outcomes": {e: {s: collections.Counter(d["outcome"] for (ee, ss, _), d in runs.items() if ee == e and ss == s) for s in ("baseline", "clio")} for e in EXPS}},
          open(f"{HERE}/data/summary.json", "w"), indent=1, default=dict)

# ------------------------------------------------------------------ H1 cost decomposition (means)
fig, ax = plt.subplots(figsize=(10, 4.6))
labels, x = [], []
parts = [("Output tokens", "cost_output", SLOT[0]), ("Cache reads", "cost_cache_read", SLOT[1]),
         ("Cache writes — incremental", None, SLOT[2]), ("Cache writes — full-context re-sends", "resend", SLOT[3])]
xi = 0
for e in EXPS:
    for s in ("baseline", "clio"):
        ds = [d for (ee, ss, _), d in runs.items() if ee == e and ss == s]
        if not ds:
            continue
        mean = lambda k: np.mean([d[k] for d in ds])
        res = mean("resend_cache_write") * 20e-6
        segs = [mean("cost_output"), mean("cost_cache_read"), mean("cost_cache_write") - res, res]
        bottom = 0
        for (lab, _, c), v in zip(parts, segs):
            ax.bar(xi, v, 0.62, bottom=bottom, color=c, edgecolor=SURF, linewidth=1.2, label=lab if xi == 0 else None)
            bottom += v
        ax.text(xi, bottom + 0.2, f"${mean('cost'):.2f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=INK)
        labels.append(f"{e}\n{'Claude Code' if s == 'baseline' else 'CLIO 0.5.0'}\nn={len(ds)}"); x.append(xi); xi += 1
    xi += 0.6
ax.set_xticks(x, labels, fontsize=8)
ax.set_ylabel("Mean cost per run (USD)"); ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
ax.legend(frameon=False, ncol=4, loc="upper left", fontsize=8); ax.set_ylim(0, ax.get_ylim()[1] * 1.15)
ax.set_title("Cost per run by component: CLIO 0.5.0 vs Claude Code baseline (means)")
save(fig, "H1_cost_decomposition")

# ------------------------------------------------------------------ H2 per-call context and cache writes (median-cost run each)
PC = collections.defaultdict(list)
for r in csv.DictReader(l for l in open(f"{D}/usage_per_call.csv") if not l.startswith("#")):
    PC[r["key"]].append(r)
fig, axes = plt.subplots(len(EXPS), 2, figsize=(11, 2.5 * len(EXPS)), squeeze=False, sharey="row")
for i, e in enumerate(EXPS):
    for j, s in enumerate(("baseline", "clio")):
        ks = [(run, d["cost"]) for (ee, ss, run), d in runs.items() if ee == e and ss == s]
        if not ks:
            continue
        run = sorted(ks, key=lambda t: t[1])[len(ks) // 2][0]
        pref = f"baseline:{e}:{run}:" if s == "baseline" else f"clio:{e}:{run}:"
        calls = [c for k in sorted(PC) if k.startswith(pref) for c in PC[k]]
        ax = axes[i][j]
        n = np.arange(1, len(calls) + 1)
        ax.plot(n, [float(c["context"]) / 1e3 for c in calls], color=SLOT[0], lw=1.8, label="Context sent (k tokens)")
        ax.bar(n, [float(c["cache_write"]) / 1e3 for c in calls], 0.8, color=SLOT[3], label="Cache write on this call (k tokens)")
        ax.set_title(f"{e} {'Claude Code baseline' if s == 'baseline' else 'CLIO 0.5.0'} · run {run} (median cost)", fontsize=9)
        ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
        if i == len(EXPS) - 1:
            ax.set_xlabel("API call #")
axes[0][0].legend(frameon=False, fontsize=7.5, loc="upper left")
fig.tight_layout()
save(fig, "H2_per_call_context_and_cache_writes")

# ------------------------------------------------------------------ H3 time breakdown (means per session)
rowsH3 = []
for e in EXPS:
    for s in ("baseline", "clio"):
        ds = [d for (ee, ss, _), d in runs.items() if ee == e and ss == s]
        sess = ["A", "B"] if e == "E2" else ["main"]
        for se in sess:
            m = np.mean([d[f"sess_{se}_Model reasoning & writing"] for d in ds])
            t = np.mean([d[f"sess_{se}_tools"] for d in ds])
            sl = np.mean([d[f"sess_{se}_Slurm submit & wait"] for d in ds])
            rowsH3.append((f"{e} {'Claude Code' if s == 'baseline' else 'CLIO 0.5.0'} (n={len(ds)})" + (f" · session {se}" if se != "main" else ""), m, t, sl))
fig, ax = plt.subplots(figsize=(10, 0.45 * len(rowsH3) + 1.4))
y = np.arange(len(rowsH3))[::-1]
for k, (lab, c) in enumerate((("Model reasoning & writing", SLOT[0]), ("Tools (reading, authoring, Cubit, XMLGenerator, checks, records)", SLOT[1]),
                              ("Slurm submit & wait (Morphorm)", SLOT[2]))):
    left = [sum(r[1 + q] for q in range(k)) for r in rowsH3]
    v = [r[1 + k] for r in rowsH3]
    ax.barh(y, v, 0.66, left=left, color=c, label=lab, edgecolor=SURF, linewidth=1.2)
    for yi, l0, vv in zip(y, left, v):
        if vv > 2.5:
            ax.text(l0 + vv / 2, yi, f"{vv:.1f}", ha="center", va="center", fontsize=7.5, color="white" if k == 0 else INK)
for yi, r in zip(y, rowsH3):
    ax.text(sum(r[1:]) + 0.5, yi, f"{sum(r[1:]):.1f} min", va="center", fontsize=8)
ax.set_yticks(y, [r[0] for r in rowsH3], fontsize=8); ax.set_xlabel("Minutes (mean per session)")
ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.08), fontsize=7.5)
ax.set_title("Session time by activity (thesis_prelim attribution method)", pad=22)
save(fig, "H3_time_breakdown")


# ------------------------------------------------------------------ H4 work volume / H5 per-run distributions (dots + mean)
def strip(metrics, name, title, ncol=3):
    nrow = int(np.ceil(len(metrics) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.3 * ncol, 3.1 * nrow), squeeze=False)
    for ax, (m, lab, sc) in zip(axes.flat, metrics):
        xt, xl = [], []
        for i, e in enumerate(EXPS):
            for j, s in enumerate(("baseline", "clio")):
                v = vals(e, s, m) / sc
                xx = i * 2.6 + j
                ax.scatter(np.full(len(v), xx) + np.linspace(-0.13, 0.13, len(v)), v, s=26, color=C_BASE if s == "baseline" else C_CLIO,
                           edgecolor=SURF, linewidth=0.8, zorder=3)
                ax.hlines(v.mean(), xx - 0.3, xx + 0.3, color=INK, lw=1.5, zorder=4)
            st = ST.get((e, m))
            if st:
                tag = f"×{st['ratio']:.2f}\np={st['perm_p']:.3f}"
                ax.annotate(tag, (i * 2.6 + 0.5, 1.0), xycoords=("data", "axes fraction"), ha="center", va="top", fontsize=7,
                            color=SLOT[7] if st["verdict"] in ("lower", "higher") else INK)
            xt.append(i * 2.6 + 0.5); xl.append(e)
        ax.set_xticks(xt, xl); ax.set_title(lab, fontsize=9)
        ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
        lo, hi = ax.get_ylim(); ax.set_ylim(min(0, lo), hi * 1.22)
    for ax in list(axes.flat)[len(metrics):]:
        ax.axis("off")
    from matplotlib.lines import Line2D
    fig.legend(handles=[Line2D([], [], marker="o", ls="", color=C_BASE, label="Claude Code baseline run"),
                        Line2D([], [], marker="o", ls="", color=C_CLIO, label="CLIO 0.5.0 run"), Line2D([], [], color=INK, label="Mean")],
               frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.02), fontsize=8)
    fig.suptitle(title + "  (×ratio of means CLIO/baseline; exact permutation p; red = significant and CI excludes 1)",
                 fontweight="bold", fontsize=10, y=1.07)
    fig.tight_layout()
    save(fig, name)


strip([("api_calls", "API calls per run", 1), ("output", "Output tokens per run (k)", 1e3), ("cache_write", "Cache-write tokens per run (k)", 1e3)],
      "H4_work_volume", "How much work each run did")
strip([("cost", "Cost per run (USD)", 1), ("wall_min", "Session wall time (min)", 1), ("model_min", "Model reasoning & writing (min)", 1),
       ("non_slurm_min", "Time outside Slurm (min)", 1), ("slurm_min", "Slurm submit & wait (min)", 1), ("morphorm_min", "Morphorm job run time (min)", 1)],
      "H5_per_run_distributions", "Per-run distributions (baseline n = 5; CLIO n = " + "/".join(str(len(vals(e, "clio", "cost"))) for e in EXPS) + ")")

# ------------------------------------------------------------------ H6 scorecard: ratio of means with bootstrap 95 % CI
SC = [("cost", "Cost"), ("wall_min", "Wall time"), ("model_min", "Model time"), ("non_slurm_min", "Time outside Slurm"),
      ("api_calls", "API calls"), ("output", "Output tokens")]
fig, axes = plt.subplots(1, len(SC), figsize=(2.3 * len(SC), 3.0), sharey=True)
for ax, (m, lab) in zip(axes, SC):
    for i, e in enumerate(EXPS):
        st = ST.get((e, m))
        if not st:
            continue
        col = SLOT[7] if st["verdict"] in ("lower", "higher") else C_CLIO
        ax.errorbar(st["ratio"], i, xerr=[[st["ratio"] - st["ratio_ci_lo"]], [st["ratio_ci_hi"] - st["ratio"]]], fmt="o", color=col,
                    ecolor=col, elinewidth=1.6, capsize=3, ms=6)
        ax.text(st["ratio"], i + 0.28, f"{st['ratio']:.2f}×", ha="center", fontsize=7.5, color=INK)
    ax.axvline(1, color=INK, lw=1); ax.set_title(lab, fontsize=9)
    ax.grid(axis="x", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
    ax.set_ylim(-0.6, len(EXPS) - 0.3)
axes[0].set_yticks(range(len(EXPS)), EXPS)
fig.suptitle("Scorecard: CLIO 0.5.0 ÷ Claude Code baseline (ratio of means, bootstrap 95 % CI; 1.0 = same; red = significant)",
             fontweight="bold", fontsize=10, y=1.04)
fig.tight_layout()
save(fig, "H6_scorecard_vs_baseline", y=-0.08)

for e in EXPS:
    print(e, {s: len(vals(e, s, "cost")) for s in ("baseline", "clio")},
          "; ".join(f"{m} {ST[(e, m)]['ratio']:.2f} p={ST[(e, m)]['perm_p']:.3f} {ST[(e, m)]['verdict']}" for m in ("cost", "wall_min", "model_min", "non_slurm_min") if (e, m) in ST))
