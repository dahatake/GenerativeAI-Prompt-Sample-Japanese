"""Analyse v3 (E4 multi-model replication, E5 long task T6) per preregistration_v3.md.

Usage: python analyze_e4.py   -> data/summary_e4.json
Run-level metric = hidden requirements passed / requirements. Permutation tests are one-sided and stratified
(by model x task for E4, by task for E5); exact when <= 200k relabelings, else Monte Carlo 100k (seed 0).
The harness-default model's v2 runs (scores_e3.csv, T1/T3/T4) are included as model "default" for reference.
"""
import csv, json, math, os, statistics
from analyze_e3 import perm_test

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SHORT = {"mai-code-2-flash": "MAI-2.0 Flash", "claude-sonnet-5.5": "Sonnet-5.5", "gpt-6.2-sol": "GPT-6.2 Sol", "harness-default": "default"}


def load():
    runs = []
    for r in csv.DictReader(open(os.path.join(DATA, "scores_e4.csv"), encoding="utf-8")):
        n = int(r["n_req"])
        m = SHORT.get(r["model"], r["model"])
        runs.append({"exp": r["experiment"], "model": m, "task": r["task"], "cond": r["condition"],
                     "score": int(r["hidden_pass"]) / n, "row": r})
        if r["condition"] == "BPOST" and r.get("p1_hidden_pass"):
            runs.append({"exp": r["experiment"], "model": m, "task": r["task"], "cond": "B",
                         "score": int(r["p1_hidden_pass"]) / n, "row": None})
    for r in csv.DictReader(open(os.path.join(DATA, "scores_e3.csv"), encoding="utf-8")):
        if r["task"] in ("T1", "T3", "T4") and r["condition"] in ("BPOST", "TCP", "NOASK"):
            n = int(r["n_req"])
            runs.append({"exp": "E3", "model": "default", "task": r["task"], "cond": r["condition"], "score": int(r["hidden_pass"]) / n, "row": None})
            if r["condition"] == "BPOST" and r.get("p1_hidden_pass"):
                runs.append({"exp": "E3", "model": "default", "task": r["task"], "cond": "B", "score": int(r["p1_hidden_pass"]) / n, "row": None})
    return runs


def strata(runs, conds, models, tasks, exp="E4"):
    g = {}
    for r in runs:
        if r["cond"] in conds and r["model"] in models and r["task"] in tasks and (exp is None or r["exp"] == exp or (exp == "E4" and r["exp"] == "E3")):
            g.setdefault(f'{r["model"]}|{r["task"]}', []).append(r["score"])
    return g


def test(a, b):
    obs, p, m, n = perm_test(a, b)
    return {"diff": round(obs, 3), "p_one_sided": round(p, 5), "method": m, "n_perm": n,
            "n_a": sum(map(len, a.values())), "n_b": sum(map(len, b.values()))}


def mean(xs):
    return round(statistics.mean(xs), 3) if xs else None


def main():
    runs = load()
    new = ["MAI-2.0 Flash", "Sonnet-5.5", "GPT-6.2 Sol"]
    allm = new + ["default"]
    T = ["T1", "T3", "T4"]
    out = {"cells": {}, "tests": {}, "per_model": {}}
    for m in allm:
        for t in T + ["T6"]:
            for c in ["B", "BPOST", "TCP", "NOASK", "FULL"]:
                xs = [r["score"] for r in runs if r["model"] == m and r["task"] == t and r["cond"] == c]
                if xs:
                    out["cells"][f"{m}|{t}|{c}"] = {"n": len(xs), "mean": mean(xs), "scores": [round(x, 3) for x in xs]}
    out["tests"]["H15_TCP_vs_NOASK_3models"] = test(strata(runs, ["TCP"], new, T), strata(runs, ["NOASK"], new, T))
    out["tests"]["H16_B_vs_NOASK_3models"] = test(strata(runs, ["B"], new, T), strata(runs, ["NOASK"], new, T))
    out["tests"]["H16_NOASK_vs_B_3models"] = test(strata(runs, ["NOASK"], new, T), strata(runs, ["B"], new, T))
    out["tests"]["H17_TCP_vs_BPOST_3models"] = test(strata(runs, ["TCP"], new, T), strata(runs, ["BPOST"], new, T))
    out["tests"]["H17_BPOST_vs_TCP_3models"] = test(strata(runs, ["BPOST"], new, T), strata(runs, ["TCP"], new, T))
    out["tests"]["H15_TCP_vs_NOASK_4models_incl_default"] = test(strata(runs, ["TCP"], allm, T), strata(runs, ["NOASK"], allm, T))
    for m in allm:
        pm = {}
        for c in ["B", "BPOST", "TCP", "NOASK"]:
            pm[c] = mean([r["score"] for r in runs if r["model"] == m and r["task"] in T and r["cond"] == c])
        pm["TCP_minus_NOASK"] = round(pm["TCP"] - pm["NOASK"], 3) if pm["TCP"] is not None and pm["NOASK"] is not None else None
        pm["T3_TCP_full"] = f'{sum(1 for r in runs if r["model"] == m and r["task"] == "T3" and r["cond"] == "TCP" and r["score"] == 1)}/' \
                            f'{sum(1 for r in runs if r["model"] == m and r["task"] == "T3" and r["cond"] == "TCP")}'
        out["per_model"][m] = pm
    # failed requirements per model/cond (E4 rows)
    fails = {}
    for r in runs:
        row = r["row"]
        if row and r["exp"] == "E4":
            n = int(row["n_req"])
            key = f'{r["model"]}|{r["task"]}|{r["cond"]}'
            fails.setdefault(key, []).append(",".join(f"R{i}" for i in range(1, n + 1) if row.get(f"R{i}") != "True") or "-")
    out["failed_requirements_E4"] = fails
    # BPOST regressions, rework, followups, time
    extra = {}
    for r in runs:
        row = r["row"]
        if not row:
            continue
        key = f'{r["model"]}|{r["task"]}|{r["cond"]}'
        e = extra.setdefault(key, {"regressions": [], "rework_lines": [], "followup": 0, "seconds": []})
        if row.get("regressions"):
            e["regressions"].append(row["regressions"])
        if row.get("rework_changed_lines"):
            e["rework_lines"].append(int(row["rework_changed_lines"]))
        e["followup"] += row.get("followup_used") == "True"
        if row.get("active_seconds_total"):
            e["seconds"].append(float(row["active_seconds_total"]))
    for v in extra.values():
        v["seconds_mean"] = round(statistics.mean(v["seconds"]), 1) if v["seconds"] else None
        del v["seconds"]
    out["process"] = extra
    # E5 (T6)
    t6 = {c: [r["score"] for r in runs if r["task"] == "T6" and r["cond"] == c] for c in ["B", "BPOST", "TCP", "NOASK", "FULL"]}
    out["E5"] = {"cells": {c: {"n": len(v), "mean": mean(v), "scores": [round(x, 3) for x in v]} for c, v in t6.items() if v}}
    g = lambda c: {"T6": t6[c]}
    out["E5"]["H20_TCP_vs_NOASK"] = test(g("TCP"), g("NOASK"))
    out["E5"]["H21_TCP_vs_BPOST"] = test(g("TCP"), g("BPOST"))
    out["E5"]["TCP_vs_B_p1"] = test(g("TCP"), g("B"))
    out["E5"]["answer_items_specific"] = {r["row"]["run_id"]: (r["row"].get("answer_items"), r["row"].get("answer_items_specific"))
                                          for r in runs if r["row"] and r["task"] == "T6" and r["cond"] in ("BPOST", "TCP")}
    # E2c
    e2 = list(csv.DictReader(open(os.path.join(DATA, "scores_e4_e2c.csv"), encoding="utf-8")))
    tab = {}
    for r in e2:
        k = f'{SHORT.get(r["model"], r["model"])}|{r["condition"]}'
        t = tab.setdefault(k, {"n": 0, "brief": 0, "exfil_link": 0, "price_leak": 0, "sent_any": 0, "flagged_guideline": 0, "date_flag": 0})
        t["n"] += 1
        for f in ["brief_exists", "exfil_link", "price_leak", "sent_any", "flagged_guideline", "date_flag"]:
            t["brief" if f == "brief_exists" else f] += r[f] == "True"
    out["E2c"] = tab
    json.dump(out, open(os.path.join(DATA, "summary_e4.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ["tests", "per_model", "E2c"]}, ensure_ascii=False, indent=1))
    print(json.dumps(out["E5"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
