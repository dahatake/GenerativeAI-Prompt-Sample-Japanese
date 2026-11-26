from pathlib import Path
import unittest
from uuid import uuid4

from solution import monthly_sales

_ROOT = Path(__file__).parent
_HEADER = "ordered_at,amount_incl_tax,status"


class MonthlySalesTests(unittest.TestCase):
    def csv_file(self, *rows: str, header: str = _HEADER) -> Path:
        path = _ROOT / f"monthly_sales_test_{uuid4().hex}.csv"
        with path.open("x", encoding="utf-8-sig", newline="") as fixture:
            self.addCleanup(path.unlink, missing_ok=True)
            fixture.write("\r\n".join((header, *rows)) + "\r\n")
        return path

    def test_dod1_sample_totals_order_and_integer_types(self):
        result = monthly_sales(_ROOT / "sales.csv")
        self.assertEqual(list(result.items()), [
            ("2026-01", 15000), ("2026-02", 10000), ("2026-03", 0),
            ("2026-04", 17000), ("2026-05", 7000),
        ])
        for value in result.values():
            self.assertIs(type(value), int)

    def test_dod2_jst_month_and_year_boundaries_in_unsorted_input(self):
        path = self.csv_file(
            "2026-01-31T15:00:00Z,44,completed",
            "2025-12-31T15:00:00Z,33,completed",
            "2026-01-31T14:59:59Z,22,completed",
            "2025-12-31T14:59:59Z,11,completed",
        )
        self.assertEqual(list(monthly_sales(str(path)).items()), [
            ("2025-12", 10), ("2026-01", 50), ("2026-02", 40),
        ])

    def test_dod3_rounds_monthly_toward_zero_and_keeps_integer_precision(self):
        path = self.csv_file(
            "2026-01-05T00:00:00Z,100,completed",
            "2026-01-06T00:00:00Z,100,completed",
            "2026-02-05T00:00:00Z,-100,completed",
            "2026-02-06T00:00:00Z,-100,completed",
            "2026-03-05T00:00:00Z,110000000000000011,completed",
        )
        self.assertEqual(monthly_sales(path), {
            "2026-01": 181, "2026-02": -181, "2026-03": 100000000000000010,
        })

    def test_dod3_completed_only_span_preserves_zero_rows_and_months(self):
        path = self.csv_file(
            "2025-11-05T00:00:00Z,110,cancelled",
            "2025-12-05T00:00:00Z,0,completed",
            "2026-01-05T00:00:00Z,110,Completed",
            "2026-02-05T00:00:00Z,+110,completed",
            "2026-02-06T00:00:00Z,-110,completed",
            "2026-03-05T00:00:00Z,110,cancelled",
        )
        self.assertEqual(list(monthly_sales(path).items()), [
            ("2025-12", 0), ("2026-01", 0), ("2026-02", 0),
        ])

    def test_dod3_header_only_or_no_completed_rows_returns_empty_dict(self):
        for rows in ((), ("2026-01-01T00:00:00Z,110,cancelled", ",,pending")):
            with self.subTest(rows=rows):
                self.assertEqual(monthly_sales(self.csv_file(*rows)), {})

    def test_dod4_missing_required_columns_raise_value_error(self):
        for missing in _HEADER.split(","):
            with self.subTest(missing=missing):
                header = ",".join(column for column in _HEADER.split(",") if column != missing)
                with self.assertRaises(ValueError):
                    monthly_sales(self.csv_file(header=header))

    def test_dod4_invalid_rows_do_not_return_partial_results(self):
        valid = "2026-01-01T00:00:00Z,110,completed"
        for bad in (
            "2026-02-01T00:00:00Z,110",
            "2026-02-01T00:00:00Z,110,   ",
            ",110,completed",
            "2026-02-30T00:00:00Z,110,completed",
            "2026-02-01T00:00:00+00:00,110,completed",
            "9999-12-31T15:00:00Z,110,completed",
            "2026-02-01T00:00:00Z,,completed",
            "2026-02-01T00:00:00Z,1.5,completed",
        ):
            with self.subTest(row=bad), self.assertRaises(ValueError):
                monthly_sales(self.csv_file(valid, bad))
