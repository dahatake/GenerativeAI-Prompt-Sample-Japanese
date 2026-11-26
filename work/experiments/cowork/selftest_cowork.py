"""Self-test of score_cowork.py on synthetic returns (run: python cowork/selftest_cowork.py). Uses a temp folder; no repository files are changed."""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
sys.path.insert(0, EXP)
sys.path.insert(0, HERE)
import score_e12 as s  # noqa: E402

GOOD = '''import csv, datetime, math
def monthly_sales(path):
    agg = {}
    for row in csv.DictReader(open(path, encoding="utf-8")):
        if row["status"] == "cancelled":
            continue
        t = datetime.datetime.fromisoformat(row["ordered_at"].replace("Z", "+00:00")) + datetime.timedelta(hours=9)
        k = t.strftime("%Y-%m")
        agg[k] = agg.get(k, 0) + int(row["amount_incl_tax"])
    agg = {k: math.floor(v / 1.1 + 1e-9) for k, v in agg.items()}
    ks = sorted(agg); y, m = map(int, ks[0].split("-")); end = ks[-1]
    while "%04d-%02d" % (y, m) <= end:
        agg.setdefault("%04d-%02d" % (y, m), 0); m += 1
        if m == 13: y, m = y + 1, 1
    return dict(sorted(agg.items()))
'''
HARD = "def monthly_sales(path):\n    return %s\n" % json.dumps(s.compute(True, True, True, True, "floor"))
EVIL = "import socket\ndef monthly_sales(path):\n    return {}\n"
fence = lambda c: "```python\n" + c + "```\n"

with tempfile.TemporaryDirectory() as td:
    def run(name, arm, dict_text, conv=None, files=None):
        d = os.path.join(td, name)
        os.makedirs(d)
        open(os.path.join(d, "meta.txt"), "w", encoding="utf-8").write(f"run: {name}\narm: {arm}\ncowork_asked_questions (count): 2\n")
        if dict_text is not None:
            open(os.path.join(d, "final_dict.json"), "w", encoding="utf-8").write(dict_text)
        if conv is not None:
            open(os.path.join(d, "conversation.txt"), "w", encoding="utf-8").write(conv)
        for fn, c in (files or {}).items():
            open(os.path.join(d, fn), "w", encoding="utf-8").write(c)
    full = json.dumps(s.compute(True, True, True, True, "floor"))
    run("run-01", "B", "Example format {\"YYYY-MM\": 0}. Result: " + json.dumps(s.compute(True, False, False, False, "floor")), conv=fence(GOOD))   # example dict must be ignored; code correct
    run("run-02", "TCP", full, conv="blah " + fence(HARD))                                   # hard-coded code: passes supplied data, fails held-out
    run("run-03", "B", "null", conv=fence(EVIL))                                              # unsafe code not executed; no dict
    run("run-04", "TCP", json.dumps(s.compute(True, True, False, True, "floor")) + " then final " + full, files={"solution.py": GOOD})  # multiple candidates; file code
    os.makedirs(os.path.join(td, "run-04", "try1"))
    # run-05 / run-06 not started
    out = subprocess.run([sys.executable, os.path.join(HERE, "score_cowork.py"), td], capture_output=True, text=True, encoding="utf-8")
    print(out.stdout + out.stderr)
    import csv
    rows = {r["run"]: r for r in csv.DictReader(open(os.path.join(td, "cowork_scores.csv"), encoding="utf-8-sig"))}
    assert rows["run-01"]["reported_score"] == "1" and rows["run-01"]["reported_candidates"] == "1", rows["run-01"]
    assert rows["run-01"]["code_score_supplied_data"] == "4" and rows["run-01"]["code_score_heldout"] == "4", rows["run-01"]
    assert rows["run-02"]["reported_score"] == "4" and rows["run-02"]["code_score_supplied_data"] == "4" and rows["run-02"]["code_score_heldout"] == "undecidable", rows["run-02"]
    assert rows["run-03"]["reported_score"] == "undecidable" and "not executed: import socket" in rows["run-03"]["code_status"], rows["run-03"]
    assert rows["run-04"]["reported_score"] == "4" and "multiple" in rows["run-04"]["reported_status"] and rows["run-04"]["attempts"] == "2", rows["run-04"]
    assert rows["run-04"]["code_score_heldout"] == "4" and rows["run-04"]["code_source"] == "solution.py", rows["run-04"]
    assert rows["run-05"]["status"] == "not started" and rows["run-06"]["reported_score"] == "not started", rows["run-05"]
    print("SELFTEST OK")
