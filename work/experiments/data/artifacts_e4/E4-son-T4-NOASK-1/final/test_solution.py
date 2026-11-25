import os
import tempfile
import unittest

from solution import monthly_work_hours

HERE = os.path.dirname(os.path.abspath(__file__))


def run_csv(text):
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", dir=HERE) as f:
        f.write(text)
        p = f.name
    try:
        return monthly_work_hours(p)
    finally:
        os.remove(p)


class Tests(unittest.TestCase):
    def test_sample(self):
        r = monthly_work_hours(os.path.join(HERE, "shifts.csv"))
        self.assertIsInstance(r, dict)
        self.assertEqual(set(r), {"E001", "E002", "E003"})
        for k, v in r.items():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, float)
        self.assertAlmostEqual(r["E001"], 9 + 5 + 50 / 60)
        self.assertAlmostEqual(r["E002"], 14.0)
        self.assertAlmostEqual(r["E003"], 9.25)

    def test_overnight_not_negative(self):
        r = run_csv("employee,date,type,start,end\nA,2026-10-01,work,22:00,06:00\n")
        self.assertEqual(r["A"], 8.0)

    def test_paid_leave_only_is_zero(self):
        r = run_csv("employee,date,type,start,end\nB,2026-10-01,paid_leave,,\n")
        self.assertEqual(r, {"B": 0.0})
        self.assertIsInstance(r["B"], float)

    def test_invalid_work_row_raises(self):
        for bad in ("C,2026-10-01,work,,\n", "C,2026-10-01,work,9am,18:00\n"):
            with self.assertRaises(ValueError):
                run_csv("employee,date,type,start,end\n" + bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
