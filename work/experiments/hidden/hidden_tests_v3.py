"""Hidden tests for T6 (monthly billing). Usage: python hidden_tests_v3.py T6 <solution_dir>
Prints one JSON line: {"task": "T6", "R0": bool, "R1": bool, ... "R10": bool, "errors": {...}}.
Each requirement uses its own fixture so that a single violated rule fails only its own test
(validated by mutation testing: python validate_t6.py).
"""
import csv, importlib.util, json, os, sys, tempfile, traceback

GEN = ["P_G", "汎用品", "general"]
FOOD = ["P_F", "食品", "food"]


def fixture(customers, orders, prices=None, products=None):
    d = tempfile.mkdtemp(prefix="t6h_")
    def w(name, header, rows):
        with open(os.path.join(d, name), "w", newline="", encoding="utf-8") as f:
            c = csv.writer(f)
            c.writerow(header)
            c.writerows(rows)
    w("customers.csv", ["customer_id", "name", "tier"], customers)
    w("products.csv", ["sku", "name", "category"], products or [GEN, FOOD])
    w("prices.csv", ["sku", "effective_from", "unit_price"], prices or [["P_G", "2026-01-01", 100], ["P_F", "2026-01-01", 1000]])
    w("orders.csv", ["order_id", "customer_id", "ordered_at", "sku", "qty", "status"], orders)
    return d


STD = [["S1", "標準", "standard"]]
GOLD = [["G1", "ゴールド", "gold"]]


def load(sol_dir):
    spec = importlib.util.spec_from_file_location("solution_under_test", os.path.join(sol_dir, "solution.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, sol_dir)
    spec.loader.exec_module(mod)
    return mod


def t6(mod):
    f = mod.make_invoices
    def inv(d, month="2026-10"):
        return [dict(x) for x in f(d, month)]
    def one(d, cid):
        return [x for x in inv(d) if str(x["customer_id"]) == cid][0]
    def ids(x):
        return [str(l["order_id"]) for l in x["lines"]]
    def r0():
        res = inv(fixture(STD, [["A1", "S1", "2026-10-15T03:00:00Z", "P_G", 1, "completed"]]))
        keys = {"invoice_id", "customer_id", "lines", "subtotal", "discount", "tax", "total"}
        return isinstance(res, list) and len(res) == 1 and keys <= set(res[0]) and \
            {"order_id", "sku", "qty", "unit_price", "amount"} <= set(res[0]["lines"][0])
    def r1():
        d = fixture(STD, [["X1", "S1", "2026-09-30T15:30:00Z", "P_G", 1, "completed"],
                          ["X2", "S1", "2026-10-31T16:00:00Z", "P_G", 1, "completed"],
                          ["X3", "S1", "2026-10-15T03:00:00Z", "P_G", 1, "completed"]])
        return set(ids(one(d, "S1"))) == {"X1", "X3"}
    def r2():
        d = fixture(STD, [["K1", "S1", "2026-10-05T03:00:00Z", "P_G", 1, "completed"],
                          ["K2", "S1", "2026-10-06T03:00:00Z", "P_G", 1, "shipped"],
                          ["K3", "S1", "2026-10-07T03:00:00Z", "P_G", 1, "cancelled"],
                          ["K4", "S1", "2026-10-08T03:00:00Z", "P_G", 1, "returned"]])
        return set(ids(one(d, "S1"))) == {"K1", "K2"}
    def r3():
        d = fixture(STD, [["Q1", "S1", "2026-10-10T03:00:00Z", "P_G", 1, "completed"],
                          ["Q2", "S1", "2026-10-20T03:00:00Z", "P_G", 1, "completed"]],
                    prices=[["P_G", "2026-01-01", 100], ["P_G", "2026-10-16", 120], ["P_F", "2026-01-01", 1000]])
        up = {str(l["order_id"]): int(l["unit_price"]) for l in one(d, "S1")["lines"]}
        return up == {"Q1": 100, "Q2": 120}
    def r4():
        d = fixture(STD, [["F1", "S1", "2026-10-15T03:00:00Z", "P_F", 1, "completed"]])
        return int(one(d, "S1")["tax"]) == 80
    def r5():
        d = fixture(GOLD, [["D1", "G1", "2026-10-15T03:00:00Z", "P_G", 10, "completed"]])
        x = one(d, "G1")
        return int(x["discount"]) == 50 and int(x["tax"]) == 95
    def r6():
        d = fixture(GOLD, [["D2", "G1", "2026-10-15T03:00:00Z", "P_G", 1, "completed"]],
                    prices=[["P_G", "2026-01-01", 1030], ["P_F", "2026-01-01", 1000]])
        return int(one(d, "G1")["discount"]) == 51
    def r7():
        d = fixture(STD, [[f"T{i}", "S1", f"2026-10-1{i}T03:00:00Z", "P_G", 1, "completed"] for i in (1, 2, 3)],
                    prices=[["P_G", "2026-01-01", 105], ["P_F", "2026-01-01", 1000]])
        return int(one(d, "S1")["tax"]) == 31
    def r8():
        cust = [["C010", "c10", "standard"], ["C003", "c3", "standard"], ["C001", "c1", "standard"]]
        d = fixture(cust, [["N1", "C001", "2026-10-20T03:00:00Z", "P_G", 1, "completed"],
                           ["N2", "C003", "2026-10-05T03:00:00Z", "P_G", 1, "completed"],
                           ["N3", "C010", "2026-10-10T03:00:00Z", "P_G", 1, "completed"]])
        got = {str(x["customer_id"]): str(x["invoice_id"]) for x in inv(d)}
        return got == {"C001": "INV-202610-0001", "C003": "INV-202610-0002", "C010": "INV-202610-0003"}
    def r9():
        cust = [["C001", "c1", "standard"], ["C002", "c2", "standard"]]
        d = fixture(cust, [["Z1", "C001", "2026-10-05T03:00:00Z", "P_G", 1, "completed"],
                           ["Z2", "C002", "2026-10-06T03:00:00Z", "P_G", 1, "cancelled"]])
        return sorted(str(x["customer_id"]) for x in inv(d)) == ["C001"]
    def r10():
        d = fixture(STD, [["L3", "S1", "2026-10-25T03:00:00Z", "P_G", 1, "completed"],
                          ["L1", "S1", "2026-10-05T03:00:00Z", "P_G", 1, "completed"],
                          ["L2", "S1", "2026-10-15T03:00:00Z", "P_G", 1, "completed"]])
        return ids(one(d, "S1")) == ["L1", "L2", "L3"]
    return {"R0": r0, "R1": r1, "R2": r2, "R3": r3, "R4": r4, "R5": r5, "R6": r6, "R7": r7, "R8": r8, "R9": r9, "R10": r10}


def main():
    task, sol = sys.argv[1], sys.argv[2]
    out = {"task": task, "errors": {}}
    try:
        checks = {"T6": t6}[task](load(sol))
    except Exception:
        out["errors"]["load"] = traceback.format_exc(limit=1)
        print(json.dumps(out, ensure_ascii=False))
        return
    for k, fn in checks.items():
        try:
            out[k] = bool(fn())
        except Exception as e:
            out[k] = False
            out["errors"][k] = f"{type(e).__name__}: {e}"[:200]
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
