#!/usr/bin/env python3
"""COUNTED thesis study: CLIO (factorio-flat 0.5.0) vs the Claude Code baseline, E1/E2/E3, n = 5 counted trials each.

Reads both arms read-only from Thesis/ and writes data/*.csv here in the same schema as the pilot aggregation
(pilot_program_20261012_bpv2/aggregate.py), so the same meter and the same rules apply to both systems:
  usage_by_run_session.csv   per session: tokens and cost at claude-fable-5-1 list prices
                             baseline: the trial's Claude Code transcripts; CLIO: clio/usage_per_call.csv, which
                             lib/clio_usage.py computes from the Claude Code SDK transcripts CLIO's provider wrote
  time_breakdown_by_run_session.csv   thesis_prelim categories; baseline rows copied from the thesis's own
                             combined evaluation data; CLIO rows from the session trace/messages exports
  agent_morphorm_jobs.csv    Morphorm jobs from each trial's sacct records (both arms)
  outcomes_by_run.csv        scoring decision (researcher_only/scores/<run>/score.json; both arms, same scorer)
Usage: official_aggregate.py   (re-run after every scored trial; partial data is fine)
"""
import collections, csv, datetime as dt, glob, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
TH = "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis"
COMB = f"{TH}/researcher_only/evaluation_figures/combined_E1_E2_E3/data"
SC = f"{TH}/researcher_only/scores"
os.makedirs(f"{HERE}/data", exist_ok=True)
L = "COUNTED THESIS TRIALS (read-only)"
PRICE = {"in": 10e-6, "out": 50e-6, "cache_read": 0.25e-6, "cw_1h": 20e-6, "cw_5m": 12.5e-6}
U = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
EXPDIR = {"E1": "E1_uninterrupted_example8", "E2": "E2_interrupted_recovery_example16", "E3": "E3_disparate_storage_example8"}
RUNID = {"E1": "E1-example8", "E2": "E2-example16"}
BASE_TRIALS = {"E1": ["01", "02", "03", "04R2", "05"], "E2": ["01", "02R", "03", "04R", "05"], "E3": ["01", "02R", "03", "04", "05"]}
BASE_E3_DIR = {"02R": "06"}


def transcript_calls(path):
    seen = collections.OrderedDict()
    for line in open(path, errors="replace"):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("type") == "assistant" and (r["message"].get("model") or "") != "<synthetic>":
            m = r["message"]
            seen[m.get("id")] = (r.get("timestamp"), m.get("usage") or {})
    out = []
    for ts, u in seen.values():
        cc = u.get("cache_creation") or {}
        cw = u.get("cache_creation_input_tokens", 0) or 0
        cw1, cw5 = cc.get("ephemeral_1h_input_tokens", 0) or 0, cc.get("ephemeral_5m_input_tokens", 0) or 0
        if cw and not (cw1 or cw5):
            cw1 = cw
        row = dict(utc=ts, input=u.get("input_tokens", 0) or 0, output=u.get("output_tokens", 0) or 0,
                   cache_read=u.get("cache_read_input_tokens", 0) or 0, cache_write=cw, cw1=cw1, cw5=cw5)
        row["cost"] = row["input"] * PRICE["in"] + row["output"] * PRICE["out"] + row["cache_read"] * PRICE["cache_read"] + cw1 * PRICE["cw_1h"] + cw5 * PRICE["cw_5m"]
        out.append(row)
    return out


def usage_csv_calls(path):
    out = []
    for r in csv.DictReader(l for l in open(path) if not l.startswith("#")):
        out.append(dict(utc=r["utc"], input=int(r["input_tokens"]), output=int(r["output_tokens"]), cache_read=int(r["cache_read_tokens"]),
                        cache_write=int(r["cache_write_tokens"]), cw1=int(r["cache_write_1h"]), cw5=int(r["cache_write_5m"]), cost=float(r["cost_usd"])))
    return out


def summarize(calls):
    for c in calls:
        c["context"] = c["input"] + c["cache_read"] + c["cache_write"]
    s = {k: sum(c[k] for c in calls) for k in ("input", "output", "cache_read", "cache_write", "cw1", "cw5", "cost")}
    s.update(api_calls=len(calls), cost_output=s["output"] * PRICE["out"], cost_cache_read=s["cache_read"] * PRICE["cache_read"],
             cost_cache_write=s["cw1"] * PRICE["cw_1h"] + s["cw5"] * PRICE["cw_5m"], cost_input=s["input"] * PRICE["in"],
             max_context=max((c["context"] for c in calls), default=0))
    big = [c for c in calls if c["context"] > 30000 and c["cache_write"] >= 0.5 * c["context"]]
    s.update(resend_calls=len(big), resend_cache_write=sum(c["cache_write"] for c in big))
    return s


def excluded(td):
    """True when the researcher curation excludes the packet (curation_include_in_analysis: false), as for baseline E1-04/04R."""
    return any(re.match(r"^(e3dc_)?curation_include_in_analysis:\s*false", l) for l in open(f"{td}/manifest.yaml"))


def clio_trials(exp):
    """(trial, dir, [session dirs]) for every counted CLIO trial of `exp` that has records (curation-excluded packets are
    listed in trial_attempts.csv instead). Session dirs hold clio/ exports."""
    out = []
    for td in sorted(glob.glob(f"{TH}/runs/{EXPDIR[exp]}/clio/trial_*")):
        if excluded(td):
            continue
        t = td.rsplit("_", 1)[1]
        sess = sorted(d for d in glob.glob(f"{td}/logs/agent_sessions/*") + glob.glob(f"{td}/logs/session") if os.path.isdir(f"{d}/clio"))
        if sess:
            out.append((t, td, sess))
    return out


def clio_session_label(d):
    b = os.path.basename(d)
    return {"session_main": "main", "session": "main", "session_a": "A", "session_b": "B"}.get(b, b)


usage_rows, percall = [], {}
for exp, trials in BASE_TRIALS.items():
    for t in trials:
        if exp == "E3":
            groups = {"main": glob.glob(f"{TH}/runs/{EXPDIR[exp]}/baseline/trial_{BASE_E3_DIR.get(t, t)}/logs/session/transcript_*.jsonl")}
        elif exp == "E2":
            groups = {s.upper(): glob.glob(f"{TH}/runs/{EXPDIR[exp]}/baseline/trial_{t}/logs/agent_sessions/session_{s}/transcript_*.jsonl") for s in "ab"}
        else:
            groups = {"main": glob.glob(f"{TH}/runs/{EXPDIR[exp]}/baseline/trial_{t}/logs/agent_sessions/session_main/transcript_*.jsonl")}
        for sess, files in groups.items():
            calls = [c for f in files for c in transcript_calls(f)]
            if calls:
                usage_rows.append({"system": "baseline (Claude Code)", "arm": "baseline", "experiment": exp, "run": t, "session": sess, **summarize(calls)})
                percall[f"baseline:{exp}:{t}:{sess}"] = calls
for exp in EXPDIR:
    for t, td, sess_dirs in clio_trials(exp):
        for sd in sess_dirs:
            f = f"{sd}/clio/usage_per_call.csv"
            if not os.path.exists(f):
                continue
            calls = usage_csv_calls(f)
            usage_rows.append({"system": "CLIO (factorio-flat 0.5.0)", "arm": "clio", "experiment": exp, "run": t,
                               "session": clio_session_label(sd), **summarize(calls)})
            percall[f"clio:{exp}:{t}:{clio_session_label(sd)}"] = calls
ucols = ["system", "arm", "experiment", "run", "session", "api_calls", "input", "output", "cache_read", "cache_write", "cw1", "cw5", "max_context",
         "resend_calls", "resend_cache_write", "cost_output", "cost_cache_read", "cost_cache_write", "cost_input", "cost"]
with open(f"{HERE}/data/usage_by_run_session.csv", "w", newline="") as fh:
    fh.write(f"# {L}; baseline: Claude Code transcripts; CLIO: clio/usage_per_call.csv (CLIO provider's SDK transcripts); fable-5-1 list prices\n")
    w = csv.DictWriter(fh, fieldnames=ucols, extrasaction="ignore"); w.writeheader(); [w.writerow(r) for r in usage_rows]
with open(f"{HERE}/data/usage_per_call.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["key", "i", "utc", "input", "output", "cache_read", "cache_write", "context", "cost"])
    for k, cs in percall.items():
        for i, c in enumerate(cs):
            w.writerow([k, i, c["utc"], c["input"], c["output"], c["cache_read"], c["cache_write"], c["context"], round(c["cost"], 5)])

# ------------------------------------------------------------------ time breakdown (thesis_prelim categories)
CATS = ["Model reasoning & writing", "Reading inputs & manuals", "Authoring files", "Meshing (Cubit)",
        "Deck translation (XMLGenerator)", "Verification scripts", "Slurm submit & wait", "Records, copies & hashing"]
RULES = [("Meshing (Cubit)", r"(^|[;&|(]\s*|\n\s*|\btime\s+)cubit\s+-"),
         ("Deck translation (XMLGenerator)", r"(^|[;&|(]\s*|\n\s*|\btime\s+)XMLGenerator\s+\S"),
         ("Slurm submit & wait", r"wait_job\.sh|\bsbatch\b|\bsqueue\b|\bsacct\b|\bscontrol\b|\bsleep\b|\bscancel\b"),
         ("Verification scripts", r"\bpython3?\b"),
         ("Authoring files", r"cat\s*>|cat\s*<<|\btee\b|sed\s+-i|printf[^|]*>|>\s*\S+\.(i|jou|sbatch|md|py|sh)\b"),
         ("Reading inputs & manuals", r"\bsed\s+-n\b|\bgrep\b|\bpdftotext\b|\bcat\b|\bhead\b|\btail\b|\bfind\b|\bls\b|\bwc\b"),
         ("Records, copies & hashing", r"\bsha256sum\b|\bcp\b|\bmkdir\b|\bmv\b|\bdate\b")]
TOOLMAP = {"shell_bash": "Bash", "fs_read_file": "Read", "fs_write_file": "Write", "fs_edit_file": "Edit"}


def classify(cmd):
    body = re.sub(r"^\s*cd\s+\S+\s*(&&|;)\s*", "", cmd or "")
    for cat, rx in RULES:
        if re.search(rx, body):
            return cat
    return "Records, copies & hashing"


def breakdown(cdir):
    trace = json.load(open(f"{cdir}/trace.json"))["events"]
    mj = json.load(open(f"{cdir}/messages.json")); msgs = mj["messages"] if isinstance(mj, dict) else mj
    calls = {p["call_id"]: p for m in msgs for p in m.get("parts", []) if p.get("type") == "tool_call"}
    s0 = min(U(e["occurred_at"]) for e in trace if e["event_type"] == "turn.started")
    s1 = max(U(e["occurred_at"]) for e in trace if e["event_type"] in ("turn.completed", "turn.failed"))
    iv = {}
    for e in trace:
        cid = (e.get("payload") or {}).get("call_id")
        if cid and e["event_type"] in ("tool.call.started", "tool.call.completed"):
            iv.setdefault(cid, {})[e["event_type"]] = U(e["occurred_at"])
    tools = []
    for cid, d in iv.items():
        p = calls.get(cid)
        name = TOOLMAP.get(p["tool_name"], p["tool_name"]) if p else None
        cmd = (p or {}).get("input", {}).get("command", "") if p else ""
        cat = classify(cmd) if name == "Bash" else ("Reading inputs & manuals" if name == "Read" else "Authoring files" if name in ("Write", "Edit") else "Records, copies & hashing")
        tools.append((max(d.get("tool.call.started", s0), s0), min(d.get("tool.call.completed", s1), s1), cat))
    prio = {c: i for i, (c, _) in enumerate(RULES)}
    cuts = sorted({s0, s1, *[t[0] for t in tools], *[t[1] for t in tools]})
    tot = {c: 0.0 for c in CATS}
    for a, b in zip(cuts[:-1], cuts[1:]):
        if b <= a:
            continue
        cov = [t[2] for t in tools if t[0] <= a and t[1] >= b]
        tot[min(cov, key=lambda c: prio.get(c, 99)) if cov else "Model reasoning & writing"] += (b - a).total_seconds()
    return (s1 - s0).total_seconds(), tot


trows = []
for r in csv.DictReader(open(f"{COMB}/time_breakdown_by_session.csv")):
    trows.append({"system": "baseline (Claude Code)", "arm": "baseline", "experiment": r["experiment"], "run": r["trial"], "session": r["session"] or "main",
                  "wall_s": float(r["wall_s"]), **{c: float(r[c]) for c in CATS}})
for exp in EXPDIR:
    for t, td, sess_dirs in clio_trials(exp):
        for sd in sess_dirs:
            if not os.path.exists(f"{sd}/clio/trace.json"):
                continue
            wall, tot = breakdown(f"{sd}/clio")
            trows.append({"system": "CLIO (factorio-flat 0.5.0)", "arm": "clio", "experiment": exp, "run": t, "session": clio_session_label(sd),
                          "wall_s": round(wall, 1), **{c: round(v, 1) for c, v in tot.items()}})
NON = [c for c in CATS if c != "Slurm submit & wait"]
for r in trows:
    r["non_slurm_s"] = round(sum(r[c] for c in NON), 1)
with open(f"{HERE}/data/time_breakdown_by_run_session.csv", "w", newline="") as fh:
    fh.write(f"# {L}; thesis_prelim categories; baseline rows copied from {COMB}/time_breakdown_by_session.csv\n")
    w = csv.DictWriter(fh, fieldnames=["system", "arm", "experiment", "run", "session", "wall_s"] + CATS + ["non_slurm_s"]); w.writeheader(); [w.writerow(r) for r in trows]


# ------------------------------------------------------------------ Morphorm jobs (sacct records in each trial)
def hms(x):
    p = [int(v) for v in x.split("-")[-1].split(":")]
    return (p[0] * 3600 + p[1] * 60 + p[2]) if len(p) == 3 else 0


def sacct_jobs(files):
    out = []
    for f in files:
        lines = [l.rstrip("\n").split("|") for l in open(f) if "|" in l]
        hdr = lines[0] if lines and lines[0][0] == "JobID" else None
        for x in lines[1:] if hdr else lines:
            if not re.fullmatch(r"\d+", x[0]) or re.search(r"agent|host|^clio_|^e3-clio-trial_\d+$|fable-check", x[1], re.I):
                continue
            out.append({"job": x[0], "name": x[1], "state": x[hdr.index("State")] if hdr else x[2],
                        "elapsed_s": hms(x[hdr.index("Elapsed")] if hdr else x[7]), "node": x[hdr.index("NodeList")] if hdr else x[-1]})
    return out


mrows = []
for exp in EXPDIR:
    for arm in ("baseline", "clio"):
        trials = BASE_TRIALS[exp] if arm == "baseline" else [t for t, _, _ in clio_trials(exp)]
        for t in trials:
            d = f"{TH}/runs/{EXPDIR[exp]}/{arm}/trial_{BASE_E3_DIR.get(t, t) if (arm, exp) == ('baseline', 'E3') else t}"
            files = glob.glob(f"{d}/jobs/sacct_*.txt") if exp == "E3" else glob.glob(f"{d}/logs/slurm_sacct.psv")
            seen = set()
            for j in sacct_jobs(files):
                if j["job"] in seen:
                    continue
                seen.add(j["job"]); mrows.append({"experiment": exp, "arm": arm, "run": t, **j})
with open(f"{HERE}/data/agent_morphorm_jobs.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["experiment", "arm", "run", "job", "name", "state", "elapsed_s", "node"]); w.writeheader(); w.writerows(mrows)

# ------------------------------------------------------------------ outcomes (thesis scorer decisions, both arms)
orows = []
for exp in EXPDIR:
    for arm in ("baseline", "clio"):
        trials = BASE_TRIALS[exp] if arm == "baseline" else [t for t, _, _ in clio_trials(exp)]
        for t in trials:
            sd = f"{SC}/E3-{arm}-{t}" if exp == "E3" else f"{SC}/{RUNID[exp]}-{arm}-{t}"
            f = next((x for x in (f"{sd}/score_with_override.json", f"{sd}/score.json") if os.path.exists(x)), None)  # researcher overrides (RESEARCHER_DECISIONS.md) win
            js = json.load(open(f)) if f else {}
            dec = ((js.get("override") or js.get("researcher_override") or {}).get("decision") or js.get("decision")) if f else "unscored"
            orows.append({"experiment": exp, "arm": arm, "run": t, "outcome": dec, "score_dir": sd})
with open(f"{HERE}/data/outcomes_by_run.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["experiment", "arm", "run", "outcome", "score_dir"]); w.writeheader(); w.writerows(orows)
print({k: v for k, v in collections.Counter(f"{r['experiment']} {r['arm']} {r['outcome']}" for r in orows).items()})

# ------------------------------------------------------------------ CLIO trial attempts that did not count (status from each manifest)
arows = []
for exp in EXPDIR:
    for td in sorted(glob.glob(f"{TH}/runs/{EXPDIR[exp]}/clio/trial_*")):
        st = next((l.split(":", 1)[1].strip() for l in open(f"{td}/manifest.yaml") if re.match(r"^(e3dc_)?status:", l)), "?")
        if excluded(td) or st not in ("planned", "running", "completed_unscored", "awaiting_scoring", "scored"):
            note = next((l.split(":", 1)[1].strip().strip('"') for l in open(f"{td}/manifest.yaml") if re.match(r"^(e3dc_)?(curation_notes|invalid_reason|notes):\s*\S", l) and "null" not in l.split(":", 1)[1]), "")
            arows.append({"experiment": exp, "attempt": os.path.basename(td), "status": st, "note": note})
with open(f"{HERE}/data/trial_attempts.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["experiment", "attempt", "status", "note"]); w.writeheader(); w.writerows(arows)
