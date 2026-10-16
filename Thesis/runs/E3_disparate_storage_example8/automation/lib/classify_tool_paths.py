#!/usr/bin/env python3
"""Classify absolute paths used in an agent's tool inputs (read-only analysis).

Usage: classify_tool_paths.py <tool_inputs.jsonl> <forbidden_roots.txt> <allowed_roots.txt>
  tool_inputs.jsonl : one JSON object per tool call: {"id":..., "name":..., "input":{...}}
  forbidden_roots   : one absolute root per line; any path at or under one is FORBIDDEN
  allowed_roots     : one absolute root per line (permitted collections, trial root, staging dir, software)
Output (TSV on stdout): verdict  tool_use_id  tool  path
  (paths inside an allowed root are never reported; allowed roots take precedence)
  FORBIDDEN  path at/under a forbidden root
  ANCESTOR   path is a strict ancestor of a forbidden root and not inside an allowed root (broad scan: review)
Exit 0 always; the caller decides.
"""
import json, os, re, sys

PATH_RE = re.compile(r"(/(?:[A-Za-z0-9._~+@%-]+/?)+)")

def norm(p):
    return os.path.normpath(p)

def under(p, r):
    return p == r or p.startswith(r.rstrip("/") + "/")

def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)

def main():
    calls, forb, allow = sys.argv[1], sys.argv[2], sys.argv[3]
    forbidden = [norm(l.strip()) for l in open(forb) if l.strip()]
    allowed = [norm(l.strip()) for l in open(allow) if l.strip()]
    seen = set()
    for line in open(calls):
        try:
            c = json.loads(line)
        except Exception:
            continue
        for s in strings(c.get("input", {})):
            for m in PATH_RE.findall(s):
                p = norm(m)
                key = (c.get("id"), p)
                if key in seen or len(p) < 2:
                    continue
                seen.add(key)
                if any(under(p, a) for a in allowed):
                    continue
                if any(under(p, r) for r in forbidden):
                    v = "FORBIDDEN"
                elif any(under(r, p) and r != p for r in forbidden) and not any(under(p, a) for a in allowed):
                    v = "ANCESTOR"
                else:
                    continue
                print(f"{v}\t{c.get('id','')}\t{c.get('name','')}\t{p}")

if __name__ == "__main__":
    main()
