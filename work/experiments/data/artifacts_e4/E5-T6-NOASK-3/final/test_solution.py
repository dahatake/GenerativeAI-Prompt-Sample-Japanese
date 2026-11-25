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


def by_customer(invoices):
    return {inv["customer_id"]: inv for inv in invoices}


def order_ids(invoices):
    return {line["order_id"] for inv in invoices for line in inv["lines"]}


def run_cli(*args):
    return subprocess.run([sys.executable, os.path.join(HERE, "solution.py"), *args],
                          capture_output=True, text=True, cwd=HERE)


class TestInvoices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oct = make_invoices(DATA, "2026-10")
        cls.nov = make_invoices(DATA, "2026-11")
        os.makedirs(OUT_DIR, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(OUT_DIR, ignore_errors=True)

    def test_dod1_returns_list_of_dicts(self):
        self.assertIsInstance(self.oct, list)
        self.assertTrue(self.oct)
        self.assertTrue(all(isinstance(inv, dict) for inv in self.oct))

    def test_dod2_keys_and_types(self):
        for inv in self.oct + self.nov:
            self.assertEqual(set(inv), {"invoice_id", "customer_id", "lines", "subtotal",
                                        "discount", "tax", "total"})
            for k in ("subtotal", "discount", "tax", "total"):
                self.assertIs(type(inv[k]), int, k)
            for line in inv["lines"]:
                self.assertEqual(set(line), {"order_id", "sku", "qty", "unit_price", "amount"})
                self.assertIs(type(line["order_id"]), str)
                self.assertIs(type(line["sku"]), str)
                for k in ("qty", "unit_price", "amount"):
                    self.assertIs(type(line[k]), int, k)

    def test_dod3_consistency(self):
        for inv in self.oct + self.nov:
            for line in inv["lines"]:
                self.assertEqual(line["amount"], line["qty"] * line["unit_price"])
            self.assertEqual(inv["subtotal"], sum(l["amount"] for l in inv["lines"]))
            self.assertEqual(inv["total"], inv["subtotal"] - inv["discount"] + inv["tax"])
            self.assertGreaterEqual(inv["discount"], 0)
            self.assertGreaterEqual(inv["tax"], 0)

    def test_dod4_month_boundary_jst(self):
        self.assertIn("O1002", order_ids(self.oct))
        self.assertNotIn("O1021", order_ids(self.oct))
        nov_c001 = by_customer(self.nov)["C001"]
        self.assertIn("O1021", {l["order_id"] for l in nov_c001["lines"]})
        self.assertNotIn("O1001", order_ids(self.oct))

    def test_dod5_price_effective_date_jst(self):
        lines = {l["order_id"]: l for inv in self.oct for l in inv["lines"]}
        self.assertEqual(lines["O1008"]["unit_price"], 1680)
        self.assertEqual(lines["O1012"]["unit_price"], 1300)
        self.assertEqual(lines["O1007"]["unit_price"], 1580)
        self.assertEqual(lines["O1011"]["unit_price"], 1200)

    def test_dod6_status_filter(self):
        ids = order_ids(self.oct) | order_ids(self.nov)
        for oid in ("O1010", "O1017", "O1006", "O1013"):
            self.assertNotIn(oid, ids)
        self.assertNotIn("C005", by_customer(self.oct))
        self.assertIn("O1015", ids)  # shipped is billed

    def test_dod7_subtotals(self):
        got = {c: inv["subtotal"] for c, inv in by_customer(self.oct).items()}
        self.assertEqual(got, {"C001": 27180, "C002": 12560, "C003": 20960, "C004": 10280})

    def test_dod8_discount_tax_total(self):
        expected = {
            "C001": (1359, 2351, 28172),
            "C002": (0, 1124, 13684),
            "C003": (1048, 1717, 21629),
            "C004": (0, 994, 11274),
        }
        got = {c: (i["discount"], i["tax"], i["total"]) for c, i in by_customer(self.oct).items()}
        self.assertEqual(got, expected)

    def test_order_and_ids(self):
        self.assertEqual([i["customer_id"] for i in self.oct], ["C001", "C002", "C003", "C004"])
        self.assertEqual(self.oct[0]["invoice_id"], "INV-202610-C001")
        self.assertEqual([l["order_id"] for l in by_customer(self.oct)["C001"]["lines"]],
                         ["O1003", "O1008", "O1012", "O1016"])

    def test_dod9_cli(self):
        out = os.path.join(OUT_DIR, "out.csv")
        r = run_cli("data", "2026-10", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(out, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))
        self.assertEqual(rows[0], ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"])
        self.assertEqual(len(rows) - 1, len(self.oct))
        expected = [[i["invoice_id"], i["customer_id"], str(i["subtotal"]), str(i["discount"]),
                     str(i["tax"]), str(i["total"])] for i in self.oct]
        self.assertEqual(rows[1:], expected)

    def test_dod10_invalid_month(self):
        for bad in ("2026-1", "abc", "2026-13", "2026/10", ""):
            with self.assertRaises(ValueError):
                make_invoices(DATA, bad)
            r = run_cli("data", bad, os.path.join(OUT_DIR, "bad.csv"))
            self.assertNotEqual(r.returncode, 0, bad)
        self.assertNotEqual(run_cli("data").returncode, 0)

    def test_dod11_empty_month(self):
        self.assertEqual(make_invoices(DATA, "2025-01"), [])
        out = os.path.join(OUT_DIR, "empty.csv")
        r = run_cli("data", "2025-01", out)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(out, encoding="utf-8", newline="") as f:
            self.assertEqual(list(csv.reader(f)),
                             [["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
