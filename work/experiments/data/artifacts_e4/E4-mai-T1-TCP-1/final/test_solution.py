import io
import unittest
from unittest.mock import patch

from solution import monthly_sales


HEADER = "order_id,ordered_at,amount_incl_tax,status\n"


def csv_open(text):
    return patch("builtins.open", return_value=io.StringIO(text))


class MonthlySalesTests(unittest.TestCase):
    def test_sample_sales(self):
        result = monthly_sales("sales.csv")
        expected = {
            "2026-01": 19800,
            "2026-02": 7700,
            "2026-03": 0,
            "2026-04": 26400,
        }
        self.assertEqual(result, expected)

    def test_keys_and_values_are_valid_types(self):
        result = monthly_sales("sales.csv")
        for key, value in result.items():
            self.assertRegex(key, r"^\d{4}-\d{2}$")
            self.assertIs(type(value), int)

    def test_cancelled_and_negative_completed(self):
        result = monthly_sales("sales.csv")
        self.assertEqual(result["2026-02"], 7700)

    def test_missing_month_is_zero(self):
        result = monthly_sales("sales.csv")
        self.assertEqual(result["2026-03"], 0)

    def test_empty_csv(self):
        with csv_open(HEADER):
            self.assertEqual(monthly_sales("in-memory.csv"), {})

    def test_missing_header(self):
        text = "order_id,ordered_at,amount\n1,2026-01-01T00:00:00Z,100\n"
        with csv_open(text):
            with self.assertRaises(ValueError):
                monthly_sales("in-memory.csv")

    def test_invalid_datetime(self):
        text = HEADER + "1,not-a-date,100,completed\n"
        with csv_open(text):
            with self.assertRaises(ValueError):
                monthly_sales("in-memory.csv")

    def test_invalid_amount(self):
        text = HEADER + "1,2026-01-01T00:00:00Z,bad,completed\n"
        with csv_open(text):
            with self.assertRaises(ValueError):
                monthly_sales("in-memory.csv")


if __name__ == "__main__":
    unittest.main()
