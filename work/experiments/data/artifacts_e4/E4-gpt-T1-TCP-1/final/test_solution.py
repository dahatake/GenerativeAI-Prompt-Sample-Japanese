import unittest
from pathlib import Path
from uuid import uuid4

from solution import monthly_sales


_ROOT = Path(__file__).parent
_HEADER = "order_id,ordered_at,amount_incl_tax,status\n"


class MonthlySalesTests(unittest.TestCase):
    def csv_file(self, contents):
        path = _ROOT / f".sales-test-{uuid4().hex}.csv"
        with path.open("x", encoding="utf-8", newline="") as stream:
            self.addCleanup(path.unlink)
            stream.write(contents)
        return path

    def test_api_reads_given_path_with_bom_and_named_columns(self):
        path = self.csv_file(
            "\ufeffmemo,amount_incl_tax,status,ordered_at\n"
            "備考,9007199254740993,completed,0001-01-01T00:00:00Z\n"
        )
        result = monthly_sales(path)
        self.assertIs(type(result), dict)
        self.assertEqual(result, {"0001-01": 9007199254740993})
        self.assertIs(type(result["0001-01"]), int)

    def test_sales_csv_matches_approved_totals(self):
        self.assertEqual(
            monthly_sales(str(_ROOT / "sales.csv")),
            {"2026-01": 16500, "2026-02": 11000, "2026-03": 0,
             "2026-04": 18700, "2026-05": 7700},
        )

    def test_jst_boundary_negative_and_cancelled_rows(self):
        path = self.csv_file(
            _HEADER
            + "1,2026-01-31T14:59:59Z,2,completed\n"
            + "2,2026-01-31T15:00:00Z,7,completed\n"
            + "3,2026-02-14T11:11:00Z,-3,completed\n"
            + "4,2026-01-20T23:30:00Z,999,cancelled\n"
            + "5,2026-02-27T13:45:00Z,999,cancelled\n"
            + "6,2026-04-30T15:30:00Z,9,completed\n"
        )
        self.assertEqual(
            monthly_sales(path),
            {"2026-01": 2, "2026-02": 4, "2026-03": 0, "2026-04": 0, "2026-05": 9},
        )

    def test_fills_year_gap_but_not_cancelled_endpoint_months(self):
        path = self.csv_file(
            _HEADER
            + "1,2026-02-01T00:00:00Z,15,completed\n"
            + "2,2025-11-01T00:00:00Z,30,cancelled\n"
            + "3,2026-03-01T00:00:00Z,35,cancelled\n"
            + "4,2025-12-01T00:00:00Z,10,completed\n"
        )
        self.assertEqual(monthly_sales(path), {"2025-12": 10, "2026-01": 0, "2026-02": 15})

    def test_same_order_id_can_net_to_zero_in_present_month(self):
        path = self.csv_file(
            _HEADER
            + "1,2026-01-05T00:00:00Z,100,completed\n"
            + "1,2026-01-09T00:00:00Z,-100,completed\n"
        )
        self.assertEqual(monthly_sales(path), {"2026-01": 0})

    def test_header_only_and_all_cancelled_have_no_months(self):
        for data in ("", "1,2026-01-01T00:00:00Z,42,cancelled\n"):
            with self.subTest(data=data):
                self.assertEqual(monthly_sales(self.csv_file(_HEADER + data)), {})

    def test_rejects_missing_or_duplicate_required_header(self):
        for header in (
            "ordered_at,amount_incl_tax\n",
            "ordered_at,amount_incl_tax,status,status\n",
        ):
            with self.subTest(header=header):
                with self.assertRaises(ValueError):
                    monthly_sales(self.csv_file(header))

    def test_rejects_invalid_required_values_including_cancelled_rows(self):
        for row in (
            "1,2026-02-30T00:00:00Z,100,completed",
            "1,2026-01-01T00:00:00+00:00,100,completed",
            "1,9999-12-31T15:00:00Z,100,completed",
            "1,2026-01-01T00:00:00Z,100.5,completed",
            "1,2026-01-01T00:00:00Z,oops,cancelled",
            "1,2026-01-01T00:00:00Z,100,COMPLETED",
            "1,2026-01-01T00:00:00Z,100",
        ):
            with self.subTest(row=row):
                with self.assertRaises(ValueError):
                    monthly_sales(self.csv_file(_HEADER + row + "\n"))

    def test_rejects_invalid_csv_syntax(self):
        path = self.csv_file(_HEADER + '"1,2026-01-01T00:00:00Z,100,completed\n')
        with self.assertRaises(ValueError):
            monthly_sales(path)

    def test_preserves_io_error_for_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            monthly_sales(_ROOT / f".missing-sales-{uuid4().hex}.csv")
