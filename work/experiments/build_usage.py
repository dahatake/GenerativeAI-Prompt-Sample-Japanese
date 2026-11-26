"""Rebuild data/usage_by_agent.csv: per sub-agent model, tokens and API time, joined to the task name.

Sources (local, read-only):
  - ~/.copilot/session-store.db, table assistant_usage_events (copied to %TEMP% before reading)
  - ~/.copilot/session-state/<session>/events.jsonl: tool.execution_start (toolName=task, arguments.name)
    and the matching tool.execution_complete ("agent_id: <uuid>")
Usage: python build_usage.py
"""
import collections, csv, json, os, re, shutil, sqlite3, tempfile

HOME = os.path.expanduser("~")
SESSIONS = ["f6e132e2-2678-4ce4-974e-03a1e09dd9bd", "8bb72b71-4ffc-4108-a1de-1d5e982c0138"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "usage_by_agent.csv")


def agent_map():
    m = {}
    for s in SESSIONS:
        starts = {}
        for line in open(os.path.join(HOME, ".copilot", "session-state", s, "events.jsonl"), encoding="utf-8"):
            e = json.loads(line)
            d = e.get("data", {})
            if e.get("type") == "tool.execution_start" and d.get("toolName") == "task":
                a = d.get("arguments", {})
                starts[d["toolCallId"]] = (a.get("name"), a.get("agent_type"))
            elif e.get("type") == "tool.execution_complete" and d.get("toolCallId") in starts:
                g = re.search(r"agent_id: ([0-9a-f-]{36})", json.dumps(d.get("result", {})))
                if g:
                    m[g.group(1)] = starts[d["toolCallId"]]
    return m


def main():
    src = os.path.join(HOME, ".copilot", "session-store.db")
    tmp = os.path.join(tempfile.gettempdir(), "ss-usage-copy.db")
    for suf in ("", "-wal", "-shm"):
        if os.path.exists(src + suf):
            shutil.copy(src + suf, tmp + suf)
    amap = agent_map()
    c = sqlite3.connect(tmp)
    agg = collections.OrderedDict()
    q = ("select agent_id, model, input_tokens, output_tokens, cache_read_tokens, reasoning_tokens, duration_ms, created_at "
         "from assistant_usage_events where session_id in (?, ?) and agent_id is not null order by id")
    for aid, model, it, ot, cr, rt, ms, at in c.execute(q, SESSIONS):
        if aid not in amap:
            continue
        k = (aid, model)
        a = agg.setdefault(k, {"agent_id": aid, "name": amap[aid][0], "agent_type": amap[aid][1], "model": model, "calls": 0,
                               "input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0, "reasoning_tokens": 0,
                               "api_ms": 0, "first_at": at, "last_at": at})
        a["calls"] += 1
        a["input_tokens"] += it or 0
        a["output_tokens"] += ot or 0
        a["cache_read_tokens"] += cr or 0
        a["reasoning_tokens"] += rt or 0
        a["api_ms"] += ms or 0
        a["last_at"] = at
    rows = list(agg.values())
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"agents mapped={len(amap)} rows={len(rows)} unmapped_usage_agents="
          f"{c.execute('select count(distinct agent_id) from assistant_usage_events where session_id in (?, ?)', SESSIONS).fetchone()[0] - len({r['agent_id'] for r in rows})}")


if __name__ == "__main__":
    main()
