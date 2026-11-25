import os
import tempfile
import unittest

from solution import monthly_sales

HERE = os.path.dirname(os.path.abspath(__file__))


class TestMonthlySales(unittest.TestCase):
    def setUp(self):
        self.result = monthly_sales(os.path.join(HERE, "sales.csv"))

    def test_expected_dict(self):
        self.assertEqual(
            self.result,
            {"2026-01": 16500, "2026-02": 11000, "2026-04": 18700, "2026-05": 7700},
        )

    def test_jan_excludes_cancelled_and_jst_boundary(self):
        # A-1003 cancelled 除外 / A-1004 (UTC 1/31 16:20) は JST で 2 月
        self.assertEqual(self.result["2026-01"], 11000 + 5500)

    def test_feb_includes_negative_and_boundary(self):
        self.assertEqual(self.result["2026-02"], 3300 + 8800 - 1100)

    def test_apr_may_boundary(self):
        # A-1010 (UTC 4/30 15:30) は JST で 5 月
        self.assertEqual(self.result["2026-04"], 16500 + 2200)
        self.assertEqual(self.result["2026-05"], 7700)

    def test_no_empty_month_int_values_sorted_keys(self):
        self.assertNotIn("2026-03", self.result)
        self.assertTrue(all(type(v) is int for v in self.result.values()))
        self.assertEqual(list(self.result), sorted(self.result))

    def test_path_argument_used(self):
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            p = os.path.join(d, "x.csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write("order_id,ordered_at,amount_incl_tax,status\n"
                        "X1,2025-12-31T15:00:00Z,100,completed\n"
                        "X2,2025-12-31T14:59:59Z,50,completed\n")
            self.assertEqual(monthly_sales(p), {"2025-12": 50, "2026-01": 100})


if __name__ == "__main__":
    unittest.main()
