import csv
import os
import tempfile
import unittest

from solution import monthly_work_hours


class MonthlyWorkHoursTests(unittest.TestCase):
    def test_sample_csv(self):
        result = monthly_work_hours("shifts.csv")
        self.assertEqual(result["E001"], 21.25)
        self.assertEqual(result["E002"], 13.0)
        self.assertEqual(result["E003"], 8.25)
        self.assertTrue(all(isinstance(value, float) for value in result.values()))

    def test_break_exactly_six_hours_and_overnight(self):
        fd, path = tempfile.mkstemp(suffix=".csv", dir=".")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["employee", "date", "type", "start", "end"])
                writer.writerow(["A", "2026-10-01", "work", "09:00", "15:00"])
                writer.writerow(["B", "2026-10-01", "work", "22:07", "06:07"])
                writer.writerow(["F", "2026-10-01", "work", "12:00", "12:00"])
            result = monthly_work_hours(path)
            self.assertEqual(result["A"], 6.0)
            self.assertEqual(result["B"], 7.0)
            self.assertEqual(result["F"], 0.0)
        finally:
            os.unlink(path)

    def test_floor_each_shift_to_fifteen_minutes(self):
        fd, path = tempfile.mkstemp(suffix=".csv", dir=".")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["employee", "date", "type", "start", "end"])
                writer.writerow(["C", "2026-10-01", "work", "09:00", "09:14"])
                writer.writerow(["C", "2026-10-01", "work", "10:00", "10:16"])
            result = monthly_work_hours(path)
            self.assertEqual(result["C"], 0.25)
        finally:
            os.unlink(path)

    def test_paid_leave_is_7_5_hours_and_aggregates(self):
        fd, path = tempfile.mkstemp(suffix=".csv", dir=".")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["employee", "date", "type", "start", "end"])
                writer.writerow(["D", "2026-10-01", "paid_leave", "", ""])
                writer.writerow(["D", "2026-10-02", "paid_leave", "", ""])
            result = monthly_work_hours(path)
            self.assertEqual(result["D"], 15.0)
        finally:
            os.unlink(path)

    def test_invalid_work_time_raises_row_numbered_value_error(self):
        fd, path = tempfile.mkstemp(suffix=".csv", dir=".")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["employee", "date", "type", "start", "end"])
                writer.writerow(["E", "2026-10-01", "work", "25:00", "26:00"])
            with self.assertRaisesRegex(ValueError, r"row 2"):
                monthly_work_hours(path)
        finally:
            os.unlink(path)

    def test_missing_required_column_raises_value_error(self):
        fd, path = tempfile.mkstemp(suffix=".csv", dir=".")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["employee", "date", "type", "start"])
            with self.assertRaises(ValueError):
                monthly_work_hours(path)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()

