import os
import tempfile
import unittest

from solution import _excl_tax, monthly_sales


def run_csv(text):
    fd, p = tempfile.mkstemp(suffix=".csv", dir=os.path.dirname(os.path.abspath(__file__)))
    os.close(fd)
    try:
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write("order_id,ordered_at,amount_incl_tax,status\n" + text)
        return monthly_sales(p)
    finally:
        os.remove(p)


class T(unittest.TestCase):
    def test_sales_csv_exact(self):
        r = monthly_sales("sales.csv")
        self.assertEqual(r, {"2026-01": 15000, "2026-02": 10000, "2026-03": 0,
                             "2026-04": 17000, "2026-05": 7000})

    def test_types_and_keys_order(self):
        r = monthly_sales("sales.csv")
        self.assertIsInstance(r, dict)
        self.assertTrue(all(type(v) is int for v in r.values()))
        self.assertEqual(list(r), sorted(r))
        self.assertTrue(all(len(k) == 7 and k[4] == "-" for k in r))

    def test_jst_boundaries(self):
        r = run_csv("a,2026-01-31T15:00:00Z,1100,completed\n"   # JST 2/1 00:00
                    "b,2026-01-31T14:59:59Z,2200,completed\n")  # JST 1/31 23:59:59
        self.assertEqual(r, {"2026-01": 2000, "2026-02": 1000})

    def test_cancelled_excluded(self):
        r = run_csv("a,2026-01-05T00:00:00Z,1100,completed\nb,2026-01-06T00:00:00Z,9900,cancelled\n")
        self.assertEqual(r, {"2026-01": 1000})

    def test_negative_summed(self):
        r = run_csv("a,2026-01-05T00:00:00Z,2200,completed\nb,2026-01-06T00:00:00Z,-1100,completed\n")
        self.assertEqual(r, {"2026-01": 1000})

    def test_gap_months_zero_filled_across_year(self):
        r = run_csv("a,2025-11-10T00:00:00Z,1100,completed\nb,2026-02-10T00:00:00Z,1100,completed\n")
        self.assertEqual(r, {"2025-11": 1000, "2025-12": 0, "2026-01": 0, "2026-02": 1000})

    def test_rounding_per_row_half_up(self):
        self.assertEqual(_excl_tax(110), 100)
        self.assertEqual(_excl_tax(1), 1)      # 0.909 -> 1
        self.assertEqual(_excl_tax(6), 5)      # 5.4545 -> 5
        self.assertEqual(_excl_tax(-1100), -1000)
        # 各行ごとに丸めてから合算（合計後に丸めると 11 になる）
        r = run_csv("a,2026-01-05T00:00:00Z,6,completed\nb,2026-01-06T00:00:00Z,6,completed\n")
        self.assertEqual(r, {"2026-01": 10})
        r = run_csv("a,2026-01-05T00:00:00Z,4,completed\nb,2026-01-06T00:00:00Z,4,completed\n")
        self.assertEqual(r, {"2026-01": 8})  # 3.636->4 each; total-then-round would give 7

    def test_empty(self):
        self.assertEqual(run_csv(""), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
