import unittest
from pathlib import Path
from uuid import uuid4

from solution import monthly_sales

_HEADER = "order_id,ordered_at,amount_incl_tax,status\n"


class MonthlySalesTests(unittest.TestCase):
    def csv_file(self, contents, *, encoding="utf-8"):
        path = Path(__file__).with_name(f".monthly-sales-{uuid4().hex}.csv")
        with path.open("x", encoding=encoding, newline="") as output:
            self.addCleanup(path.unlink)
            output.write(contents)
        return path

    def test_given_path_bom_reordered_columns_and_types(self):
        path = self.csv_file(
            "status,amount_incl_tax,comment,ordered_at\n"
            'completed,12,"contains, comma",2026-09-05T00:00:00Z\n',
            encoding="utf-8-sig",
        )
        before = path.read_bytes()
        totals = monthly_sales(path)
        self.assertIs(type(totals), dict)
        self.assertEqual(totals, {"2026-09": 12})
        for month, amount in totals.items():
            self.assertIs(type(month), str)
            self.assertIs(type(amount), int)
        self.assertEqual(path.read_bytes(), before)

    def test_bundled_sales(self):
        self.assertEqual(
            monthly_sales("sales.csv"),
            {"2026-01": 16500, "2026-02": 11000, "2026-03": 0,
             "2026-04": 18700, "2026-05": 7700},
        )

    def test_status_exact_match_signed_amounts_and_duplicate_order_ids(self):
        path = self.csv_file(
            _HEADER
            + "A,2026-01-02T00:00:00Z,100,completed\n"
            + "A,2026-01-02T00:00:00Z,+20,pending\n"
            + "A,2026-01-02T00:00:00Z,-7,refunded\n"
            + "B,2026-01-02T00:00:00Z,3,\n"
            + "C,2026-01-02T00:00:00Z,11,Cancelled\n"
            + "D,2026-01-02T00:00:00Z,13,cancelled \n"
            + "E,2026-01-02T00:00:00Z,5000,cancelled\n"
        )
        self.assertEqual(monthly_sales(path), {"2026-01": 140})

    def test_jst_boundary_and_fill_only_eligible_range_across_year(self):
        path = self.csv_file(
            _HEADER
            + "A,2026-02-01T00:00:00Z,-3,completed\n"
            + "B,2025-11-30T14:59:59Z,5,completed\n"
            + "C,2025-11-30T15:00:00Z,10,completed\n"
            + "D,2025-10-01T00:00:00Z,900,cancelled\n"
            + "E,2026-03-01T00:00:00Z,800,cancelled\n"
        )
        self.assertEqual(
            monthly_sales(path),
            {"2025-11": 5, "2025-12": 10, "2026-01": 0, "2026-02": -3},
        )

    def test_no_eligible_rows(self):
        for data in ("", "A,ignored,ignored,cancelled\n"):
            with self.subTest(data=data):
                self.assertEqual(monthly_sales(self.csv_file(_HEADER + data)), {})

    def test_required_column_missing(self):
        required = ("ordered_at", "amount_incl_tax", "status")
        for missing in required:
            with self.subTest(column=missing):
                header = ",".join(column for column in required if column != missing)
                with self.assertRaises(ValueError):
                    monthly_sales(self.csv_file(header + "\n"))

    def test_invalid_eligible_row_raises_instead_of_returning_partial_total(self):
        for row in (
            "B,2026-02-30T00:00:00Z,1,completed",
            "B,2026-2-01T00:00:00Z,1,pending",
            "B,2026-02-01T00:00:00Z,1.5,refunded",
            "B,2026-02-01T00:00:00Z,,",
            "B,2026-02-01T00:00:00Z,1",
        ):
            with self.subTest(row=row):
                path = self.csv_file(
                    _HEADER + "A,2026-02-01T00:00:00Z,100,completed\n" + row + "\n"
                )
                with self.assertRaises(ValueError):
                    monthly_sales(path)

    def test_io_error_is_not_converted(self):
        path = Path(__file__).with_name(f".missing-{uuid4().hex}.csv")
        with self.assertRaises(FileNotFoundError):
            monthly_sales(path)
