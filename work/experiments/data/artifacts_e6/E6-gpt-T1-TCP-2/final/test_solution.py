import unittest
from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

from solution import monthly_sales


HEADER = "order_id,ordered_at,amount_incl_tax,status\n"


class MonthlySalesTests(unittest.TestCase):
    def from_csv(self, text):
        def open_csv(path, *, encoding, newline):
            return TextIOWrapper(BytesIO(text.encode("utf-8")), encoding=encoding, newline=newline)

        with patch("solution.open", side_effect=open_csv, create=True):
            return monthly_sales("virtual.csv")

    def test_sales_csv(self):
        source = Path("sales.csv")
        before = source.read_bytes()
        totals = monthly_sales("sales.csv")
        self.assertEqual(totals, {
            "2026-01": 16500, "2026-02": 11000, "2026-03": 0,
            "2026-04": 18700, "2026-05": 7700,
        })
        self.assertTrue(all(type(value) is int for value in totals.values()))
        self.assertEqual(source.read_bytes(), before)

    def test_year_boundary_gap_and_cancelled_bounds(self):
        self.assertEqual(self.from_csv(HEADER +
            "5,2027-04-30T15:00:00Z,100,cancelled\n"
            "4,2027-01-31T15:00:00Z,30,completed\n"
            "3,2026-12-31T15:00:00Z,11,completed\n"
            "2,2026-10-31T15:00:00Z,-7,completed\n"
            "1,2026-10-31T15:00:00Z,7,completed\n"
            "0,2026-10-31T14:59:59Z,100,cancelled\n"
        ), {"2026-11": 0, "2026-12": 0, "2027-01": 11, "2027-02": 30})

    def test_no_completed_orders(self):
        for orders in ("", "1,2026-01-01T00:00:00Z,7,cancelled\n"):
            with self.subTest(orders=orders):
                self.assertEqual(self.from_csv(HEADER + orders), {})

    def test_bom_reordered_columns_blank_lines_and_duplicate_orders(self):
        self.assertEqual(self.from_csv(
            "\ufeff\nstatus,amount_incl_tax,ordered_at,order_id\n"
            "completed,+7,2026-01-01T00:00:00Z,same-id\n\n"
            "completed,-2,2026-01-01T00:00:00Z,same-id\n"
        ), {"2026-01": 5})

    def test_invalid_csv(self):
        valid_date = "2026-01-01T00:00:00Z"
        cases = {
            "missing header": "",
            "missing column": "ordered_at,amount_incl_tax\n",
            "duplicate column": "ordered_at,amount_incl_tax,status,status\n",
            "too few fields": HEADER + f"1,{valid_date},7\n",
            "too many fields": HEADER + f"1,{valid_date},7,completed,extra\n",
            "bad quoting": HEADER + f'1,"{valid_date},7,completed\n',
            "invalid calendar date": HEADER + "1,2026-02-29T00:00:00Z,7,completed\n",
            "invalid format": HEADER + "1,2026-1-01T00:00:00Z,7,completed\n",
            "decimal amount": HEADER + f"1,{valid_date},7.5,completed\n",
            "invalid cancelled amount": HEADER + f"1,{valid_date},,cancelled\n",
            "unknown status": HEADER + f"1,{valid_date},7,pending\n",
        }
        for case, text in cases.items():
            with self.subTest(case=case):
                with self.assertRaises(ValueError):
                    self.from_csv(text)

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            monthly_sales("missing-sales-test-input.csv")
