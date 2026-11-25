"""Analyse blinded adjudications (U7 disclosure, U11 reviewability).

Usage: python analyze_blind.py <blind_root | --archived>
Reads <blind_root>/<task>/judgments.json and data/blind_key.json; ground truth per
requirement comes from re-running the hidden tests on each archived solution.
Writes data/blind_judgments.json (de-anonymised) and data/summary_blind.json.
"""
import csv, json, os, subprocess, sys
from analyze_e3 import perm_test

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def cond_of(run):
    if run.endswith("@p1"):
        return "B"
    parts = run.split("-")
    c = parts[2] if run.startswith("E3-") else parts[1]
    return {"TCP": "TC", "TC": "TC"}.get(c, c)


def truth(task, sol_dir):
    tests, tname = ("hidden_tests.py", task) if task in ("T1", "T2", "T3") else ("hidden_tests_v2.py", task)
    p = subprocess.run([sys.executable, "-B", os.path.join(HERE, "hidden", tests), tname, os.path.join(HERE, sol_dir)],
                       capture_output=True, text=True, encoding="utf-8")
    res = json.loads(p.stdout.strip().splitlines()[-1])
    if task == "T5":
        # Exploratory correction (deviation D-v2-3): the preregistered R1 case cannot detect a 30-day window.
        q = subprocess.run([sys.executable, "-B", os.path.join(HERE, "hidden", "hidden_tests_v2.py"), "T5S", os.path.join(HERE, sol_dir)],
                           capture_output=True, text=True, encoding="utf-8")
        res["_R1_corrected"] = bool(res.get("R1")) and json.loads(q.stdout.strip().splitlines()[-1]).get("R1_window28") is True
    return res


def main():
    root = sys.argv[1]
    key = json.load(open(os.path.join(DATA, "blind_key.json"), encoding="utf-8"))
    kw = {r["run_id"]: r for r in csv.DictReader(open(os.path.join(DATA, "scores_e1.csv"), encoding="utf-8"))}
    rows = []
    for task in sorted({v["task"] for v in key.values()}):
        jp = os.path.join(DATA, "blind_judgments_raw", task + ".json") if root == "--archived" else os.path.join(root, task, "judgments.json")
        j = json.load(open(jp, encoding="utf-8"))
        for bid, reqs in j.items():
            k = key[bid]
            gt = truth(task, k["solution_dir"])
            for r, d in reqs.items():
                if r not in gt:
                    continue
                v = str(d.get("verdict", "")).lower()
                tc = gt["_R1_corrected"] if (task == "T5" and r == "R1") else bool(gt[r])
                rows.append({"blind_id": bid, "run": k["run"], "task": task, "cond": cond_of(k["run"]), "is_tcp": "-TCP-" in k["run"], "req": r,
                             "disclosed": str(d.get("disclosed", "")).lower() == "yes", "verdict": v,
                             "truth": bool(gt[r]),
                             "correct": (v == "met" and gt[r]) or (v == "unmet" and not gt[r]),
                             "false_met": v == "met" and not gt[r],
                             "truth_corrected": tc,
                             "correct_corrected": (v == "met" and tc) or (v == "unmet" and not tc),
                             "kw_disclosed": (kw[k["run"]][f"D_{r}"] == "True") if k["run"] in kw else None})
    json.dump(rows, open(os.path.join(DATA, "blind_judgments.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)

    def rate(sel, f):
        s = [x for x in rows if sel(x)]
        return {"n": len(s), "rate": round(sum(f(x) for x in s) / len(s), 3) if s else None}

    conds = ["B", "TC", "BPOST", "NOASK", "FULL"]
    out = {"disclosure_manual": {c: rate(lambda x, c=c: x["cond"] == c, lambda x: x["disclosed"]) for c in conds},
           "review_correct": {c: rate(lambda x, c=c: x["cond"] == c, lambda x: x["correct"]) for c in conds},
           "review_correct_T5S_corrected": {c: rate(lambda x, c=c: x["cond"] == c, lambda x: x["correct_corrected"]) for c in conds},
           "review_unclear": {c: rate(lambda x, c=c: x["cond"] == c, lambda x: x["verdict"] == "unclear") for c in conds},
           "review_false_met": {c: rate(lambda x, c=c: x["cond"] == c and not x["truth"], lambda x: x["false_met"]) for c in conds},
           "unmet_requirements_flagged": {c: rate(lambda x, c=c: x["cond"] == c and not x["truth"], lambda x: x["verdict"] == "unmet") for c in conds}}
    v1 = [x for x in rows if x["kw_disclosed"] is not None]
    agree = sum(x["kw_disclosed"] == x["disclosed"] for x in v1)
    out["keyword_vs_manual_v1"] = {"n": len(v1), "agreement": round(agree / len(v1), 3),
                                   "kw_no_manual_yes": sum((not x["kw_disclosed"]) and x["disclosed"] for x in v1),
                                   "kw_yes_manual_no": sum(x["kw_disclosed"] and not x["disclosed"] for x in v1)}

    def runlevel(cond, f, tc_only=False):
        g = {}
        for run in {x["run"] for x in rows if x["cond"] == cond and not (tc_only and x["is_tcp"])}:
            s = [x for x in rows if x["run"] == run]
            g.setdefault(s[0]["task"], []).append(sum(f(x) for x in s) / len(s))
        return g
    for name, f in [("H13_review_correct_TC_vs_B", lambda x: x["correct"]), ("H13_corrected_TC_vs_B", lambda x: x["correct_corrected"]),("U7_disclosed_TC_vs_B", lambda x: x["disclosed"])]:
        obs, p, m, n = perm_test(runlevel("TC", f), runlevel("B", f))
        out[name] = {"diff": round(obs, 3), "p_one_sided": round(p, 5), "method": m, "n_perm": n}
    for name, f in [("PREREG_H13_TConly_vs_B", lambda x: x["correct"]), ("PREREG_H13_TConly_vs_B_corrected", lambda x: x["correct_corrected"])]:
        obs, p, m, n = perm_test(runlevel("TC", f, tc_only=True), runlevel("B", f))
        out[name] = {"diff": round(obs, 3), "p_one_sided": round(p, 5), "method": m, "n_perm": n}
    json.dump(out, open(os.path.join(DATA, "summary_blind.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
