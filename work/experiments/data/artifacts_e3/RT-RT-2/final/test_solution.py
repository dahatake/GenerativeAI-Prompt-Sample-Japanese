import os
import shutil
import tempfile
import unittest
from datetime import date, datetime

from solution import reorder_plan

HERE = os.path.dirname(os.path.abspath(__file__))
INV_HEADER = "sku,name,stock,on_order,lead_time_days,safety_stock,lot,discontinued\n"


class _TmpDirCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(dir=HERE)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, name, text, encoding="utf-8"):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding=encoding, newline="") as f:
            f.write(text)
        return path

    def plan(self, inventory, shipments, today="2026-11-10", encoding="utf-8"):
        inv = self.write("inventory.csv", INV_HEADER + inventory, encoding)
        shp = self.write("shipments.csv", "date,sku,qty\n" + shipments, encoding)
        return reorder_plan(inv, shp, today)


class PinnedBehaviorTest(_TmpDirCase):
    """Current behavior that does not contradict answers.md."""

    def test_sample_data(self):
        result = reorder_plan(
            os.path.join(HERE, "inventory.csv"), os.path.join(HERE, "shipments.csv"), "2026-11-10"
        )
        self.assertEqual(result, [{"sku": "A100", "qty": 50}])

    def test_discontinued_not_ordered(self):
        result = self.plan("X1,x,0,0,5,10,10,true\nX2,x,0,0,5,10,10,TRUE\nX3,x,0,0,5,10,10,false\n", "")
        self.assertEqual(result, [{"sku": "X3", "qty": 10}])

    def test_shipments_on_or_after_today_ignored(self):
        result = self.plan(
            "X1,x,10,0,10,5,10,false\n",
            "2026-11-10,X1,1000\n2026-11-11,X1,1000\n",
        )
        self.assertEqual(result, [])

    def test_unknown_sku_shipments_ignored_and_no_shipments_means_zero_demand(self):
        # Demand 0 -> reorder point = safety_stock (5).
        result = self.plan("X1,x,4,0,10,5,10,false\nX2,x,6,0,10,5,10,false\n", "2026-11-05,ZZZ,1000\n")
        self.assertEqual(result, [{"sku": "X1", "qty": 10}])

    def test_shortage_rounded_up_to_lot_multiple(self):
        result = self.plan("X1,x,3,0,5,25,10,false\nX2,x,0,5,5,26,7,false\n", "")
        self.assertEqual(result, [{"sku": "X1", "qty": 30}, {"sku": "X2", "qty": 21}])

    def test_on_order_counts_as_position(self):
        result = self.plan("X1,x,5,10,5,12,10,false\n", "")
        self.assertEqual(result, [])

    def test_sorted_by_sku_and_qty_is_int(self):
        result = self.plan("B,x,0,0,5,10,10,false\nA,x,0,0,5,10,10,false\n", "")
        self.assertEqual([r["sku"] for r in result], ["A", "B"])
        self.assertTrue(all(type(r["qty"]) is int for r in result))

    def test_today_formats(self):
        inv = "X1,x,0,0,5,10,10,false\n"
        expected = [{"sku": "X1", "qty": 10}]
        for today in ("2026-11-10", date(2026, 11, 10), datetime(2026, 11, 10, 9, 30)):
            self.assertEqual(self.plan(inv, "", today=today), expected)

    def test_utf8_bom(self):
        result = self.plan("X1,ボルト,0,0,5,10,10,false\n", "", encoding="utf-8-sig")
        self.assertEqual(result, [{"sku": "X1", "qty": 10}])


class AnsweredSpecTest(_TmpDirCase):
    """Behavior required by answers.md (Q2, Q4, Q6)."""

    def test_window_is_28_days_before_today(self):
        # 2026-10-13 is today-28 (inside), 2026-10-12 is today-29 (outside).
        inv = "X1,x,0,0,1,0,1,false\n"
        self.assertEqual(self.plan(inv, "2026-10-13,X1,28\n"), [{"sku": "X1", "qty": 1}])
        self.assertEqual(self.plan(inv, "2026-10-12,X1,28\n"), [])

    def test_daily_demand_is_sum_over_28(self):
        # 56 shipped in window -> 2/day; lead time 10 -> reorder point 20.
        result = self.plan("X1,x,0,0,10,0,1,false\n", "2026-10-20,X1,56\n")
        self.assertEqual(result, [{"sku": "X1", "qty": 20}])

    def test_short_history_still_divided_by_28(self):
        # Only one shipment, 2 days before today: 28/28 = 1/day, not 28/2.
        result = self.plan("X1,x,0,0,10,0,1,false\n", "2026-11-08,X1,28\n")
        self.assertEqual(result, [{"sku": "X1", "qty": 10}])

    def test_qty_is_shortage_rounded_to_lot_without_minimum(self):
        # position == reorder point -> shortage 0 -> nothing to order.
        self.assertEqual(self.plan("X1,x,10,0,5,10,50,false\n", ""), [])


if __name__ == "__main__":
    unittest.main()
