import csv
import os
import unittest

from solution import monthly_work_hours


class MonthlyWorkHoursTests(unittest.TestCase):
    def setUp(self):
        self.fixture = os.path.join(os.getcwd(), "test_boundary_shifts.csv")

    def tearDown(self):
        if os.path.exists(self.fixture):
            os.unlink(self.fixture)

    def write_csv(self, rows):
        with open(self.fixture, "w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["employee", "date", "type", "start", "end"])
            writer.writeheader()
            writer.writerows(rows)

    def test_confirmed_shifts_csv_contract(self):
        result = monthly_work_hours(os.path.join(os.getcwd(), "shifts.csv"))
        self.assertEqual(result, {"E001": 21.25, "E002": 13.0, "E003": 8.25})

    def test_paid_leave_adds_7_5_hours_even_when_times_are_empty(self):
        self.write_csv([
            {"employee": "P001", "date": "2026-10-01", "type": "paid_leave", "start": "", "end": ""},
        ])
        self.assertEqual(monthly_work_hours(self.fixture), {"P001": 7.5})

    def test_night_shift_receives_break_and_is_overnight(self):
        self.write_csv([
            {"employee": "N001", "date": "2026-10-01", "type": "work", "start": "22:00", "end": "06:00"},
        ])
        self.assertEqual(monthly_work_hours(self.fixture), {"N001": 7.0})

    def test_exactly_six_hours_has_no_break(self):
        self.write_csv([
            {"employee": "S001", "date": "2026-10-01", "type": "work", "start": "13:00", "end": "19:00"},
        ])
        self.assertEqual(monthly_work_hours(self.fixture), {"S001": 6.0})

    def test_each_shift_is_floored_to_fifteen_minutes_after_break(self):
        self.write_csv([
            {"employee": "F001", "date": "2026-10-01", "type": "work", "start": "09:00", "end": "16:07"},
        ])
        # 427 minutes - 60 break = 367; floor to 15-minute units = 360 minutes.
        self.assertEqual(monthly_work_hours(self.fixture), {"F001": 6.0})

    def test_same_missing_invalid_and_unknown_rows_are_handled(self):
        self.write_csv([
            {"employee": "Z001", "date": "2026-10-01", "type": "work", "start": "09:00", "end": "09:00"},
            {"employee": "Z002", "date": "2026-10-01", "type": "work", "start": "", "end": ""},
            {"employee": "Z003", "date": "2026-10-01", "type": "work", "start": "09:61", "end": "10:00"},
            {"employee": "", "date": "2026-10-01", "type": "work", "start": "08:00", "end": "17:00"},
            {"employee": "Z004", "date": "2026-10-01", "type": "other", "start": "08:00", "end": "17:00"},
        ])
        self.assertEqual(monthly_work_hours(self.fixture), {
            "Z001": 0.0,
        })

    def test_employee_order_is_csv_first_appearance(self):
        self.write_csv([
            {"employee": "B", "date": "2026-10-01", "type": "work", "start": "09:00", "end": "10:00"},
            {"employee": "A", "date": "2026-10-01", "type": "paid_leave", "start": "", "end": ""},
            {"employee": "B", "date": "2026-10-02", "type": "paid_leave", "start": "", "end": ""},
        ])
        result = monthly_work_hours(self.fixture)
        self.assertEqual(list(result), ["B", "A"])


if __name__ == "__main__":
    unittest.main()
