import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from solution import monthly_work_hours


_HEADER = "employee,date,type,start,end\n"


class MonthlyWorkHoursTests(unittest.TestCase):
    def csv_file(self, contents, *, encoding="utf-8"):
        with NamedTemporaryFile(mode="w", encoding=encoding, newline="", suffix=".csv",
                                dir=".", delete=False) as fixture:
            path = Path(fixture.name)
            self.addCleanup(path.unlink, missing_ok=True)
            fixture.write(contents)
        return path

    def test_return_types_and_zero_hours(self):
        path = self.csv_file(_HEADER + "001,2026-10-01,work,09:00,09:00\n")
        result = monthly_work_hours(path)
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {"001": 0.0})
        self.assertIsInstance(next(iter(result.values())), float)

    def test_sample(self):
        result = monthly_work_hours(Path(__file__).with_name("shifts.csv"))
        expected = {"E001": 21.25, "E002": 13.0, "E003": 8.25}
        self.assertEqual(result.keys(), expected.keys())
        for employee, hours in expected.items():
            with self.subTest(employee=employee):
                self.assertAlmostEqual(result[employee], hours, delta=1e-9)

    def test_break_and_rounding_boundaries(self):
        for end, expected in (
            ("15:00", 6.0), ("15:01", 5.0), ("15:14", 5.0),
            ("15:15", 5.25), ("17:00", 7.0), ("17:01", 7.0),
        ):
            with self.subTest(end=end):
                path = self.csv_file(_HEADER + f"E,2026-10-01,work,09:00,{end}\n")
                self.assertEqual(monthly_work_hours(path), {"E": expected})

    def test_rounding_is_per_shift_and_duplicate_rows_count(self):
        path = self.csv_file(_HEADER + "E,2026-10-01,work,09:00,14:14\n" * 2)
        self.assertEqual(monthly_work_hours(path), {"E": 10.0})

    def test_overnight_and_month_end_use_start_date(self):
        path = self.csv_file(
            _HEADER + "E1,2026-10-01,work,22:00,06:00\n"
            "E2,2026-10-31,work,22:00,06:00\n"
        )
        self.assertEqual(monthly_work_hours(path), {"E1": 7.0, "E2": 7.0})

    def test_paid_leave_only(self):
        path = self.csv_file(
            _HEADER + "E1,2026-10-01,paid_leave,,\n"
            "E1,2026-10-02,paid_leave,,\nE2,2026-10-01,paid_leave,,\n"
        )
        self.assertEqual(monthly_work_hours(path), {"E1": 15.0, "E2": 7.5})

    def test_rejects_multiple_calendar_months(self):
        for other_day in ("2026-11-01", "2027-10-01"):
            with self.subTest(other_day=other_day):
                path = self.csv_file(
                    _HEADER + "E1,2026-10-31,work,22:00,06:00\n"
                    f"E2,{other_day},paid_leave,,\n"
                )
                with self.assertRaisesRegex(ValueError, "line 3:.*calendar month"):
                    monthly_work_hours(path)

    def test_header_only(self):
        self.assertEqual(monthly_work_hours(self.csv_file(_HEADER)), {})

    def test_bom_reordered_and_extra_columns(self):
        path = self.csv_file(
            'note,type,end,start,date,employee\r\n"a,b",work,09:30,09:00,2026-10-01,001\r\n',
            encoding="utf-8-sig",
        )
        self.assertEqual(monthly_work_hours(path), {"001": 0.5})

    def test_bad_headers(self):
        for header, error in (("", "missing"), ("employee,date,type,start\n", "missing"),
                              (_HEADER.strip() + ",employee\n", "duplicate")):
            with self.subTest(header=header), self.assertRaisesRegex(ValueError, error):
                monthly_work_hours(self.csv_file(header))

    def test_invalid_rows_report_line_numbers(self):
        for row, error in (
            ("E,2026-10-01,work,09:00,24:01", "invalid time"),
            ("E,2026-10-01,work,,10:00", "invalid time"),
            (" ,2026-10-01,work,09:00,10:00", "employee ID"),
            ("E,2026-02-30,work,09:00,10:00", "invalid date"),
            ("E,2026-10-01,unknown,,", "unknown shift type"),
            ("E,2026-10-01,paid_leave,09:00,", "blank start and end"),
            ("E,2026-10-01,work,09:00", "number of columns"),
            ('"E"x,2026-10-01,work,09:00,10:00', "invalid CSV"),
        ):
            with self.subTest(row=row), self.assertRaisesRegex(ValueError, f"line 3:.*{error}"):
                monthly_work_hours(self.csv_file(_HEADER + "\n" + row + "\n"))

    def test_missing_file_error_propagates(self):
        path = self.csv_file(_HEADER)
        path.unlink()
        with self.assertRaises(FileNotFoundError):
            monthly_work_hours(path)
