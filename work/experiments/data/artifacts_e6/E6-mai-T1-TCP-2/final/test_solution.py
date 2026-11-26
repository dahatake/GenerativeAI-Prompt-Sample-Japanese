import csv
import os
import unittest

from solution import monthly_sales


WORKDIR = os.path.dirname(os.path.abspath(__file__))
SALES = os.path.join(WORKDIR, "sales.csv")


class MonthlySalesTests(unittest.TestCase):
    def test_relative_and_absolute_paths(self):
        relative = "sales.csv"
        absolute = SALES
        self.assertEqual(monthly_sales(relative), monthly_sales(absolute))

    def test_sample_aggregation_jst_missing_month(self):
        expected = {
            "2026-01": 16500,
            "2026-02": 11000,
            "2026-03": 0,
            "2026-04": 18700,
            "2026-05": 7700,
        }
        self.assertEqual(monthly_sales(SALES), expected)

    def test_cancelled_and_negative_rows(self):
        result = monthly_sales(SALES)
        self.assertNotIn(22000, result.values())
        self.assertNotIn(4400, result.values())
        self.assertEqual(result["2026-02"], 11000)

    def test_same_month_rows_sum(self):
        result = monthly_sales(SALES)
        self.assertEqual(result["2026-01"], 16500)
        self.assertEqual(result["2026-04"], 18700)
        self.assertEqual(result["2026-05"], 7700)

    def test_empty_file_and_header_only(self):
        paths = []
        for name, content in (("empty.csv", ""), ("header.csv", "ordered_at,amount_incl_tax,status\n")):
            path = os.path.join(WORKDIR, name)
            paths.append(path)
            with open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(content)
        try:
            self.assertEqual(monthly_sales(paths[0]), {})
            self.assertEqual(monthly_sales(paths[1]), {})
        finally:
            for path in paths:
                os.remove(path)

    def test_invalid_headers_raise_value_error(self):
        path = os.path.join(WORKDIR, "bad-header.csv")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write("ordered_at,amount_incl_tax\n2026-01-01T00:00:00Z,100\n")
        try:
            with self.assertRaises(ValueError):
                monthly_sales(path)
        finally:
            os.remove(path)

    def test_invalid_rows_are_skipped(self):
        path = os.path.join(WORKDIR, "invalid-rows.csv")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write("ordered_at,amount_incl_tax,status\n")
            handle.write("bad-date,100,completed\n")
            handle.write("2026-05-01T00:00:00Z,abc,completed\n")
            handle.write("2026-06-01T00:00:00Z,300,unknown\n")
        try:
            self.assertEqual(monthly_sales(path), {})
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)



