import unittest
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from solution import monthly_sales


BASE = Path(__file__).resolve().parent
HEADER = "order_id,ordered_at,amount_incl_tax,status\n"


@contextmanager
def sales_file(contents, encoding="utf-8"):
    path = BASE / f"test_sales_{uuid4().hex}.csv"
    stream = path.open("x", encoding=encoding, newline="")
    try:
        with stream:
            stream.write(contents)
        yield path
    finally:
        path.unlink()


class MonthlySalesTests(unittest.TestCase):
    def test_dod1_sample_values_types_and_order(self):
        result = monthly_sales(BASE / "sales.csv")
        self.assertIs(type(result), dict)
        self.assertEqual(list(result.items()), [
            ("2026-01", 15000), ("2026-02", 10000), ("2026-03", 0),
            ("2026-04", 17000), ("2026-05", 7000),
        ])
        self.assertTrue(all(type(value) is int for value in result.values()))

    def test_dod1_fills_year_boundary_on_another_path(self):
        with sales_file(HEADER + (
            "1,2025-10-10T00:00:00Z,110,cancelled\n"
            "2,2026-02-10T00:00:00Z,220,completed\n"
            "3,2025-11-10T00:00:00Z,110,completed\n"
            "4,2026-03-10T00:00:00Z,110,pending\n"
        ), encoding="utf-8-sig") as path:
            self.assertEqual(list(monthly_sales(str(path)).items()), [
                ("2025-11", 100), ("2025-12", 0), ("2026-01", 0), ("2026-02", 200),
            ])

    def test_dod2_jst_month_boundary(self):
        with sales_file(HEADER + (
            "1,2026-01-31T14:59:59Z,110,completed\n"
            "2,2026-01-31T15:00:00Z,220,completed\n"
            "3,2026-01-31T10:00:00-05:00,330,completed\n"
            "4,2026-02-01T00:00:00.1+09:00,440,completed\n"
        )) as path:
            self.assertEqual(monthly_sales(path), {"2026-01": 100, "2026-02": 900})

    def test_dod2_calendar_limits_are_checked_in_jst(self):
        valid = {
            "0001-01-01T00:00:00+08:00": "0001-01",
            "9999-12-31T23:59:59+09:00": "9999-12",
        }
        for timestamp, month in valid.items():
            with self.subTest(timestamp=timestamp):
                with sales_file(HEADER + f"1,{timestamp},110,completed\n") as path:
                    self.assertEqual(monthly_sales(path), {month: 100})

        for timestamp in ("0001-01-01T00:00:00+10:00", "9999-12-31T15:00:00Z"):
            with self.subTest(timestamp=timestamp):
                with sales_file(HEADER + f"1,{timestamp},110,completed\n") as path:
                    with self.assertRaises(ValueError):
                        monthly_sales(path)

    def test_dod3_rounds_signed_monthly_totals_and_keeps_zero_months(self):
        with sales_file(HEADER + (
            "1,2026-01-10T00:00:00Z,100,completed\n"
            "2,2026-01-11T00:00:00Z,-100,completed\n"
            "3,2026-01-12T00:00:00Z,0,completed\n"
            "4,2026-01-13T00:00:00Z,999,cancelled\n"
            "5,2026-02-10T00:00:00Z,5,completed\n"
            "6,2026-02-11T00:00:00Z,5,completed\n"
            "7,2026-03-10T00:00:00Z,-6,completed\n"
            "8,2026-04-10T00:00:00Z,-1,completed\n"
            "9,2026-05-10T00:00:00Z,9223372036854775808,completed\n"
            "10,2026-06-10T00:00:00Z,0,completed\n"
        )) as path:
            self.assertEqual(monthly_sales(path), {
                "2026-01": 0, "2026-02": 9, "2026-03": -5, "2026-04": -1,
                "2026-05": 8384883669867978007, "2026-06": 0,
            })

    def test_dod4_returns_empty_if_no_eligible_rows(self):
        cases = {
            "header only": "\n" + HEADER + "\n",
            "ignored fields": HEADER + "1,no-date,no-amount,cancelled\n2,,,Completed\n",
        }
        for description, contents in cases.items():
            with self.subTest(description=description), sales_file(contents) as path:
                self.assertEqual(monthly_sales(path), {})

    def test_dod4_rejects_missing_or_invalid_fields(self):
        cases = {
            "empty file": "",
            "missing header column": "ordered_at,status\n",
            "empty status": HEADER + "1,2026-01-10T00:00:00Z,110, \n",
            "missing status": HEADER + "1,2026-01-10T00:00:00Z,110\n",
            "empty timestamp": HEADER + "1,,110,completed\n",
            "empty amount": HEADER + "1,2026-01-10T00:00:00Z,,completed\n",
            "nonexistent date": HEADER + "1,2026-02-29T00:00:00Z,110,completed\n",
            "missing offset": HEADER + "1,2026-01-10T00:00:00,110,completed\n",
            "invalid offset": HEADER + "1,2026-01-10T00:00:00+05:60,110,completed\n",
            "decimal amount": HEADER + "1,2026-01-10T00:00:00Z,1.0,completed\n",
        }
        for description, contents in cases.items():
            with self.subTest(description=description), sales_file(contents) as path:
                with self.assertRaises(ValueError):
                    monthly_sales(path)

    def test_dod4_sorts_unordered_input_and_trims_values(self):
        with sales_file(HEADER + (
            "1, 2026-02-10T00:00:00Z , +220 , completed \n"
            "\n"
            "2,2026-01-10T00:00:00Z,110,completed\n"
        )) as path:
            self.assertEqual(list(monthly_sales(path).items()), [
                ("2026-01", 100), ("2026-02", 200),
            ])


if __name__ == "__main__":
    unittest.main()
