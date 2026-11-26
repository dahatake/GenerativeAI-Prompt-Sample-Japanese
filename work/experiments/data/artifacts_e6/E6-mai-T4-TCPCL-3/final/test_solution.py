import csv
import os
import unittest

from solution import monthly_work_hours


class MonthlyWorkHoursTests(unittest.TestCase):
    def setUp(self):
        self.fixture = "test_contract_fixture.csv"

    def tearDown(self):
        if os.path.exists(self.fixture):
            os.remove(self.fixture)

    def write_fixture(self, rows):
        with open(self.fixture, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["employee", "date", "type", "start", "end"])
            writer.writerows(rows)

    def test_sample_contract_values(self):
        result = monthly_work_hours("shifts.csv")
        self.assertEqual(result["E001"], 22.25)
        self.assertEqual(result["E002"], 14.0)
        self.assertEqual(result["E003"], 9.25)
        self.assertTrue(all(isinstance(value, float) for value in result.values()))

    def test_paid_leave_is_7_5_hours(self):
        self.write_fixture([
            ["A", "2026-10-03", "paid_leave", "", ""],
        ])
        self.assertEqual(monthly_work_hours(self.fixture), {"A": 7.5})

    def test_overnight_and_multiple_rows(self):
        self.write_fixture([
            ["A", "2026-10-01", "work", "22:00", "06:00"],
            ["A", "2026-10-02", "work", "13:00", "19:00"],
        ])
        self.assertEqual(monthly_work_hours(self.fixture), {"A": 14.0})

    def test_missing_and_invalid_rows_are_skipped(self):
        self.write_fixture([
            ["A", "2026-10-01", "work", "", "17:00"],
            ["A", "2026-10-02", "work", "09:00", "24:00"],
            ["B", "2026-10-03", "other", "09:00", "17:00"],
            ["", "2026-10-04", "paid_leave", "", ""],
        ])
        self.assertEqual(monthly_work_hours(self.fixture), {})

    def test_each_shift_is_rounded_down_to_15_minutes(self):
        self.write_fixture([
            ["A", "2026-10-01", "work", "09:00", "09:14"],
            ["A", "2026-10-02", "work", "09:00", "14:50"],
            ["B", "2026-10-03", "work", "08:30", "17:45"],
        ])
        result = monthly_work_hours(self.fixture)
        self.assertEqual(result["A"], 5.75)
        self.assertEqual(result["B"], 9.25)

    def test_equal_times_and_normal_shift_boundaries(self):
        self.write_fixture([
            ["A", "2026-10-01", "work", "09:00", "09:00"],
            ["B", "2026-10-02", "work", "00:00", "01:00"],
        ])
        self.assertEqual(monthly_work_hours(self.fixture), {"A": 0.0, "B": 1.0})


if __name__ == "__main__":
    unittest.main(verbosity=2)
