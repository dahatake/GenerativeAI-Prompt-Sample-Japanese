import unittest
from pathlib import Path

from solution import _elapsed_minutes, _work_minutes, monthly_work_hours

_DIRECTORY = Path(__file__).parent
_HEADER = "employee,date,type,start,end\n"


class MonthlyWorkHoursTests(unittest.TestCase):
    def run_csv(self, body, header=_HEADER):
        path = _DIRECTORY / ".monthly_work_hours_test_input.csv"
        source = path.open("x", encoding="utf-8-sig", newline="")
        try:
            with source:
                source.write(header + body)
            return monthly_work_hours(path)
        finally:
            path.unlink()

    def test_sample_returns_float_hours_without_changing_input(self):
        path = _DIRECTORY / "shifts.csv"
        before = path.read_bytes()
        totals = monthly_work_hours(str(path))
        self.assertEqual(path.read_bytes(), before)
        self.assertIsInstance(totals, dict)
        expected = {"E001": 21.25, "E002": 13.0, "E003": 8.25}
        self.assertEqual(totals.keys(), expected.keys())
        for employee, hours in expected.items():
            with self.subTest(employee=employee):
                self.assertIsInstance(totals[employee], float)
                self.assertAlmostEqual(totals[employee], hours, delta=1e-9)

    def test_overnight_work_and_equal_times(self):
        self.assertEqual(_elapsed_minutes("22:00", "06:00"), 480)
        totals = self.run_csv(
            "night,2026-10-01,work,22:00,06:00\n"
            "zero,2026-10-02,work,09:00,09:00\n"
        )
        self.assertEqual(totals, {"night": 7.0, "zero": 0.0})
        self.assertIsInstance(totals["zero"], float)

    def test_overnight_work_at_month_end_belongs_to_start_month(self):
        totals = self.run_csv(
            "E001,2026-12-01,work,09:00,10:00\n"
            "E001,2026-12-31,work,22:00,06:00\n"
        )
        self.assertEqual(totals, {"E001": 8.0})

    def test_paid_leave_only_counts_450_minutes_per_row(self):
        totals = self.run_csv(
            "001,2026-10-01,paid_leave,,\n"
            "002,2026-10-01,paid_leave,,\n"
            "002,2026-10-02,paid_leave,unused,ignored\n"
        )
        self.assertEqual(totals, {"001": 7.5, "002": 15.0})

    def test_header_only_returns_empty_dict(self):
        self.assertEqual(self.run_csv(""), {})

    def test_invalid_headers_and_rows_raise_value_error(self):
        with self.assertRaises(ValueError):
            self.run_csv("", header="employee,date,type,start\n")
        for body in (
            "E001,2026-10-01,work,09:00,\n",
            "E001,2026-10-01,work,20:00,24:00\n",
            "E001,2026-02-30,work,09:00,10:00\n",
            "E001,2026-10-01,unknown,,\n",
            "  ,2026-10-01,paid_leave,,\n",
        ):
            with self.subTest(body=body), self.assertRaises(ValueError):
                self.run_csv(body)

    def test_different_month_or_year_raises_value_error(self):
        for other_date in ("2026-11-01", "2027-10-01"):
            with self.subTest(other_date=other_date), self.assertRaises(ValueError):
                self.run_csv(
                    "E001,2026-10-31,work,22:00,06:00\n"
                    f"E002,{other_date},paid_leave,,\n"
                )

    def test_break_threshold_uses_unrounded_elapsed_minutes(self):
        self.assertEqual(_work_minutes(360), 360)
        self.assertEqual(_work_minutes(361), 301)
        totals = self.run_csv(
            "six-hours,2026-10-01,work,09:00,15:00\n"
            "six-hours-one-minute,2026-10-01,work,09:00,15:01\n"
        )
        self.assertEqual(totals, {"six-hours": 6.0, "six-hours-one-minute": 5.0})

    def test_rounding_is_per_row_and_duplicate_rows_are_counted(self):
        totals = self.run_csv(
            "short,2026-10-01,work,09:00,09:08,one\n"
            "short,2026-10-01,work,09:00,09:08,two\n"
            "repeat,2026-10-01,work,09:00,09:20,duplicate\n"
            "repeat,2026-10-01,work,09:00,09:20,duplicate\n",
            header="employee,date,type,start,end,note\n",
        )
        self.assertEqual(totals, {"short": 0.0, "repeat": 0.5})
