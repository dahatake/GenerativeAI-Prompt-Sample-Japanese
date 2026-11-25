"""Score addendum-B runs (E3-RT): regression-test instruction vs control, from T5-B-POST-1's Phase-1 state.

Usage: python score_rt.py [<sandbox_root>]   (omit to rescore data/artifacts_e3/RT-*/final)
Writes data/scores_e3_rt.csv; with a sandbox root, also archives artifacts to data/artifacts_e3/RT-*/final.
"""
import csv, difflib, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
TESTS = os.path.join(HERE, "hidden", "hidden_tests_v2.py")
P1 = os.path.join(DATA, "artifacts_e3", "E3-T5-BPOST-1", "p1", "solution.py")


def run(task, d):
    p = subprocess.run([sys.executable, "-B", TESTS, task, d], capture_output=True, text=True, encoding="utf-8")
    return json.loads(p.stdout.strip().splitlines()[-1])


def read(p):
    for q in (p, p + ".txt"):
        if os.path.exists(q):
            return open(q, encoding="utf-8", errors="ignore").read()
    return ""


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else None
    rows = []
    base = open(P1, encoding="utf-8").read().splitlines()
    for cond in ("CTRL", "RT"):
        for i in (1, 2, 3):
            rid = f"RT-{cond}-{i}"
            dst = os.path.join(DATA, "artifacts_e3", rid, "final")
            if root:
                os.makedirs(dst, exist_ok=True)
                for n in ("solution.py", "test_solution.py", "report.md", "answers.md", "timing.txt"):
                    s = os.path.join(root, rid, n)
                    if os.path.exists(s):
                        shutil.copy(s, os.path.join(dst, n + ".txt" if n.endswith(".md") else n))
            h, s5 = run("T5", dst), run("T5S", dst)
            sol = open(os.path.join(dst, "solution.py"), encoding="utf-8").read().splitlines()
            changed = sum(1 for l in difflib.unified_diff(base, sol, lineterm="", n=0) if l[:1] in "+-" and not l.startswith(("+++", "---")))
            t = [float(x) for x in read(os.path.join(dst, "timing.txt")).split()]
            rep = read(os.path.join(dst, "report.md"))
            rows.append({"run_id": rid, "condition": cond, **{f"R{k}": h.get(f"R{k}") for k in range(1, 7)},
                         "T5S_window28": s5.get("R1_window28"), "changed_lines": changed,
                         "seconds": round(t[1] - t[0], 1) if len(t) >= 2 else "",
                         "wrote_tests": os.path.exists(os.path.join(dst, "test_solution.py")),
                         "flagged_equality_question": bool(re.search(r"ちょうど|等しい|equal", rep, re.I))})
    with open(os.path.join(DATA, "scores_e3_rt.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
