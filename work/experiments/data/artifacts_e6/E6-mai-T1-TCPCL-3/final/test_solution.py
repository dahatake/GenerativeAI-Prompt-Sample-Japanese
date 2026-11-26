import unittest
import os
from solution import monthly_sales


FIXTURE = r"C:\Users\dahatake\AppData\Local\Temp\tc-exp6\E6-mai-T1-TCPCL-3\test_fixture.csv"


class MonthlySalesTests(unittest.TestCase):
    def tearDown(self):
        if os.path.exists(FIXTURE):
            os.remove(FIXTURE)

    def write_fixture(self, text):
        with open(FIXTURE, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)

    def test_sales_csv_approved_values_and_empty_month(self):
        result = monthly_sales(r"C:\Users\dahatake\AppData\Local\Temp\tc-exp6\E6-mai-T1-TCPCL-3\sales.csv")
        self.assertEqual(result, {
            "2026-01": 15000,
            "2026-02": 10000,
            "2026-03": 0,
            "2026-04": 17000,
            "2026-05": 7000,
        })

    def test_cancelled_is_excluded_and_month_keys_are_sorted(self):
        result = monthly_sales(r"C:\Users\dahatake\AppData\Local\Temp\tc-exp6\E6-mai-T1-TCPCL-3\sales.csv")
        self.assertEqual(list(result), ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05"])

    def test_jst_boundary_and_negative_amount(self):
        self.write_fixture(
            "order_id,ordered_at,amount_incl_tax,status\n"
            "A,2026-01-31T15:30:00Z,-1100,completed\n"
            "B,2026-01-31T14:30:00Z,1100,completed\n"
        )
        self.assertEqual(monthly_sales(FIXTURE), {
            "2026-01": 1000,
            "2026-02": -1000,
        })

    def test_round_each_row_before_month_sum(self):
        self.write_fixture(
            "order_id,ordered_at,amount_incl_tax,status\n"
            "A,2026-05-01T00:00:00Z,6,completed\n"
            "B,2026-05-02T00:00:00Z,6,completed\n"
        )
        self.assertEqual(monthly_sales(FIXTURE), {"2026-05": 10})

    def test_zero_value_keeps_month(self):
        self.write_fixture(
            "order_id,ordered_at,amount_incl_tax,status\n"
            "A,2026-06-01T00:00:00Z,0,completed\n"
        )
        self.assertEqual(monthly_sales(FIXTURE), {"2026-06": 0})

    def test_missing_required_value_raises(self):
        self.write_fixture(
            "order_id,ordered_at,amount_incl_tax,status\n"
            "A,2026-07-01T00:00:00Z,,completed\n"
        )
        with self.assertRaises(ValueError):
            monthly_sales(FIXTURE)

    def test_all_values_are_int(self):
        result = monthly_sales(r"C:\Users\dahatake\AppData\Local\Temp\tc-exp6\E6-mai-T1-TCPCL-3\sales.csv")
        self.assertTrue(all(isinstance(value, int) for value in result.values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
