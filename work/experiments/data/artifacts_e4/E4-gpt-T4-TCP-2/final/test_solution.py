from pathlib import Path
from tempfile import NamedTemporaryFile
import unittest

from solution import monthly_work_hours


HEADER = "employee,date,type,start,end\n"


class MonthlyWorkHoursTest(unittest.TestCase):
    def csv_file(self, contents):
        with NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=".", delete=False) as file:
            path = Path(file.name)
            self.addCleanup(path.unlink, missing_ok=True)
            file.write(contents)
        return path

    def test_api_types_zero_and_row_order(self):
        rows = [
            "001,2026-10-01,work,08:00,08:00\n",
            "002,2026-10-01,work,08:00,09:00\n",
            "002,2026-10-02,work,10:00,10:30\n",
        ]
        result = monthly_work_hours(str(self.csv_file(HEADER + "".join(rows))))
        reversed_result = monthly_work_hours(self.csv_file(HEADER + "".join(reversed(rows))))
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {"001": 0.0, "002": 1.5})
        self.assertEqual(reversed_result, result)
        for employee, hours in result.items():
            self.assertIsInstance(employee, str)
            self.assertIsInstance(hours, float)

    def test_sample(self):
        result = monthly_work_hours("shifts.csv")
        expected = {"E001": 21.25, "E002": 13.0, "E003": 8.25}
        self.assertEqual(result.keys(), expected.keys())
        for employee, hours in expected.items():
            self.assertAlmostEqual(result[employee], hours, delta=1e-9)
        print(f"sample result: {result}", flush=True)

    def test_break_and_rounding_boundaries(self):
        cases = {"06:00": 6.0, "06:01": 5.0, "06:14": 5.0, "06:15": 5.25,
                 "08:00": 7.0, "08:01": 7.0}
        for end, hours in cases.items():
            with self.subTest(end=end):
                path = self.csv_file(HEADER + f"A,2026-10-01,work,00:00,{end}\n")
                self.assertEqual(monthly_work_hours(path), {"A": hours})

    def test_rounding_is_per_shift(self):
        path = self.csv_file(HEADER + "A,2026-10-01,work,09:00,09:59\n"
                             "A,2026-10-02,work,09:00,09:59\n")
        self.assertEqual(monthly_work_hours(path), {"A": 1.5})

    def test_overnight_at_month_end(self):
        path = self.csv_file(HEADER + "B,2026-10-01,work,08:00,09:00\n"
                             "A,2026-10-31,work,22:00,06:00\n")
        self.assertEqual(monthly_work_hours(path), {"A": 7.0, "B": 1.0})

    def test_mixed_months_are_invalid(self):
        for other_date in ("2026-11-01", "2025-10-01"):
            with self.subTest(other_date=other_date):
                path = self.csv_file(HEADER + "A,2026-10-31,work,22:00,06:00\n"
                                     f"B,{other_date},paid_leave,,\n")
                with self.assertRaisesRegex(ValueError, "more than one month"):
                    monthly_work_hours(path)

    def test_paid_leave_ignores_times(self):
        path = self.csv_file(HEADER + "A,2026-10-01,paid_leave,ignored,ignored\n")
        self.assertEqual(monthly_work_hours(path), {"A": 7.5})

    def test_csv_bom_named_columns_and_blank_lines(self):
        path = self.csv_file("\ufeff\r\ntype,end,extra,date,start,employee\r\n\r\n"
                             "work,12:00,note,2026-10-01,09:00,A\r\n\r\n")
        self.assertEqual(monthly_work_hours(path), {"A": 3.0})
        self.assertEqual(monthly_work_hours(self.csv_file(HEADER)), {})

    def test_invalid_input(self):
        invalid_cases = {
            "empty file": "",
            "missing header column": "employee,date,type,start\n",
            "empty employee ID": HEADER + ",2026-10-01,work,09:00,10:00\n",
            "invalid calendar date": HEADER + "A,2026-02-29,work,09:00,10:00\n",
            "invalid date format": HEADER + "A,20261001,work,09:00,10:00\n",
            "invalid time range": HEADER + "A,2026-10-01,work,09:00,24:00\n",
            "invalid time format": HEADER + "A,2026-10-01,work,9:00,10:00\n",
            "missing work time": HEADER + "A,2026-10-01,work,09:00,\n",
            "unknown shift type": HEADER + "A,2026-10-01,other,09:00,10:00\n",
        }
        for case, contents in invalid_cases.items():
            with self.subTest(case=case), self.assertRaises(ValueError):
                monthly_work_hours(self.csv_file(contents))

    def test_missing_file(self):
        path = self.csv_file(HEADER)
        path.unlink()
        with self.assertRaises(FileNotFoundError):
            monthly_work_hours(path)
