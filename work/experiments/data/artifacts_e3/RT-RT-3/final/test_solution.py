import os
import tempfile
import unittest
from datetime import date, datetime, timedelta

from solution import reorder_plan

HERE = os.path.dirname(os.path.abspath(__file__))
INV_HEADER = "sku,name,stock,on_order,lead_time_days,safety_stock,lot,discontinued"
TODAY = date(2026, 11, 10)


def daily(sku, qty, days, today=TODAY):
    """Constant demand every day for `days` days before today (window-length independent)."""
    return [f"{(today - timedelta(days=i)).isoformat()},{sku},{qty}" for i in range(1, days + 1)]


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=HERE)
        self.dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name, lines, encoding="utf-8"):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding=encoding, newline="") as f:
            f.write("\n".join(lines) + "\n")
        return path

    def plan(self, inv_rows, ship_rows, today=TODAY, encoding="utf-8"):
        inv = self.write("inventory.csv", [INV_HEADER] + inv_rows, encoding)
        shp = self.write("shipments.csv", ["date,sku,qty"] + ship_rows, encoding)
        return reorder_plan(inv, shp, today)


class PinnedBehaviour(Base):
    """Current behaviour that is consistent with answers.md."""

    def test_sample_data(self):
        result = reorder_plan(os.path.join(HERE, "inventory.csv"), os.path.join(HERE, "shipments.csv"), "2026-11-10")
        self.assertEqual(result, [{"sku": "A100", "qty": 50}])

    def test_discontinued_not_ordered(self):
        result = self.plan(["X,x,0,0,7,20,10,true", "Y,y,0,0,7,20,10,false"], daily("X", 5, 60) + daily("Y", 5, 60))
        self.assertEqual([r["sku"] for r in result], ["Y"])

    def test_reorder_point_and_lot_round_up(self):
        # daily 2 * lead 5 + safety 10 = 20; position 5+3=8; shortage 12 -> 2 lots of 10
        result = self.plan(["X,x,5,3,5,10,10,false"], daily("X", 2, 60))
        self.assertEqual(result, [{"sku": "X", "qty": 20}])

    def test_fractional_shortage_rounds_up_to_one_lot(self):
        # reorder point 20.5 vs position 20 -> 1 lot
        result = self.plan(["X,x,20,0,1,20,50,false"], daily("X", 0.5, 60))
        self.assertEqual(result, [{"sku": "X", "qty": 50}])

    def test_no_order_above_reorder_point(self):
        self.assertEqual(self.plan(["X,x,100,0,5,10,10,false"], daily("X", 2, 60)), [])

    def test_shipments_on_or_after_today_ignored(self):
        base = daily("X", 2, 60)
        extra = [f"{TODAY.isoformat()},X,1000", f"{(TODAY + timedelta(days=3)).isoformat()},X,1000"]
        inv = ["X,x,5,3,5,10,10,false"]
        self.assertEqual(self.plan(inv, base + extra), self.plan(inv, base))

    def test_unknown_sku_ignored_and_no_shipment_means_zero_demand(self):
        # Y has no shipments: reorder point = safety stock 10 > position 4 -> 6 -> 1 lot of 10
        result = self.plan(["Y,y,4,0,5,10,10,false"], daily("ZZZ", 100, 60))
        self.assertEqual(result, [{"sku": "Y", "qty": 10}])

    def test_today_formats(self):
        inv = ["X,x,5,3,5,10,10,false"]
        ships = daily("X", 2, 60)
        expected = [{"sku": "X", "qty": 20}]
        for t in (TODAY, datetime(2026, 11, 10, 15, 30), "2026-11-10"):
            self.assertEqual(self.plan(inv, ships, today=t), expected)

    def test_utf8_bom(self):
        result = self.plan(["X,ボルト,5,3,5,10,10,false"], daily("X", 2, 60), encoding="utf-8-sig")
        self.assertEqual(result, [{"sku": "X", "qty": 20}])

    def test_sorted_by_sku_and_int_qty(self):
        result = self.plan(["B,b,0,0,1,5,10,false", "A,a,0,0,1,5,10,false"], [])
        self.assertEqual([r["sku"] for r in result], ["A", "B"])
        self.assertTrue(all(type(r["qty"]) is int for r in result))


class AnsweredBehaviour(Base):
    """Behaviour changed according to answers.md (Q2, Q4, Q6)."""

    def test_window_is_28_days_before_today(self):
        # Shipment 28 days before today counts, 29 days before does not.
        inv = ["X,x,0,0,1,0,1,false"]
        in_window = [f"{(TODAY - timedelta(days=28)).isoformat()},X,28"]
        out_window = [f"{(TODAY - timedelta(days=29)).isoformat()},X,28"]
        self.assertEqual(self.plan(inv, in_window), [{"sku": "X", "qty": 1}])
        self.assertEqual(self.plan(inv, out_window), [])

    def test_short_history_still_divided_by_28(self):
        # 56 shipped over the last 2 days -> 56/28 = 2/day; lead 10 -> reorder point 20
        result = self.plan(["X,x,0,0,10,0,1,false"], daily("X", 28, 2))
        self.assertEqual(result, [{"sku": "X", "qty": 20}])

    def test_position_equal_to_reorder_point_orders_nothing(self):
        # reorder point = 1*5 + 10 = 15, position = 15 -> shortage 0 -> qty 0 -> not listed
        self.assertEqual(self.plan(["X,x,10,5,5,10,10,false"], daily("X", 1, 60)), [])


if __name__ == "__main__":
    unittest.main()
