import unittest
from pathlib import Path
from uuid import uuid4

from solution import monthly_work_hours


ROOT = Path(__file__).resolve().parent
HEADER = "employee,date,type,start,end\n"


class MonthlyWorkHoursTests(unittest.TestCase):
    def csv_file(self, contents, *, encoding="utf-8"):
        path = ROOT / f".test-shifts-{uuid4().hex}.csv"
        with path.open("x", encoding=encoding, newline="") as output:
            self.addCleanup(path.unlink)
            output.write(contents)
        return path

    def test_sample_file(self):
        result = monthly_work_hours(ROOT / "shifts.csv")
        expected = {"E001": 890 / 60, "E002": 14.0, "E003": 9.25}
        self.assertIsInstance(result, dict)
        self.assertEqual(result.keys(), expected.keys())
        for employee, hours in expected.items():
            with self.subTest(employee=employee):
                self.assertIs(type(result[employee]), float)
                self.assertAlmostEqual(result[employee], hours)

    def test_overnight_shift_is_eight_hours(self):
        path = self.csv_file(HEADER + "E001,2026-10-01,work,22:00,06:00\n")
        self.assertEqual(monthly_work_hours(path), {"E001": 8.0})

    def test_month_end_shift_is_credited_entirely_to_start_month(self):
        path = self.csv_file(HEADER + "E001,2026-12-31,work,22:00,06:00\n")
        self.assertEqual(monthly_work_hours(path), {"E001": 8.0})

    def test_multiple_year_months_are_rejected(self):
        for other_date in ("2026-11-01", "2027-10-01"):
            with self.subTest(other_date=other_date):
                path = self.csv_file(
                    HEADER
                    + "E001,2026-10-31,work,22:00,06:00\n"
                    + f"E002,{other_date},paid_leave,,\n"
                )
                with self.assertRaises(ValueError):
                    monthly_work_hours(path)

    def test_paid_leave_only_employees_get_zero_hours(self):
        path = self.csv_file(
            HEADER + "E001,2026-10-01,paid_leave,,\n"
            "E002,2026-10-02,paid_leave,09:00,18:00\n"
        )
        result = monthly_work_hours(path)
        self.assertEqual(result, {"E001": 0.0, "E002": 0.0})
        self.assertIs(type(result["E001"]), float)

    def test_header_only_returns_empty_dict(self):
        self.assertEqual(monthly_work_hours(self.csv_file(HEADER)), {})

    def test_missing_required_column_is_rejected(self):
        path = self.csv_file("employee,date,type,start\n")
        with self.assertRaises(ValueError):
            monthly_work_hours(path)

    def test_invalid_times_are_rejected(self):
        for kind, start, end in (
            ("work", "09:00", "24:00"),
            ("work", "9:00", "18:00"),
            ("work", "", "18:00"),
            ("paid_leave", "invalid", ""),
        ):
            with self.subTest(kind=kind, start=start, end=end):
                path = self.csv_file(HEADER + f"E001,2026-10-01,{kind},{start},{end}\n")
                with self.assertRaises(ValueError):
                    monthly_work_hours(path)

    def test_invalid_employee_date_and_type_are_rejected(self):
        for row in (
            ",2026-10-01,work,09:00,18:00",
            "E001,2026-02-29,work,09:00,18:00",
            "E001,2026-10-01,unknown,09:00,18:00",
        ):
            with self.subTest(row=row):
                path = self.csv_file(HEADER + row + "\n")
                with self.assertRaises(ValueError):
                    monthly_work_hours(path)

    def test_bom_equal_times_and_string_employee_id(self):
        path = self.csv_file(HEADER + "001,2026-10-01,work,09:00,09:00\n", encoding="utf-8-sig")
        self.assertEqual(monthly_work_hours(path), {"001": 0.0})


if __name__ == "__main__":
    unittest.main()
