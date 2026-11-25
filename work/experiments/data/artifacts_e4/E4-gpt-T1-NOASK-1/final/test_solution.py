import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from solution import monthly_sales


_HEADER = "ordered_at,amount_incl_tax,status\n"


def _sales_from_text(text):
    with patch("builtins.open", mock_open(read_data=text)):
        return monthly_sales("unused.csv")


class MonthlySalesTests(unittest.TestCase):
    def test_sample_totals_types_and_unchanged_input(self):
        path = Path(__file__).with_name("sales.csv")
        original = path.read_bytes()
        totals = monthly_sales(path)
        self.assertIsInstance(totals, dict)
        self.assertEqual(totals, {
            "2026-01": 16500,
            "2026-02": 11000,
            "2026-04": 18700,
            "2026-05": 7700,
        })
        self.assertTrue(all(type(amount) is int for amount in totals.values()))
        self.assertEqual(path.read_bytes(), original)

    def test_jst_month_boundaries(self):
        self.assertEqual(_sales_from_text(_HEADER +
            "2026-01-31T16:20:00Z,3300,completed\n"
            "2026-04-30T14:59:59Z,100,completed\n"
            "2026-04-30T15:00:00Z,200,completed\n"
            "2026-04-30T15:30:00Z,7700,completed\n"
        ), {"2026-02": 3300, "2026-04": 100, "2026-05": 7900})

    def test_cancellations_excluded_and_negative_amount_subtracted(self):
        self.assertEqual(_sales_from_text(_HEADER +
            "2026-01-20T23:30:00Z,22000,cancelled\n"
            "2026-01-31T16:20:00Z,3300,completed\n"
            "2026-02-03T05:00:00Z,8800,completed\n"
            "2026-02-14T11:11:00Z,-1100,completed\n"
            "2026-02-27T13:45:00Z,4400,cancelled\n"
        ), {"2026-02": 11000})

    def test_no_sales_month_omitted_but_zero_net_preserved(self):
        self.assertEqual(_sales_from_text(_HEADER +
            "2026-02-01T00:00:00Z,500,completed\n"
            "2026-02-02T00:00:00Z,-500,completed\n"
            "2026-03-01T00:00:00Z,25,cancelled\n"
            "2026-04-01T00:00:00Z,10,completed\n"
        ), {"2026-02": 0, "2026-04": 10})

    def test_header_only_and_all_cancelled_are_empty(self):
        for rows in ("", "2026-01-20T23:30:00Z,22000,cancelled\n"):
            with self.subTest(rows=rows):
                self.assertEqual(_sales_from_text(_HEADER + rows), {})

    def test_missing_required_column_raises_value_error(self):
        columns = _HEADER.strip().split(",")
        for missing in columns:
            with self.subTest(missing=missing):
                header = ",".join(column for column in columns if column != missing)
                with self.assertRaises(ValueError):
                    _sales_from_text(header + "\n")

    def test_invalid_or_empty_field_raises_value_error(self):
        for row in (
            ",1,completed",
            "2026-02-29T00:00:00Z,1,completed",
            "2026-2-01T00:00:00Z,1,completed",
            "2026-01-01T00:00:00Z,,completed",
            "2026-01-01T00:00:00Z,1.5,completed",
            "2026-01-01T00:00:00Z,bad,cancelled",
            "2026-01-01T00:00:00Z,1,",
            "2026-01-01T00:00:00Z,1,pending",
        ):
            with self.subTest(row=row), self.assertRaises(ValueError):
                _sales_from_text(_HEADER + row + "\n")
