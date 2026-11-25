"""Post-hoc supplementary scoring of T6 (exploratory, deviation D-v3-4).

1. Validates hidden/hidden_tests_v3s.py on the full reference (must pass all) and on every mutant of validate_t6.py
   (records which supplementary checks each mutant fails) -> data/t6s_validation.json
2. Scores every E5 artifact (p1 and final) -> data/scores_t6s.csv

Usage: python score_t6s.py
"""
import csv, glob, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from validate_t6 import EXPECTED, NAIVE, variant  # noqa: E402

TESTS = os.path.join(HERE, "hidden", "hidden_tests_v3s.py")


def run(d):
    p = subprocess.run([sys.executable, "-B", TESTS, d], capture_output=True, text=True, encoding="utf-8")
    return json.loads(p.stdout.strip().splitlines()[-1])


def main():
    tmp = tempfile.mkdtemp(prefix="t6s_")
    val = {}
    for m in list(EXPECTED) + ["naive"]:
        muts = NAIVE if m == "naive" else ([m] if m else [])
        r = run(variant(muts, os.path.join(tmp, m or "full")))
        val[m or "full"] = {k: r.get(k) for k in ("S56", "S7", "E2E")}
    shutil.rmtree(tmp, ignore_errors=True)
    json.dump(val, open(os.path.join(HERE, "data", "t6s_validation.json"), "w", encoding="utf-8"), indent=1)
    for k, v in val.items():
        print(f"{k:20s}", v)
    rows = []
    for d in sorted(glob.glob(os.path.join(HERE, "data", "artifacts_e4", "E5-T6-*", "*"))):
        if not os.path.exists(os.path.join(d, "solution.py")):
            continue
        r = run(d)
        rows.append({"run_id": os.path.basename(os.path.dirname(d)), "phase": os.path.basename(d),
                     "S56": r.get("S56"), "S7": r.get("S7"), "E2E": r.get("E2E"),
                     "E2E_mismatch_months": ";".join(r.get("E2E_mismatch", [])),
                     "errors": json.dumps(r.get("errors", {}), ensure_ascii=False)})
    with open(os.path.join(HERE, "data", "scores_t6s.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r["run_id"], r["phase"], r["S56"], r["S7"], r["E2E"], r["E2E_mismatch_months"], r["errors"][:120])


if __name__ == "__main__":
    main()
