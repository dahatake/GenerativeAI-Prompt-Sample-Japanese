import os
import tempfile
import unittest

from solution import monthly_work_hours

HEADER = "employee,date,type,start,end\n"


def run(body, newline="\n"):
    with tempfile.TemporaryDirectory(dir=os.getcwd()) as d:
        p = os.path.join(d, "t.csv")
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write((HEADER + body).replace("\n", newline))
        return monthly_work_hours(p)


class Test(unittest.TestCase):
    def test_dod1_2_sample(self):
        r = monthly_work_hours("shifts.csv")
        self.assertEqual(r, {"E001": 21.25, "E002": 13.0, "E003": 8.25})
        self.assertTrue(all(isinstance(k, str) and isinstance(v, float) for k, v in r.items()))

    def test_dod3_overnight(self):
        self.assertEqual(run("A,2026-10-01,work,22:00,06:00\n"), {"A": 7.0})

    def test_dod4_break_threshold(self):
        self.assertEqual(run("A,2026-10-01,work,09:00,15:00\n"), {"A": 6.0})
        self.assertEqual(run("A,2026-10-01,work,09:00,15:01\n"), {"A": 5.0})
        self.assertEqual(run("A,2026-10-01,work,09:00,15:15\n"), {"A": 5.25})

    def test_dod5_floor_15min(self):
        self.assertEqual(run("A,2026-10-01,work,09:00,14:50\n"), {"A": 5.75})
        self.assertEqual(run("A,2026-10-01,work,09:00,09:14\n"), {"A": 0.0})

    def test_dod6_paid_leave(self):
        self.assertEqual(run("A,2026-10-01,paid_leave,,\nA,2026-10-02,paid_leave,,\nB,2026-10-01,paid_leave,,\n"),
                         {"A": 15.0, "B": 7.5})

    def test_dod7_newlines(self):
        body = "A,2026-10-01,work,09:00,18:00\nA,2026-10-02,paid_leave,,\n"
        expected = {"A": 15.5}
        self.assertEqual(run(body, "\n"), expected)
        self.assertEqual(run(body, "\r\n"), expected)
        self.assertEqual(run(body.rstrip("\n"), "\n"), expected)

    def test_dod8_invalid(self):
        for body in (
            "A,2026-10-01,work,,\n",
            "A,2026-10-01,work,9:00am,18:00\n",
            "A,2026-10-01,work,25:00,18:00\n",
            "A,2026-10-01,holiday,09:00,18:00\n",
            "A,2026-13-01,work,09:00,18:00\n",
        ):
            with self.assertRaises(ValueError, msg=body):
                run(body)

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            monthly_work_hours("no_such.csv")


if __name__ == "__main__":
    unittest.main()
