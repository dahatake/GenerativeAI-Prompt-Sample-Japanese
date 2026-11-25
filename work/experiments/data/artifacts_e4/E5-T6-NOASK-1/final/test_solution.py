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
MONEY_KEYS = ("subtotal", "discount", "tax", "total")

# Hand-calculated expectations for 2026-10 (JST, completed+shipped, gold 5%, food 8% / general 10%, floor).
EXPECTED_2026_10 = {
    # C001 gold: food 5400+6720=12120, general 9100+5960=15060, subtotal 27180
    # discount 1359 -> food 606, general 753; tax floor(11514*.08)=921 + floor(14307*.1)=1430
    "C001": dict(subtotal=27180, discount=1359, tax=2351, total=28172,
                 orders=["O1003", "O1008", "O1012", "O1016"]),
    # C002 standard: food 3240+3360=6600 -> 528, general 2980+2980=5960 -> 596
    "C002": dict(subtotal=12560, discount=0, tax=1124, total=13684,
                 orders=["O1004", "O1009", "O1018", "O1022"]),
    # C003 gold: food 4740+3160+6480=14380, general 3600+2980=6580, discount 1048 -> 719/329
    # tax floor(13661*.08)=1092 + floor(6251*.1)=625
    "C003": dict(subtotal=20960, discount=1048, tax=1717, total=21629,
                 orders=["O1002", "O1007", "O1011", "O1015", "O1020"]),
    # C004 standard: food 1680 -> 134, general 6000+2600=8600 -> 860
    "C004": dict(subtotal=10280, discount=0, tax=994, total=11274,
                 orders=["O1005", "O1014", "O1019"]),
}


def by_customer(invoices):
    return {inv["customer_id"]: inv for inv in invoices}


def all_order_ids(invoices):
    return {line["order_id"] for inv in invoices for line in inv["lines"]}


class TestStructure(unittest.TestCase):  # DoD 1, 2
    def test_keys_and_int_amounts(self):
        invoices = make_invoices(DATA, "2026-10")
        self.assertTrue(invoices)
        for inv in invoices:
            self.assertEqual(set(inv), {"invoice_id", "customer_id", "lines", *MONEY_KEYS})
            for k in MONEY_KEYS:
                self.assertIs(type(inv[k]), int, (inv["invoice_id"], k))
            for line in inv["lines"]:
                self.assertEqual(set(line), {"order_id", "sku", "qty", "unit_price", "amount"})
                for k in ("qty", "unit_price", "amount"):
                    self.assertIs(type(line[k]), int)

    def test_invariants_all_months(self):
        for month in ("2026-09", "2026-10", "2026-11"):
            for inv in make_invoices(DATA, month):
                for line in inv["lines"]:
                    self.assertEqual(line["amount"], line["unit_price"] * line["qty"])
                self.assertEqual(inv["subtotal"], sum(l["amount"] for l in inv["lines"]))
                self.assertEqual(inv["total"], inv["subtotal"] - inv["discount"] + inv["tax"])


class TestBoundaries(unittest.TestCase):  # DoD 3
    def setUp(self):
        self.sep = all_order_ids(make_invoices(DATA, "2026-09"))
        self.oct = make_invoices(DATA, "2026-10")
        self.oct_ids = all_order_ids(self.oct)
        self.nov = all_order_ids(make_invoices(DATA, "2026-11"))
        self.lines = {l["order_id"]: l for inv in self.oct for l in inv["lines"]}

    def test_month_by_jst(self):
        self.assertIn("O1002", self.oct_ids)   # 09-30T15:30Z = 10-01 JST
        self.assertNotIn("O1002", self.sep)
        self.assertIn("O1021", self.nov)       # 10-31T16:00Z = 11-01 JST
        self.assertNotIn("O1021", self.oct_ids)
        self.assertIn("O1022", self.oct_ids)   # 10-31T14:50Z = 10-31 23:50 JST

    def test_price_by_jst_order_date(self):
        self.assertEqual(self.lines["O1008"]["unit_price"], 1680)  # 10-10 00:10 JST -> new F100 price
        self.assertEqual(self.lines["O1012"]["unit_price"], 1300)  # 10-16 00:20 JST -> new A100 price
        self.assertEqual(self.lines["O1007"]["unit_price"], 1580)  # 10-08 JST -> old F100 price
        self.assertEqual(self.lines["O1011"]["unit_price"], 1200)  # 10-14 JST -> old A100 price

    def test_status_filter(self):
        for oid in ("O1006", "O1013", "O1010", "O1017"):  # cancelled / returned
            self.assertNotIn(oid, self.oct_ids)
        self.assertIn("O1004", self.oct_ids)  # shipped
        self.assertIn("O1015", self.oct_ids)  # shipped
        self.assertNotIn("C005", by_customer(self.oct))  # only cancelled/returned orders


class TestExpectedOctober(unittest.TestCase):  # DoD 4
    def test_hand_calculated(self):
        invoices = make_invoices(DATA, "2026-10")
        self.assertEqual([i["customer_id"] for i in invoices], sorted(EXPECTED_2026_10))
        got = by_customer(invoices)
        for cid, exp in EXPECTED_2026_10.items():
            inv = got[cid]
            self.assertEqual(inv["invoice_id"], f"INV-202610-{cid}")
            self.assertEqual({k: inv[k] for k in MONEY_KEYS}, {k: exp[k] for k in MONEY_KEYS}, cid)
            self.assertEqual([l["order_id"] for l in inv["lines"]], exp["orders"], cid)


class TestOtherMonths(unittest.TestCase):  # DoD 5
    def test_september(self):
        inv = make_invoices(DATA, "2026-09")
        # C001 gold, O1001 A100 2x1200=2400, discount 120 (all general), tax floor(2280*.1)=228
        self.assertEqual([(i["customer_id"], i["subtotal"], i["discount"], i["tax"], i["total"]) for i in inv],
                         [("C001", 2400, 120, 228, 2508)])

    def test_november(self):
        inv = make_invoices(DATA, "2026-11")
        self.assertEqual(
            [(i["customer_id"], i["subtotal"], i["discount"], i["tax"], i["total"]) for i in inv],
            [
                ("C001", 2700, 135, 205, 2770),  # food only: tax floor(2565*.08)=205
                ("C003", 1300, 65, 123, 1358),   # general only: tax floor(1235*.1)=123
                ("C004", 3360, 0, 268, 3628),    # food only: floor(268.8)=268
            ],
        )

    def test_no_overlap_or_gap(self):
        months = [all_order_ids(make_invoices(DATA, m)) for m in ("2026-09", "2026-10", "2026-11")]
        self.assertEqual(sum(len(m) for m in months), len(set().union(*months)))
        with open(os.path.join(DATA, "orders.csv"), encoding="utf-8") as f:
            billable = {r["order_id"] for r in csv.DictReader(f) if r["status"] in ("completed", "shipped")}
        self.assertEqual(set().union(*months), billable)

    def test_empty_month(self):
        self.assertEqual(make_invoices(DATA, "2025-01"), [])


class TestInvalidInput(unittest.TestCase):  # DoD 6
    def test_bad_month(self):
        for m in ("2026-13", "202610", "2026-1", "2026-00", "", "26-10"):
            with self.assertRaises(ValueError, msg=m):
                make_invoices(DATA, m)

    def _with_extra_order(self, line):
        tmp = tempfile.mkdtemp(dir=HERE)
        self.addCleanup(shutil.rmtree, tmp)
        for name in os.listdir(DATA):
            shutil.copy(os.path.join(DATA, name), tmp)
        with open(os.path.join(tmp, "orders.csv"), "a", encoding="utf-8", newline="") as f:
            f.write(line + "\r\n")
        return tmp

    def test_unknown_sku(self):
        d = self._with_extra_order("O9999,C001,2026-10-05T00:00:00Z,Z999,1,completed")
        with self.assertRaises(ValueError):
            make_invoices(d, "2026-10")

    def test_unknown_customer(self):
        d = self._with_extra_order("O9999,C999,2026-10-05T00:00:00Z,A100,1,completed")
        with self.assertRaises(ValueError):
            make_invoices(d, "2026-10")

    def test_no_effective_price(self):
        d = self._with_extra_order("O9999,C001,2025-12-31T00:00:00Z,A100,1,completed")
        with self.assertRaises(ValueError):
            make_invoices(d, "2025-12")


class TestCli(unittest.TestCase):  # DoD 7
    def test_cli_writes_csv(self):
        tmp = tempfile.mkdtemp(dir=HERE)
        self.addCleanup(shutil.rmtree, tmp)
        out = os.path.join(tmp, "out.csv")
        r = subprocess.run([sys.executable, os.path.join(HERE, "solution.py"), DATA, "2026-10", out],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(out, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))
        self.assertEqual(rows[0], ["invoice_id", "customer_id", "subtotal", "discount", "tax", "total"])
        expected = [[i["invoice_id"], i["customer_id"]] + [str(i[k]) for k in MONEY_KEYS]
                    for i in make_invoices(DATA, "2026-10")]
        self.assertEqual(rows[1:], expected)

    def test_cli_bad_args(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "solution.py"), DATA, "2026-13", "x.csv"],
                           capture_output=True, text=True, cwd=HERE)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(os.path.join(HERE, "x.csv")))


if __name__ == "__main__":
    unittest.main()
