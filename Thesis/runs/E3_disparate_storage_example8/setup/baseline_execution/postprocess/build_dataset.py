#!/usr/bin/env python3
"""Build the preliminary E3 baseline-only dataset (researcher-side; same method as the E1/E2 thesis_prelim builder).

Reads finished trial records (read-only), the raw collection made by collect_raw.sh, and the E1 symmetry-honored
reference history (researcher-only, read-only). Writes CSV/JSON/Markdown under <out>/data and <out>/tables.
All five trials are always listed; scientific series are built only for trials whose terminal state is 'valid'.
Usage: python3 -I build_dataset.py --e3-root <E3> --raw <out>/raw --out <out>
"""
import argparse, csv, glob, json, os, re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ap = argparse.ArgumentParser()
ap.add_argument("--e3-root", required=True); ap.add_argument("--raw", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--reference-history", default="/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/ground_truth/example_8/"
                "reference_case/results/ex8_symmetry_honored_variant_criterion_history.csv")
a = ap.parse_args()
E3, RAW, OUT = a.e3_root, a.raw, a.out
DATA, TAB = os.path.join(OUT, "data"), os.path.join(OUT, "tables")
os.makedirs(DATA, exist_ok=True); os.makedirs(TAB, exist_ok=True)
DENVER = ZoneInfo("America/Denver")  # sacct prints local time
TRIALS = ["01", "02", "03", "04", "05"]

# ---- E1/E2 activity classification (identical rules and priority to thesis_prelim/analysis/build_dataset.py) ----
CATEGORIES = ["Model reasoning & writing", "Reading inputs & manuals", "Authoring files", "Meshing (Cubit)",
              "Deck translation (XMLGenerator)", "Verification scripts", "Slurm submit & wait", "Records, copies & hashing"]
RULES = [
    ("Meshing (Cubit)", r"(^|[;&|(]\s*|\n\s*|\btime\s+)cubit\s+-"),
    ("Deck translation (XMLGenerator)", r"(^|[;&|(]\s*|\n\s*|\btime\s+)XMLGenerator\s+\S"),
    ("Slurm submit & wait", r"\bsbatch\b|\bsqueue\b|\bsacct\b|\bscontrol\b|\bsleep\b|\bscancel\b"),
    ("Verification scripts", r"\bpython3?\b"),
    ("Authoring files", r"cat\s*>|cat\s*<<|\btee\b|sed\s+-i|printf[^|]*>|>\s*\S+\.(i|jou|sbatch|md|py|sh)\b"),
    ("Reading inputs & manuals", r"\bsed\s+-n\b|\bgrep\b|\bpdftotext\b|\bcat\b|\bhead\b|\btail\b|\bfind\b|\bls\b|\bwc\b"),
    ("Records, copies & hashing", r"\bsha256sum\b|\bcp\b|\bmkdir\b|\bmv\b|\bdate\b"),
]
# E3 addition (reported separately so E1 categories stay comparable): Globus/staging commands
GLOBUS_RX = r"\bglobus\b|globus_stage_file\.sh|stage_file\.sh"

def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)

def local_ts(s):
    if not s or s in ("Unknown", "None", ""):
        return None
    return datetime.fromisoformat(s).replace(tzinfo=DENVER).astimezone(timezone.utc)

def classify(cmd):
    body = re.sub(r"^\s*cd\s+\S+\s*(&&|;)\s*", "", cmd or "")
    for cat, rx in RULES:
        if re.search(rx, body):
            return cat
    return "Records, copies & hashing"

def jload(p, default=None):
    try:
        return json.load(open(p))
    except Exception:
        return default

def manifest(p):
    d = {}
    if os.path.isfile(p):
        for line in open(p):
            m = re.match(r"^(\w+):\s*(.*?)\s*(#.*)?$", line)
            if m:
                d[m.group(1)] = m.group(2).strip().strip('"')
    return d

def kv_file(p):
    d = {}
    if os.path.isfile(p):
        for line in open(p):
            m = re.match(r"^([\w.]+):\s*(.*)$", line)
            if m:
                d[m.group(1)] = m.group(2).strip()
    return d

def tsv(p):
    return list(csv.DictReader(open(p), delimiter="\t")) if os.path.isfile(p) and os.path.getsize(p) else []

def psv(p):
    if not os.path.isfile(p):
        return []
    lines = [l for l in open(p).read().splitlines() if l.strip()]
    if not lines or "|" not in lines[0]:
        return []
    hdr = lines[0].split("|")
    return [dict(zip(hdr, l.split("|"))) for l in lines[1:]]

def dur_s(s):  # sacct [D-]HH:MM:SS[.mmm] or MM:SS.mmm
    if not s:
        return None
    d = 0
    if "-" in s:
        dd, s = s.split("-", 1); d = int(dd)
    parts = [float(x) for x in s.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    return d * 86400 + parts[0] * 3600 + parts[1] * 60 + parts[2]

def mem_mb(s):
    if not s:
        return None
    m = re.match(r"^([\d.]+)([KMGT]?)", s)
    if not m:
        return None
    return float(m.group(1)) * {"": 1 / 1048576, "K": 1 / 1024, "M": 1, "G": 1024, "T": 1048576}[m.group(2)]

def diag(path):
    rows = []
    if os.path.isfile(path):
        for line in open(path):
            p = line.split()
            if p and p[0].isdigit() and len(p) >= 5:
                rows.append((int(p[0]), float(p[2]), float(p[4])))
    return rows

def session_breakdown(sdir):
    """E1/E2 method: tool intervals from transcript timestamps; uncovered time = model reasoning & writing."""
    rec = jload(f"{sdir}/session_record.json") or {}
    trs = glob.glob(f"{sdir}/transcript_*.jsonl")
    if not rec.get("start_utc") or not rec.get("end_utc") or not trs:
        return None
    s0, s1 = ts(rec["start_utc"]), ts(rec["end_utc"])
    starts, ends = {}, {}
    for line in open(trs[0]):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = e.get("message") or {}
        cont = msg.get("content") if isinstance(msg.get("content"), list) else []
        for b in cont:
            if b.get("type") == "tool_use":
                starts[b["id"]] = (ts(e["timestamp"]), b.get("name"), (b.get("input") or {}).get("command", "") or "")
            elif b.get("type") == "tool_result":
                ends[b.get("tool_use_id")] = ts(e["timestamp"])
    tools, globus_s = [], 0.0
    for tid, (t0, name, cmd) in starts.items():
        t1 = ends.get(tid, s1)
        cat = classify(cmd) if name == "Bash" else ("Reading inputs & manuals" if name == "Read" else "Authoring files" if name in ("Write", "Edit") else "Records, copies & hashing")
        tools.append((max(t0, s0), min(t1, s1), cat, cmd[:200]))
        if name == "Bash" and re.search(GLOBUS_RX, cmd):
            globus_s += max(0.0, (min(t1, s1) - max(t0, s0)).total_seconds())
    prio = {c: i for i, (c, _) in enumerate(RULES)}
    cuts = sorted({s0, s1, *[t[0] for t in tools], *[t[1] for t in tools]})
    totals = {c: 0.0 for c in CATEGORIES}
    segments = []
    for x, y in zip(cuts[:-1], cuts[1:]):
        if y <= x:
            continue
        cov = [t[2] for t in tools if t[0] <= x and t[1] >= y]
        cat = min(cov, key=lambda c: prio.get(c, 99)) if cov else "Model reasoning & writing"
        totals[cat] += (y - x).total_seconds()
        if segments and segments[-1][2] == cat and segments[-1][1] == x:
            segments[-1] = (segments[-1][0], y, cat)
        else:
            segments.append((x, y, cat))
    return {"s0": s0, "s1": s1, "totals": totals, "segments": segments, "n_tools": len(tools), "globus_tool_s": globus_s}

sub = {r["label"]: r for r in tsv(os.path.join(RAW, "submission_manifest.tsv"))}
sac = psv(os.path.join(RAW, "slurm", "sacct_trial_jobs.psv"))
wfs = psv(os.path.join(RAW, "slurm", "sacct_workflow_jobs.psv"))
wfx = psv(os.path.join(RAW, "slurm", "sacct_workflow_jobs_X.psv"))
ref_hist = []
if os.path.isfile(a.reference_history):
    for r in csv.DictReader(open(a.reference_history)):
        ref_hist.append((int(r["iteration"]), float(r["compliance_F"]), float(r["volume_constraint_H1"])))

def job_acct(jid, rows):
    alloc = next((r for r in rows if r.get("JobID") == jid), None)
    steps = [r for r in rows if r.get("JobID", "").startswith(jid + ".")]
    rss = [mem_mb(r.get("MaxRSS")) for r in steps if mem_mb(r.get("MaxRSS"))]
    return alloc, steps, (max(rss) if rss else None)

trials, prov, breakdown, gantt, timeline, hist, wf_rows = [], [], [], [], [], [], []
for n in TRIALS:
    td = f"{E3}/baseline/trial_{n}"; rd = f"{RAW}/trials/trial_{n}"; ex = f"{RAW}/execution/trial_{n}"
    m = manifest(f"{td}/manifest.yaml")
    st = jload(f"{td}/TRIAL_STATUS.json") or jload(f"{ex}/trial_end_record.json") or {}
    ns = jload(f"{ex}/not_started_record.json") or {}
    sr = jload(f"{ex}/trial_start_record.json") or {}
    srec = jload(f"{td}/logs/session/session_record.json") or {}
    lp = jload(f"{td}/logs/session/launch_plan.json") or {}
    met = jload(f"{td}/provenance/metrics.json") or {}
    res = jload(f"{td}/logs/session/result.json") or {}
    jid = (sub.get(f"trial_{n}") or {}).get("slurm_job_id", "")
    alloc, steps, peak = job_acct(jid, sac)
    state = st.get("terminal_state") or ns.get("terminal_state") or ("no_record" if alloc else "not_run")
    sub_t, start_t, end_t = (local_ts(alloc.get(k)) if alloc else None for k in ("Submit", "Start", "End"))
    elig_t = local_ts(alloc.get("Eligible")) if alloc else None
    staged = tsv(f"{td}/staging-manifest/staged_files.tsv"); gx = tsv(f"{td}/staging-manifest/globus_transfers.tsv")
    returned = tsv(f"{td}/staging-manifest/returned_files.tsv")
    gx_s = sum((ts(r["utc_finished"]) - ts(r["utc_submitted"])).total_seconds() for r in gx if r.get("utc_finished") and r.get("utc_submitted"))
    nlf = kv_file(f"{td}/staging-manifest/node_local_final_summary.txt")
    usage = res.get("usage") or {}
    bd = session_breakdown(f"{td}/logs/session")
    # agent workflow jobs (WorkDir inside this trial)
    my_wf = [r for r in wfx if r.get("WorkDir", "").startswith(td)]
    wf_run = sum((dur_s(r.get("Elapsed")) or 0) for r in my_wf)
    wf_cpu = sum((dur_s((job_acct(r["JobID"], wfs)[0] or {}).get("TotalCPU")) or 0) for r in my_wf)  # -X rows report 0; use the full export
    for r in my_wf:
        _, _, wpeak = job_acct(r["JobID"], wfs)
        wf_rows.append({"trial": n, "job_id": r["JobID"], "name": r.get("JobName"), "state": r.get("State"), "exit": r.get("ExitCode"),
                        "submit_utc": local_ts(r.get("Submit")).isoformat() if local_ts(r.get("Submit")) else "",
                        "start_utc": local_ts(r.get("Start")).isoformat() if local_ts(r.get("Start")) else "",
                        "end_utc": local_ts(r.get("End")).isoformat() if local_ts(r.get("End")) else "",
                        "elapsed_s": dur_s(r.get("Elapsed")), "total_cpu_s": dur_s((job_acct(r["JobID"], wfs)[0] or {}).get("TotalCPU")), "peak_rss_mb": wpeak,
                        "alloc_cpus": r.get("AllocCPUS"), "nodes": r.get("NodeList")})
    hrows = diag(f"{td}/outputs/morphorm_oc_optimizer_diagnostics.txt")
    row = {"trial": n, "run_id": f"E3-baseline-trial_{n}", "slurm_job_id": jid, "terminal_state": state,
           "reason": st.get("reason") or ns.get("reason", ""), "counted_preliminary": state == "valid",
           "node": (alloc or {}).get("NodeList", ""), "slurm_state": (alloc or {}).get("State", ""), "slurm_exit": (alloc or {}).get("ExitCode", ""),
           "submit_utc": sub_t.isoformat() if sub_t else "", "eligible_utc": elig_t.isoformat() if elig_t else "",
           "start_utc": start_t.isoformat() if start_t else "", "end_utc": end_t.isoformat() if end_t else "",
           "queue_wait_after_eligible_s": (start_t - elig_t).total_seconds() if start_t and elig_t else None,
           "job_elapsed_s": dur_s((alloc or {}).get("Elapsed")), "job_timelimit_min": (alloc or {}).get("TimelimitRaw"),
           "alloc_cpus": (alloc or {}).get("AllocCPUS"), "req_mem": (alloc or {}).get("ReqMem"),
           "job_total_cpu_s": dur_s((alloc or {}).get("TotalCPU")), "job_peak_rss_mb": round(peak, 1) if peak else None,
           "session_exit": srec.get("exit_code"), "session_timeout_hit": srec.get("timeout_hit"),
           "session_wall_s": (bd["s1"] - bd["s0"]).total_seconds() if bd else ((met.get("session") or {}).get("duration_ms") or 0) / 1000 or None,
           "session_api_s": (res.get("duration_api_ms") or 0) / 1000 or None, "turns": res.get("num_turns"),
           "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
           "cache_read_tokens": usage.get("cache_read_input_tokens"), "cache_creation_tokens": usage.get("cache_creation_input_tokens"),
           "reported_cost_usd": res.get("total_cost_usd"), "tool_calls": bd["n_tools"] if bd else None,
           "bash_commands_with_error": met.get("bash_commands_with_error"),
           "files_staged": len(staged), "bytes_staged": sum(int(r.get("bytes") or 0) for r in staged),
           "files_staged_private_source_via_globus": sum(1 for r in staged if r.get("collection_alias") == "e3-private-source"),
           "files_staged_candidate_archive": sum(1 for r in staged if r.get("collection_alias") == "e3-chpc-candidate-archive"),
           "files_staged_control": sum(1 for r in staged if r.get("collection_alias") == "e3-control"),
           "globus_transfers": len(gx), "globus_bytes": sum(int(r.get("bytes") or 0) for r in gx),
           "globus_transfer_wall_s": round(gx_s, 1), "globus_failed_transfers": sum(1 for r in gx if r.get("status") != "SUCCEEDED"),
           "agent_globus_tool_time_s": round(bd["globus_tool_s"], 1) if bd else None,
           "files_returned": len(returned), "bytes_returned": sum(int(r.get("bytes") or 0) for r in returned),
           "node_local_final_files": nlf.get("files"), "node_local_final_bytes": nlf.get("bytes"),
           "boundary_audit": st.get("boundary_audit") or m.get("e3dc_boundary_audit"), "completed_verification": st.get("completed_verification"),
           "sources_unchanged": m.get("e3dc_sources_unchanged"), "action_required": st.get("action_required_codes", ""),
           "workflow_jobs": ";".join(r["JobID"] for r in my_wf), "workflow_run_s": wf_run or None, "workflow_cpu_s": wf_cpu or None,
           "final_iteration": hrows[-1][0] if hrows else None, "final_compliance": hrows[-1][1] if hrows else None,
           "manifest_status": m.get("e3dc_status")}
    trials.append(row)
    prep = kv_file(f"{td}/provenance/preparation.txt")
    ai = f"{td}/provenance/agent_inputs.sha256"
    env_mods = ""
    es = f"{ex}/environment_snapshot.txt"
    if os.path.isfile(es):
        lines = open(es).read().splitlines()
        if "# module list" in lines:
            i = lines.index("# module list"); mods = []
            for l in lines[i + 1:]:
                if l.startswith("#"):
                    break
                mods.append(l.strip())
            env_mods = " ".join(x for x in mods if x)
    prov.append({"trial": n, "slurm_job_id": jid, "node": sr.get("node", ""), "terminal_state": state,
                 "packet_files": prep.get("agent_inputs_files", ""),
                 "packet_hash_list_sha256": __import__("hashlib").sha256(open(ai, "rb").read()).hexdigest() if os.path.isfile(ai) else "",
                 "control_commit": prep.get("control_commit", "") or sr.get("control_commit", ""),
                 "prompt_sha256": lp.get("prompt_sha256", "") or sr.get("prompt_sha256", ""),
                 "globus_source_collection": sr.get("globus_source_collection", ""), "globus_destination_collection": sr.get("globus_destination_collection", ""),
                 "source_manifest_sha256": sr.get("source_manifest_sha256", ""),
                 "claude_version": sr.get("claude_version", ""), "claude_sha256": sr.get("claude_sha256", ""), "model": sr.get("model", ""),
                 "reasoning_effort": sr.get("reasoning_effort", ""), "access_model": lp.get("access_model", ""),
                 "freeze_sha256": sr.get("freeze_sha256", ""), "job_body_sha256": sr.get("job_body_sha256", ""), "runner_sha256": sr.get("runner_sha256", ""),
                 "globus_cli": sr.get("globus_cli", ""), "python": sr.get("python", ""), "git": sr.get("git", ""),
                 "modules_at_job_start": env_mods, "node_local_tmpdir": sr.get("node_local_tmpdir", "")})
    # timeline lanes (absolute UTC)
    if sub_t and start_t:
        timeline.append({"trial": n, "lane": "Slurm queue / dependency wait", "start_utc": sub_t.isoformat(), "end_utc": start_t.isoformat()})
    if bd and start_t:
        timeline.append({"trial": n, "lane": "Job setup + preparation (pin clone, packet, checks)", "start_utc": start_t.isoformat(), "end_utc": bd["s0"].isoformat()})
        timeline.append({"trial": n, "lane": "Agent session", "start_utc": bd["s0"].isoformat(), "end_utc": bd["s1"].isoformat()})
        if end_t:
            timeline.append({"trial": n, "lane": "Records, audit, verification", "start_utc": bd["s1"].isoformat(), "end_utc": end_t.isoformat()})
    elif start_t and end_t:
        timeline.append({"trial": n, "lane": "Job (no agent session)", "start_utc": start_t.isoformat(), "end_utc": end_t.isoformat()})
    for r in my_wf:
        s, b, e = local_ts(r.get("Submit")), local_ts(r.get("Start")), local_ts(r.get("End"))
        if s and b and e:
            timeline.append({"trial": n, "lane": f"Workflow job {r['JobID']} (queue)", "start_utc": s.isoformat(), "end_utc": b.isoformat()})
            timeline.append({"trial": n, "lane": f"Workflow job {r['JobID']} (run)", "start_utc": b.isoformat(), "end_utc": e.isoformat()})
    if bd:
        b = {"trial": n, "terminal_state": state, "wall_s": (bd["s1"] - bd["s0"]).total_seconds(), "api_s_reported": row["session_api_s"]}
        b.update({c: round(v, 1) for c, v in bd["totals"].items()})
        b["globus_staging_tool_s (overlaps categories)"] = round(bd["globus_tool_s"], 1)
        q = r_ = 0.0
        for r in my_wf:
            s_, b_, e_ = local_ts(r.get("Submit")), local_ts(r.get("Start")), local_ts(r.get("End"))
            if s_ and b_ and e_ and bd["s0"] <= s_ <= bd["s1"]:
                q += (b_ - s_).total_seconds(); r_ += (e_ - b_).total_seconds()
                gantt.append({"trial": n, "category": "Slurm queue", "start_utc": s_.isoformat(), "end_utc": b_.isoformat()})
                gantt.append({"trial": n, "category": "Slurm run", "start_utc": b_.isoformat(), "end_utc": e_.isoformat()})
        b["slurm_queue_s"], b["slurm_run_s"] = q, r_
        breakdown.append(b)
        for x, y, c in bd["segments"]:
            gantt.append({"trial": n, "category": c, "start_utc": x.isoformat(), "end_utc": y.isoformat()})
    if state == "valid":
        for it, F, H in hrows:
            hist.append({"series": f"trial_{n}", "iteration": it, "compliance": F, "volume_H1": H})
for it, F, H in ref_hist:
    hist.append({"series": "E1 reference (symmetry-honored variant)", "iteration": it, "compliance": F, "volume_H1": H})

def write(name, rows):
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(os.path.join(DATA, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys or ["empty"]); w.writeheader(); w.writerows(rows)
    print(f"wrote {name}: {len(rows)} rows")

write("trials.csv", trials); write("provenance.csv", prov); write("time_breakdown_by_trial.csv", breakdown)
write("gantt_segments.csv", gantt); write("timeline_lanes.csv", timeline); write("compliance_histories.csv", hist); write("workflow_jobs.csv", wf_rows)
json.dump({"categories": CATEGORIES, "classification_rules_priority": RULES, "globus_rule_reported_separately": GLOBUS_RX,
           "notes": ["Same method as Thesis/researcher_only/evaluation_figures/thesis_prelim (E1/E2).",
                     "Tool intervals = tool_use timestamp to tool_result timestamp from the session transcript.",
                     "Overlapping parallel tool calls are assigned once, to the highest-priority category.",
                     "Uncovered session time = model reasoning & writing (cross-check: api_s_reported).",
                     "Globus/staging command time is reported separately and overlaps the E1 categories.",
                     "sacct times are America/Denver local and converted to UTC.",
                     "Queue wait is measured from Eligible (dependency satisfied) to Start; trials ran one at a time by design.",
                     "Scientific series only for terminal_state == valid; every trial is listed in trials.csv."]},
          open(os.path.join(DATA, "method_notes.json"), "w"), indent=2)

def fmt(v, nd=1):
    if v is None or v == "":
        return "–"
    if isinstance(v, float):
        return f"{v:,.{nd}f}"
    return str(v)

def mins(v):
    return fmt(v / 60 if isinstance(v, (int, float)) else None)

with open(os.path.join(TAB, "tables.md"), "w") as f:
    f.write("# E3 baseline — preliminary tables (generated by build_dataset.py)\n\n## 1. Trial status and validity\n\n")
    f.write("| Trial | Slurm job | Node | Terminal state | Counted (prelim.) | Session exit | Audit | Verification | Sources unchanged | Reason |\n|---|---|---|---|---|---|---|---|---|---|\n")
    for t in trials:
        f.write(f"| {t['trial']} | {t['slurm_job_id'] or '–'} | {t['node'] or '–'} | **{t['terminal_state']}** | {'yes' if t['counted_preliminary'] else 'no (excluded)'} | "
                f"{fmt(t['session_exit'])} | {fmt(t['boundary_audit'])} | {fmt(t['completed_verification'])} | {fmt(t['sources_unchanged'])} | {t['reason'] or '–'} |\n")
    f.write("\n## 2. Telemetry\n\n| Trial | Queue after eligible (min) | Job elapsed (min) | Job CPU time (min) | Peak RSS (MB) | Alloc | Session wall (min) | API (min) | Turns | Tool calls | Output tokens | Cost (USD) | Staged files / bytes | Globus transfers / bytes / wall (s) | Workflow jobs (run min) | Audit |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
    for t in trials:
        f.write(f"| {t['trial']} | {mins(t['queue_wait_after_eligible_s'])} | {mins(t['job_elapsed_s'])} | {mins(t['job_total_cpu_s'])} | {fmt(t['job_peak_rss_mb'])} | "
                f"{t['alloc_cpus'] or '–'} CPU / {t['req_mem'] or '–'} | {mins(t['session_wall_s'])} | {mins(t['session_api_s'])} | {fmt(t['turns'])} | {fmt(t['tool_calls'])} | "
                f"{fmt(t['output_tokens'])} | {fmt(t['reported_cost_usd'], 2)} | {t['files_staged']} / {t['bytes_staged']:,} | {t['globus_transfers']} / {t['globus_bytes']:,} / {fmt(t['globus_transfer_wall_s'])} | "
                f"{t['workflow_jobs'] or '–'} ({mins(t['workflow_run_s'])}) | {fmt(t['boundary_audit'])} |\n")
    f.write("\nTokens, cost and tool counts are descriptive audit metadata, not performance measures (as in E1/E2).\n\n## 3. Workflow / provenance pins\n\n")
    f.write("| Trial | Packet files (hash-list sha256) | Control commit | Prompt sha256 | Globus source → destination | Source manifest | Claude / sha256 | Model / effort | Modules at job start | Freeze sha256 |\n|---|---|---|---|---|---|---|---|---|---|\n")
    for p in prov:
        f.write(f"| {p['trial']} | {p['packet_files'] or '–'} ({(p['packet_hash_list_sha256'] or '–')[:12]}) | {(p['control_commit'] or '–')[:12]} | {(p['prompt_sha256'] or '–')[:12]} | "
                f"{(p['globus_source_collection'] or '–')[:8]} → {(p['globus_destination_collection'] or '–')[:8]} | {(p['source_manifest_sha256'] or '–')[:12]} | "
                f"{p['claude_version'] or '–'} / {(p['claude_sha256'] or '–')[:12]} | {p['model'] or '–'} / {p['reasoning_effort'] or '–'} | {p['modules_at_job_start'] or '–'} | {(p['freeze_sha256'] or '–')[:12]} |\n")
print("wrote tables/tables.md")
