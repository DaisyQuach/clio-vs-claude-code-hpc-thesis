#!/usr/bin/env python3
"""Build the preliminary thesis dataset for the controlled E1/E2 baseline trials (researcher-only).

Reads only finished trial packets, session evidence, scores and reference histories; writes CSV/JSON
under ../data/.  Re-runnable; overwrites only its own outputs.
Usage: python3 build_dataset.py
"""
import csv, glob, json, os, re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

T = "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(OUT, exist_ok=True)
DENVER = ZoneInfo("America/Denver")  # sacct prints local time

EXPS = {
    "E1": {"dir": "E1_uninterrupted_example8", "sessions": ["session_main"],
           "ref": [f"{T}/researcher_only/ground_truth/example_8/reference_case/results/ex8_symmetry_honored_variant_criterion_history.csv"]},
    "E2": {"dir": "E2_interrupted_recovery_example16", "sessions": ["session_a", "session_b"],
           "ref": [f"{T}/researcher_only/ground_truth/example_16/reference_case/results/ex16_stage1_criterion_history.csv",
                   f"{T}/researcher_only/ground_truth/example_16/reference_case/results/ex16_restart_corrected_21_criterion_history.csv"]},
}
# category order = fixed palette slot order (adjacent pairs validated); priority for classification is separate
CATEGORIES = ["Model reasoning & writing", "Reading inputs & manuals", "Authoring files", "Meshing (Cubit)",
              "Deck translation (XMLGenerator)", "Verification scripts", "Slurm submit & wait", "Records, copies & hashing"]
RULES = [  # (category, regex) in priority order for a command
    ("Meshing (Cubit)", r"(^|[;&|(]\s*|\n\s*|\btime\s+)cubit\s+-"),
    ("Deck translation (XMLGenerator)", r"(^|[;&|(]\s*|\n\s*|\btime\s+)XMLGenerator\s+\S"),
    ("Slurm submit & wait", r"\bsbatch\b|\bsqueue\b|\bsacct\b|\bscontrol\b|\bsleep\b|\bscancel\b"),
    ("Verification scripts", r"\bpython3?\b"),
    ("Authoring files", r"cat\s*>|cat\s*<<|\btee\b|sed\s+-i|printf[^|]*>|>\s*\S+\.(i|jou|sbatch|md|py|sh)\b"),
    ("Reading inputs & manuals", r"\bsed\s+-n\b|\bgrep\b|\bpdftotext\b|\bcat\b|\bhead\b|\btail\b|\bfind\b|\bls\b|\bwc\b"),
    ("Records, copies & hashing", r"\bsha256sum\b|\bcp\b|\bmkdir\b|\bmv\b|\bdate\b"),
]

def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)

def local_ts(s):
    if not s or s in ("Unknown", "None"):
        return None
    return datetime.fromisoformat(s).replace(tzinfo=DENVER).astimezone(timezone.utc)

def classify(cmd):
    body = re.sub(r"^\s*cd\s+\S+\s*(&&|;)\s*", "", cmd or "")
    for cat, rx in RULES:
        if re.search(rx, body):
            return cat
    return "Records, copies & hashing"

def manifest(path):
    d = {}
    for line in open(path):
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            d[m.group(1)] = m.group(2).strip().strip('"')
    return d

def diag(path):
    rows = []
    for line in open(path):
        p = line.split()
        if p and p[0].isdigit():
            rows.append((int(p[0]), float(p[2]), float(p[4])))
    return rows

def sacct_rows(path):
    rows = {}
    if not os.path.isfile(path):
        return rows
    lines = open(path).read().splitlines()
    hdr = lines[0].split("|")
    for l in lines[1:]:
        f = dict(zip(hdr, l.split("|")))
        if re.fullmatch(r"\d+", f.get("JobID", "")):
            rows[f["JobID"]] = f
    return rows

def session_breakdown(sdir):
    rec = json.load(open(f"{sdir}/session_record.json"))
    s0, s1 = ts(rec["start_utc"]), ts(rec["end_utc"])
    tr = glob.glob(f"{sdir}/transcript_*.jsonl")[0]
    starts, ends = {}, {}
    for line in open(tr):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = e.get("message") or {}
        cont = msg.get("content") if isinstance(msg.get("content"), list) else []
        for b in cont:
            if b.get("type") == "tool_use":
                starts[b["id"]] = (ts(e["timestamp"]), b.get("name"), (b.get("input") or {}).get("command", ""))
            elif b.get("type") == "tool_result":
                ends[b.get("tool_use_id")] = ts(e["timestamp"])
    tools = []
    for tid, (t0, name, cmd) in starts.items():
        t1 = ends.get(tid, s1)
        cat = classify(cmd) if name == "Bash" else ("Reading inputs & manuals" if name == "Read" else "Authoring files" if name in ("Write", "Edit") else "Records, copies & hashing")
        tools.append((max(t0, s0), min(t1, s1), cat, cmd[:200]))
    # sweep: each elementary interval gets the highest-priority covering tool category, else model time
    prio = {c: i for i, (c, _) in enumerate(RULES)}
    prio["Authoring files"] = prio.get("Authoring files", 50)
    cuts = sorted({s0, s1, *[t[0] for t in tools], *[t[1] for t in tools]})
    totals = {c: 0.0 for c in CATEGORIES}
    segments = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        if b <= a:
            continue
        cov = [t[2] for t in tools if t[0] <= a and t[1] >= b]
        cat = min(cov, key=lambda c: prio.get(c, 99)) if cov else "Model reasoning & writing"
        dur = (b - a).total_seconds()
        totals[cat] += dur
        if segments and segments[-1][2] == cat and segments[-1][1] == a:
            segments[-1] = (segments[-1][0], b, cat)
        else:
            segments.append((a, b, cat))
    res = {}
    for l in open(f"{sdir}/stream.jsonl"):
        if '"type":"result"' in l.replace(" ", ""):
            try:
                res = json.loads(l)
            except json.JSONDecodeError:
                pass
    return rec, s0, s1, totals, segments, tools, res

trials, breakdown, hist_rows, gantt = [], [], [], []
for exp, cfg in EXPS.items():
    base = f"{T}/runs/{cfg['dir']}/baseline"
    for td in sorted(glob.glob(f"{base}/trial_*")):
        m = manifest(f"{td}/manifest.yaml")
        rid = m["run_id"]
        counted = m.get("scoring_decision") == "accepted" and m.get("curation_include_in_analysis") != "false"
        excluded = m.get("curation_include_in_analysis") == "false"
        row = {"experiment": exp, "run_id": rid, "trial_dir": os.path.relpath(td, T), "status": m.get("status"),
               "scoring_decision": m.get("scoring_decision"), "counted": counted, "excluded": excluded,
               "curation_notes": m.get("curation_notes", "")}
        sc_path = f"{T}/researcher_only/scores/{rid}/score_with_override.json"
        if not os.path.isfile(sc_path):
            sc_path = f"{T}/researcher_only/scores/{rid}/score.json"
        if counted and os.path.isfile(sc_path):
            ms = json.load(open(sc_path))["measured"]
            if exp == "E1":
                row["final_compliance_rel_diff_vs_ref"] = ms.get("matched_final_rel_diff")
                row["final_density_max_abs_diff_vs_ref"] = ms["reference_comparison"][ms["matched_variant"]]["final_topology"].get("max_abs_diff")
                row["generated_config_checks"] = ms["generated_config"].get("summary")
            else:
                row["final_compliance_rel_diff_vs_ref"] = ms["stage2_history_vs_reference"].get("final_rel_diff_compliance")
                row["final_density_max_abs_diff_vs_ref"] = ms["stage2_final_topology_vs_reference"].get("max_abs_diff")
                row["resumed_from_stage1_iteration"] = ms["continuation"]["matched_stage1_iteration"]
                row["restart_compliance_abs_diff"] = ms["continuation"]["compliance_abs_diff_at_match"]
        sac = sacct_rows(f"{td}/logs/slurm_sacct.psv")
        wf_ids = sorted(set(re.findall(r"\b\d{6,}\b", open(f"{td}/jobs/job_ids.txt").read()))) if os.path.isfile(f"{td}/jobs/job_ids.txt") else []
        tot_wall = tot_api = tot_turns = tot_out = tot_cost = 0.0
        for s in cfg["sessions"]:
            sdir = f"{td}/logs/agent_sessions/{s}"
            if not os.path.isfile(f"{sdir}/session_record.json"):
                continue
            rec, s0, s1, totals, segments, tools, res = session_breakdown(sdir)
            wall = (s1 - s0).total_seconds()
            tot_wall += wall; tot_api += res.get("duration_api_ms", 0) / 1000; tot_turns += res.get("num_turns", 0)
            tot_out += (res.get("usage") or {}).get("output_tokens", 0); tot_cost += res.get("total_cost_usd", 0) or 0
            row[f"{s}_wall_s"] = wall; row[f"{s}_tool_calls"] = len(tools); row[f"{s}_turns"] = res.get("num_turns")
            row[f"{s}_api_s"] = res.get("duration_api_ms", 0) / 1000
            if counted:
                b = {"experiment": exp, "run_id": rid, "session": s, "wall_s": wall, "api_s_reported": res.get("duration_api_ms", 0) / 1000}
                b.update({c: round(v, 1) for c, v in totals.items()})
                # Slurm workflow jobs submitted during this session
                for j in wf_ids:
                    f = sac.get(j)
                    if not f:
                        continue
                    sub, st, en = local_ts(f["Submit"]), local_ts(f["Start"]), local_ts(f["End"])
                    if sub and s0 <= sub <= s1:
                        b.setdefault("slurm_jobs", []).append(j)
                        b["slurm_queue_s"] = b.get("slurm_queue_s", 0) + (st - sub).total_seconds()
                        b["slurm_run_s"] = b.get("slurm_run_s", 0) + (en - st).total_seconds()
                        gantt.append({"experiment": exp, "run_id": rid, "session": s, "category": "Slurm queue", "start_utc": sub.isoformat(), "end_utc": st.isoformat()})
                        gantt.append({"experiment": exp, "run_id": rid, "session": s, "category": "Slurm run", "start_utc": st.isoformat(), "end_utc": en.isoformat()})
                b["slurm_jobs"] = ";".join(b.get("slurm_jobs", []))
                breakdown.append(b)
                for a, z, c in segments:
                    gantt.append({"experiment": exp, "run_id": rid, "session": s, "category": c, "start_utc": a.isoformat(), "end_utc": z.isoformat()})
        row.update({"agent_wall_s_total": tot_wall, "agent_api_s_total": tot_api, "agent_turns_total": tot_turns,
                    "output_tokens_total": tot_out, "reported_cost_usd_total": round(tot_cost, 4)})
        trials.append(row)
        if counted:
            if exp == "E1":
                for it, F, H in diag(f"{td}/outputs/morphorm_oc_optimizer_diagnostics.txt"):
                    hist_rows.append({"experiment": exp, "series": rid, "global_iteration": it, "compliance": F, "volume_H1": H})
            else:
                for it, F, H in diag(f"{td}/outputs/stage1/morphorm_oc_optimizer_diagnostics.txt"):
                    hist_rows.append({"experiment": exp, "series": rid, "global_iteration": it, "compliance": F, "volume_H1": H})
                for it, F, H in diag(f"{td}/outputs/stage2/morphorm_oc_optimizer_diagnostics.txt"):
                    hist_rows.append({"experiment": exp, "series": rid, "global_iteration": 20 + it, "compliance": F, "volume_H1": H})
    off = 0
    for i, rf in enumerate(cfg["ref"]):
        for r in csv.DictReader(open(rf)):
            hist_rows.append({"experiment": exp, "series": "reference", "global_iteration": int(r["iteration"]) + (20 if (exp == "E2" and i == 1) else 0),
                              "compliance": float(r["compliance_F"]), "volume_H1": float(r["volume_constraint_H1"])})

def write(name, rows):
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(os.path.join(OUT, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    print(f"wrote {name}: {len(rows)} rows")

write("trials.csv", trials)
write("time_breakdown_by_session.csv", breakdown)
write("compliance_histories.csv", hist_rows)
write("gantt_segments.csv", gantt)
json.dump({"categories": CATEGORIES, "classification_rules_priority": RULES,
           "notes": ["Tool intervals = tool_use timestamp to tool_result timestamp from the session transcript.",
                     "Overlapping parallel tool calls are assigned once, to the highest-priority category.",
                     "Uncovered session time = model reasoning & writing (cross-check: api_s_reported).",
                     "sacct times are America/Denver local and converted to UTC.",
                     "Slurm run time overlaps agent 'Slurm submit & wait' time; it is a parallel lane, not additive."]},
          open(os.path.join(OUT, "method_notes.json"), "w"), indent=2)
