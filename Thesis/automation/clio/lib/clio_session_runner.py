#!/usr/bin/env python3
"""Drive ONE counted CLIO session through the deployment's local API (stdlib only).

Counted-run counterpart of the headless `claude --print` call in ../../launch_headless_claude.sh, derived from the
pilot runner (clioSessions/CLIO_E1_API_pilots/pilot_program_20261011_tuned/api_runner.py) with the pilot-only
behaviour removed: the prompt file is sent verbatim (no banner), one user message per session by default, questions
and permission requests are never answered (the session is cancelled instead), and the session limit is the
baseline's 6600 s.

Usage: clio_session_runner.py --port P --trial-dir D --evidence-dir E --prompt-file F --run-id ID --label L
          --model M --approval A --effort default|low|medium|high|max --blueprint-id B --blueprint-version V
          --timeout-s 6600 [--max-nudges 0] [--poll-s 15] [--validate-only]
--validate-only: health, workspace and session creation, blueprint and settings read-back; no message is sent (no model call).
Writes only under --evidence-dir (EVIDENCE/clio/*.json[l]); exit 0 = session finished idle, 1 = otherwise.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid

a = argparse.ArgumentParser()
for k in ("port", "trial-dir", "evidence-dir", "prompt-file", "run-id", "label", "model", "approval", "effort",
          "blueprint-id", "blueprint-version"):
    a.add_argument("--" + k, required=k != "prompt-file")
a.add_argument("--timeout-s", type=int, default=6600)
a.add_argument("--max-nudges", type=int, default=0)
a.add_argument("--poll-s", type=int, default=15)
a.add_argument("--validate-only", action="store_true")
A = a.parse_args()
BASE = f"http://127.0.0.1:{A.port}"
EV = os.path.join(A.evidence_dir, "clio")
os.makedirs(EV, exist_ok=True)
STATE_F = os.path.join(EV, "runner_state.json")
EVENTS_F = os.path.join(EV, "runner_events.jsonl")
POLL_F = os.path.join(EV, "poll_log.jsonl")
NUDGE = ("[Automated runner - no human is available] Your previous turn ended before the task's completion criteria were "
         "met: {why}. Continue the same task autonomously, following agent_inputs/ exactly. If a required fact is unavailable, "
         "record the blocking condition in work/run_summary.md and stop.")


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def jdump(name, obj):
    p = os.path.join(EV, name)
    with open(p + ".tmp", "w") as f:
        json.dump(obj, f, indent=2, default=str)
    os.replace(p + ".tmp", p)


def event(_event, **kw):
    rec = {"utc": now(), "event": _event, **kw}
    with open(EVENTS_F, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")
    print(json.dumps(rec, default=str)[:500], flush=True)


def api(method, path, body=None, tries=6, timeout=60, ok404=False):
    data = json.dumps(body).encode() if body is not None else None
    last = None
    for i in range(tries):
        req = urllib.request.Request(BASE + path, data=data, method=method,
                                     headers={"Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                try:
                    return json.loads(raw) if raw else {}
                except ValueError:
                    return {"_raw": raw.decode(errors="replace")}
        except urllib.error.HTTPError as e:
            txt = e.read().decode(errors="replace")
            if e.code == 404 and ok404:
                return None
            if e.code < 500 and e.code != 429:
                raise RuntimeError(f"{method} {path} -> HTTP {e.code}: {txt[:2000]}")
            last = f"HTTP {e.code}: {txt[:500]}"
        except Exception as e:  # transient connection problems are retried and recorded
            last = repr(e)
        event("api_retry", method=method, path=path, attempt=i + 1, error=last)
        time.sleep(min(60, 3 * 2 ** i))
    raise RuntimeError(f"{method} {path} failed after {tries} tries: {last}")


def sse_capture(sid, stop):
    """CLIO's session event stream -> stream.jsonl (one JSON object per SSE data line; the CLIO analogue of stream-json)."""
    out = open(os.path.join(A.evidence_dir, "stream.jsonl"), "a")
    while not stop.is_set():
        try:
            req = urllib.request.Request(f"{BASE}/v1/sessions/{sid}/events",
                                         headers={"Accept": "text/event-stream", "x-gact-version": "0.2"})
            with urllib.request.urlopen(req, timeout=3600) as r:
                ev_name = None
                for raw in r:
                    if stop.is_set():
                        break
                    line = raw.decode(errors="replace").rstrip("\n")
                    if line.startswith("event:"):
                        ev_name = line[6:].strip()
                    elif line.startswith("data:"):
                        d = line[5:].strip()
                        try:
                            obj = json.loads(d)
                        except ValueError:
                            obj = {"raw": d}
                        out.write(json.dumps({"utc": now(), "sse_event": ev_name, "data": obj}, default=str) + "\n")
                        out.flush()
        except Exception as e:
            out.write(json.dumps({"utc": now(), "sse_error": repr(e)}) + "\n")
            out.flush()
            stop.wait(5)


def agent_job_ids():
    jf = os.path.join(A.trial_dir, "jobs", "job_ids.txt")
    return sorted(set(re.findall(r"\b(\d{6,9})\b", open(jf, errors="replace").read()))) if os.path.exists(jf) else []


def main():
    st = {"run_id": A.run_id, "session_label": A.label, "runner_start_utc": now(), "host": socket.gethostname(),
          "slurm_job_id": os.environ.get("SLURM_JOB_ID"), "settings": vars(A)}
    jdump("runner_state.json", st)
    event("runner_start", validate_only=A.validate_only)
    # ---- preflight (no model call) -------------------------------------------------------------------------------
    health, waited = api("GET", "/v1/health"), 0
    while waited < 180:  # the provider's sign-in/model probe completes asynchronously after start
        lm = [i for i in health.get("integrations", []) if i.get("name") == "lm_provider"]
        if lm and lm[0].get("status") == "ready":
            break
        time.sleep(10)
        waited += 10
        health = api("GET", "/v1/health")
    st["lm_provider_wait_s"] = waited
    jdump("health_preflight.json", health)
    jdump("openapi_live.json", api("GET", "/openapi.json"))
    for name, path in (("runtime_settings_live", "/v1/settings/runtime"), ("capabilities", "/v1/capabilities"),
                       ("session_defaults", "/v1/session-defaults")):
        jdump(f"{name}.json", api("GET", path, ok404=True, tries=2))
    if not health.get("healthy"):
        raise SystemExit("CLIO health not healthy; nothing dispatched")
    nss = api("GET", "/v1/sessions", ok404=True) or {}
    prior = nss if isinstance(nss, list) else nss.get("sessions") or nss.get("items") or []
    if prior:
        raise SystemExit(f"deployment is not fresh: {len(prior)} session(s) already exist")
    if A.blueprint_id != "none":
        jdump("blueprint_installed.json", api("GET", f"/v1/agent-blueprints/{A.blueprint_id}"))
    ws = api("POST", "/v1/workspaces", {"name": A.run_id + " " + A.label, "root_path": A.trial_dir,
                                         "metadata": {"thesis_run_id": A.run_id, "session_label": A.label}})
    jdump("workspace_created.json", ws)
    wsid = ws.get("id") or (ws.get("workspace") or {}).get("id")
    md = {"thesis_run_id": A.run_id, "session_label": A.label}
    if A.effort != "default":
        md.update(effort=A.effort, effort_source="user")
    model = {"provider_id": "claude_code", "model_id": A.model}
    sreq = {"workspace_id": wsid, "title": f"{A.run_id} {A.label}", "model": model, "mode": "edit",
            "approval_mode": A.approval, "metadata": md}
    jdump("session_request.json", sreq)
    sess = api("POST", "/v1/sessions", sreq)
    sid = sess["id"]
    st.update(workspace_id=wsid, session_id=sid)
    jdump("runner_state.json", st)
    event("session_created", session_id=sid, workspace_id=wsid)
    if A.blueprint_id != "none":
        jdump("blueprint_attach_response.json", api("POST", f"/v1/sessions/{sid}/agent-blueprint", {"blueprint_id": A.blueprint_id}))
    sbp = api("GET", f"/v1/sessions/{sid}/agent-blueprint", ok404=True) or {}
    jdump("session_blueprint.json", sbp)
    active = sbp.get("active_agent_blueprint_id") or ""
    active_ver = (sbp.get("agent_blueprint") or {}).get("version")
    # blueprint activation may reset session fields: re-assert approval, model and metadata, then read back
    api("PATCH", f"/v1/sessions/{sid}", {"approval_mode": A.approval, "model": model, "metadata": {**(sess.get("metadata") or {}), **md}})
    s2 = api("GET", f"/v1/sessions/{sid}")
    jdump("session_preflight.json", s2)
    m2 = s2.get("metadata") or {}
    eff = {"model_id": (s2.get("model") or {}).get("model_id"), "provider_id": (s2.get("model") or {}).get("provider_id"),
           "approval_mode": s2.get("approval_mode"), "effort": m2.get("effort") if m2.get("effort_source") == "user" else "default",
           "blueprint_id": active or "none", "blueprint_version": active_ver}
    st["effective"] = eff
    problems = []
    if eff["model_id"] != A.model or eff["provider_id"] != "claude_code":
        problems.append(f"model {eff['provider_id']}/{eff['model_id']} != claude_code/{A.model}")
    if eff["approval_mode"] != A.approval:
        problems.append(f"approval_mode {eff['approval_mode']} != {A.approval}")
    if eff["effort"] != A.effort:
        problems.append(f"effort {eff['effort']} != {A.effort}")
    if A.blueprint_id == "none":
        if active:
            problems.append(f"standard agent requested but blueprint {active} is active")
    elif active != A.blueprint_id or (not A.blueprint_version.startswith("TBD") and active_ver != A.blueprint_version):
        problems.append(f"blueprint {active}@{active_ver} != {A.blueprint_id}@{A.blueprint_version}")
    prompt = open(A.prompt_file).read() if A.prompt_file else ""
    freeze = {"run_id": A.run_id, "session_label": A.label, "frozen_utc": now(), "api_base": BASE, "workspace_id": wsid,
              "session_id": sid, "effective": eff, "requested": vars(A), "problems": problems,
              "clio_version": (api("GET", "/openapi.json").get("info") or {}).get("version"),
              "health_non_ready": {i.get("name"): i.get("status") for i in health.get("integrations", []) if i.get("status") != "ready"},
              "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest() if prompt else None,
              "prompt_policy": "prompt file sent verbatim as the only user message",
              "message_behavior": {"execution_mode": "execute", "confirmation_policy": A.approval,
                                   **({"reasoning_effort": A.effort} if A.effort != "default" else {})}}
    jdump("configuration_freeze.json", freeze)
    st["configuration_frozen"] = freeze["frozen_utc"]
    jdump("runner_state.json", st)
    if problems:
        st["end_reason"] = "preflight_failed"
        jdump("runner_state.json", st)
        raise SystemExit("preflight verification failed: " + "; ".join(problems))
    if A.validate_only:
        st["end_reason"] = "validate_only"
        jdump("runner_state.json", st)
        event("validate_only_done", effective=eff)
        return 0
    # ---- dispatch the one prompt ----------------------------------------------------------------------------------
    stop = threading.Event()
    threading.Thread(target=sse_capture, args=(sid, stop), daemon=True).start()
    time.sleep(2)

    def post(text, kind):
        key = f"{A.run_id}-{A.label}-{kind}-{uuid.uuid4().hex[:12]}"
        r = api("POST", f"/v1/sessions/{sid}/messages", {
            "text": text, "client_message_id": key, "idempotency_key": key, "delivery": "auto",
            "metadata": {"thesis_run_id": A.run_id, "runner_kind": kind}, "behavior": freeze["message_behavior"]}, tries=4, timeout=120)
        st.setdefault("messages", []).append({"kind": kind, "utc": now(), "client_message_id": key,
                                              "message_id": r.get("id") or (r.get("message") or {}).get("id")})
        jdump(f"message_{kind}_{len(st['messages'])}.json", r)
        jdump("runner_state.json", st)
        event("message_posted", kind=kind)

    st["start_utc"] = now()
    t0 = time.time()
    post(prompt, "task")
    seen_running, idle_streak, nudges, end_reason = False, 0, 0, None
    while True:
        time.sleep(A.poll_s)
        try:
            s = api("GET", f"/v1/sessions/{sid}", tries=3)
        except Exception as e:
            event("poll_error", error=str(e))
            if time.time() - t0 >= A.timeout_s:
                end_reason = "timeout"
                break
            continue
        status = s.get("status")
        with open(POLL_F, "a") as f:
            f.write(json.dumps({"utc": now(), "status": status, "message_count": s.get("message_count"),
                                "cost_usd": s.get("cost_usd"), "agent_jobs": agent_job_ids()}) + "\n")
        if status == "running":
            seen_running, idle_streak = True, 0
        elif status in ("waiting_permission", "waiting_user"):
            end_reason = f"stopped_{status}"   # never answered: a headless baseline cannot answer either
            break
        elif status in ("error", "cancelled"):
            end_reason = status
            break
        elif status == "idle":
            idle_streak += 1
            if (seen_running or time.time() - t0 > 120) and idle_streak >= 2:
                summary = os.path.join(A.trial_dir, "work", "run_summary.md")
                if nudges < A.max_nudges and not os.path.exists(summary):
                    post(NUDGE.format(why="work/run_summary.md does not exist"), "nudge")
                    nudges, seen_running, idle_streak = nudges + 1, False, 0
                    continue
                end_reason = "finished_idle"
                break
        if time.time() - t0 >= A.timeout_s:
            end_reason = "timeout"
            break
    if end_reason != "finished_idle":
        try:
            jdump("cancel_response.json", api("POST", f"/v1/sessions/{sid}/cancel", {}, tries=2))
        except Exception as e:
            event("cancel_failed", error=str(e))
        time.sleep(20)
    st.update(end_utc=now(), end_reason=end_reason, timeout_hit=end_reason == "timeout", nudges_sent=nudges)
    jdump("runner_state.json", st)
    event("session_ended", end_reason=end_reason)
    time.sleep(5)
    stop.set()
    # ---- retain the complete CLIO session record ----------------------------------------------------------------------
    for name, path in (("session_final", f"/v1/sessions/{sid}"), ("export_transcript", f"/v1/sessions/{sid}/export?mode=transcript"),
                       ("export_full", f"/v1/sessions/{sid}/export?mode=full"),
                       ("messages", f"/v1/sessions/{sid}/messages?limit=100000&include_system=true"),
                       ("trace", f"/v1/sessions/{sid}/trace"), ("interactions", f"/v1/sessions/{sid}/interactions"),
                       ("questions", f"/v1/sessions/{sid}/questions"), ("attempts", f"/v1/sessions/{sid}/attempts"),
                       ("agent_tasks", f"/v1/sessions/{sid}/agent-tasks"), ("provenance_execution", f"/v1/sessions/{sid}/provenance/execution"),
                       ("session_blueprint_final", f"/v1/sessions/{sid}/agent-blueprint"), ("permissions_at_end", "/v1/permissions")):
        try:
            jdump(f"{name}.json", api("GET", path, tries=3, timeout=300, ok404=True))
        except Exception as e:
            event("collect_failed", name=name, error=str(e))
    msgs = json.load(open(os.path.join(EV, "messages.json"))) or {}
    ml = msgs if isinstance(msgs, list) else msgs.get("messages") or msgs.get("items") or []
    st["user_messages_in_session"] = sum(1 for m in ml if m.get("role") == "user")
    st["runner_end_utc"] = now()
    jdump("runner_state.json", st)
    event("runner_done", end_reason=end_reason, user_messages=st["user_messages_in_session"])
    return 0 if end_reason == "finished_idle" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit as e:
        event("runner_stop", reason=str(e))
        sys.exit(e.code if isinstance(e.code, int) else 3)
    except Exception as e:
        event("runner_exception", error=repr(e))
        try:  # never leave a session running behind a failed runner
            sid = json.load(open(STATE_F)).get("session_id")
            if sid:
                api("POST", f"/v1/sessions/{sid}/cancel", {}, tries=2)
                event("session_cancelled_after_exception", session_id=sid)
        except Exception as e2:
            event("cancel_after_exception_failed", error=repr(e2))
        sys.exit(1)
