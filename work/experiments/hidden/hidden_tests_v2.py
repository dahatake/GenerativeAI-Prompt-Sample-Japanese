"""Hidden requirement tests for experiment E3 (tasks T4, T5) and a supplemental T3 check.

Usage: python hidden_tests_v2.py <task_id> <sandbox_dir>
task_id: T4 | T5 | T3S (supplemental: future years within 2020-2099 must be valid) | T5S (post-hoc: 28-day window boundary)
Prints one JSON line with R0..Rn booleans. Each requirement is tested in isolation.
"""
import csv, importlib.util, json, os, sys, tempfile, traceback
from datetime import date, timedelta


def load(sandbox):
    spec = importlib.util.spec_from_file_location("solution_under_test_v2", os.path.join(sandbox, "solution.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, sandbox)
    spec.loader.exec_module(mod)
    return mod


def csv_file(header, rows):
    fd, p = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return p


H4 = ["employee", "date", "type", "start", "end"]


def t4(mod):
    f = mod.monthly_work_hours
    def val(rows, emp):
        return float(f(csv_file(H4, rows))[emp])
    def r0():
        res = f(csv_file(H4, [["X", "2026-10-01", "work", "09:00", "12:00"]]))
        return isinstance(res, dict) and abs(float(res["X"]) - 3.0) < 1e-9
    def r1():
        v = val([["X", "2026-10-01", "work", "22:00", "06:00"]], "X")
        return any(abs(v - c) < 1e-9 for c in (7.0, 7.25, 8.0))
    def r2():
        a = val([["A", "2026-10-01", "work", "09:00", "18:00"]], "A")
        b = val([["B", "2026-10-01", "work", "09:00", "15:00"]], "B")
        return abs(a - 8.0) < 1e-9 and abs(b - 6.0) < 1e-9
    def r3():
        return abs(val([["X", "2026-10-01", "work", "09:00", "14:50"]], "X") - 5.75) < 1e-9
    def r4():
        rows = [["X", "2026-10-01", "work", "09:00", "12:00"], ["X", "2026-10-02", "paid_leave", "", ""]]
        return abs(val(rows, "X") - 10.5) < 1e-9
    return {"R0": r0, "R1": r1, "R2": r2, "R3": r3, "R4": r4}


HI = ["sku", "name", "stock", "on_order", "lead_time_days", "safety_stock", "lot", "discontinued"]
HS = ["date", "sku", "qty"]
TODAY = date(2026, 11, 10)


def ship(sku, days_ago_list, qty):
    return [[(TODAY - timedelta(days=d)).isoformat(), sku, qty] for d in days_ago_list]


def t5(mod):
    f = mod.reorder_plan
    def run(inv, shp, today=TODAY):
        ip, sp = csv_file(HI, inv), csv_file(HS, shp)
        try:
            res = f(ip, sp, today)
        except (TypeError, AttributeError, ValueError):
            res = f(ip, sp, today.isoformat())
        return [dict(r) for r in res]
    def skus(res):
        return [str(r["sku"]) for r in res]
    def r0():
        res = run([["S1", "n", 0, 0, 1, 5, 1, "false"]], [])
        return isinstance(res, list) and len(res) == 1 and set(res[0]).issuperset({"sku", "qty"})
    def r1():
        inv = [["OLD", "n", 1, 0, 1, 0, 1, "false"], ["TOD", "n", 1, 0, 1, 0, 1, "false"], ["NEW", "n", 1, 0, 1, 0, 1, "false"]]
        shp = ship("OLD", [35], 280) + ship("TOD", [0], 280) + ship("NEW", [3], 280)
        res = run(inv, shp)
        s = skus(res)
        new_qty = [r for r in res if str(r["sku"]) == "NEW"]
        return "OLD" not in s and "TOD" not in s and "NEW" in s and int(new_qty[0]["qty"]) == 9
    def r2():
        inv = [["S1", "n", 5, 100, 1, 50, 1, "false"]]
        return "S1" not in skus(run(inv, []))
    def r3():
        inv = [["S1", "n", 47, 0, 1, 50, 10, "false"]]
        res = run(inv, [])
        return len(res) == 1 and int(res[0]["qty"]) == 10
    def r4():
        inv = [["S1", "n", 0, 0, 1, 50, 1, "true"], ["S2", "n", 0, 0, 1, 50, 1, "false"]]
        return skus(run(inv, [])) == ["S2"]
    def r5():
        inv = [["Z9", "n", 0, 0, 1, 5, 1, "false"], ["A1", "n", 0, 0, 1, 5, 1, "false"], ["M5", "n", 0, 0, 1, 5, 1, "false"]]
        res = run(inv, [])
        return skus(res) == ["A1", "M5", "Z9"] and all(isinstance(r["qty"], int) for r in res)
    def r6():
        inv = [["EQ", "n", 50, 0, 1, 50, 1, "false"]]
        return "EQ" in skus(run(inv, []))
    return {"R0": r0, "R1": r1, "R2": r2, "R3": r3, "R4": r4, "R5": r5, "R6": r6}


def t3s(mod):
    f = mod.validate_invoice_id
    def r2f():
        return all(f(x) is True for x in ["INV-203001-0001", "INV-209912-0001", "INV-202001-0001"])
    return {"R2_future_valid": r2f}


# Post-hoc supplementary test (deviation D-v2-3): the preregistered T5 R1 case yields qty 9
# under both a 28-day and a 30-day window, so it cannot detect the 30-day default.
def t5s(mod):
    f = mod.reorder_plan
    def run(inv, shp):
        ip, sp = csv_file(HI, inv), csv_file(HS, shp)
        try:
            res = f(ip, sp, TODAY)
        except (TypeError, AttributeError, ValueError):
            res = f(ip, sp, TODAY.isoformat())
        return [dict(r) for r in res]
    def r1w():
        inv = [["D29", "n", 1, 0, 1, 0, 1, "false"], ["D28", "n", 1, 0, 1, 0, 1, "false"]]
        shp = ship("D29", [29], 280) + ship("D28", [28], 280)
        res = run(inv, shp)
        got = {str(r["sku"]): int(r["qty"]) for r in res}
        return "D29" not in got and got.get("D28") == 9
    return {"R1_window28": r1w}


def main():
    task, sandbox = sys.argv[1], sys.argv[2]
    out = {"task": task, "errors": {}}
    try:
        mod = load(sandbox)
        checks = {"T4": t4, "T5": t5, "T3S": t3s, "T5S": t5s}[task](mod)
    except Exception:
        out["load_error"] = traceback.format_exc(limit=1)
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
