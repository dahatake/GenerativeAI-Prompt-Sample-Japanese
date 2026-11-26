import unittest
from pathlib import Path
from uuid import uuid4

from solution import monthly_work_hours

_DIRECTORY = Path(__file__).resolve().parent
_HEADER = "employee,date,type,start,end\n"


class MonthlyWorkHoursTests(unittest.TestCase):
    def setUp(self):
        self.fixture = _DIRECTORY / f".test_shifts_{uuid4().hex}.csv"
        with self.fixture.open("x", encoding="utf-8"):
            pass
        self.addCleanup(self.fixture.unlink, missing_ok=True)

    def aggregate(self, body, *, header=_HEADER, encoding="utf-8"):
        self.fixture.write_text(header + body, encoding=encoding)
        return monthly_work_hours(self.fixture)

    def test_d1_sample_hours_type_order_and_read_only(self):
        sample = _DIRECTORY / "shifts.csv"
        original = sample.read_bytes()
        totals = monthly_work_hours(str(sample))
        self.assertIs(type(totals), dict)
        self.assertEqual(totals, {"E001": 21.25, "E002": 13.0, "E003": 8.25})
        self.assertEqual(list(totals), ["E001", "E002", "E003"])
        for total in totals.values():
            self.assertIs(type(total), float)
        self.assertEqual(sample.read_bytes(), original)

    def test_d2_month_end_overnight_and_mixed_months(self):
        october = "A,2026-10-31,work,22:00,06:00\nA,2026-10-01,work,00:00,01:00\n"
        self.assertEqual(self.aggregate(october), {"A": 8.0})
        for other_date in ("2026-11-01", "2027-10-01"):
            for extra in ("work,00:00,01:00", "paid_leave,,"):
                with self.subTest(other_date=other_date, extra=extra):
                    with self.assertRaises(ValueError):
                        self.aggregate(october + f"A,{other_date},{extra}\n")

    def test_d3_break_threshold_and_rounding(self):
        cases = {"05:50": 5.75, "06:00": 6.0, "06:01": 5.0, "08:00": 7.0, "08:01": 7.0}
        rows = "".join(f"{end},2026-10-01,work,00:00,{end}\n" for end in cases)
        self.assertEqual(self.aggregate(rows), cases)

    def test_d4_leave_without_times_and_header_only(self):
        rows = (
            "A,2026-10-01,paid_leave,,\n"
            "A,2026-10-02,paid_leave,ignored,ignored\n"
            "B,2026-10-01,paid_leave,,\n"
        )
        self.assertEqual(self.aggregate(rows), {"A": 15.0, "B": 7.5})
        self.assertEqual(self.aggregate(""), {})

    def test_d5_zero_and_maximum_shift(self):
        rows = (
            "equal,2026-10-01,work,08:00,08:00\n"
            "short,2026-10-01,work,08:00,08:14\n"
            "maximum,2026-10-01,work,00:00,23:59\n"
        )
        totals = self.aggregate(rows)
        self.assertEqual(totals, {"equal": 0.0, "short": 0.0, "maximum": 22.75})
        self.assertIs(type(totals["equal"]), float)
        self.assertIs(type(totals["short"]), float)

    def test_d6_invalid_csv_and_values(self):
        for header in ("", "employee,date,type,start\n", "employee,date,type,start,end,date\n"):
            with self.subTest(header=header):
                with self.assertRaises(ValueError):
                    self.aggregate("", header=header)
        valid = "A,2026-10-01,work,00:00,01:00\n"
        bad_rows = (
            ",2026-10-01,work,09:00,18:00",
            "B,,work,09:00,18:00",
            "B,2026-10-01,,09:00,18:00",
            "B,2026-10-01,work,,18:00",
            "B,2026-10-01,work,09:00,",
            "B,2026-10-01,work,09:00,24:00",
            "B,2026-10-01,work,9:00,18:00",
            "B,2026-10-1,work,09:00,18:00",
            "B,2026-02-29,work,09:00,18:00",
            "B,2026-10-01,WORK,09:00,18:00",
            "B,2026-10-01,work,09:00",
            "B,2026-10-01,work,09:00,18:00,extra",
            '"B,2026-10-01,work,09:00,18:00',
        )
        for row in bad_rows:
            with self.subTest(row=row):
                with self.assertRaises(ValueError):
                    self.aggregate(valid + row + "\n")

    def test_d6_missing_path_propagates_io_error(self):
        self.fixture.unlink()
        with self.assertRaises(FileNotFoundError):
            monthly_work_hours(self.fixture)

    def test_d7_id_order_and_round_each_shift_before_summing(self):
        rows = (
            "2,2026-10-01,work,09:00,10:00\n"
            "001,2026-10-01,work,09:00,10:14\n"
            "001,2026-10-02,work,09:00,10:14\n"
        )
        totals = self.aggregate(rows)
        self.assertEqual(list(totals), ["001", "2"])
        self.assertEqual(totals, {"001": 2.0, "2": 1.0})

    def test_d8_bom_reordered_header_ignored_status_and_duplicate_rows(self):
        header = "\nstatus,end,employee,type,start,date\n"
        row = 'rejected, 10:00 ," A,1 ", work , 09:00 , 2026-10-01 \n'
        self.assertEqual(self.aggregate(row + "\n" + row, header=header, encoding="utf-8-sig"), {"A,1": 2.0})
