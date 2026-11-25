import re
import unittest

from solution import monthly_sales


class MonthlySalesTests(unittest.TestCase):
    def test_sales_csv_exact_totals(self):
        result = monthly_sales("sales.csv")
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {
            "2026-01": 19800,
            "2026-02": 7700,
            "2026-04": 26400,
        })

    def test_cancelled_and_negative_rows(self):
        result = monthly_sales("sales.csv")
        self.assertNotIn("2026-03", result)
        self.assertEqual(result["2026-01"], 19800)
        self.assertEqual(result["2026-02"], 7700)

    def test_result_types_and_key_format(self):
        result = monthly_sales("sales.csv")
        for month, amount in result.items():
            self.assertIsInstance(month, str)
            self.assertRegex(month, r"^\d{4}-\d{2}$")
            self.assertIsInstance(amount, int)

    def test_timezone_is_normalized_to_utc_month(self):
        import csv

        test_path = "test_edge_sales.csv"
        try:
            with open(test_path, "w", encoding="utf-8", newline="") as csv_file:
                writer = csv.DictWriter(
                    csv_file,
                    fieldnames=["order_id", "ordered_at", "amount_incl_tax", "status"],
                )
                writer.writeheader()
                writer.writerow({
                    "order_id": "T-1",
                    "ordered_at": "2026-02-01T00:30:00+09:00",
                    "amount_incl_tax": "100",
                    "status": "completed",
                })
            self.assertEqual(monthly_sales(test_path), {"2026-01": 100})
        finally:
            import os
            if os.path.exists(test_path):
                os.remove(test_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)

