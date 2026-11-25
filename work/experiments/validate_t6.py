"""Mutation-test validation of the T6 hidden tests.

For every mutant (the full reference with exactly one business rule violated) the hidden tests must fail
exactly the expected requirement set, and the full reference must pass all. Also builds hidden/ref_naive_T6
(plausible defaults for every rule) and checks it fails every requirement.
Usage: python validate_t6.py   -> writes data/t6_mutation_matrix.json, exits 1 on any mismatch.
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "hidden", "ref_full_T6", "solution.py")
TESTS = os.path.join(HERE, "hidden", "hidden_tests_v3.py")
REQS = [f"R{i}" for i in range(1, 11)]
EXPECTED = {
    "": set(),
    "M1_utc": {"R1"}, "M2_completed_only": {"R2"}, "M2_not_cancelled": {"R2"},
    "M3_latest": {"R3"}, "M3_first": {"R3"}, "M4_flat10": {"R4"},
    "M5_no_discount": {"R5", "R6"}, "M5_after_tax": {"R5", "R6"}, "M6_round": {"R6"},
    "M7_per_line": {"R7"}, "M7_round": {"R7"}, "M8_csv_order": {"R8"}, "M8_first_order": {"R8"},
    "M9_zero_invoices": {"R9"}, "M10_file_order": {"R10"},
}
NAIVE = ["M1_utc", "M2_completed_only", "M3_latest", "M4_flat10", "M5_no_discount", "M7_per_line",
         "M8_csv_order", "M9_zero_invoices", "M10_file_order"]


def variant(muts, d):
    os.makedirs(d, exist_ok=True)
    src = open(REF, encoding="utf-8").read().replace("MUTATIONS = set()", f"MUTATIONS = {set(muts)!r}" if muts else "MUTATIONS = set()")
    open(os.path.join(d, "solution.py"), "w", encoding="utf-8").write(src)
    return d


def run(d):
    p = subprocess.run([sys.executable, "-B", TESTS, "T6", d], capture_output=True, text=True, encoding="utf-8")
    return json.loads(p.stdout.strip().splitlines()[-1])


def main():
    tmp = tempfile.mkdtemp(prefix="t6mut_")
    matrix, ok = {}, True
    for m, exp in EXPECTED.items():
        r = run(variant([m] if m else [], os.path.join(tmp, m or "full")))
        failed = {k for k in REQS if not r.get(k)}
        good = failed == exp and r.get("R0") is True
        ok &= good
        matrix[m or "full"] = {"expected_fail": sorted(exp), "failed": sorted(failed), "R0": r.get("R0"), "ok": good}
    naive_dir = os.path.join(HERE, "hidden", "ref_naive_T6")
    shutil.rmtree(naive_dir, ignore_errors=True)
    r = run(variant(NAIVE, naive_dir))
    failed = {k for k in REQS if not r.get(k)}
    matrix["naive"] = {"mutations": NAIVE, "failed": sorted(failed), "R0": r.get("R0"), "ok": failed == set(REQS)}
    ok &= matrix["naive"]["ok"]
    shutil.rmtree(tmp, ignore_errors=True)
    json.dump(matrix, open(os.path.join(HERE, "data", "t6_mutation_matrix.json"), "w", encoding="utf-8"), indent=1)
    for k, v in matrix.items():
        print(("OK  " if v["ok"] else "BAD ") + k, v["failed"])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
