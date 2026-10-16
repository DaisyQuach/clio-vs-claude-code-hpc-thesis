#!/usr/bin/env python3
"""Model-usage telemetry for one CLIO session, in the baseline's shapes. Read-only on its sources.

Usage: clio_usage.py <evidence_dir> <claude_config_dir> <clio_home>

Sources (both written by the deployment itself):
 1. Claude Code transcripts that CLIO's claude_code provider wrote under the session's ISOLATED CLAUDE_CONFIG_DIR
    (<claude_config_dir>/projects/**/*.jsonl). The directory belongs to this session only, so no attribution heuristics
    are needed. Each API call carries the full usage block, including cache_creation_input_tokens, which CLIO's own
    message/trace usage reports as 0.
 2. CLIO's stream audit (<clio_home>/state/stream_audit.jsonl, CLIO_STREAM_AUDIT_LOG): provider.stateful rows give, per
    call, "delta" (conversation kept) or a full re-send with its typed reset reason.
Writes (evidence_dir):
  transcript_<sdk-session-id>.jsonl  copies of the SDK transcripts (same role as the baseline transcript_<uuid>.jsonl)
  result.json                        baseline-shaped summary ({"type":"result", duration_ms, num_turns, total_cost_usd, usage{...}})
  clio/usage_per_call.csv, clio/usage_summary.json, clio/stream_audit_provider_rows.jsonl
"""
import collections, csv, datetime as dt, glob, json, os, shutil, sys

EV, CFG, HOME = (os.path.abspath(p) for p in sys.argv[1:4])
C = os.path.join(EV, "clio")
os.makedirs(C, exist_ok=True)
# claude-fable-5-1 list prices (USD per token); they reproduce Claude Code's and CLIO's own cost_usd to the cent (pilots)
PRICE = {"in": 10e-6, "out": 50e-6, "cache_read": 0.25e-6, "cw_1h": 20e-6, "cw_5m": 12.5e-6}
U = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))

calls, cli_versions, copied = [], collections.Counter(), []
for f in sorted(glob.glob(os.path.join(CFG, "projects", "**", "*.jsonl"), recursive=True)):
    rows = []
    for line in open(f, errors="replace"):
        try:
            rows.append(json.loads(line))
        except ValueError:
            pass
    if not rows:
        continue
    sdk_sid = next((r.get("sessionId") for r in rows if r.get("sessionId")), os.path.basename(f)[:-6])
    dst = os.path.join(EV, f"transcript_{sdk_sid}.jsonl")
    if os.path.exists(dst):
        dst = os.path.join(EV, f"transcript_{sdk_sid}_{len(copied)}.jsonl")
    shutil.copy2(f, dst)
    copied.append(os.path.basename(dst))
    seen = collections.OrderedDict()
    for r in rows:
        if r.get("version"):
            cli_versions[r["version"]] += 1
        if r.get("type") == "assistant":
            m = r.get("message") or {}
            seen[m.get("id")] = (r.get("timestamp"), m.get("model"), m.get("usage") or {})
    for mid, (ts, model, u) in seen.items():
        cc = u.get("cache_creation") or {}
        cw = u.get("cache_creation_input_tokens", 0) or 0
        cw1, cw5 = cc.get("ephemeral_1h_input_tokens", 0) or 0, cc.get("ephemeral_5m_input_tokens", 0) or 0
        if cw and not (cw1 or cw5):
            cw1 = cw  # TTL split absent: Claude Code requests 1 h caching on subscription auth (all pilots)
        row = {"utc": ts, "sdk_session_id": sdk_sid, "message_id": mid, "model": model, "input_tokens": u.get("input_tokens", 0) or 0,
               "output_tokens": u.get("output_tokens", 0) or 0, "cache_read_tokens": u.get("cache_read_input_tokens", 0) or 0,
               "cache_write_tokens": cw, "cache_write_1h": cw1, "cache_write_5m": cw5}
        row["context_tokens"] = row["input_tokens"] + row["cache_read_tokens"] + cw
        row["cost_usd"] = (row["input_tokens"] * PRICE["in"] + row["output_tokens"] * PRICE["out"] + row["cache_read_tokens"] * PRICE["cache_read"]
                           + cw1 * PRICE["cw_1h"] + cw5 * PRICE["cw_5m"])
        calls.append(row)
calls.sort(key=lambda r: r["utc"] or "")
fields = list(calls[0].keys()) if calls else ["utc"]
with open(os.path.join(C, "usage_per_call.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    [w.writerow(r) for r in calls]

audit, stateful = [], []
for f in glob.glob(os.path.join(HOME, "state", "stream_audit*.jsonl")):
    for line in open(f, errors="replace"):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("stage") == "provider.raw_event":
            continue  # chunk rows: size only
        audit.append(r)
        if r.get("stage") == "provider.stateful":
            stateful.append(r)
with open(os.path.join(C, "stream_audit_provider_rows.jsonl"), "w") as fh:
    for r in audit:
        fh.write(json.dumps(r, sort_keys=True) + "\n")
reset_reasons, modes = collections.Counter(), collections.Counter()
for r in stateful:
    modes[r.get("stateful_mode")] += 1
    rr = r.get("reset_reason") or r.get("reason") or (r.get("stateful_reset") or {}).get("reason")
    if rr:
        reset_reasons[rr] += 1
idle_reaps = sum(1 for r in audit if "idle_reaped" in json.dumps(r))

K = ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens", "cache_write_1h", "cache_write_5m", "cost_usd")
tot = {k: sum(r[k] for r in calls) for k in K}
resends = [r for r in calls if r["context_tokens"] > 30000 and r["cache_write_tokens"] >= 0.5 * r["context_tokens"]]
st = {}
try:
    st = json.load(open(os.path.join(C, "runner_state.json")))
except Exception:
    pass
dur_ms = None
if st.get("start_utc") and st.get("end_utc"):
    dur_ms = int((U(st["end_utc"]) - U(st["start_utc"])).total_seconds() * 1000)
summary = {"descriptive_only": True, "api_calls": len(calls), "totals": tot,
           "cost_breakdown_usd": {"output": tot["output_tokens"] * PRICE["out"], "cache_read": tot["cache_read_tokens"] * PRICE["cache_read"],
                                  "cache_write": tot["cache_write_1h"] * PRICE["cw_1h"] + tot["cache_write_5m"] * PRICE["cw_5m"],
                                  "input_uncached": tot["input_tokens"] * PRICE["in"]},
           "claude_cli_versions_seen": dict(cli_versions), "sdk_transcripts": copied,
           "full_resend_calls": len(resends), "full_resend_cache_write_tokens": sum(r["cache_write_tokens"] for r in resends),
           "stream_audit": {"rows": len(audit), "stateful_modes": dict(modes), "reset_reasons": dict(reset_reasons), "idle_reaps": idle_reaps},
           "pricing_usd_per_token": PRICE}
json.dump(summary, open(os.path.join(C, "usage_summary.json"), "w"), indent=2, default=str)
# Baseline-shaped result record. Field meanings differ where noted; the analysis reads clio/usage_summary.json for detail.
result = {"type": "result", "subtype": st.get("end_reason"), "is_error": st.get("end_reason") != "finished_idle",
          "duration_ms": dur_ms, "duration_api_ms": None, "num_turns": len(calls), "total_cost_usd": round(tot["cost_usd"], 6),
          "session_id": st.get("session_id"),
          "usage": {"input_tokens": tot["input_tokens"], "output_tokens": tot["output_tokens"],
                    "cache_read_input_tokens": tot["cache_read_tokens"], "cache_creation_input_tokens": tot["cache_write_tokens"]},
          "clio_note": "synthesized from the SDK transcripts: num_turns = Claude API calls (Claude Code's num_turns counts agent turns); "
                       "duration_api_ms not available from CLIO; total_cost_usd recomputed at list price"}
json.dump(result, open(os.path.join(EV, "result.json"), "w"))
print(json.dumps({"api_calls": len(calls), "cost_usd": round(tot["cost_usd"], 2), "resends": len(resends),
                  "reset_reasons": dict(reset_reasons), "idle_reaps": idle_reaps, "cli_versions": dict(cli_versions)}))
