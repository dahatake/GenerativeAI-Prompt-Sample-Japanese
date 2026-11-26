import unittest
from pathlib import Path
from uuid import uuid4

from solution import monthly_work_hours


_ROOT = Path(__file__).parent
_HEADER = "employee,date,type,start,end\n"


class MonthlyWorkHoursTests(unittest.TestCase):
    def aggregate(self, text: str) -> dict[str, float]:
        path = _ROOT / f".shift-fixture-{uuid4().hex}.csv"
        with path.open("xb") as fixture:
            self.addCleanup(path.unlink)
            fixture.write(text.encode("utf-8"))
        return monthly_work_hours(path)

    def test_dod_1_sample(self):
        result = monthly_work_hours(str(_ROOT / "shifts.csv"))
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {"E001": 21.25, "E002": 13.0, "E003": 8.25})
        for hours in result.values():
            self.assertIsInstance(hours, float)

    def test_dod_2_month_end_same_time_and_leave_only(self):
        result = self.aggregate(
            _HEADER
            + "night,2026-10-31,work,22:00,06:00\n"
            + "zero,2026-10-31,work,09:00,09:00\n"
            + "leave,2026-10-31,paid_leave,,\n"
        )
        self.assertEqual(result, {"night": 7.0, "zero": 0.0, "leave": 7.5})

    def test_dod_2_header_only(self):
        self.assertEqual(self.aggregate(_HEADER), {})

    def test_dod_2_bom_column_order_id_and_duplicates(self):
        result = self.aggregate(
            "\ufeffnote,start,employee,end,type,date\n"
            '"ignored, quoted",08:00,001,08:30,work,2026-10-01\n'
            '"ignored, quoted",08:00,001,08:30,work,2026-10-01\n'
        )
        self.assertEqual(result, {"001": 1.0})

    def test_dod_3_invalid_csv(self):
        good = "E001,2026-10-01,work,09:00,10:00\n"
        for case, content in {
            "missing column": "employee,date,type,start\n",
            "blank ID": _HEADER + ",2026-10-01,work,09:00,10:00\n",
            "invalid calendar date": _HEADER + "E001,2026-10-32,work,09:00,10:00\n",
            "invalid clock time": _HEADER + "E001,2026-10-01,work,09:00,24:00\n",
            "missing field": _HEADER + "E001,2026-10-01,work,09:00\n",
            "unknown type after valid row": _HEADER + good + "E001,2026-10-02,other,,\n",
            "mixed months": _HEADER + good + "E001,2026-11-01,paid_leave,,\n",
            "unterminated quoted field": _HEADER + '"E001,2026-10-01,work,09:00,10:00\n',
        }.items():
            with self.subTest(case=case), self.assertRaises(ValueError):
                self.aggregate(content)

    def test_dod_3_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            monthly_work_hours(_ROOT / f".absent-shifts-{uuid4().hex}.csv")

    def test_dod_4_break_threshold(self):
        self.assertEqual(self.aggregate(
            _HEADER
            + "exact,2026-10-01,work,09:00,15:00\n"
            + "over,2026-10-01,work,09:00,15:01\n"
        ), {"exact": 6.0, "over": 5.0})

    def test_dod_4_rounds_each_shift_before_summing(self):
        self.assertEqual(self.aggregate(
            _HEADER
            + "E001,2026-10-01,work,09:00,09:14\n"
            + "E001,2026-10-02,work,09:00,09:14\n"
        ), {"E001": 0.0})
