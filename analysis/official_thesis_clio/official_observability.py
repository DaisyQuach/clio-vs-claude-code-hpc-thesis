#!/usr/bin/env python3
"""COUNTED THESIS TRIALS: observability of the 15 counted CLIO trials (factorio-flat 0.5.0) vs the 15 counted Claude Code
baseline trials, with the same 14 diagnostic questions and record inventory as the pilot study
(../observability_study/observability_metrics.py, copied here 2026-10-13; Thesis is read only).

Differences from the pilot script (all marked "OFFICIAL"):
  * CLIO runs are the counted trials (logs/agent_sessions/<label>/ and logs/session/ for E3), files named as the counted
    evidence pipeline names them (clio/trace.json, clio/provenance_execution.json, ...).
  * CLIO's SSE event stream (stream.jsonl, captured from GET /v1/sessions/{sid}/events) is a native CLIO record and is
    counted as source clio_events. The pilots did not keep it. It answers Q4 (tool.call.progress events while a tool runs).
  * The collector-written result.json of a CLIO session is a harness file (synthesised from the transcripts) and is not
    counted.

Only records the SYSTEM itself produced are counted ("native"):
  baseline  Claude Code stream-json (stream.jsonl), Claude Code transcript (transcript_*.jsonl), final result (result.json)
  CLIO      the same Claude Code transcript (written by CLIO's provider, sdk_transcripts/) = "inherited", plus
            CLIO API exports (trace, provenance, messages, attempts, tasks, questions, session state/preflight),
            and CLIO's stream audit (opt-in via CLIO_STREAM_AUDIT_LOG) = "CLIO-added".
Harness files written by our runners/automation (launch plans, poll logs, sstat, sacct, evidence hashes) are excluded.

Outputs (data/): record_inventory.csv, diagnostic_coverage.csv, coverage_summary.json; figures/: obs1, obs2.
"""
import collections
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PILOTS = os.path.dirname(HERE)
OUT = f"{HERE}/observability"  # OFFICIAL: outputs under official_thesis_clio/observability/
TH = "/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs"
# counted baseline trials and where each keeps its session records (read-only)
BASELINE = {
    "E1": [f"{TH}/E1_uninterrupted_example8/baseline/trial_{t}/logs/agent_sessions/session_main" for t in ("01", "02", "03", "05", "04R2")],
    "E2": [f"{TH}/E2_interrupted_recovery_example16/baseline/trial_{t}/logs/agent_sessions/session_{{a,b}}" for t in ("01", "02R", "03", "04R", "05")],
    "E3": [f"{TH}/E3_disparate_storage_example8/baseline/trial_{t}/logs/session" for t in ("01", "03", "04", "05", "06")],
}


def finished_clio(d):
    t = f"{d}/telemetry"
    return os.path.exists(f"{t}/session_B/session_final.json") or (os.path.exists(f"{t}/session_final.json") and os.path.exists(f"{t}/session_trace.json"))


# CLIO pilots with full API exports and the stream audit (programs 20261011 onward; 20261010 kept neither)
# OFFICIAL: the counted CLIO trials (excluded attempts E1-03, E2-05, E3-01, E3-02 left out)
CLIO = {
    "E1": [f"{TH}/E1_uninterrupted_example8/clio/trial_{t}/logs/agent_sessions/session_main" for t in ("01", "02", "03R", "04", "05")],
    "E2": [f"{TH}/E2_interrupted_recovery_example16/clio/trial_{t}/logs/agent_sessions/session_{{a,b}}" for t in ("01", "02", "03", "04", "05R")],
    "E3": [f"{TH}/E3_disparate_storage_example8/clio/trial_{t}/logs/session" for t in ("03", "04", "05", "06", "07")],
}
os.makedirs(f"{OUT}/data", exist_ok=True)
os.makedirs(f"{OUT}/figures", exist_ok=True)


def jl(path):
    out = []
    with open(path, errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def jload(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def paths(x, pre="", acc=None):
    """Distinct JSON field paths (list indices collapsed to [])."""
    acc = set() if acc is None else acc
    if isinstance(x, dict):
        for k, v in x.items():
            p = f"{pre}.{k}" if pre else k
            acc.add(p)
            paths(v, p, acc)
    elif isinstance(x, list):
        for v in x[:50]:
            paths(v, pre + "[]", acc)
    return acc


def rtype(rec, source):
    if source == "cc_stream":
        return f"{rec.get('type')}/{rec.get('subtype') or ''}"
    if source == "cc_transcript":
        t = rec.get("type")
        return f"{t}/{(rec.get('attachment') or {}).get('type', '')}" if t == "attachment" else f"{t}/{rec.get('subtype') or ''}"
    if source == "clio_trace":
        return rec.get("event_type", "?")
    if source == "clio_provenance":
        return f"{rec.get('kind')}/{rec.get('event_type')}"
    if source == "clio_audit":
        return rec.get("stage") or ("segments" if "segments" in rec else "?")
    if source == "clio_events":
        return rec.get("type", "?")
    if source == "clio_messages":
        return f"message/{rec.get('role', '')}"
    return source


def has_ts(rec):
    s = json.dumps(rec)[:4000]
    return bool(re.search(r'"(timestamp|occurred_at|iso|start_time|created_at|ts)"', s))


# ------------------------------------------------------------------ collect native records per run
def baseline_sources(pattern):
    src = collections.defaultdict(list)
    dirs = [pattern.replace("{a,b}", x) for x in "ab"] if "{a,b}" in pattern else [pattern]
    for d in dirs:
        if os.path.exists(f"{d}/stream.jsonl"):
            src["cc_stream"] += jl(f"{d}/stream.jsonl")
        for f in glob.glob(f"{d}/transcript_*.jsonl"):
            src["cc_transcript"] += jl(f)
        r = jload(f"{d}/result.json")
        if r:
            src["cc_result"].append(r)
    return src


def clio_sources(pattern):  # OFFICIAL layout of the counted evidence
    src = collections.defaultdict(list)
    dirs = [pattern.replace("{a,b}", x) for x in "ab"] if "{a,b}" in pattern else [pattern]
    for d in dirs:
        for f in glob.glob(f"{d}/transcript_*.jsonl"):
            src["cc_transcript"] += jl(f)
        if os.path.exists(f"{d}/stream.jsonl"):
            src["clio_events"] += [r.get("data") or r for r in jl(f"{d}/stream.jsonl")]
        c = f"{d}/clio"
        t = jload(f"{c}/trace.json") or {}
        src["clio_trace"] += t.get("events", [])
        p = jload(f"{c}/provenance_execution.json") or {}
        src["clio_provenance"] += p.get("spans", [])
        if p:
            src["clio_provenance_meta"].append({k: p.get(k) for k in ("complete", "truncated", "lineage_truncated", "degradations")})
        m = jload(f"{c}/messages.json")
        if isinstance(m, dict):
            m = m.get("messages") or m.get("items") or []
        src["clio_messages"] += m if isinstance(m, list) else []
        for name, key in (("attempts", "session_attempts"), ("agent_tasks", "session_agent_tasks"), ("questions", "session_questions"),
                          ("session_final", "session_final"), ("session_preflight", "session_preflight"),
                          ("session_blueprint", "session_blueprint"), ("health_preflight", "health_preflight"),
                          ("session_defaults", "session_defaults_preflight")):
            x = jload(f"{c}/{name}.json")
            if x is not None:
                src["clio_state:" + key].append(x)
        if os.path.exists(f"{c}/stream_audit_provider_rows.jsonl"):
            src["clio_audit"] += jl(f"{c}/stream_audit_provider_rows.jsonl")
        rs = jload(f"{c}/runtime_settings_live.json")
        if rs:
            src["clio_state:runtime_settings"].append(rs)
    return src


INHERITED = {"cc_stream", "cc_transcript", "cc_result"}


def inventory(label, system, src, n_calls):
    rows = []
    for s, recs in sorted(src.items()):
        if s.endswith("_meta"):
            continue
        fp = set()
        for r in recs[:4000]:
            paths(r, "", fp)
        rows.append({"system": system, "run": label, "source": s,
                     "origin": "Claude Code" if s in INHERITED else "CLIO-added",
                     "records": len(recs), "record_types": len({rtype(r, s) for r in recs if isinstance(r, dict)}),
                     "field_paths": len(fp), "timestamped": sum(1 for r in recs if isinstance(r, dict) and has_ts(r)),
                     "model_calls": n_calls})
    return rows


def n_model_calls(src):
    ids = {(r.get("message") or {}).get("id") for r in src.get("cc_transcript", []) if r.get("type") == "assistant"}
    return len(ids - {None})


# ------------------------------------------------------------------ diagnostic questions (capability checks)
def anyrec(recs, pred):
    return any(isinstance(r, dict) and pred(r) for r in recs)


def j(r):
    return json.dumps(r)


QUESTIONS = [
    # (id, question, baseline check -> (score, evidence), clio check -> (score, evidence))
    ("Q1", "Per-call token usage including cache writes",
     lambda s: (1, "transcript assistant.message.usage.cache_creation_input_tokens") if anyrec(s["cc_transcript"], lambda r: "cache_creation_input_tokens" in j(r.get("message", {}))) else (0, ""),
     lambda s: (1, "audit provider.call_usage.usage_cache_creation_input_tokens (+ inherited transcript)") if anyrec(s["clio_audit"], lambda r: "usage_cache_creation_input_tokens" in r) else (1, "inherited transcript") if anyrec(s["cc_transcript"], lambda r: "cache_creation_input_tokens" in j(r.get("message", {}))) else (0, "")),
    ("Q2", "Typed reason for each prompt-cache reset / full-context re-send",
     lambda s: (0, "no reset concept or field (compaction would appear as a system event)"),
     lambda s: (1, "audit provider.stateful.reason (first_call, session_evicted, ...)") if anyrec(s["clio_audit"], lambda r: r.get("stage") == "provider.stateful" and r.get("reason")) else (0, "")),
    ("Q3", "Start and end time of every tool call, including parallel calls",
     lambda s: (1, "tool_use timestamp + one tool_result user entry per call (own timestamp)") if anyrec(s["cc_transcript"], lambda r: r.get("type") == "user" and "tool_result" in j(r.get("message", {}))) else (0, ""),
     lambda s: (1, "trace tool.call.started / tool.call.completed per call_id") if anyrec(s["clio_trace"], lambda r: r.get("event_type") == "tool.call.completed") else (0, "")),
    ("Q4", "Liveness of a long-running tool while it runs",
     lambda s: (1, "stream tool_progress heartbeats (elapsed_time_seconds)") if anyrec(s["cc_stream"], lambda r: r.get("type") == "tool_progress") else (0, ""),
     lambda s: (1, "SSE tool.call.progress events while the tool runs (OFFICIAL: SSE stream kept)") if anyrec(s["clio_events"], lambda r: r.get("type") == "tool.call.progress")
     else (0.5, "trace tool.call.started without completed (no heartbeat)") if anyrec(s["clio_trace"], lambda r: r.get("event_type") == "tool.call.started") else (0, "")),
    ("Q5", "Typed reason when a tool call or turn fails (timeout, watchdog, provider error)",
     lambda s: (0.5, "result.json terminal_reason/is_error per session; tool errors only as tool_result text") if anyrec(s["cc_result"], lambda r: "terminal_reason" in r) else (0, ""),
     lambda s: (1, "trace turn.failed / llm.response.failed / tool.call.completed status (e3a: provider_timeout)") if anyrec(s["clio_trace"], lambda r: "status" in r and r.get("event_type", "").endswith(("completed", "failed"))) else (0, "")),
    ("Q6", "Effective configuration read back from the running system (model, permissions, effort, agent definition, timeouts)",
     lambda s: (0.5, "stream system/init: model, permissionMode, version, tools, per_turn_effort_active (no effort level, no timeouts)") if anyrec(s["cc_stream"], lambda r: r.get("subtype") == "init") else (0, ""),
     lambda s: (1, "API: session model/approval/metadata, attached blueprint + version, /v1/settings/runtime (timeouts)") if s.get("clio_state:session_preflight") and s.get("clio_state:runtime_settings") else (0, "")),
    ("Q7", "Causal links: which model step issued which tool call",
     lambda s: (1, "tool_use.id <-> tool_result.tool_use_id; parentUuid chain") if anyrec(s["cc_transcript"], lambda r: "tool_use_id" in j(r.get("message", {}))) else (0, ""),
     lambda s: (1, "trace react.step.completed + call_id; provenance spans with parent_id") if anyrec(s["clio_provenance"], lambda r: r.get("parent_id")) else (0, "")),
    ("Q8", "Which skills / domain knowledge the agent loaded",
     lambda s: (0.5, "derivable only from tool calls in the transcript (no skill event)"),
     lambda s: (1, "trace skill.loaded") if anyrec(s["clio_trace"], lambda r: r.get("event_type") == "skill.loaded") else (0, "")),
    ("Q9", "Slurm jobs the agent submitted, attributed to the session",
     lambda s: (0.5, "derivable by parsing sbatch output in tool results"),
     lambda s: (0.5, "derivable by parsing sbatch output in tool results (CLIO has no job-attribution field; our runner's agent_jobs came from the jobs file)")),
    ("Q10", "Provider rate-limit / quota state during the run",
     lambda s: (1, "stream rate_limit_event (status, utilization, resetsAt)") if anyrec(s["cc_stream"], lambda r: r.get("type") == "rate_limit_event") else (0, ""),
     lambda s: (0.5, "only when a limit stops the turn: trace turn.failed reason claude_code_plan_limit (rate_limit_type, resets_at); no running quota state") if anyrec(s["clio_trace"], lambda r: "claude_code_plan_limit" in j(r)) else (0, "not recorded (CLIO consumes the CLI stream and does not keep it; a limit that stops a turn is recorded as turn.failed)")),
    ("Q11", "Reasoning volume per model call",
     lambda s: (1, "stream system/thinking_tokens") if anyrec(s["cc_stream"], lambda r: r.get("subtype") == "thinking_tokens") else (0, ""),
     lambda s: (1, "audit provider.batch_response.reasoning_len") if anyrec(s["clio_audit"], lambda r: "reasoning_len" in r) else (0, "")),
    ("Q12", "Whether each call's prompt prefix matched the previous one (cache stability)",
     lambda s: (0, "not recorded"),
     lambda s: (1, "audit provider.call_started.prefix_2k/16k_sha256") if anyrec(s["clio_audit"], lambda r: "prefix_16k_sha256" in r) else (0, "")),
    ("Q13", "Runtime health and degraded integrations",
     lambda s: (0, "stderr only"),
     lambda s: (1, "API /v1/health integrations + audit *_degraded rows") if s.get("clio_state:health_preflight") else (0, "")),
    ("Q14", "Which call created or changed each output file",
     lambda s: (0.5, "Write/Edit tool inputs name the file; shell-written files only derivable from commands"),
     lambda s: (0.5, "trace artifact.transform.recorded per tool call, but shell transforms record 0 used / 0 generated") if anyrec(s["clio_trace"], lambda r: r.get("event_type", "").startswith("artifact.")) else (0, "")),
]


def run_label(system, path):
    m = re.search(r"trial_(\w+)/logs", path)
    return f"{'baseline' if system == 'baseline' else 'CLIO'} {m.group(1)}"


def main():
    inv, cov = [], []
    for exp in ("E1", "E2", "E3"):
        runs = [("baseline", run_label("baseline", d), baseline_sources(d)) for d in BASELINE[exp]]
        runs += [("clio", run_label("clio", d), clio_sources(d)) for d in CLIO[exp]]
        for system, label, src in runs:
            src = collections.defaultdict(list, src)
            inv += [{"experiment": exp, **r} for r in inventory(label, system, src, n_model_calls(src))]
            variants = [(system, src)]
            if system == "clio":  # the stream audit is opt-in: also score CLIO without it
                variants.append(("clio_no_audit", collections.defaultdict(list, {k: v for k, v in src.items() if k != "clio_audit"})))
            for sysn, ss in variants:
                for qid, q, fb, fc in QUESTIONS:
                    sc, ev = (fb if sysn == "baseline" else fc)(ss)
                    cov.append({"experiment": exp, "system": sysn, "run": label, "qid": qid, "question": q, "score": sc, "evidence": ev})
    for name, rows_ in (("record_inventory", inv), ("diagnostic_coverage", cov)):
        with open(f"{OUT}/data/{name}.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows_[0]))
            w.writeheader(); w.writerows(rows_)
    summ = {}
    for exp in ("E1", "E2", "E3", "all"):
        for system in ("baseline", "clio", "clio_no_audit"):
            cc = [c for c in cov if c["system"] == system and exp in (c["experiment"], "all")]
            if not cc:
                continue
            by_q = collections.defaultdict(list)
            for c in cc:
                by_q[c["qid"]].append(c["score"])
            qscore = {q: max(v) for q, v in by_q.items()}  # capability = best evidence seen in any run of that system
            rr = [r for r in inv if r["system"] == system.replace("_no_audit", "") and exp in (r["experiment"], "all")]
            per_run = collections.defaultdict(collections.Counter)
            for r in rr:
                k = "inherited" if r["origin"] == "Claude Code" else "clio_added"
                key = f"{r['experiment']} {r['run']}"
                per_run[key][k + "_records"] += r["records"]
                per_run[key][k + "_types"] += r["record_types"]
                per_run[key]["model_calls"] = r["model_calls"]
            summ[f"{exp}:{system}"] = {"runs": sorted({c["run"] for c in cc}), "question_scores": qscore,
                                        "coverage_points": sum(qscore.values()), "questions": len(qscore),
                                        "native_full": sum(1 for v in qscore.values() if v == 1),
                                        "per_run": {k: dict(v) for k, v in per_run.items()}}
    json.dump(summ, open(f"{OUT}/data/coverage_summary.json", "w"), indent=1)
    for k, x in summ.items():
        print(f"{k:22s} coverage {x['coverage_points']:4g}/{x['questions']} ({x['native_full']} fully recorded); runs {len(x['runs'])}")
    return summ, inv


def figures(summ, inv):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    SLOT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
    INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
    SEQ = {0: "#eeedea", 0.5: "#9ec5ee", 1: "#2a78d6"}  # one hue, light -> dark
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
                         "axes.titleweight": "bold", "axes.titlesize": 10})
    FOOT = ("COUNTED THESIS TRIALS · 5 Claude Code baseline and 5 CLIO (factorio-flat 0.5.0) trials per experiment · native records only "
            "(harness files excluded) · same 14 questions as the pilot study; CLIO's SSE event stream counted")

    def save(fig, name, foot_y=-0.03):
        fig.text(0.01, foot_y, FOOT, fontsize=6.5, color=INK2, transform=fig.transFigure)
        fig.savefig(f"{OUT}/figures/{name}.png", dpi=300, bbox_inches="tight")
        fig.savefig(f"{OUT}/figures/{name}.pdf", bbox_inches="tight")
        plt.close(fig)

    # obs1: coverage matrix, one baseline/CLIO column pair per experiment
    qs = [(qid, q) for qid, q, _, _ in QUESTIONS]
    cols = [(e, sy) for e in ("E1", "E2", "E3") for sy in ("baseline", "clio")]
    X = lambda xi: xi + 0.35 * (xi // 2)  # gap between experiments
    fig, ax = plt.subplots(figsize=(13, 0.36 * len(qs) + 2.0))
    for xi, (e, sy) in enumerate(cols):
        qsc = summ[f"{e}:{sy}"]["question_scores"]
        for yi, (qid, q) in enumerate(qs):
            v = qsc[qid]
            ax.add_patch(plt.Rectangle((X(xi) + 0.04, yi + 0.06), 0.92, 0.88, color=SEQ[v], lw=0))
            ax.text(X(xi) + 0.5, yi + 0.5, {0: "absent", 0.5: "derivable", 1: "recorded"}[v],
                    ha="center", va="center", fontsize=7.5, color="white" if v == 1 else INK)
    ax.set_xlim(0, X(len(cols) - 1) + 1); ax.set_ylim(len(qs), 0)
    ticks, labels = [], []
    for xi, (e, sy) in enumerate(cols):
        x = summ[f"{e}:{sy}"]
        ticks.append(X(xi) + 0.5)
        n = len(x["runs"])
        labels.append(f"{e} {'Claude Code' if sy == 'baseline' else 'CLIO'}\n{x['coverage_points']:g}/{len(qs)} pts · n={n}")
    ax.set_xticks(ticks, labels, fontsize=8.5)
    ax.xaxis.tick_top()
    ax.set_yticks([i + 0.5 for i in range(len(qs))], [f"{qid}  {q}" for qid, q in qs], fontsize=8)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    ax.set_title("Which diagnostic questions each system's own records answer, per experiment (recorded = 1, derivable = 0.5, absent = 0)",
                 pad=38, loc="left")
    na = " · ".join(f"{e}: {summ[f'{e}:clio_no_audit']['coverage_points']:g}" for e in ("E1", "E2", "E3"))
    fig.text(0.01, -0.0, f"CLIO without the opt-in stream audit (CLIO_STREAM_AUDIT_LOG unset): {na} points", fontsize=7.5, color=INK2,
             transform=fig.transFigure)
    save(fig, "obs1_diagnostic_coverage", foot_y=-0.03)

    # obs2: record variety and volume per run, all experiments
    keys = []
    for e in ("E1", "E2", "E3"):
        for sy in ("baseline", "clio"):
            keys += [(e, sy, r) for r in sorted({z["run"] for z in inv if z["experiment"] == e and z["system"] == sy
                                                 and int(z["model_calls"]) > 0})]  # 10-Oct pilots kept no transcripts: excluded
    groups_ = []
    for k in keys:
        if not groups_ or groups_[-1][0] != k[:2]:
            groups_.append([k[:2], []])
        groups_[-1][1].append(k)
    pos, xs = {}, 0.0
    for g, ks in groups_:
        for k in ks:
            pos[k] = xs; xs += 1
        xs += 0.8
    fig, axes = plt.subplots(2, 1, figsize=(13, 6.8))
    for ax, (metric, title) in zip(axes, (("record_types", "Distinct record / event types per run"),
                                          ("records", "Structured records per model call"))):
        x = [pos[k] for k in keys]
        bottom = [0.0] * len(keys)
        for i, origin in enumerate(("Claude Code", "CLIO-added")):
            vals = []
            for e, sy, r in keys:
                rows_ = [z for z in inv if z["experiment"] == e and z["run"] == r and z["origin"] == origin and z["system"] == sy]
                v = sum(int(z[metric]) for z in rows_)
                calls = max(1, int(rows_[0]["model_calls"])) if rows_ else 1
                vals.append(v / calls if metric == "records" else v)
            ax.bar(x, vals, 0.66, bottom=bottom, color=SLOT[i], edgecolor=SURF, linewidth=1.0,
                   label="Claude Code records (stream, transcript, result)" if i == 0 else "CLIO-added records (trace, provenance, audit, API state)")
            bottom = [b + v for b, v in zip(bottom, vals)]
        for xi, b in zip(x, bottom):
            ax.text(xi, b * 1.01, f"{b:.0f}", ha="center", va="bottom", fontsize=6.5, color=INK)
        ax.set_xticks(x, [r.split()[-1] for e, sy, r in keys], fontsize=7)
        for g, ks in groups_:
            mid = (pos[ks[0]] + pos[ks[-1]]) / 2
            ax.text(mid, -0.16, f"{g[0]} {'Claude Code' if g[1] == 'baseline' else 'CLIO'}", transform=ax.get_xaxis_transform(),
                    ha="center", va="top", fontsize=8, color=INK, fontweight="bold")
        ax.set_title(title, loc="left")
        ax.grid(axis="y", color=GRID, linewidth=0.8); ax.set_axisbelow(True)
        ax.set_ylim(0, max(bottom) * 1.15)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=8, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.03))
    fig.tight_layout(rect=(0, 0, 1, 0.97), h_pad=2.5)
    fig.text(0.01, -0.02, "Run labels are trial numbers. Most CLIO-added records are stream-audit rows and SSE deltas (per streamed chunk). "
             "E2 runs sum Sessions A and B.",
             fontsize=6.5, color=INK2, transform=fig.transFigure)
    save(fig, "obs2_record_volume_and_variety", foot_y=-0.05)


if __name__ == "__main__":
    figures(*main())
