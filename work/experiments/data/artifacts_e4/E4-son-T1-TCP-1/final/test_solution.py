import os
import tempfile
import unittest

from solution import monthly_sales

HEADER = "order_id,ordered_at,amount_incl_tax,status\n"


def run(body):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", dir=".") as f:
        f.write(HEADER + body)
        name = f.name
    try:
        return monthly_sales(name)
    finally:
        os.remove(name)


class MonthlySalesTest(unittest.TestCase):
    def test_sample_file(self):
        self.assertEqual(
            monthly_sales("sales.csv"),
            {"2026-01": 15000, "2026-02": 10000, "2026-03": 0, "2026-04": 17000, "2026-05": 7000},
        )

    def test_keys_ascending_and_int_values(self):
        r = monthly_sales("sales.csv")
        self.assertEqual(list(r), sorted(r))
        self.assertTrue(all(type(v) is int for v in r.values()))

    def test_jst_month_boundary(self):
        r = run("X1,2026-01-31T15:00:00Z,1100,completed\nX2,2026-01-31T14:59:59Z,2200,completed\n")
        self.assertEqual(r, {"2026-01": 2000, "2026-02": 1000})

    def test_cancelled_excluded(self):
        self.assertEqual(run("X1,2026-01-05T00:00:00Z,1100,cancelled\n"), {})

    def test_negative_subtracts(self):
        r = run("X1,2026-01-05T00:00:00Z,2200,completed\nX2,2026-01-06T00:00:00Z,-1100,completed\n")
        self.assertEqual(r, {"2026-01": 1000})

    def test_zero_fill_across_year(self):
        r = run("X1,2025-11-05T00:00:00Z,1100,completed\nX2,2026-02-05T00:00:00Z,1100,completed\n")
        self.assertEqual(r, {"2025-11": 1000, "2025-12": 0, "2026-01": 0, "2026-02": 1000})

    def test_empty_and_header_only(self):
        self.assertEqual(run(""), {})


if __name__ == "__main__":
    unittest.main()
