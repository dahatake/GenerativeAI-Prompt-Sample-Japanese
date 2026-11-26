import os
import re
import unittest

from solution import monthly_sales


class MonthlySalesTests(unittest.TestCase):
    def setUp(self):
        self.fixture = os.path.abspath("test_sales_fixture.csv")

    def tearDown(self):
        if os.path.exists(self.fixture):
            os.remove(self.fixture)

    def test_existing_sales_csv(self):
        result = monthly_sales(os.path.abspath("sales.csv"))
        self.assertEqual(
            result,
            {"2026-01": 16500, "2026-02": 11000, "2026-03": 0, "2026-04": 18700, "2026-05": 7700},
        )

    def test_month_keys_are_dict_int_and_complete_range(self):
        result = monthly_sales(os.path.abspath("sales.csv"))
        self.assertIsInstance(result, dict)
        self.assertTrue(all(re.fullmatch(r"\d{4}-\d{2}", key) for key in result))
        self.assertTrue(all(isinstance(value, int) and not isinstance(value, bool) for value in result.values()))

    def test_cancel_negative_timezone_and_zero_month(self):
        with open(self.fixture, "w", encoding="utf-8", newline="") as f:
            f.write("order_id,ordered_at,amount_incl_tax,status\n")
            f.write("A1,2026-01-31T16:20:00Z,3000,completed\n")
            f.write("A2,2026-01-20T23:30:00Z,9999,cancelled\n")
            f.write("A3,2026-03-01T00:30:00Z,-500,completed\n")
            f.write("A4,2026-04-30T15:30:00Z,2000,completed\n")
        self.assertEqual(
            monthly_sales(self.fixture),
            {"2026-02": 3000, "2026-03": -500, "2026-04": 0, "2026-05": 2000},
        )

    def test_no_completed_rows_returns_empty_dict(self):
        with open(self.fixture, "w", encoding="utf-8", newline="") as f:
            f.write("order_id,ordered_at,amount_incl_tax,status\n")
            f.write("A1,2026-01-01T00:00:00Z,100,cancelled\n")
        self.assertEqual(monthly_sales(self.fixture), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
