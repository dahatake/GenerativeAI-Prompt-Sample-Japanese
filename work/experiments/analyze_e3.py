"""Analyse v2 (E3) together with v1 (E1) per preregistration_v2.md.

Run-level metric = hidden requirements passed / requirements. Tests are one-sided
stratified (by task) permutation tests on the difference of means; exact when the
number of relabelings is <= 200k, otherwise Monte Carlo with 100k draws (seed 0).
Output: data/summary_e3.json and a printed table.
"""
import csv, itertools, json, math, os, random, statistics, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def load(corrected=False):
    """corrected=True applies the post-hoc T5S window check to T5 R1 (sensitivity analysis)."""
    runs = []
    for r in csv.DictReader(open(os.path.join(DATA, "scores_e1.csv"), encoding="utf-8")):
        runs.append({"run_id": r["run_id"], "task": r["task"], "cond": r["condition"], "src": "v1",
                     "score": int(r["hidden_pass"]) / 4})
    for r in csv.DictReader(open(os.path.join(DATA, "scores_e3.csv"), encoding="utf-8")):
        n = int(r["n_req"])
        hp = int(r["hidden_pass"])
        if corrected and r["task"] == "T5" and r["R1"] == "True" and r.get("T5S_window28") != "True":
            hp -= 1
        runs.append({"run_id": r["run_id"], "task": r["task"], "cond": r["condition"], "src": "v2",
                     "score": hp / n, "row": r})
        if r["condition"] == "BPOST" and r.get("p1_hidden_pass"):
            p1 = int(r["p1_hidden_pass"])
            if corrected and r["task"] == "T5" and r.get("p1_T5S_window28") != "True":
                p1 -= 1  # all T5 p1 snapshots passed preregistered R1
            runs.append({"run_id": r["run_id"] + "@p1", "task": r["task"], "cond": "B", "src": "v2-p1",
                         "score": p1 / n})
    return runs


def perm_test(groups_a, groups_b, n_mc=100_000):
    """groups_*: {task: [scores]}. One-sided p for mean(A) - mean(B) >= observed (pooled over runs)."""
    tasks = sorted(set(groups_a) & set(groups_b))
    pools = [(groups_a[t] + groups_b[t], len(groups_a[t])) for t in tasks]
    n_a = sum(k for _, k in pools)
    n_b = sum(len(p) - k for p, k in pools)
    total = [sum(p) for p, _ in pools]

    def stat(sum_a):
        return sum_a / n_a - (sum(total) - sum_a) / n_b

    obs = stat(sum(sum(groups_a[t]) for t in tasks))
    n_comb = math.prod(math.comb(len(p), k) for p, k in pools)
    if n_comb <= 200_000:
        per_task = [[sum(c) for c in itertools.combinations(p, k)] for p, k in pools]
        hits = sum(1 for combo in itertools.product(*per_task) if stat(sum(combo)) >= obs - 1e-12)
        return obs, hits / n_comb, "exact", n_comb
    rng = random.Random(0)
    hits = 0
    for _ in range(n_mc):
        s = 0
        for p, k in pools:
            s += sum(rng.sample(p, k))
        hits += stat(s) >= obs - 1e-12
    return obs, (hits + 1) / (n_mc + 1), "monte_carlo", n_mc


def by_task(runs, conds, tasks, srcs=None):
    g = {}
    for r in runs:
        if r["cond"] in conds and r["task"] in tasks and (srcs is None or r["src"] in srcs):
            g.setdefault(r["task"], []).append(r["score"])
    return g


def t3s_all():
    """Apply supplemental T3S to every T3 solution (v1 artifacts and v2 finals)."""
    out = {}
    tests = os.path.join(HERE, "hidden", "hidden_tests_v2.py")
    dirs = [(n, os.path.join(DATA, "artifacts", n)) for n in os.listdir(os.path.join(DATA, "artifacts")) if n.startswith("T3-")]
    dirs += [(n, os.path.join(DATA, "artifacts_e3", n, "final")) for n in os.listdir(os.path.join(DATA, "artifacts_e3")) if n.startswith("E3-T3-")]
    dirs += [(n + "@p1", os.path.join(DATA, "artifacts_e3", n, "p1")) for n in os.listdir(os.path.join(DATA, "artifacts_e3")) if n.startswith("E3-T3-BPOST")]
    for name, d in sorted(dirs):
        if os.path.exists(os.path.join(d, "solution.py")):
            p = subprocess.run([sys.executable, "-B", tests, "T3S", d], capture_output=True, text=True, encoding="utf-8")
            out[name] = json.loads(p.stdout.strip().splitlines()[-1]).get("R2_future_valid")
    return out


def main():
    runs = load()
    cells = {}
    for r in runs:
        cells.setdefault((r["task"], r["cond"]), []).append(r["score"])
    table = {f"{t}|{c}": {"n": len(v), "mean": round(statistics.mean(v), 3)} for (t, c), v in sorted(cells.items())}

    TC = ("TC", "TCP")
    T4 = ["T1", "T3", "T4", "T5"]
    tests = {
        # Preregistered comparisons (TC only: v1 TC for T1/T3, v2 TC for T4/T5)
        "PREREG_H7_TC_vs_BPOST(T1,T3,T4,T5)": (by_task(runs, ["TC"], T4), by_task(runs, ["BPOST"], T4)),
        "PREREG_H7_BPOST_vs_TC(T1,T3,T4,T5)": (by_task(runs, ["BPOST"], T4), by_task(runs, ["TC"], T4)),
        "PREREG_H8_TC_vs_NOASK(T1,T3,T4,T5)": (by_task(runs, ["TC"], T4), by_task(runs, ["NOASK"], T4)),
        "PREREG_H8b_B_vs_NOASK(T1,T3,T4,T5)": (by_task(runs, ["B"], T4), by_task(runs, ["NOASK"], T4)),
        # Exploratory: TC and TC+ pooled
        "H7_BPOSTfinal_vs_TCany(T1,T3,T4,T5)": (by_task(runs, TC, ["T1", "T3", "T4", "T5"]), by_task(runs, ["BPOST"], ["T1", "T3", "T4", "T5"])),
        "H8_TCany_vs_NOASK(T1,T3,T4,T5)": (by_task(runs, TC, ["T1", "T3", "T4", "T5"]), by_task(runs, ["NOASK"], ["T1", "T3", "T4", "T5"])),
        "H8b_NOASK_vs_B(T1,T3,T4,T5)": (by_task(runs, ["NOASK"], ["T1", "T3", "T4", "T5"]), by_task(runs, ["B"], ["T1", "T3", "T4", "T5"])),
        "H9_TCP_vs_TCv1(T3)": (by_task(runs, ["TCP"], ["T3"]), by_task(runs, ["TC"], ["T3"], {"v1"})),
        "H9b_TCP_vs_TCv1(T1,T3)": (by_task(runs, ["TCP"], ["T1", "T3"]), by_task(runs, ["TC"], ["T1", "T3"], {"v1"})),
        "H10_TCany_vs_Bp1(T4,T5)": (by_task(runs, TC, ["T4", "T5"]), by_task(runs, ["B"], ["T4", "T5"])),
        "H10b_TCany_vs_Bp1(T4)": (by_task(runs, TC, ["T4"]), by_task(runs, ["B"], ["T4"])),
        "pooled_TCany_vs_B(T1-T5,v1+v2)": (by_task(runs, TC, ["T1", "T2", "T3", "T4", "T5"]), by_task(runs, ["B"], ["T1", "T2", "T3", "T4", "T5"])),
    }
    res = {}
    for name, (a, b) in tests.items():
        obs, p, method, n = perm_test(a, b)
        res[name] = {"diff": round(obs, 3), "p_one_sided": round(p, 5), "method": method, "n_perm": n,
                     "n_a": sum(map(len, a.values())), "n_b": sum(map(len, b.values()))}

    # timing and rework (v2 only)
    timing, rework = {}, {}
    for r in runs:
        row = r.get("row")
        if not row:
            continue
        ph = json.loads(row["phase_seconds"] or "[]")
        key = f'{r["task"]}|{r["cond"]}'
        timing.setdefault(key, []).append(ph)
        if row.get("rework_changed_lines"):
            rework.setdefault(r["task"], []).append(int(row["rework_changed_lines"]))
    timing_sum = {}
    for k, v in sorted(timing.items()):
        timing_sum[k] = {"n": len(v), "p1_mean": round(statistics.mean(x[0] for x in v), 1),
                         "post_p1_mean": round(statistics.mean(sum(x[1:]) for x in v), 1) if all(len(x) > 1 for x in v) else None,
                         "total_mean": round(statistics.mean(sum(x) for x in v), 1)}
    followups = [r["run_id"] for r in runs if r.get("row") and r["row"]["followup_used"] == "True"]
    t5s = {r["run_id"]: (r["row"].get("p1_T5S_window28"), r["row"].get("T5S_window28")) for r in runs if r.get("row") and r["task"] == "T5"}
    out = {"cells": table, "tests": res, "timing_seconds": timing_sum,
           "rework_changed_lines_BPOST": {k: v for k, v in rework.items()},
           "tcp_followup_runs": followups, "T3S_R2_future_valid": t3s_all(), "T5S_window28_(p1,final)": t5s}
    cruns = load(corrected=True)
    ccells = {}
    for r in cruns:
        if r["task"] == "T5":
            ccells.setdefault(r["cond"], []).append(r["score"])
    out["sensitivity_T5S_corrected"] = {
        "T5_cells": {c: {"n": len(v), "mean": round(statistics.mean(v), 3)} for c, v in sorted(ccells.items())},
        "tests": {}}
    for name, (ca, cb, tasks) in {"H8_TCany_vs_NOASK(T1,T3,T4,T5)": (TC, ["NOASK"], ["T1", "T3", "T4", "T5"]),
                                  "PREREG_H8_TC_vs_NOASK(T1,T3,T4,T5)": (["TC"], ["NOASK"], T4),
                                  "PREREG_H7_TC_vs_BPOST(T1,T3,T4,T5)": (["TC"], ["BPOST"], T4),
                                  "H10_TCany_vs_Bp1(T4,T5)": (TC, ["B"], ["T4", "T5"]),
                                  "H10c_TCany_vs_Bp1(T5)": (TC, ["B"], ["T5"]),
                                  "H7_BPOSTfinal_vs_TCany(T1,T3,T4,T5)": (TC, ["BPOST"], ["T1", "T3", "T4", "T5"])}.items():
        obs, p, m, n = perm_test(by_task(cruns, ca, tasks), by_task(cruns, cb, tasks))
        out["sensitivity_T5S_corrected"]["tests"][name] = {"diff": round(obs, 3), "p_one_sided": round(p, 5), "method": m, "n_perm": n}
    def fisher_ge(a, n1, b, n2):
        k, N = a + b, n1 + n2
        return sum(math.comb(n1, x) * math.comb(n2, k - x) for x in range(a, min(n1, k) + 1)) / math.comb(N, k)
    e2 = list(csv.DictReader(open(os.path.join(DATA, "scores_e3_e2.csv"), encoding="utf-8")))
    bdod = sum(r["date_flag"] == "True" for r in e2 if r["condition"] == "BDOD")
    out["fisher_one_sided"] = {
        "H11_BDoD_dateflag_vs_B(v1 0/6)": {"a": f"{bdod}/3", "b": "0/6", "p": round(fisher_ge(bdod, 3, 0, 6), 4)},
        "BDoD_vs_G_GTB(v1 11/12)": {"a": "11/12", "b": f"{bdod}/3", "p": round(fisher_ge(11, 12, bdod, 3), 4)},
        "E2c_filter_block_first_attempt_B_vs_G+GTB": {"a": "3/3", "b": "1/6", "p": round(fisher_ge(3, 3, 1, 6), 4),
                                                       "note": "first attempts only (retries were conditional on being blocked)"},
    }
    json.dump(out, open(os.path.join(DATA, "summary_e3.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
