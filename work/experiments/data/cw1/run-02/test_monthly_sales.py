"""monthly_sales の検証(標準ライブラリ unittest。pytest からも実行可能)。"""
import csv
import tempfile
import unittest
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from pathlib import Path
from zoneinfo import ZoneInfo

from monthly_sales import monthly_sales, to_tax_excluded

DATA = Path(__file__).with_name("sales.csv")
HEADER = "order_id,ordered_at,amount_incl_tax,status\n"
EXPECTED = {"2026-01": 15000, "2026-02": 10000, "2026-03": 0,
            "2026-04": 17000, "2026-05": 7000}


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, body, name="s.csv", header=HEADER, encoding="utf-8"):
        p = self.tmp / name
        p.write_text(header + body, encoding=encoding)
        return str(p)


class DoD1_ExactResult(Base):
    def test_exact_result(self):
        self.assertEqual(monthly_sales(str(DATA)), EXPECTED)

    def test_independent_reference_decimal_and_tzdata(self):
        ref = {}
        with open(DATA, encoding="utf-8") as f:
            for r in csv.DictReader(line for line in f if line.strip()):
                if r["status"] != "completed":
                    continue
                dt = datetime.fromisoformat(r["ordered_at"].replace("Z", "+00:00"))
                m = dt.astimezone(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m")
                ex = (Decimal(r["amount_incl_tax"]) / Decimal("1.1")).quantize(0, ROUND_DOWN)
                ref[m] = ref.get(m, 0) + int(ex)
        ref.setdefault("2026-03", 0)
        self.assertEqual(monthly_sales(str(DATA)), dict(sorted(ref.items())))


class DoD2_Types(Base):
    def test_all_int(self):
        res = monthly_sales(str(DATA))
        self.assertTrue(all(type(v) is int for v in res.values()))
        self.assertTrue(all(len(k) == 7 and k[4] == "-" for k in res))


class DoD3_MonthBoundary(Base):
    def test_boundary(self):
        cases = [
            ("A-1004,2026-01-31T16:20:00Z,3300,completed\n", "2026-02"),
            ("A-1010,2026-04-30T15:30:00Z,7700,completed\n", "2026-05"),
            ("X,2026-01-31T14:59:59Z,1100,completed\n", "2026-01"),  # JST 23:59:59
            ("X,2026-01-31T15:00:00Z,1100,completed\n", "2026-02"),  # JST 00:00:00
        ]
        for row, month in cases:
            with self.subTest(row=row):
                self.assertEqual(list(monthly_sales(self.write(row))), [month])


class DoD4_Cancelled(Base):
    def test_cancelled_excluded(self):
        p = self.write("A,2026-01-05T00:00:00Z,11000,completed\n"
                       "B,2026-01-06T00:00:00Z,22000,cancelled\n")
        self.assertEqual(monthly_sales(p), {"2026-01": 10000})


class DoD5_BlankLines(Base):
    def test_same_result(self):
        lines = [l for l in DATA.read_text(encoding="utf-8").splitlines() if l.strip()]
        p = self.write("\n".join(lines[1:]) + "\n", "compact.csv")
        self.assertEqual(monthly_sales(p), monthly_sales(str(DATA)))
        self.assertEqual(monthly_sales(p), EXPECTED)


class DoD6_Malformed(Base):
    def test_bad_rows(self):
        bodies = [
            "A,not-a-date,1100,completed\n",
            "A,2026-01-05T00:00:00,1100,completed\n",       # タイムゾーンなし
            "A,2026-01-05T00:00:00Z,11.5,completed\n",      # 小数
            "A,2026-01-05T00:00:00Z,abc,completed\n",
            "A,2026-01-05T00:00:00Z,,completed\n",          # 金額空
            "A,2026-01-05T00:00:00Z,1100,\n",               # status 空
            "A,2026-01-05T00:00:00Z,1100\n",                # 列不足
            "A,2026-01-05T00:00:00Z,1100,completed,x\n",    # 列過多
            "A,bad,1100,cancelled\n",                       # cancelled 行も検証
        ]
        for body in bodies:
            with self.subTest(body=body):
                with self.assertRaises(ValueError) as cm:
                    monthly_sales(self.write(body))
                self.assertIn("line", str(cm.exception))

    def test_missing_column(self):
        p = self.write("A,2026-01-05T00:00:00Z,completed\n",
                       header="order_id,ordered_at,status\n")
        with self.assertRaises(ValueError):
            monthly_sales(p)


class DoD7_FillMonths(Base):
    def test_contiguous_with_zero(self):
        res = monthly_sales(str(DATA))
        self.assertEqual(list(res), ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05"])
        self.assertEqual(res["2026-03"], 0)

    def test_year_crossing(self):
        p = self.write("A,2025-11-10T00:00:00Z,1100,completed\n"
                       "B,2026-02-10T00:00:00Z,2200,completed\n")
        self.assertEqual(monthly_sales(p), {"2025-11": 1000, "2025-12": 0,
                                            "2026-01": 0, "2026-02": 2000})


class DoD8_TaxExcluded(Base):
    def test_conversion(self):
        for incl, ex in [(11000, 10000), (3300, 3000), (1000, 909), (1, 0),
                         (0, 0), (-1100, -1000), (-1000, -909)]:
            with self.subTest(incl=incl):
                self.assertEqual(to_tax_excluded(incl), ex)

    def test_negative_included(self):
        # 2026-02(JST): 3300(A-1004) + 8800 - 1100 → 税抜 3000 + 8000 - 1000
        self.assertEqual(monthly_sales(str(DATA))["2026-02"], 10000)


class Assumptions(Base):
    def test_bom(self):
        p = self.write("A,2026-01-05T00:00:00Z,1100,completed\n", encoding="utf-8-sig")
        self.assertEqual(monthly_sales(p), {"2026-01": 1000})

    def test_empty(self):
        p = self.tmp / "e.csv"
        p.write_text("")
        self.assertEqual(monthly_sales(str(p)), {})
        self.assertEqual(monthly_sales(self.write("", "h.csv")), {})

    def test_unknown_status_skipped_with_warning(self):
        p = self.write("A,2026-01-05T00:00:00Z,1100,completed\n"
                       "B,2026-01-06T00:00:00Z,2200,refunded\n")
        with self.assertWarns(UserWarning):
            self.assertEqual(monthly_sales(p), {"2026-01": 1000})


if __name__ == "__main__":
    unittest.main(verbosity=2)
