"""Supplementary (post-hoc, exploratory) checks for T6, added after the v3 runs (deviation D-v3-4).

The preregistered hidden tests (hidden_tests_v3.py) check R5-R7 with a single tax category only, so an
implementation that computes the gold discount (or tax) over the whole invoice instead of per tax-rate group
can pass them. These checks mix food (8%) and general (10%) items, and compare every invoice on the actual
task data with the full reference implementation.

Usage: python hidden_tests_v3s.py <solution_dir>
Prints one JSON line: {"S56": bool, "S7": bool, "E2E": bool, "E2E_mismatch": [...], "errors": {...}}.
"""
import csv, importlib.util, json, os, sys, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hidden_tests_v3 import fixture, GOLD, STD, load  # noqa: E402

DATA = os.path.join(HERE, "..", "tasks", "T6_billing", "data")
REF = os.path.join(HERE, "ref_full_T6")
FIELDS = ("invoice_id", "customer_id", "subtotal", "discount", "tax", "total")


def months():
    from datetime import datetime, timedelta
    ms = set()
    with open(os.path.join(DATA, "orders.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t = datetime.fromisoformat(r["ordered_at"].replace("Z", "+00:00")) + timedelta(hours=9)
            ms.add(t.strftime("%Y-%m"))
    return sorted(ms)


def summary(mod, month):
    out = []
    for x in mod.make_invoices(DATA, month):
        x = dict(x)
        row = tuple(str(x[k]) if k in ("invoice_id", "customer_id") else int(x[k]) for k in FIELDS)
        out.append(row + (tuple(str(l["order_id"]) for l in x["lines"]),))
    return out


def main():
    sol = sys.argv[1]
    res = {"errors": {}}
    try:
        mod = load(sol)
    except Exception:
        res["errors"]["load"] = traceback.format_exc(limit=1)
        print(json.dumps(res, ensure_ascii=False))
        return
    f = mod.make_invoices

    def one(d, cid):
        return [dict(x) for x in f(d, "2026-10") if str(dict(x)["customer_id"]) == cid][0]

    def s56():
        # gold, food 199 + general 199: per-group discount 9 + 9 = 18; tax (190*8//100) + (190*10//100) = 15 + 19 = 34
        d = fixture(GOLD, [["M1", "G1", "2026-10-15T03:00:00Z", "P_F", 1, "completed"],
                           ["M2", "G1", "2026-10-16T03:00:00Z", "P_G", 1, "completed"]],
                    prices=[["P_G", "2026-01-01", 199], ["P_F", "2026-01-01", 199]])
        x = one(d, "G1")
        return (int(x["discount"]), int(x["tax"]), int(x["total"])) == (18, 34, 414)

    def s7():
        # standard, 3 food lines x105 and 3 general lines x103: tax 315*8//100 + 309*10//100 = 25 + 30 = 55
        orders = [[f"F{i}", "S1", f"2026-10-1{i}T03:00:00Z", "P_F", 1, "completed"] for i in (1, 2, 3)] + \
                 [[f"G{i}", "S1", f"2026-10-2{i}T03:00:00Z", "P_G", 1, "completed"] for i in (1, 2, 3)]
        d = fixture(STD, orders, prices=[["P_G", "2026-01-01", 103], ["P_F", "2026-01-01", 105]])
        return int(one(d, "S1")["tax"]) == 55

    for k, fn in (("S56", s56), ("S7", s7)):
        try:
            res[k] = bool(fn())
        except Exception as e:
            res[k] = False
            res["errors"][k] = f"{type(e).__name__}: {e}"[:200]
    try:
        ref = load(REF)
        mism = []
        for m in months():
            a, b = summary(mod, m), summary(ref, m)
            if a != b:
                mism.append(m)
        res["E2E"] = not mism
        res["E2E_mismatch"] = mism
    except Exception as e:
        res["E2E"] = False
        res["errors"]["E2E"] = f"{type(e).__name__}: {e}"[:200]
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
