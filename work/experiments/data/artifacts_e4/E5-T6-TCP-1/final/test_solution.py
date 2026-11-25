import csv
import os
import shutil
import subprocess
import sys
import unittest

from solution import make_invoices

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
WORK = os.path.join(HERE, "_test_work")
KEYS = {"invoice_id", "customer_id", "lines", "subtotal", "discount", "tax", "total"}
LINE_KEYS = {"order_id", "sku", "qty", "unit_price", "amount"}
EXPECTED_OCT = [
    ["INV-202610-0001", "C001", "27180", "1359", "2351", "28172"],
    ["INV-202610-0002", "C002", "12560", "0", "1124", "13684"],
    ["INV-202610-0003", "C003", "20960", "1048", "1717", "21629"],
    ["INV-202610-0004", "C004", "10280", "0", "994", "11274"],
]


def run_cli(*args):
    return subprocess.run([sys.executable, os.path.join(HERE, "solution.py"), *args],
                          capture_output=True, text=True, cwd=HERE)


class InvoiceTests(unittest.TestCase):
    def setUp(self):
        os.makedirs(WORK, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(WORK, ignore_errors=True)

    # DoD 1
    def test_dod1_structure_and_int_types(self):
        invs = make_invoices(DATA, "2026-10")
        self.assertIsInstance(invs, list)
        self.assertTrue(invs)
        for inv in invs:
            self.assertEqual(set(inv), KEYS)
            for k in ("subtotal", "discount", "tax", "total"):
                self.assertIs(type(inv[k]), int)
            for line in inv["lines"]:
                self.assertEqual(set(line), LINE_KEYS)
                for k in ("qty", "unit_price", "amount"):
                    self.assertIs(type(line[k]), int)

    # DoD 2
    def test_dod2_invariants(self):
        for month in ("2026-09", "2026-10", "2026-11"):
            for inv in make_invoices(DATA, month):
                for line in inv["lines"]:
                    self.assertEqual(line["amount"], line["qty"] * line["unit_price"])
                self.assertEqual(inv["subtotal"], sum(l["amount"] for l in inv["lines"]))
                self.assertEqual(inv["total"], inv["subtotal"] - inv["discount"] + inv["tax"])

    # DoD 3
    def test_dod3_october_expected_values(self):
        invs = make_invoices(DATA, "2026-10")
        got = [[i["invoice_id"], i["customer_id"], str(i["subtotal"]), str(i["discount"]),
                str(i["tax"]), str(i["total"])] for i in invs]
        self.assertEqual(got, EXPECTED_OCT)
        self.assertNotIn("C005", [i["customer_id"] for i in invs])

    def test_dod3_boundary_orders(self):
        oct_lines = {l["order_id"]: l for i in make_invoices(DATA, "2026-10") for l in i["lines"]}
        nov_ids = {l["order_id"] for i in make_invoices(DATA, "2026-11") for l in i["lines"]}
        sep_ids = {l["order_id"] for i in make_invoices(DATA, "2026-09") for l in i["lines"]}
        self.assertEqual(oct_lines["O1012"]["unit_price"], 1300)
        self.assertEqual(oct_lines["O1008"]["unit_price"], 1680)
        self.assertIn("O1002", oct_lines)
        self.assertNotIn("O1002", sep_ids)
        self.assertNotIn("O1021", oct_lines)
        self.assertIn("O1021", nov_ids)
        for excluded in ("O1010", "O1017", "O1013", "O1006"):  # returned / cancelled
            self.assertNotIn(excluded, oct_lines)

    def test_dod3_lines_sorted_by_ordered_at(self):
        c001 = make_invoices(DATA, "2026-10")[0]
        self.assertEqual([l["order_id"] for l in c001["lines"]],
                         ["O1003", "O1008", "O1012", "O1016"])

    # DoD 4
    def test_dod4_empty_month(self):
        self.assertEqual(make_invoices(DATA, "2026-12"), [])
        out = os.path.join(WORK, "empty.csv")
        r = run_cli(DATA, "2026-12", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(out, encoding="utf-8", newline="") as f:
            self.assertEqual(list(csv.reader(f)),
                             [["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"]])

    # DoD 5
    def test_dod5_cli_october(self):
        out = os.path.join(WORK, "out.csv")
        r = run_cli("data", "2026-10", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(out, "rb") as f:
            self.assertFalse(f.read(3) == b"\xef\xbb\xbf")
        with open(out, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))
        self.assertEqual(rows[0], ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"])
        self.assertEqual(rows[1:], EXPECTED_OCT)

    # DoD 6
    def test_dod6_invalid_month(self):
        for bad in ("2026-13", "202610", "2026-1", "2026-00", "", None):
            with self.assertRaises(ValueError):
                make_invoices(DATA, bad)

    def test_dod6_cli_usage_and_bad_month(self):
        r = run_cli("data", "2026-10")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("usage", r.stderr)
        r = run_cli("data", "2026-13", os.path.join(WORK, "x.csv"))
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(os.path.join(WORK, "x.csv")))

    # A11: abnormal input stops with an error
    def test_a11_unknown_sku_and_missing_price(self):
        d = os.path.join(WORK, "data")
        shutil.copytree(DATA, d)
        with open(os.path.join(d, "orders.csv"), "a", encoding="utf-8", newline="") as f:
            f.write("O9999,C001,2026-10-05T00:00:00Z,Z999,1,completed\n")
        with self.assertRaises(ValueError):
            make_invoices(d, "2026-10")
        shutil.copy(os.path.join(DATA, "orders.csv"), os.path.join(d, "orders.csv"))
        with open(os.path.join(d, "orders.csv"), "a", encoding="utf-8", newline="") as f:
            f.write("O9998,C001,2025-12-01T00:00:00Z,A100,1,completed\n")
        with self.assertRaises(ValueError):
            make_invoices(d, "2025-12")


if __name__ == "__main__":
    unittest.main(verbosity=2)
