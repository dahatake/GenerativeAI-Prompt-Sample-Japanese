import unittest
from pathlib import Path
from uuid import uuid4

from solution import monthly_sales

_HEADER = "ordered_at,amount_incl_tax,status\n"


class MonthlySalesTest(unittest.TestCase):
    def csv_file(self, contents, *, encoding="utf-8"):
        path = Path(f"verify-sales-{uuid4().hex}.csv")
        with path.open("x", encoding=encoding, newline="") as source:
            self.addCleanup(path.unlink)
            source.write(contents)
        return path

    def test_sample_totals_and_types(self):
        result = monthly_sales("sales.csv")
        self.assertIs(type(result), dict)
        self.assertEqual(result, {
            "2026-01": 16500, "2026-02": 11000, "2026-04": 18700, "2026-05": 7700,
        })
        for month, amount in result.items():
            self.assertRegex(month, r"^[0-9]{4}-(0[1-9]|1[0-2])$")
            self.assertIs(type(amount), int)
        print(f"sales.csv: {result}", flush=True)

    def test_jst_month_and_year_boundaries(self):
        path = self.csv_file(_HEADER
            + "2026-12-31T14:59:59Z,5,completed\n"
            + "2026-12-31T15:00:00Z,7,completed\n"
            + "2027-01-31T15:00:00Z,11,completed\n")
        self.assertEqual(monthly_sales(path), {"2026-12": 5, "2027-01": 7, "2027-02": 11})

    def test_only_completed_rows_and_signed_amounts(self):
        path = self.csv_file(_HEADER
            + "2026-02-14T11:11:00Z,+900,completed\n"
            + "2026-02-14T11:11:00Z,-1100,completed\n"
            + "2026-02-14T11:11:00Z,3000,cancelled\n"
            + "2026-02-14T11:11:00Z,4000,pending\n")
        self.assertEqual(monthly_sales(path), {"2026-02": -200})

    def test_gaps_omitted_but_zero_total_retained(self):
        path = self.csv_file(_HEADER
            + "2026-01-10T00:00:00Z,400,completed\n"
            + "2026-01-11T00:00:00Z,-400,completed\n"
            + "2026-02-10T00:00:00Z,500,cancelled\n"
            + "2026-04-10T00:00:00Z,600,completed\n")
        self.assertEqual(monthly_sales(path), {"2026-01": 0, "2026-04": 600})

    def test_header_only(self):
        self.assertEqual(monthly_sales(self.csv_file(_HEADER)), {})

    def test_missing_required_column(self):
        fields = _HEADER.strip().split(",")
        for missing in fields:
            with self.subTest(missing=missing):
                path = self.csv_file(",".join(field for field in fields if field != missing) + "\n")
                with self.assertRaisesRegex(ValueError, missing):
                    monthly_sales(path)

    def test_invalid_or_empty_date_and_amount(self):
        valid_date = "2026-02-01T00:00:00Z"
        for ordered_at, amount, invalid_field in [
            ("2026-02-30T00:00:00Z", "10", "ordered_at"),
            ("", "10", "ordered_at"),
            (valid_date, "10.5", "amount_incl_tax"),
            (valid_date, "", "amount_incl_tax"),
        ]:
            with self.subTest(ordered_at=ordered_at, amount=amount):
                path = self.csv_file(_HEADER + f"{ordered_at},{amount},completed\n")
                with self.assertRaisesRegex(ValueError, invalid_field):
                    monthly_sales(path)

    def test_utf8_bom(self):
        path = self.csv_file(_HEADER + "2026-02-01T00:00:00Z,10,completed\n", encoding="utf-8-sig")
        self.assertEqual(monthly_sales(path), {"2026-02": 10})

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            monthly_sales(Path(f"missing-sales-{uuid4().hex}.csv"))
