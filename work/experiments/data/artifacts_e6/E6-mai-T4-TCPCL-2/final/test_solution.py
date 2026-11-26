import csv
import os
import unittest

from solution import monthly_work_hours


class MonthlyWorkHoursTests(unittest.TestCase):
    def setUp(self):
        self.fixture = "test_shifts_fixture.csv"

    def tearDown(self):
        if os.path.exists(self.fixture):
            os.remove(self.fixture)

    def write_fixture(self, rows):
        with open(self.fixture, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["employee", "date", "type", "start", "end"])
            writer.writerows(rows)

    def test_sample_contract(self):
        result = monthly_work_hours("shifts.csv")
        self.assertEqual(result, {"E001": 21.25, "E002": 13.0, "E003": 8.25})
        self.assertTrue(all(isinstance(value, float) for value in result.values()))

    def test_threshold_crossing_and_rounding(self):
        self.write_fixture([
            ["A", "2026-10-01", "work", "09:00", "15:00"],
            ["B", "2026-10-01", "work", "09:00", "15:01"],
            ["C", "2026-10-01", "work", "22:00", "06:00"],
            ["D", "2026-10-01", "work", "09:00", "09:16"],
        ])
        result = monthly_work_hours(self.fixture)
        self.assertEqual(result["A"], 6.0)
        self.assertEqual(result["B"], 5.0)
        self.assertEqual(result["C"], 7.0)
        self.assertEqual(result["D"], 0.25)

    def test_paid_leave_missing_times_and_aggregation(self):
        self.write_fixture([
            ["A", "2026-10-01", "work", "09:00", "14:50"],
            ["A", "2026-10-02", "paid_leave", "", ""],
            ["A", "2026-10-03", "work", "09:00", "09:00"],
        ])
        result = monthly_work_hours(self.fixture)
        self.assertEqual(result["A"], 13.25)

    def test_missing_work_times_are_skipped(self):
        self.write_fixture([
            ["A", "2026-10-01", "work", "", ""],
            ["A", "2026-10-02", "other", "09:00", "10:00"],
        ])
        self.assertEqual(monthly_work_hours(self.fixture), {})

    def test_invalid_work_time_raises_value_error(self):
        self.write_fixture([
            ["A", "2026-10-01", "work", "25:00", "26:00"],
        ])
        with self.assertRaises(ValueError):
            monthly_work_hours(self.fixture)


if __name__ == "__main__":
    unittest.main(verbosity=2)


