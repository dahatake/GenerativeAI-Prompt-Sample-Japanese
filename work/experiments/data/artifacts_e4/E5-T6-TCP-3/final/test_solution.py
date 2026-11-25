import csv
import os
import shutil
import subprocess
import sys
import unittest

from solution import make_invoices

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT_DIR = os.path.join(HERE, "test_out")

EXPECTED_OCT = [
    ("INV-202610-0001", "C001", 27180, 1359, 2351, 28172),
    ("INV-202610-0002", "C002", 12560, 0, 1124, 13684),
    ("INV-202610-0003", "C003", 20960, 1048, 1717, 21629),
    ("INV-202610-0004", "C004", 10280, 0, 994, 11274),
]
# Hand-computed (JST): O1021 C001 F200x5, O1023 C004 F100x2, O1024 C003 A100x1
EXPECTED_NOV = [
    ("INV-202611-0001", "C001", 2700, 135, 205, 2770),
    ("INV-202611-0002", "C003", 1300, 65, 123, 1358),
    ("INV-202611-0003", "C004", 3360, 0, 268, 3628),
]
INVOICE_KEYS = {"invoice_id", "customer_id", "lines", "subtotal", "discount", "tax", "total"}
LINE_KEYS = {"order_id", "sku", "qty", "unit_price", "amount"}


def summary(invoices):
    return [
        (i["invoice_id"], i["customer_id"], i["subtotal"], i["discount"], i["tax"], i["total"])
        for i in invoices
    ]


def all_lines(invoices):
    return {l["order_id"]: (i["customer_id"], l) for i in invoices for l in i["lines"]}


class TestMakeInvoices(unittest.TestCase):
    def test_dod1_returns_list(self):
        self.assertIsInstance(make_invoices(DATA, "2026-10"), list)

    def test_dod2_keys_and_int_types(self):
        for month in ("2026-09", "2026-10", "2026-11"):
            for inv in make_invoices(DATA, month):
                self.assertEqual(set(inv), INVOICE_KEYS)
                for k in ("subtotal", "discount", "tax", "total"):
                    self.assertIs(type(inv[k]), int)
                self.assertTrue(inv["lines"])
                for line in inv["lines"]:
                    self.assertEqual(set(line), LINE_KEYS)
                    for k in ("qty", "unit_price", "amount"):
                        self.assertIs(type(line[k]), int)

    def test_dod3_invariants(self):
        for month in ("2026-09", "2026-10", "2026-11"):
            for inv in make_invoices(DATA, month):
                for line in inv["lines"]:
                    self.assertEqual(line["amount"], line["unit_price"] * line["qty"])
                self.assertEqual(inv["subtotal"], sum(l["amount"] for l in inv["lines"]))
                self.assertEqual(inv["total"], inv["subtotal"] - inv["discount"] + inv["tax"])

    def test_dod4_excluded_statuses(self):
        for month in ("2026-09", "2026-10", "2026-11"):
            ids = set(all_lines(make_invoices(DATA, month)))
            self.assertFalse(ids & {"O1006", "O1010", "O1013", "O1017"})

    def test_dod5_october_expected_values(self):
        invoices = make_invoices(DATA, "2026-10")
        self.assertEqual(summary(invoices), EXPECTED_OCT)
        self.assertNotIn("C005", [i["customer_id"] for i in invoices])

    def test_dod5_boundary_cases(self):
        lines = all_lines(make_invoices(DATA, "2026-10"))
        self.assertNotIn("O1021", lines)  # 2026-11-01 01:00 JST
        self.assertEqual(lines["O1002"][0], "C003")  # 2026-10-01 00:30 JST
        self.assertEqual(lines["O1008"][1]["unit_price"], 1680)  # 2026-10-10 JST
        self.assertEqual(lines["O1012"][1]["unit_price"], 1300)  # 2026-10-16 JST
        self.assertEqual(lines["O1011"][1]["unit_price"], 1200)  # 2026-10-14 JST

    def test_dod5_lines_sorted_by_ordered_at(self):
        invoices = {i["customer_id"]: i for i in make_invoices(DATA, "2026-10")}
        self.assertEqual(
            [l["order_id"] for l in invoices["C003"]["lines"]],
            ["O1002", "O1007", "O1011", "O1015", "O1020"],
        )
        self.assertEqual(
            [l["order_id"] for l in invoices["C001"]["lines"]],
            ["O1003", "O1008", "O1012", "O1016"],
        )

    def test_november_expected_values(self):
        self.assertEqual(summary(make_invoices(DATA, "2026-11")), EXPECTED_NOV)

    def test_dod7_invalid_month(self):
        for bad in ("2026-1", "202610", "2026-13", "2026-00", "2026/10", ""):
            with self.assertRaises(ValueError):
                make_invoices(DATA, bad)

    def test_dod7_empty_month(self):
        self.assertEqual(make_invoices(DATA, "2026-12"), [])


class TestCli(unittest.TestCase):
    def setUp(self):
        os.makedirs(OUT_DIR, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(OUT_DIR, ignore_errors=True)

    def run_cli(self, month, out):
        return subprocess.run(
            [sys.executable, os.path.join(HERE, "solution.py"), DATA, month, out],
            capture_output=True, text=True,
        )

    def read(self, path):
        with open(path, encoding="utf-8", newline="") as f:
            return list(csv.reader(f))

    def test_dod6_cli_october(self):
        out = os.path.join(OUT_DIR, "out.csv")
        proc = self.run_cli("2026-10", out)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = self.read(out)
        self.assertEqual(rows[0], ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"])
        self.assertEqual(rows[1:], [[str(v) for v in r] for r in EXPECTED_OCT])

    def test_dod7_cli_empty_month_header_only(self):
        out = os.path.join(OUT_DIR, "empty.csv")
        proc = self.run_cli("2026-12", out)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self.read(out), [["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"]])

    def test_cli_invalid_month_fails(self):
        out = os.path.join(OUT_DIR, "bad.csv")
        proc = self.run_cli("202610", out)
        self.assertNotEqual(proc.returncode, 0)
        self.assertFalse(os.path.exists(out))


if __name__ == "__main__":
    unittest.main()
