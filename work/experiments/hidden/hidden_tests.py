"""Hidden requirement tests for the Task Contract experiment (E1).

Usage: python hidden_tests.py <task_id> <sandbox_dir>
Prints one JSON line: {"task":..., "R0":bool, "R1":bool, ..., "errors":{...}}
Each requirement is tested in isolation so that one failure does not mask another.
"""
import csv, importlib.util, json, os, re, sys, tempfile, traceback


def load(sandbox):
    path = os.path.join(sandbox, "solution.py")
    spec = importlib.util.spec_from_file_location("solution_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, sandbox)
    spec.loader.exec_module(mod)
    return mod


def write_csv(rows):
    fd, p = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["order_id", "ordered_at", "amount_incl_tax", "status"])
        for r in rows:
            w.writerow(r)
    return p


def t1(mod):
    f = mod.monthly_sales
    out = {}
    def r0():
        res = f(write_csv([["X1", "2026-01-10T03:00:00Z", "1100", "completed"]]))
        return isinstance(res, dict) and all(re.fullmatch(r"\d{4}-\d{2}", str(k)) for k in res) and all(isinstance(v, int) for v in res.values())
    def r1():
        res = f(write_csv([["X1", "2026-01-10T03:00:00Z", "1100", "completed"], ["X2", "2026-01-11T03:00:00Z", "5500", "cancelled"]]))
        return res.get("2026-01") in (1000, 1100)
    def r2():
        res = f(write_csv([["X1", "2026-01-31T16:00:00Z", "1100", "completed"]]))
        return res.get("2026-02") in (1000, 1100) and not res.get("2026-01")
    def r3():
        res = f(write_csv([["X1", "2026-01-10T03:00:00Z", "1100", "completed"]]))
        return res.get("2026-01") == 1000
    def r4():
        res = f(write_csv([["X1", "2026-01-10T03:00:00Z", "1100", "completed"], ["X2", "2026-03-10T03:00:00Z", "2200", "completed"]]))
        return "2026-02" in res and res["2026-02"] == 0
    return {"R0": r0, "R1": r1, "R2": r2, "R3": r3, "R4": r4}


def t2(mod):
    f = mod.dedupe
    def norm(e):
        return (e or "").strip().lower()
    def r0():
        res = f([{"id": 1, "name": "a", "email": "a@x.com", "updated_at": "2026-01-01T00:00:00+09:00"}])
        return isinstance(res, list) and len(res) == 1 and isinstance(res[0], dict)
    def r1():
        res = f([{"id": 1, "name": "a", "email": "A@x.com ", "updated_at": "2026-01-01T00:00:00+09:00"},
                 {"id": 2, "name": "a", "email": "a@x.com", "updated_at": "2026-01-01T00:00:00+09:00"}])
        return len(res) == 1
    def r2():
        res = f([{"id": 1, "name": "a", "email": "a@x.com", "updated_at": "2026-01-01T00:00:00+09:00"},
                 {"id": 2, "name": "a", "email": "a@x.com", "updated_at": "2026-03-01T00:00:00+09:00"}])
        return len(res) == 1 and res[0]["id"] == 2
    def r3():
        res = f([{"id": 1, "name": "b", "email": "b@x.com", "updated_at": "2026-01-01T00:00:00+09:00"},
                 {"id": 2, "name": "a", "email": "a@x.com", "updated_at": "2026-01-01T00:00:00+09:00"},
                 {"id": 3, "name": "b", "email": "b@x.com", "updated_at": "2026-03-01T00:00:00+09:00"}])
        return [norm(r["email"]) for r in res] == ["b@x.com", "a@x.com"]
    def r4():
        res = f([{"id": 1, "name": "a", "email": "", "updated_at": "2026-01-01T00:00:00+09:00"},
                 {"id": 2, "name": "b", "email": "", "updated_at": "2026-01-02T00:00:00+09:00"},
                 {"id": 3, "name": "c", "email": None, "updated_at": "2026-01-03T00:00:00+09:00"},
                 {"id": 4, "name": "d", "email": None, "updated_at": "2026-01-04T00:00:00+09:00"}])
        return sorted(r["id"] for r in res) == [1, 2, 3, 4]
    return {"R0": r0, "R1": r1, "R2": r2, "R3": r3, "R4": r4}


def t3(mod):
    f = mod.validate_invoice_id
    def r0():
        return all(f(x) is True for x in ["INV-202601-0001", "INV-202512-0347", "INV-202603-1200"])
    def r1():
        return all(f(x) is False for x in ["inv-202601-0001", "INV202601-0001", "INV-202601-001", "INV-202601-0001 "])
    def r2():
        return all(f(x) is False for x in ["INV-202613-0001", "INV-202600-0001", "INV-201912-0001"])
    def r3():
        return f("INV-202601-0000") is False
    def r4():
        return all(f(x) is False for x in [None, 202601, 3.14, ["INV-202601-0001"]])
    return {"R0": r0, "R1": r1, "R2": r2, "R3": r3, "R4": r4}


def main():
    task, sandbox = sys.argv[1], sys.argv[2]
    result = {"task": task, "sandbox": sandbox, "errors": {}}
    try:
        mod = load(sandbox)
        checks = {"T1": t1, "T2": t2, "T3": t3}[task](mod)
    except Exception:
        result["load_error"] = traceback.format_exc(limit=1)
        for k in ["R0", "R1", "R2", "R3", "R4"]:
            result[k] = False
        print(json.dumps(result, ensure_ascii=False))
        return
    for name, fn in checks.items():
        try:
            result[name] = bool(fn())
        except Exception as e:
            result[name] = False
            result["errors"][name] = f"{type(e).__name__}: {e}"[:200]
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
