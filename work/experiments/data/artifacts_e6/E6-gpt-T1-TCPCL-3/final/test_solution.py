import unittest
from pathlib import Path
from uuid import uuid4

from solution import monthly_sales


_ROOT = Path(__file__).resolve().parent
_HEADER = "ordered_at,amount_incl_tax,status\n"


class MonthlySalesTests(unittest.TestCase):
    def run_csv(self, rows, header=_HEADER, encoding="utf-8"):
        path = _ROOT / f".monthly-sales-test-{uuid4().hex}.csv"
        with path.open("xb") as fixture:
            self.addCleanup(path.unlink)
            fixture.write((header + rows).encode(encoding))
        return monthly_sales(path)

    def test_d1_sample_totals_order_and_types(self):
        result = monthly_sales(_ROOT / "sales.csv")
        expected = {
            "2026-01": 15000,
            "2026-02": 10000,
            "2026-03": 0,
            "2026-04": 17000,
            "2026-05": 7000,
        }
        self.assertIs(type(result), dict)
        self.assertEqual(list(result.items()), list(expected.items()))
        self.assertTrue(all(type(value) is int for value in result.values()))

    def test_d2_jst_month_boundary_and_equivalent_offset(self):
        for boundary in ("2026-01-31T15:00:00Z", "2026-02-01T00:00:00+09:00"):
            with self.subTest(boundary=boundary):
                result = self.run_csv(
                    "2026-01-31T14:59:59Z,110,completed\n"
                    f"{boundary},220,completed\n"
                )
                self.assertEqual(result, {"2026-01": 100, "2026-02": 200})

    def test_d3_filter_negatives_and_keep_zero_months(self):
        result = self.run_csv(
            "2026-02-02T00:00:00Z,110,completed\n"
            "2025-12-01T00:00:00Z,1100,cancelled\n"
            "2026-01-02T00:00:00Z,0,completed\n"
            "2026-02-02T00:00:00Z,-22,completed\n"
            "2026-02-02T00:00:00Z,1100,pending\n"
            "2026-03-02T00:00:00Z,11,completed\n"
            "2026-03-02T00:00:00Z,-11,completed\n"
            "2026-04-02T00:00:00Z,1100,Completed\n"
        )
        self.assertEqual(list(result.items()), [("2026-01", 0), ("2026-02", 80), ("2026-03", 0)])

    def test_d4_empty_selection_and_header_only(self):
        self.assertEqual(self.run_csv("", encoding="utf-8-sig"), {})
        self.assertEqual(self.run_csv("2026-02-01T00:00:00Z,110,cancelled\n"), {})

    def test_d5_missing_columns_and_invalid_values(self):
        cases = {
            "missing header column": ("ordered_at,status\n", ""),
            "duplicate header column": (_HEADER.strip() + ",status\n", ""),
            "short row": (_HEADER, "2026-02-01T00:00:00Z,100\n"),
            "blank amount on cancelled row": (_HEADER, "2026-02-01T00:00:00Z, ,cancelled\n"),
            "blank date": (_HEADER, ",100,completed\n"),
            "blank status": (_HEADER, "2026-02-01T00:00:00Z,100, \n"),
            "decimal amount": (_HEADER, "2026-02-01T00:00:00Z,10.5,completed\n"),
            "naive date": (_HEADER, "2026-02-01T00:00:00,100,completed\n"),
            "nonexistent date": (_HEADER, "2026-02-29T00:00:00Z,100,completed\n"),
            "invalid offset": (_HEADER, "2026-02-01T00:00:00+00:60,100,completed\n"),
            "JST overflow": (_HEADER, "9999-12-31T23:59:59Z,100,completed\n"),
            "JST underflow": (_HEADER, "0001-01-01T00:00:00+10:00,100,completed\n"),
        }
        for name, (header, row) in cases.items():
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.run_csv(row, header)

    def test_d6_round_once_per_month_with_exact_arithmetic(self):
        result = self.run_csv(
            "2026-01-02T00:00:00Z,6,completed\n"
            "2026-01-03T00:00:00Z,6,completed\n"
            "2026-02-02T00:00:00Z,100,completed\n"
            "2026-03-02T00:00:00Z,-100,completed\n"
            "2026-04-02T00:00:00Z,-6,completed\n"
            "2026-04-03T00:00:00Z,-6,completed\n"
            "2026-05-02T00:00:00Z,110000000000000000011,completed\n"
        )
        self.assertEqual(result, {
            "2026-01": 11,
            "2026-02": 91,
            "2026-03": -91,
            "2026-04": -11,
            "2026-05": 100000000000000000010,
        })

    def test_d7_fill_across_year_end_and_format_limiting_years(self):
        result = self.run_csv(
            "2027-01-02T00:00:00Z,220,completed\n"
            "\n"
            "2026-11-02T00:00:00Z,110,completed\n",
            encoding="utf-8-sig",
        )
        self.assertEqual(list(result.items()), [("2026-11", 100), ("2026-12", 0), ("2027-01", 200)])
        for stamp, month in (
            ("0001-01-01T00:00:00.1+09:00", "0001-01"),
            ("9999-12-31T23:59:59.999999+09:00", "9999-12"),
        ):
            with self.subTest(month=month):
                self.assertEqual(self.run_csv(f"{stamp},110,completed\n"), {month: 100})
