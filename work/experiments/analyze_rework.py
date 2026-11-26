"""U16 (H29): rework size vs task scale and Phase 1 failures, for all post-hoc correction runs.

Units: B-POST (v2 E3, v3 E4/E5; same session), E7a BALL and E7b OFULL/OFILE (v4; E7b in a new session).
Fields: n_req (4, 6, 10), p1_failed = n_req - p1_hidden_pass, rework_changed_lines (diff of solution.py, p1 -> final).
Usage: python analyze_rework.py  (descriptive only; Spearman rank correlation without a test)
"""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def spearman(x, y):
    def ranks(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                j += 1
            for k in range(i, j + 1):
                r[s[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


def load(f, cond_ok, nreq=None):
    out = []
    p = os.path.join(DATA, f)
    if not os.path.exists(p):
        return out
    for r in csv.DictReader(open(p, encoding="utf-8")):
        if not cond_ok(r) or r.get("rework_changed_lines", "") == "" or r.get("p1_hidden_pass", "") == "":
            continue
        n = int(r.get("n_req") or nreq or 4)
        if r["task"] == "T5":
            n = 6
        out.append({"src": f, "run_id": r["run_id"], "task": r["task"], "condition": r["condition"], "n_req": n,
                    "p1_failed": n - int(r["p1_hidden_pass"]), "final_failed": n - int(r["hidden_pass"]),
                    "rework": int(r["rework_changed_lines"])})
    return out


def main():
    rows = load("scores_e3.csv", lambda r: r["condition"] == "BPOST")
    rows += load("scores_e4.csv", lambda r: r["condition"] == "BPOST")
    rows += load("scores_e6.csv", lambda r: r["condition"] in ("BALL", "OFULL", "OFILE"))
    with open(os.path.join(DATA, "rework_vs_scale.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("n =", len(rows))
    for key in ("n_req", "p1_failed"):
        groups = {}
        for r in rows:
            groups.setdefault(r[key], []).append(r["rework"])
        print(key, {k: (len(v), round(sum(v) / len(v), 1), min(v), max(v)) for k, v in sorted(groups.items())})
    print("spearman rework~n_req", round(spearman([r["n_req"] for r in rows], [r["rework"] for r in rows]), 2))
    print("spearman rework~p1_failed", round(spearman([r["p1_failed"] for r in rows], [r["rework"] for r in rows]), 2))
    fixed = [r for r in rows if r["p1_failed"] > 0]
    print("total rework / total p1_failed (all runs):", round(sum(r["rework"] for r in rows) / sum(r["p1_failed"] for r in rows), 1), "lines")
    print("same, runs with p1_failed>0 only:", round(sum(r["rework"] for r in fixed) / sum(r["p1_failed"] for r in fixed), 1), "lines")


if __name__ == "__main__":
    main()
