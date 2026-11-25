import os
import shutil
import tempfile
import unittest
from datetime import date, datetime, timedelta

from solution import reorder_plan

HERE = os.path.dirname(os.path.abspath(__file__))
INV_HEADER = "sku,name,stock,on_order,lead_time_days,safety_stock,lot,discontinued"
TODAY = date(2026, 11, 10)


def _d(days_before):
    return (TODAY - timedelta(days=days_before)).isoformat()


class ReorderPlanTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(dir=HERE)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, name, lines, encoding="utf-8"):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding=encoding, newline="") as f:
            f.write("\n".join(lines) + "\n")
        return path

    def run_plan(self, inv_lines, ship_lines, today=TODAY):
        inv = self.write("inventory.csv", [INV_HEADER] + inv_lines)
        # An old shipment of an unrelated sku keeps the history long, so results
        # here do not depend on how short histories are handled.
        ship = self.write("shipments.csv", ["date,sku,qty", f"{_d(100)},ZZZ,1"] + ship_lines)
        return reorder_plan(inv, ship, today)


class CurrentBehaviorTests(ReorderPlanTestBase):
    """Behavior fixed before the change; it does not contradict answers.md."""

    def test_sample_data(self):
        result = reorder_plan(
            os.path.join(HERE, "inventory.csv"), os.path.join(HERE, "shipments.csv"), "2026-11-10"
        )
        self.assertEqual(result, [{"sku": "A100", "qty": 50}])

    def test_discontinued_item_is_not_ordered(self):
        result = self.run_plan(
            ["X1,x,0,0,7,10,5,true", "X2,x,0,0,7,10,5,TRUE", "X3,x,0,0,7,10,5,false"], []
        )
        self.assertEqual(result, [{"sku": "X3", "qty": 10}])

    def test_shipments_on_or_after_today_are_ignored(self):
        ships = [f"{TODAY.isoformat()},X1,1000", f"{(TODAY + timedelta(days=3)).isoformat()},X1,1000"]
        self.assertEqual(self.run_plan(["X1,x,10,0,7,5,10,false"], ships), [])

    def test_yesterday_shipment_is_counted(self):
        # 28 * 10 shipped yesterday -> daily 10 -> reorder point 10*1+0 = 10 > 5
        result = self.run_plan(["X1,x,5,0,1,0,1,false"], [f"{_d(1)},X1,280"])
        self.assertEqual(result, [{"sku": "X1", "qty": 5}])

    def test_unknown_sku_shipments_ignored_and_no_shipment_means_zero_demand(self):
        result = self.run_plan(
            ["X1,x,5,0,7,4,10,false", "X2,x,3,0,7,4,10,false"], [f"{_d(1)},NOPE,99999"]
        )
        self.assertEqual(result, [{"sku": "X2", "qty": 10}])

    def test_effective_stock_includes_on_order(self):
        result = self.run_plan(["X1,x,1,10,7,5,10,false", "X2,x,1,2,7,5,10,false"], [])
        self.assertEqual(result, [{"sku": "X2", "qty": 10}])

    def test_qty_is_shortage_rounded_up_to_lot_multiple(self):
        # demand 28*2/28 = 2/day, lead 5 -> RP = 10 + 3 = 13; position 0 -> shortage 13 -> 3 lots of 5
        ships = [f"{_d(i)},X1,2" for i in range(1, 29)]
        self.assertEqual(self.run_plan(["X1,x,0,0,5,3,5,false"], ships), [{"sku": "X1", "qty": 15}])

    def test_exact_lot_multiple_is_not_rounded_further(self):
        self.assertEqual(self.run_plan(["X1,x,0,0,7,20,10,false"], []), [{"sku": "X1", "qty": 20}])

    def test_today_accepts_date_datetime_and_iso_string(self):
        inv = ["X1,x,5,0,1,0,1,false"]
        ships = [f"{_d(1)},X1,280"]
        expected = [{"sku": "X1", "qty": 5}]
        for today in (TODAY, datetime(2026, 11, 10, 15, 30), "2026-11-10"):
            with self.subTest(today=today):
                self.assertEqual(self.run_plan(inv, ships, today), expected)

    def test_utf8_bom_csv(self):
        inv = self.write("inventory.csv", [INV_HEADER, "X1,ボルト,0,0,7,10,5,false"], "utf-8-sig")
        ship = self.write("shipments.csv", ["date,sku,qty"], "utf-8-sig")
        self.assertEqual(reorder_plan(inv, ship, TODAY), [{"sku": "X1", "qty": 10}])

    def test_sorted_by_sku_and_qty_is_int(self):
        result = self.run_plan(["B1,x,0,0,7,1,1,false", "A1,x,0,0,7,1,1,false"], [])
        self.assertEqual([r["sku"] for r in result], ["A1", "B1"])
        self.assertTrue(all(type(r["qty"]) is int for r in result))

    def test_empty_when_nothing_to_order(self):
        self.assertEqual(self.run_plan(["X1,x,100,0,7,5,10,false"], []), [])


class AnsweredSpecTests(ReorderPlanTestBase):
    """Behavior changed according to answers.md."""

    def test_window_is_28_days_before_today(self):
        # Q2: today-28 is counted, today-29 is not. 28 / 28 = 1/day -> RP = 1*10 = 10 > 5
        inv = ["X1,x,5,0,10,0,1,false"]
        self.assertEqual(self.run_plan(inv, [f"{_d(28)},X1,28"]), [{"sku": "X1", "qty": 5}])
        self.assertEqual(self.run_plan(inv, [f"{_d(29)},X1,28"]), [])

    def test_short_history_is_still_divided_by_28(self):
        # Q4: only shipment ever is 2 days ago; 56 / 28 = 2/day -> RP = 2*10 = 20 -> qty 15
        inv = self.write("inventory.csv", [INV_HEADER, "X1,x,5,0,10,0,1,false"])
        ship = self.write("shipments.csv", ["date,sku,qty", f"{_d(2)},X1,56"])
        self.assertEqual(reorder_plan(inv, ship, TODAY), [{"sku": "X1", "qty": 15}])

    def test_no_order_when_effective_stock_equals_reorder_point(self):
        # Q6: qty = ceil((RP - position) / lot) * lot, which is 0 here
        self.assertEqual(self.run_plan(["X1,x,10,0,7,10,50,false"], []), [])


if __name__ == "__main__":
    unittest.main()
