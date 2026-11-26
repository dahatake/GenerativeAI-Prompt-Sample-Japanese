import math
import unittest

from solution import monthly_work_hours


class MonthlyWorkHoursTests(unittest.TestCase):
    def test_sample_shifts(self):
        result = monthly_work_hours("shifts.csv")
        self.assertAlmostEqual(result["E001"], 22.25)
        self.assertAlmostEqual(result["E002"], 14.0)
        self.assertAlmostEqual(result["E003"], 9.25)
        self.assertTrue(all(isinstance(value, float) for value in result.values()))

    def test_paid_leave_is_7_5_hours(self):
        result = monthly_work_hours("shifts.csv")
        self.assertEqual(result["E001"], 22.25)

    def test_each_shift_is_floored_to_quarter_hour(self):
        result = monthly_work_hours("shifts.csv")
        self.assertEqual(result["E001"], 9.0 + 5.75 + 7.5)

    def test_overnight_shift_crosses_midnight(self):
        result = monthly_work_hours("shifts.csv")
        self.assertEqual(result["E002"], 14.0)


if __name__ == "__main__":
    unittest.main()
