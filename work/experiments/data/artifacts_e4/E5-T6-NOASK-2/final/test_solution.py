"""DoD verification tests for solution.make_invoices / CLI (run: python -m unittest -v test_solution)."""

import csv
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from solution import make_invoices

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
INVOICE_KEYS = {"invoice_id", "customer_id", "lines", "subtotal", "discount", "tax", "total"}
LINE_KEYS = {"order_id", "sku", "qty", "unit_price", "amount"}
MONTHS = ["2026-09", "2026-10", "2026-11"]

# Hand-calculated (JST, completed+shipped, gold 10%, food 8% / general 10%, floor per rate group).
EXPECTED = {
    "2026-09": [
        ("INV-202609-C001", "C001", 2400, 240, 216, 2376),
    ],
    "2026-10": [
        ("INV-202610-C001", "C001", 27180, 2718, 2227, 26689),
        ("INV-202610-C002", "C002", 12560, 0, 1124, 13684),
        ("INV-202610-C003", "C003", 20960, 2096, 1627, 20491),
        ("INV-202610-C004", "C004", 10280, 0, 994, 11274),
    ],
    "2026-11": [
        ("INV-202611-C001", "C001", 2700, 270, 194, 2624),
        ("INV-202611-C003", "C003", 1300, 130, 117, 1287),
        ("INV-202611-C004", "C004", 3360, 0, 268, 3628),
    ],
}
EXPECTED_ORDERS_2026_10 = {
    "C001": ["O1003", "O1008", "O1012", "O1016"],
    "C002": ["O1004", "O1009", "O1018", "O1022"],
    "C003": ["O1002", "O1007", "O1011", "O1015", "O1020"],
    "C004": ["O1005", "O1014", "O1019"],
}


def summary(invoices):
    return [(i["invoice_id"], i["customer_id"], i["subtotal"], i["discount"], i["tax"], i["total"])
            for i in invoices]


def line_by_order(invoices):
    return {l["order_id"]: (inv["customer_id"], l) for inv in invoices for l in inv["lines"]}


class DoD1Structure(unittest.TestCase):
    def test_returns_list_with_required_keys(self):
        invoices = make_invoices(DATA, "2026-10")
        self.assertIsInstance(invoices, list)
        self.assertTrue(invoices)
        for inv in invoices:
            self.assertEqual(set(inv), INVOICE_KEYS)
            self.assertIsInstance(inv["lines"], list)
            for line in inv["lines"]:
                self.assertEqual(set(line), LINE_KEYS)


class DoD2Arithmetic(unittest.TestCase):
    def test_invariants_all_months(self):
        for month in MONTHS:
            for inv in make_invoices(DATA, month):
                for k in ("subtotal", "discount", "tax", "total"):
                    self.assertIs(type(inv[k]), int, (month, k))
                for line in inv["lines"]:
                    for k in ("qty", "unit_price", "amount"):
                        self.assertIs(type(line[k]), int, (month, k))
                    self.assertEqual(line["amount"], line["unit_price"] * line["qty"])
                self.assertEqual(inv["subtotal"], sum(l["amount"] for l in inv["lines"]))
                self.assertEqual(inv["total"], inv["subtotal"] - inv["discount"] + inv["tax"])


class DoD3UnitPrice(unittest.TestCase):
    def test_jst_price_switch_boundaries(self):
        lines = line_by_order(make_invoices(DATA, "2026-10"))
        # O1008: 2026-10-09T15:10Z = 2026-10-10 JST -> F100 new price 1680 (UTC would give 1580)
        self.assertEqual(lines["O1008"][1]["unit_price"], 1680)
        # O1012: 2026-10-15T15:20Z = 2026-10-16 JST -> A100 new price 1300 (UTC would give 1200)
        self.assertEqual(lines["O1012"][1]["unit_price"], 1300)
        # Before switch dates
        self.assertEqual(lines["O1007"][1]["unit_price"], 1580)
        self.assertEqual(lines["O1011"][1]["unit_price"], 1200)
        # After switch dates
        self.assertEqual(lines["O1014"][1]["unit_price"], 1680)
        self.assertEqual(lines["O1019"][1]["unit_price"], 1300)


class DoD4MonthAssignment(unittest.TestCase):
    def test_jst_month_boundaries(self):
        oct_lines = line_by_order(make_invoices(DATA, "2026-10"))
        sep_lines = line_by_order(make_invoices(DATA, "2026-09"))
        nov_lines = line_by_order(make_invoices(DATA, "2026-11"))
        # O1002: 2026-09-30T15:30Z = 2026-10-01 JST
        self.assertIn("O1002", oct_lines)
        self.assertNotIn("O1002", sep_lines)
        # O1021: 2026-10-31T16:00Z = 2026-11-01 JST
        self.assertNotIn("O1021", oct_lines)
        self.assertIn("O1021", nov_lines)
        # O1022: 2026-10-31T14:50Z = 2026-10-31 23:50 JST
        self.assertIn("O1022", oct_lines)

    def test_exact_order_set_and_line_order_2026_10(self):
        invoices = make_invoices(DATA, "2026-10")
        got = {inv["customer_id"]: [l["order_id"] for l in inv["lines"]] for inv in invoices}
        self.assertEqual(got, EXPECTED_ORDERS_2026_10)


class DoD5StatusFilter(unittest.TestCase):
    def test_excluded_statuses(self):
        all_orders = set()
        customers = set()
        for month in MONTHS:
            invoices = make_invoices(DATA, month)
            all_orders |= set(line_by_order(invoices))
            if month == "2026-10":
                customers = {i["customer_id"] for i in invoices}
        for oid in ("O1006", "O1010", "O1013", "O1017"):
            self.assertNotIn(oid, all_orders)
        self.assertNotIn("C005", customers)
        # shipped orders are billed
        for oid in ("O1004", "O1008", "O1015", "O1024"):
            self.assertIn(oid, all_orders)


class DoD6DiscountTax(unittest.TestCase):
    def test_hand_calculated_values(self):
        for month, expected in EXPECTED.items():
            self.assertEqual(summary(make_invoices(DATA, month)), expected, month)


class DoD7Cli(unittest.TestCase):
    def test_cli_writes_csv_matching_function(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            out = os.path.join(tmp, "out.csv")
            r = subprocess.run([sys.executable, os.path.join(HERE, "solution.py"), DATA, "2026-10", out],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(out, encoding="utf-8", newline="") as f:
                rows = list(csv.reader(f))
        self.assertEqual(rows[0], ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"])
        expected = [[str(v) for v in row] for row in summary(make_invoices(DATA, "2026-10"))]
        self.assertEqual(rows[1:], expected)

    def test_cli_usage_error(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "solution.py"), DATA],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("usage", r.stderr)


class DoD8EmptyAndInvalid(unittest.TestCase):
    def test_empty_month(self):
        self.assertEqual(make_invoices(DATA, "2026-08"), [])
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            out = os.path.join(tmp, "out.csv")
            r = subprocess.run([sys.executable, os.path.join(HERE, "solution.py"), DATA, "2026-08", out],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(out, encoding="utf-8", newline="") as f:
                self.assertEqual(list(csv.reader(f)),
                                 [["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"]])

    def test_invalid_month(self):
        for bad in ("2026-13", "202610", "2026-1", "2026/10", "", "2026-00"):
            with self.assertRaises(ValueError, msg=bad):
                make_invoices(DATA, bad)
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            r = subprocess.run([sys.executable, os.path.join(HERE, "solution.py"), DATA, "2026-13",
                                os.path.join(tmp, "out.csv")], capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)

    def _broken_data(self, tmp, filename, extra_row):
        d = os.path.join(tmp, "data")
        shutil.copytree(DATA, d)
        with open(os.path.join(d, filename), "a", encoding="utf-8", newline="") as f:
            f.write(extra_row + "\n")
        return d

    def test_invalid_reference_data_raises(self):
        cases = [
            "O9001,C999,2026-10-05T00:00:00Z,A100,1,completed",  # unknown customer
            "O9002,C001,2026-10-05T00:00:00Z,Z999,1,completed",  # unknown sku
            "O9003,C001,2026-10-05T00:00:00Z,A100,1,pending",    # unknown status
            "O9004,C001,2025-10-05T00:00:00Z,A100,1,completed",  # no price yet
        ]
        for i, row in enumerate(cases):
            with tempfile.TemporaryDirectory(dir=HERE) as tmp:
                d = self._broken_data(tmp, "orders.csv", row)
                month = "2025-10" if i == 3 else "2026-10"
                with self.assertRaises(ValueError, msg=row):
                    make_invoices(d, month)


class DoD9Determinism(unittest.TestCase):
    def test_input_row_order_independent(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            d = os.path.join(tmp, "data")
            shutil.copytree(DATA, d)
            for name in ("orders.csv", "prices.csv", "customers.csv"):
                path = os.path.join(d, name)
                with open(path, encoding="utf-8") as f:
                    lines = f.read().splitlines()
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write("\n".join([lines[0]] + lines[:0:-1]) + "\n")
            for month in MONTHS:
                self.assertEqual(make_invoices(d, month), make_invoices(DATA, month))


if __name__ == "__main__":
    unittest.main()
