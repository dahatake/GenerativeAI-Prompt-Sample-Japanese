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

EXPECTED_2026_10 = [
    # invoice_id, customer_id, order_ids, subtotal, discount, tax, total
    ("INV-202610-0001", "C001", ["O1003", "O1008", "O1012", "O1016"], 27180, 1359, 2351, 28172),
    ("INV-202610-0002", "C002", ["O1004", "O1009", "O1018", "O1022"], 12560, 0, 1124, 13684),
    ("INV-202610-0003", "C003", ["O1002", "O1007", "O1011", "O1015", "O1020"], 20960, 1048, 1717, 21629),
    ("INV-202610-0004", "C004", ["O1005", "O1014", "O1019"], 10280, 0, 994, 11274),
]


class TestMakeInvoices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.invoices = make_invoices(DATA, "2026-10")

    def _lines(self):
        return {l["order_id"]: l for inv in self.invoices for l in inv["lines"]}

    def test_dod1_returns_list_with_required_keys(self):
        self.assertIsInstance(self.invoices, list)
        for inv in self.invoices:
            self.assertEqual(
                set(inv), {"invoice_id", "customer_id", "lines", "subtotal", "discount", "tax", "total"}
            )
            for line in inv["lines"]:
                self.assertEqual(set(line), {"order_id", "sku", "qty", "unit_price", "amount"})

    def test_dod2_invariants_and_int_amounts(self):
        for inv in self.invoices:
            for key in ("subtotal", "discount", "tax", "total"):
                self.assertIs(type(inv[key]), int)
            for line in inv["lines"]:
                for key in ("qty", "unit_price", "amount"):
                    self.assertIs(type(line[key]), int)
                self.assertEqual(line["amount"], line["qty"] * line["unit_price"])
            self.assertEqual(inv["subtotal"], sum(l["amount"] for l in inv["lines"]))
            self.assertEqual(inv["total"], inv["subtotal"] - inv["discount"] + inv["tax"])

    def test_dod3_jst_month_and_price_boundaries(self):
        lines = self._lines()
        self.assertIn("O1002", lines)  # 2026-09-30T15:30Z = 10-01 JST
        self.assertNotIn("O1021", lines)  # 2026-10-31T16:00Z = 11-01 JST
        self.assertEqual(lines["O1008"]["unit_price"], 1680)  # 10-10 JST
        self.assertEqual(lines["O1012"]["unit_price"], 1300)  # 10-16 JST
        nov = {l["order_id"] for inv in make_invoices(DATA, "2026-11") for l in inv["lines"]}
        self.assertIn("O1021", nov)
        sep = {l["order_id"] for inv in make_invoices(DATA, "2026-09") for l in inv["lines"]}
        self.assertNotIn("O1002", sep)

    def test_dod4_status_filter(self):
        lines = self._lines()
        for oid in ("O1006", "O1010", "O1013", "O1017"):
            self.assertNotIn(oid, lines)
        self.assertNotIn("C005", [inv["customer_id"] for inv in self.invoices])

    def test_dod5_expected_values(self):
        actual = [
            (i["invoice_id"], i["customer_id"], [l["order_id"] for l in i["lines"]],
             i["subtotal"], i["discount"], i["tax"], i["total"])
            for i in self.invoices
        ]
        self.assertEqual(actual, [(*e[:2], e[2], *e[3:]) for e in EXPECTED_2026_10])

    def test_dod5_discount_per_tax_category(self):
        # food 19 + general 19: per-category floor(0.95)+floor(0.95)=0, whole-invoice floor would be 1
        tmp = tempfile.mkdtemp(dir=HERE)
        try:
            files = {
                "customers.csv": "customer_id,name,tier\nG1,x,gold\n",
                "products.csv": "sku,name,category\nF,f,food\nG,g,general\n",
                "prices.csv": "sku,effective_from,unit_price\nF,2026-01-01,19\nG,2026-01-01,19\n",
                "orders.csv": "order_id,customer_id,ordered_at,sku,qty,status\n"
                "X1,G1,2026-10-02T00:00:00Z,F,1,completed\nX2,G1,2026-10-01T00:00:00Z,G,1,shipped\n",
            }
            for name, text in files.items():
                with open(os.path.join(tmp, name), "w", encoding="utf-8", newline="") as f:
                    f.write(text)
            [inv] = make_invoices(tmp, "2026-10")
            self.assertEqual(inv["discount"], 0)
            self.assertEqual(inv["tax"], 19 * 8 // 100 + 19 * 10 // 100)  # 1 + 1
            self.assertEqual([l["order_id"] for l in inv["lines"]], ["X2", "X1"])
        finally:
            shutil.rmtree(tmp)

    def test_dod6_cli_csv(self):
        out = os.path.join(HERE, "out_test.csv")
        try:
            proc = subprocess.run(
                [sys.executable, os.path.join(HERE, "solution.py"), DATA, "2026-10", out],
                capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with open(out, encoding="utf-8", newline="") as f:
                rows = list(csv.reader(f))
            self.assertEqual(rows[0], ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"])
            self.assertEqual(
                rows[1:], [[e[0], e[1], *map(str, e[3:])] for e in EXPECTED_2026_10]
            )
        finally:
            if os.path.exists(out):
                os.remove(out)

    def test_dod7_invalid_month_and_empty_month(self):
        for bad in ("2026-13", "2026/10", "2026-1", "202610", "2026-00"):
            with self.assertRaises(ValueError):
                make_invoices(DATA, bad)
        self.assertEqual(make_invoices(DATA, "2025-01"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
