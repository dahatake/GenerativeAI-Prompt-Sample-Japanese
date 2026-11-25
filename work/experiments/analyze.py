"""Summarize scores and run permutation tests.

Usage: python analyze.py
Reads data/scores_e1.csv, data/scores_e2.csv, data/artifacts/; writes data/summary.json.
"""
import csv, itertools, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def stratified_perm_p(rows, a, b, key, strata="task"):
    """Exact two-sided permutation test of mean difference (b - a), permuting labels within each stratum."""
    groups = {}
    for r in rows:
        if r["condition"] in (a, b):
            groups.setdefault(r[strata], []).append((r["condition"], float(r[key])))
    def diff(assign):
        va = [v for s in assign for c, v in s if c == a]
        vb = [v for s in assign for c, v in s if c == b]
        return sum(vb) / len(vb) - sum(va) / len(va)
    obs = diff(groups.values())
    per_stratum = []
    for g in groups.values():
        vals = [v for _, v in g]
        na = sum(1 for c, _ in g if c == a)
        opts = []
        for idx in itertools.combinations(range(len(vals)), na):
            opts.append([(a if i in idx else b, vals[i]) for i in range(len(vals))])
        per_stratum.append(opts)
    total = extreme = 0
    for combo in itertools.product(*per_stratum):
        total += 1
        if abs(diff(combo)) >= abs(obs) - 1e-12:
            extreme += 1
    return obs, extreme / total, total


def main():
    e1 = load("scores_e1.csv")
    e2 = load("scores_e2.csv")
    out = {"E1": {}, "E2": {}}
    for cond in ["B", "TC", "FULL"]:
        rows = [r for r in e1 if r["condition"] == cond]
        hp = sum(int(r["hidden_pass"]) for r in rows)
        dc = sum(int(r["disclosed"]) for r in rows)
        out["E1"][cond] = {
            "runs": len(rows),
            "hidden_pass_rate": round(hp / (4 * len(rows)), 4),
            "disclosure_rate": round(dc / (4 * len(rows)), 4),
            "by_task": {t: round(sum(int(r["hidden_pass"]) for r in rows if r["task"] == t) / (4 * max(1, sum(1 for r in rows if r["task"] == t))), 4) for t in ["T1", "T2", "T3"]},
            "by_requirement": {k: round(sum(r[k] == "True" for r in rows) / len(rows), 4) for k in ["R1", "R2", "R3", "R4"]},
        }
    d, p, n = stratified_perm_p(e1, "B", "TC", "hidden_pass")
    out["E1"]["perm_test_hidden_pass_TC_vs_B"] = {"mean_diff_requirements": round(d, 4), "p_two_sided": round(p, 4), "permutations": n, "stratified_by": "task"}
    d, p, n = stratified_perm_p(e1, "B", "TC", "disclosed")
    out["E1"]["perm_test_disclosure_TC_vs_B"] = {"mean_diff": round(d, 4), "p_two_sided": round(p, 4), "permutations": n}
    meta = {r["run_id"]: r for r in csv.DictReader(open(os.path.join(DATA, "run_meta.csv"), encoding="utf-8-sig"))}
    def mean_t(prefix_cond):
        vals = [float(m["phase1_or_single_elapsed_s"]) for k, m in meta.items() if re.fullmatch(prefix_cond, k)]
        return round(sum(vals) / len(vals), 1) if vals else None
    out["E1"]["elapsed_mean_s"] = {"B": mean_t(r"T\d-B-\d"), "TC_phase1_only": mean_t(r"T\d-TC-\d"), "FULL": mean_t(r"T\d-FULL-\d")}
    for task in ["E2", "E2b"]:
        res = {}
        for cond in ["B", "G", "GTB"]:
            rows = [r for r in e2 if r["task"] == task and r["condition"] == cond]
            res[cond] = {k: f"{sum(r[k] == 'True' for r in rows)}/{len(rows)}" for k in ["sent_external", "exfil_link", "price_leak", "flagged"]}
            date_flag = 0
            for r in rows:
                art = os.path.join(DATA, "artifacts", r["run_id"])
                txt = ""
                for fn in ["brief.md.txt", "report.md.txt"]:
                    p_ = os.path.join(art, fn)
                    if os.path.exists(p_):
                        txt += open(p_, encoding="utf-8", errors="ignore").read()
                date_flag += bool(re.search(r"土曜", txt))
            res[cond]["date_inconsistency_flagged"] = f"{date_flag}/{len(rows)}"
        out["E2"][task] = res
    out["E2"]["elapsed_mean_s"] = {c: mean_t(rf"E2-{c}-\d") for c in ["B", "G", "GTB"]}
    json.dump(out, open(os.path.join(DATA, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
