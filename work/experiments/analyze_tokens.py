"""U17: tokens and API time per condition, from data/usage_by_agent.csv (built by build_usage.py).

Subject agents are matched by task name == run_id (one agent per run; later phases continue the same agent with
write_agent, so its usage covers all phases. E7b Phase 2 is a separate new-session agent). When a run_id appears more
than once (re-launched runs, including the v3 GPT-6.2 Sol re-runs named "<run_id>b"), the last agent (by first_at) is
used, because it produced the scored artifacts.
Oracle agents (names starting with "oracle") are aggregated separately by the run they answered.
Usage: python analyze_tokens.py  -> data/tokens_by_condition.csv
"""
import collections, csv, os, re, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
PAT = [
    (r"^(T[123])-(B|TC|FULL)-(\d)$", lambda m: ("v1", "E1", "opus-default", m[1], m[2])),
    (r"^E3-(T\d)-(BPOST|TC|TCP|NOASK|FULL)-(\d)$", lambda m: ("v2", "E3", "opus-default", m[1], m[2])),
    (r"^E4-(mai|son|gpt)-(T\d)-(BPOST|TCP|NOASK)-(\d)b?$", lambda m: ("v3", "E4", m[1], m[2], m[3])),
    (r"^E5-(T6)-(BPOST|TCP|NOASK|FULL)-(\d)$", lambda m: ("v3", "E5", "opus-default", m[1], m[2])),
    (r"^E6-(mai|gpt)-(T\d)-(TCP|TCPCL)-(\d)$", lambda m: ("v4", "E6", m[1], m[2], m[3])),
    (r"^E7a-(mai|gpt)-(T\d)-(BALL)-(\d)$", lambda m: ("v4", "E7a", m[1], m[2], m[3])),
    (r"^E7b-(mai|gpt)-(T\d)-(OFULL|OFILE)-(\d)$", lambda m: ("v4", "E7b-p2", m[1], m[2], m[3])),
]


def classify(name):
    for p, f in PAT:
        m = re.match(p, name or "")
        if m:
            return f(m)
    return None


def main():
    rows = list(csv.DictReader(open(os.path.join(DATA, "usage_by_agent.csv"), encoding="utf-8")))
    last = {}
    for r in sorted(rows, key=lambda r: r["first_at"]):
        if classify(r["name"]):
            # v3 GPT-6.2 Sol runs were re-launched as "<run_id>b" (D-v3-1); the last-launched agent produced the scored artifacts
            last[re.sub(r"(-\d)b$", r"\1", r["name"])] = r
    groups = collections.defaultdict(list)
    for name, r in last.items():
        groups[classify(name)].append(r)
    out = []
    for k in sorted(groups):
        g = groups[k]
        tot = [int(r["input_tokens"]) + int(r["output_tokens"]) for r in g]
        out.append({"version": k[0], "experiment": k[1], "model": k[2], "task": k[3], "condition": k[4], "n": len(g),
                    "subject_model": ",".join(sorted({r["model"] for r in g})),
                    "mean_input_tokens": round(statistics.mean(int(r["input_tokens"]) for r in g)),
                    "mean_cache_read_tokens": round(statistics.mean(int(r["cache_read_tokens"]) for r in g)),
                    "mean_output_tokens": round(statistics.mean(int(r["output_tokens"]) for r in g)),
                    "mean_total_tokens": round(statistics.mean(tot)),
                    "mean_api_seconds": round(statistics.mean(int(r["api_ms"]) for r in g) / 1000, 1),
                    "mean_calls": round(statistics.mean(int(r["calls"]) for r in g), 1)})
    with open(os.path.join(DATA, "tokens_by_condition.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    orc = collections.defaultdict(list)
    for r in rows:
        if (r["name"] or "").startswith("oracle"):
            orc[r["model"]].append(int(r["input_tokens"]) + int(r["output_tokens"]))
    for o in out:
        print({k: o[k] for k in ("version", "experiment", "model", "task", "condition", "n", "mean_total_tokens", "mean_output_tokens", "mean_api_seconds")})
    print("oracle agents by model:", {m: (len(v), round(statistics.mean(v))) for m, v in orc.items()})


if __name__ == "__main__":
    main()
