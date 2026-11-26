import unittest
from pathlib import Path
from uuid import uuid4

from solution import monthly_work_hours


HEADER = "employee,date,type,start,end\n"
HERE = Path(__file__).resolve().parent


class MonthlyWorkHoursTests(unittest.TestCase):
    def aggregate(self, text):
        path = HERE / f"test_shifts_{uuid4().hex}.csv"
        stream = path.open("x", encoding="utf-8", newline="")
        try:
            with stream:
                stream.write(text)
            return monthly_work_hours(path)
        finally:
            path.unlink()

    def test_dod_1_sample_values_order_and_types(self):
        result = monthly_work_hours(HERE / "shifts.csv")
        self.assertIsInstance(result, dict)
        self.assertEqual(list(result.items()), [("E001", 21.25), ("E002", 13.0), ("E003", 8.25)])
        self.assertTrue(all(type(hours) is float for hours in result.values()))

    def test_dod_1_bom_column_order_ids_and_status(self):
        result = self.aggregate(
            "\ufeffend,employee,type,date,status,start\n"
            '10:00," 002 ", work , 2026-10-01 ,rejected, 09:00\n'
            "09:15,001,work,2026-10-01,open,09:00\n"
            "10:00,002,work,2026-10-01,rejected,09:00\n"
        )
        self.assertEqual(list(result.items()), [("001", 0.25), ("002", 2.0)])

    def test_dod_2_month_end_overnight_in_start_month(self):
        result = self.aggregate(
            HEADER + "night,2026-10-31,work,22:00,06:00\n"
            "night,2026-10-01,work,00:00,01:00\n"
        )
        self.assertEqual(result, {"night": 8.0})

    def test_dod_2_reject_mixed_months_even_with_only_leave_in_second(self):
        october = "night,2026-10-31,work,22:00,06:00\n"
        for november in ("day,2026-11-01,work,00:00,01:00\n", "leave,2026-11-01,paid_leave,,\n"):
            with self.subTest(november=november), self.assertRaises(ValueError):
                self.aggregate(HEADER + october + november)

    def test_dod_3_break_and_rounding_boundaries(self):
        cases = (("05:59", 5.75), ("06:00", 6.0), ("06:01", 5.0),
                 ("08:00", 7.0), ("08:01", 7.0), ("00:14", 0.0), ("00:15", 0.25))
        for end, expected in cases:
            with self.subTest(end=end):
                self.assertEqual(
                    self.aggregate(HEADER + f"E1,2026-10-01,work,00:00,{end}\n"),
                    {"E1": expected},
                )

    def test_dod_3_round_each_shift_before_summing(self):
        result = self.aggregate(
            HEADER + "E1,2026-10-01,work,09:00,09:14\n"
            "E1,2026-10-02,work,08:00,08:14\n"
        )
        self.assertEqual(result, {"E1": 0.0})

    def test_dod_4_paid_leave_zero_hours_and_header_only(self):
        result = self.aggregate(
            HEADER + "leave,2026-10-01,paid_leave,,\n"
            "twice,2026-10-01,paid_leave,unused,also unused\n"
            "twice,2026-10-02,paid_leave,,\n"
            "zero,2026-10-01,work,09:15,09:15\n"
        )
        self.assertEqual(result, {"leave": 7.5, "twice": 15.0, "zero": 0.0})
        self.assertIs(type(result["zero"]), float)
        self.assertEqual(self.aggregate("\n" + HEADER + "\n"), {})

    def test_dod_5_invalid_headers_and_rows(self):
        cases = {
            "empty file": "",
            "missing column": "employee,date,type,start\n",
            "duplicate header": "employee,date,type,start,end,date\n",
            "short row": HEADER + "E1,2026-10-01,work,09:00\n",
            "long row": HEADER + "E1,2026-10-01,work,09:00,10:00,extra\n",
            "missing ID": HEADER + " ,2026-10-01,work,09:00,10:00\n",
            "missing date": HEADER + "E1,,paid_leave,,\n",
            "missing type": HEADER + "E1,2026-10-01,,09:00,10:00\n",
            "missing start": HEADER + "E1,2026-10-01,work,,10:00\n",
            "missing end": HEADER + "E1,2026-10-01,work,09:00,\n",
            "invalid date": HEADER + "E1,2026-02-29,work,09:00,10:00\n",
            "noncanonical date": HEADER + "E1,20261001,work,09:00,10:00\n",
            "invalid hour": HEADER + "E1,2026-10-01,work,00:00,24:00\n",
            "invalid minute": HEADER + "E1,2026-10-01,work,09:60,10:00\n",
            "noncanonical time": HEADER + "E1,2026-10-01,work,9:00,10:00\n",
            "unknown type": HEADER + "E1,2026-10-01,Work,09:00,10:00\n",
        }
        for label, contents in cases.items():
            with self.subTest(label=label), self.assertRaises(ValueError):
                self.aggregate(contents)

    def test_dod_5_maximum_duration_and_file_error(self):
        self.assertEqual(
            self.aggregate(HEADER + "E1,2026-10-01,work,00:00,23:59\n"),
            {"E1": 22.75},
        )
        with self.assertRaises(FileNotFoundError):
            monthly_work_hours(HERE / f"missing_shifts_{uuid4().hex}.csv")
