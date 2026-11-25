import math
import os
import tempfile
import unittest

from solution import monthly_work_hours


class MonthlyWorkHoursTests(unittest.TestCase):
    def write_csv(self, content):
        fd, path = tempfile.mkstemp(suffix=".csv", dir=".")
        os.close(fd)
        with open(path, "w", encoding="utf-8", newline="") as csv_file:
            csv_file.write(content)
        self.addCleanup(os.remove, path)
        return path

    def test_sample_csv(self):
        result = monthly_work_hours("shifts.csv")
        self.assertTrue(math.isclose(result["E001"], 14.833333333333334, rel_tol=0, abs_tol=1e-12))
        self.assertTrue(math.isclose(result["E002"], 14.0, rel_tol=0, abs_tol=1e-12))
        self.assertTrue(math.isclose(result["E003"], 9.25, rel_tol=0, abs_tol=1e-12))

    def test_paid_leave_is_not_counted(self):
        path = self.write_csv(
            "employee,date,type,start,end\n"
            "E1,2026-10-01,work,09:00,17:30\n"
            "E1,2026-10-02,paid_leave,,\n"
        )
        self.assertEqual(monthly_work_hours(path), {"E1": 8.5})

    def test_overnight_and_equal_times(self):
        path = self.write_csv(
            "employee,date,type,start,end\n"
            "E1,2026-10-01,work,22:00,06:00\n"
            "E1,2026-10-02,work,10:00,10:00\n"
        )
        self.assertEqual(monthly_work_hours(path), {"E1": 8.0})

    def test_invalid_work_time_raises_value_error(self):
        path = self.write_csv(
            "employee,date,type,start,end\n"
            "E1,2026-10-01,work,25:00,26:00\n"
        )
        with self.assertRaisesRegex(ValueError, "CSV row 2"):
            monthly_work_hours(path)

    def test_missing_required_header_raises_value_error(self):
        path = self.write_csv("employee,type,start\nE1,work,09:00\n")
        with self.assertRaisesRegex(ValueError, "Missing required CSV column"):
            monthly_work_hours(path)


if __name__ == "__main__":
    unittest.main()
