"""Analyse v4 (E6, E7a, E7b, E8) per preregistration_v4.md.

Usage: python analyze_e6.py   -> data/summary_e6.json
Run-level metric = hidden requirements passed / 4. Permutation tests are one-sided, stratified by model x task
(exact when <= 200k relabelings, else Monte Carlo; see analyze_e3.perm_test). Controls from v3 (scores_e4.csv):
TC+ (TCP) and B-POST for the same models and tasks. E7b is paired (same Phase 1 state): exact sign-flip test.
E8: one-sided Fisher exact test on price transcription counts.
"""
import csv, itertools, json, math, os, statistics
from analyze_e3 import perm_test

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SHORT = {"mai-code-2-flash": "mai", "gpt-6.2-sol": "gpt", "mai": "mai", "gpt": "gpt"}


def load():
    runs = []
    for r in csv.DictReader(open(os.path.join(DATA, "scores_e6.csv"), encoding="utf-8")):
        runs.append({"ver": "v4", "model": SHORT[r["model"]], "task": r["task"], "cond": r["condition"], "rep": r["rep"],
                     "score": int(r["hidden_pass"]) / 4, "p1": int(r["p1_hidden_pass"]) / 4 if r.get("p1_hidden_pass") else None, "row": r})
    for r in csv.DictReader(open(os.path.join(DATA, "scores_e4.csv"), encoding="utf-8")):
        m = SHORT.get(r["model"])
        if m and r["task"] in ("T1", "T4") and r["condition"] in ("TCP", "BPOST"):
            runs.append({"ver": "v3", "model": m, "task": r["task"], "cond": r["condition"], "rep": r["run_id"][-1],
                         "score": int(r["hidden_pass"]) / 4, "p1": int(r["p1_hidden_pass"]) / 4 if r.get("p1_hidden_pass") else None, "row": r})
    return runs


def strata(runs, pred):
    g = {}
    for r in runs:
        if pred(r):
            g.setdefault(f'{r["model"]}|{r["task"]}', []).append(r["score"])
    return g


def test(a, b):
    obs, p, m, n = perm_test(a, b)
    return {"diff": round(obs, 3), "p_one_sided": round(p, 5), "method": m, "n_perm": n,
            "n_a": sum(map(len, a.values())), "n_b": sum(map(len, b.values())),
            "mean_a": round(statistics.mean([x for v in a.values() for x in v]), 3),
            "mean_b": round(statistics.mean([x for v in b.values() for x in v]), 3)}


def paired_signflip(diffs):
    obs = sum(diffs)
    cnt = tot = 0
    for signs in itertools.product((1, -1), repeat=len(diffs)):
        s = sum(d * g for d, g in zip(diffs, signs))
        tot += 1
        cnt += s >= obs - 1e-12
    return {"n_pairs": len(diffs), "mean_diff": round(obs / len(diffs), 3), "p_one_sided": round(cnt / tot, 5), "diffs": diffs}


def fisher_less(a_yes, a_n, b_yes, b_n):
    """One-sided P(X <= a_yes) for group A count under the hypergeometric null (A has fewer 'yes' than B)."""
    K, N = a_yes + b_yes, a_n + b_n
    p = 0.0
    for x in range(0, a_yes + 1):
        if K - x > b_n or K - x < 0:
            continue
        p += math.comb(K, x) * math.comb(N - K, a_n - x) / math.comb(N, a_n)
    return round(p, 5)


def main():
    runs = load()
    out = {"cells": {}, "tests": {}}
    for r in runs:
        k = f'{r["ver"]}|{r["model"]}|{r["task"]}|{r["cond"]}'
        c = out["cells"].setdefault(k, {"scores": [], "p1": []})
        c["scores"].append(r["score"])
        if r["p1"] is not None:
            c["p1"].append(r["p1"])
    for c in out["cells"].values():
        c["mean"] = round(statistics.mean(c["scores"]), 3)
        c["p1_mean"] = round(statistics.mean(c["p1"]), 3) if c["p1"] else None
    tcpcl = strata(runs, lambda r: r["cond"] == "TCPCL")
    tcp_all = strata(runs, lambda r: r["cond"] == "TCP")
    tcp_v4 = strata(runs, lambda r: r["cond"] == "TCP" and r["ver"] == "v4")
    tcp_v3 = strata(runs, lambda r: r["cond"] == "TCP" and r["ver"] == "v3")
    out["tests"]["H23_TCPCL_vs_TCP_v3v4"] = test(tcpcl, tcp_all)
    out["tests"]["H23_TCPCL_vs_TCP_v4_only"] = test(tcpcl, tcp_v4)
    out["tests"]["ref_TCP_v4_vs_TCP_v3"] = test(tcp_v4, tcp_v3)
    ball = strata(runs, lambda r: r["cond"] == "BALL")
    bpost3 = strata(runs, lambda r: r["cond"] == "BPOST" and r["ver"] == "v3")
    out["tests"]["H24_BALL_vs_BPOST_v3"] = test(ball, bpost3)
    out["tests"]["ref_BALL_p1_vs_B_v3_p1"] = test(
        {k: [r["p1"] for r in runs if r["cond"] == "BALL" and f'{r["model"]}|{r["task"]}' == k] for k in ball},
        {k: [r["p1"] for r in runs if r["cond"] == "BPOST" and r["ver"] == "v3" and r["p1"] is not None and f'{r["model"]}|{r["task"]}' == k]
         for k in ball if any(r["cond"] == "BPOST" and r["ver"] == "v3" and r["p1"] is not None and f'{r["model"]}|{r["task"]}' == k for r in runs)})
    full = {(r["model"], r["task"], r["rep"]): r["score"] for r in runs if r["cond"] == "OFULL"}
    fil = {(r["model"], r["task"], r["rep"]): r["score"] for r in runs if r["cond"] == "OFILE"}
    out["tests"]["H25_OFULL_vs_OFILE_paired"] = paired_signflip([round(full[k] - fil[k], 3) for k in sorted(full)])
    out["tests"]["H25_pairs"] = {f"{k[0]}|{k[1]}|{k[2]}": {"OFULL": full[k], "OFILE": fil[k],
                                                          "p1": next(r["p1"] for r in runs if r["cond"] == "OFULL" and (r["model"], r["task"], r["rep"]) == k)}
                                 for k in sorted(full)}
    e8 = list(csv.DictReader(open(os.path.join(DATA, "scores_e6_e8.csv"), encoding="utf-8")))
    tab = {}
    for r in e8:
        t = tab.setdefault(r["condition"], {"n": 0, "price_leak": 0, "exfil_link": 0, "sent_any": 0, "flagged_guideline": 0})
        t["n"] += 1
        for f in ("price_leak", "exfil_link", "sent_any", "flagged_guideline"):
            t[f] += r[f] == "True"
    out["E8"] = tab
    out["tests"]["H26_GTB2_lt_G_price_leak_fisher"] = fisher_less(tab["GTB2"]["price_leak"], tab["GTB2"]["n"], tab["G"]["price_leak"], tab["G"]["n"])
    out["tests"]["H27_GTB_lt_G_price_leak_fisher"] = fisher_less(tab["GTB"]["price_leak"], tab["GTB"]["n"], tab["G"]["price_leak"], tab["G"]["n"])
    out["tests"]["ref_GTB2_lt_GTB_price_leak_fisher"] = fisher_less(tab["GTB2"]["price_leak"], tab["GTB2"]["n"], tab["GTB"]["price_leak"], tab["GTB"]["n"])
    fails = {}
    for r in runs:
        if r["ver"] == "v4":
            fails.setdefault(f'{r["model"]}|{r["task"]}|{r["cond"]}', []).append(
                ",".join(f"R{i}" for i in range(1, 5) if r["row"].get(f"R{i}") != "True") or "-")
    out["failed_requirements_v4"] = fails
    proc = {}
    for r in runs:
        if r["ver"] != "v4":
            continue
        k = f'{r["cond"]}'
        p = proc.setdefault(k, {"followup": 0, "n": 0, "rework": [], "answer_items": [], "answer_items_specific": [], "seconds": []})
        p["n"] += 1
        p["followup"] += r["row"]["followup_used"] == "True"
        if r["row"].get("rework_changed_lines"):
            p["rework"].append(int(r["row"]["rework_changed_lines"]))
        p["answer_items"].append(int(r["row"]["answer_items"]))
        p["answer_items_specific"].append(int(r["row"]["answer_items_specific"]))
        if r["row"].get("active_seconds_total"):
            p["seconds"].append(float(r["row"]["active_seconds_total"]))
    for p in proc.values():
        for f in ("rework", "answer_items", "answer_items_specific", "seconds"):
            p[f + "_mean"] = round(statistics.mean(p[f]), 1) if p[f] else None
            del p[f]
    out["process_v4"] = proc
    json.dump(out, open(os.path.join(DATA, "summary_e6.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("tests", "E8", "failed_requirements_v4", "process_v4")}, ensure_ascii=False, indent=1))
    for k, v in sorted(out["cells"].items()):
        print(k, v["mean"], v["scores"], "p1", v["p1_mean"])


if __name__ == "__main__":
    main()
