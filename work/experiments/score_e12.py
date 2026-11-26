"""E12 scorer: decode which T1 hidden requirements a monthly_sales result on tasks/T1_sales/sales.csv satisfies.

Each of the 16 combinations of (R1 exclude cancelled, R2 JST month, R3 tax-exclusive, R4 fill empty months with 0)
yields a distinct dict on sales.csv. A reported dict is matched against all 16 (rounding variants for R3 are accepted:
floor, round-half-up, banker's rounding of total/1.1, and per-row conversion).
Usage: python score_e12.py '<json dict>'   -> prints matching combinations
       python score_e12.py --rescore        -> re-scores the saved E12 TC+ Phase 2 answers (runs the shown code on sales.csv)
       python score_e12.py                  -> checks that the 16 combinations give 16 distinct dicts
"""
import csv, datetime, itertools, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = list(csv.DictReader(open(os.path.join(HERE, "tasks", "T1_sales", "sales.csv"), encoding="utf-8")))


def compute(r1, r2, r3, r4, rounding):
    agg = {}
    for row in ROWS:
        if r1 and row["status"] == "cancelled":
            continue
        t = datetime.datetime.fromisoformat(row["ordered_at"].replace("Z", "+00:00"))
        if r2:
            t = t + datetime.timedelta(hours=9)
        k = t.strftime("%Y-%m")
        a = int(row["amount_incl_tax"])
        if r3 and rounding == "row":
            a = math.floor(a / 1.1 + 1e-9)
        agg[k] = agg.get(k, 0) + a
    if r3 and rounding != "row":
        f = {"floor": lambda x: math.floor(x / 1.1 + 1e-9), "half_up": lambda x: math.floor(x / 1.1 + 0.5),
             "bankers": lambda x: round(x / 1.1)}[rounding]
        agg = {k: f(v) for k, v in agg.items()}
    if r4 and agg:
        ks = sorted(agg)
        y, m = map(int, ks[0].split("-"))
        end = ks[-1]
        while f"{y:04d}-{m:02d}" <= end:
            agg.setdefault(f"{y:04d}-{m:02d}", 0)
            m += 1
            if m == 13:
                y, m = y + 1, 1
    return dict(sorted(agg.items()))


def decode(result):
    hits = []
    for r1, r2, r3, r4 in itertools.product((False, True), repeat=4):
        for rounding in (("floor", "half_up", "bankers", "row") if r3 else ("floor",)):
            if compute(r1, r2, r3, r4, rounding) == dict(sorted(result.items())):
                hits.append({"R1": r1, "R2": r2, "R3": r3, "R4": r4, "rounding": rounding if r3 else None})
    return hits


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--rescore":
        # Re-score E12 TC+: run the monthly_sales code shown in each saved Phase 2 answer on the real sales.csv
        import glob, re
        for f in sorted(glob.glob(os.path.join(HERE, "data", "e12", "raw", "E12-TCP-*_p2_answer.md.txt"))):
            ans = open(f, encoding="utf-8").read()
            impl = [c for c in re.findall(r"```python\n(.*?)```", ans, re.S) if "def monthly_sales" in c][0]
            ns = {}
            exec(impl, ns)
            r = ns["monthly_sales"](os.path.join(HERE, "tasks", "T1_sales", "sales.csv"))
            print(os.path.basename(f), r, decode(r))
    elif len(sys.argv) > 1:
        print(json.dumps(decode(json.loads(sys.argv[1])), ensure_ascii=False))
    else:
        seen = {}
        for r1, r2, r3, r4 in itertools.product((False, True), repeat=4):
            seen.setdefault(json.dumps(compute(r1, r2, r3, r4, "floor")), []).append((r1, r2, r3, r4))
        print("distinct dicts for 16 combinations:", len(seen))
        print("all-correct:", compute(True, True, True, True, "floor"))
