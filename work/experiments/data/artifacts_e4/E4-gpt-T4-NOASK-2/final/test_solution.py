import io
import math
from pathlib import Path
import unittest
from unittest.mock import patch

import solution


_HEADER = "employee,date,type,start,end\n"


def _hours(csv_text):
    with patch.object(solution, "open", return_value=io.StringIO(csv_text), create=True):
        return solution.monthly_work_hours("fixture.csv")


class MonthlyWorkHoursTests(unittest.TestCase):
    def test_sample(self):
        actual = solution.monthly_work_hours(Path(__file__).with_name("shifts.csv"))
        expected = {"E001": 890 / 60, "E002": 14.0, "E003": 9.25}
        self.assertIsInstance(actual, dict)
        self.assertEqual(actual.keys(), expected.keys())
        for employee, hours in expected.items():
            with self.subTest(employee=employee):
                self.assertIs(type(actual[employee]), float)
                self.assertTrue(math.isclose(actual[employee], hours, rel_tol=0, abs_tol=1e-12))

    def test_month_end_overnight_counts_full_shift(self):
        self.assertEqual(_hours(_HEADER + "E001,2026-10-31,work,22:00,06:00\n"), {"E001": 8.0})

    def test_rejects_mixed_months(self):
        for date_text in ("2026-11-01", "2027-10-01"):
            with self.subTest(date_text=date_text):
                csv_text = _HEADER + "E001,2026-10-31,work,22:00,06:00\n"
                csv_text += f"E002,{date_text},paid_leave,,\n"
                with self.assertRaisesRegex(ValueError, r"line 3: .*multiple calendar months"):
                    _hours(csv_text)

    def test_paid_leave_only_includes_zero_hours(self):
        actual = _hours(_HEADER + "E001,2026-10-01,paid_leave,,\n")
        self.assertEqual(actual, {"E001": 0.0})
        self.assertIs(type(actual["E001"]), float)

    def test_header_only_returns_empty_dict(self):
        self.assertEqual(_hours(_HEADER), {})

    def test_bad_work_time_reports_row(self):
        for end in ("25:00", "09:00:00", ""):
            with self.subTest(end=end):
                csv_text = _HEADER + "E001,2026-10-01,work,09:00,10:00\n"
                csv_text += f"E001,2026-10-02,work,09:00,{end}\n"
                with self.assertRaisesRegex(ValueError, r"line 3:"):
                    _hours(csv_text)

    def test_equal_times_count_as_zero_and_id_is_preserved(self):
        self.assertEqual(_hours(_HEADER + "001,2026-10-01,work,09:00,09:00\n"), {"001": 0.0})

    def test_missing_required_column_is_rejected(self):
        with self.assertRaises(ValueError):
            _hours("employee,date,type,start\n")

    def test_bad_rows_report_line_number(self):
        for row in (
            "E001,2026-02-30,work,09:00,10:00\n",
            " ,2026-10-01,work,09:00,10:00\n",
            "E001,2026-10-01,unknown,09:00,10:00\n",
            "E001,2026-10-01,work,09:00\n",
        ):
            with self.subTest(row=row), self.assertRaisesRegex(ValueError, r"line 2:"):
                _hours(_HEADER + row)


if __name__ == "__main__":
    unittest.main()
