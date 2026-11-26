import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from solution import monthly_work_hours


HERE = Path(__file__).parent
HEADER = "employee,date,type,start,end\n"


class MonthlyWorkHoursTests(unittest.TestCase):
    def fixture(self, content):
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=HERE,
            prefix=".shifts-test-", suffix=".csv", delete=False,
        ) as stream:
            path = Path(stream.name)
            self.addCleanup(path.unlink)
            stream.write(content)
        return path

    def test_d1_sample_totals_types_and_order(self):
        result = monthly_work_hours(str(HERE / "shifts.csv"))
        self.assertEqual(list(result.items()), [("E001", 21.25), ("E002", 13.0), ("E003", 8.25)])
        self.assertTrue(all(type(value) is float for value in result.values()))

    def test_d2_break_boundaries_and_maximum_shift(self):
        path = self.fixture(HEADER + (
            "E359,2026-10-01,work,09:00,14:59\n"
            "E360,2026-10-01,work,09:00,15:00\n"
            "E361,2026-10-01,work,09:00,15:01\n"
            "E479,2026-10-01,work,09:00,16:59\n"
            "E480,2026-10-01,work,09:00,17:00\n"
            "E481,2026-10-01,work,09:00,17:01\n"
            "E1439,2026-10-01,work,00:00,23:59\n"
        ))
        self.assertEqual(monthly_work_hours(path), {
            "E359": 5.75, "E360": 6.0, "E361": 5.0, "E479": 6.75,
            "E480": 7.0, "E481": 7.0, "E1439": 22.75,
        })

    def test_d2_round_each_shift_before_summing(self):
        path = self.fixture(HEADER + (
            "E001,2026-10-01,work,09:00,09:29\n"
            "E001,2026-10-02,work,09:00,09:29\n"
        ))
        self.assertEqual(monthly_work_hours(path), {"E001": 0.5})

    def test_d3_overnight_shift_is_attributed_to_start_month(self):
        path = self.fixture(HEADER + (
            "E001,2026-10-31,work,22:00,06:00\n"
            "E002,2026-10-01,paid_leave,,\n"
        ))
        self.assertEqual(monthly_work_hours(path), {"E001": 7.0, "E002": 7.5})

    def test_d3_rejects_multiple_start_months_for_included_types(self):
        for november_row in ("E002,2026-11-01,work,09:00,09:01\n", "E002,2026-11-01,paid_leave,,\n"):
            with self.subTest(row=november_row):
                path = self.fixture(HEADER + "E001,2026-10-31,work,22:00,06:00\n" + november_row)
                with self.assertRaisesRegex(ValueError, r"line 3:.*single calendar month"):
                    monthly_work_hours(path)

    def test_d4_counts_leave_without_reading_punches_and_ignores_other_types(self):
        path = self.fixture(HEADER + (
            "E001,2026-10-01,paid_leave,,\n"
            " E001 ,2026-10-02, paid_leave ,invalid,24:00\n"
            "E002,2026-11-01,holiday,,\n"
            "E003,invalid,WORK,,\n"
        ))
        self.assertEqual(monthly_work_hours(path), {"E001": 15.0})

    def test_d4_reports_line_for_missing_or_invalid_required_values(self):
        for row, field in (
            ("E001,2026-10-01,work,,17:00", "start"),
            ("E001,2026-10-01,work,09:00,", "end"),
            ("E001,2026-02-29,paid_leave,,", "date"),
            (" ,2026-10-01,paid_leave,,", "employee"),
            ("E001,2026-10-01, ,,", "type"),
        ):
            with self.subTest(field=field):
                path = self.fixture(HEADER + "\n" + row + "\n")
                with self.assertRaisesRegex(ValueError, rf"line 3:.*{field}"):
                    monthly_work_hours(path)

    def test_d5_keeps_zero_time_and_returns_empty_dict_without_included_rows(self):
        path = self.fixture(HEADER + "E001,2026-10-01,work,09:00,09:00\n")
        result = monthly_work_hours(path)
        self.assertEqual(result, {"E001": 0.0})
        self.assertIs(type(result["E001"]), float)
        for data in (HEADER, HEADER + "E001,2026-10-01,holiday,,\n"):
            with self.subTest(data=data):
                self.assertEqual(monthly_work_hours(self.fixture(data)), {})

    def test_d6_bom_reordered_headers_extra_fields_and_id_order(self):
        header = "\ufeff\nend,status,employee,type,date,start\n"
        rows = [
            "10:00,approved,1,work,2026-10-01,09:00\n",
            "11:00,rejected,001,work,2026-10-01,09:00\n",
        ]
        for order in (rows, rows[::-1]):
            with self.subTest(order=order):
                path = self.fixture(header + "\n".join(order))
                self.assertEqual(list(monthly_work_hours(path).items()), [("001", 2.0), ("1", 1.0)])

    def test_d6_rejects_invalid_csv_structure_and_time_format(self):
        for content, message in (
            ("", "header"),
            ("E001,2026-10-01,work,00:00,10:00\n", "header"),
            ("employee,date,type,start\n", "header"),
            ("employee,date,type,start,end,end\n", "header"),
            (HEADER + "E001,2026-10-01,work,00:00\n", r"line 2:.*columns"),
            (HEADER + '"E001,2026-10-01,work,00:00,10:00\n', r"line 2:"),
            (HEADER + "E001,2026-10-01,work,00:00,24:00\n", r"line 2:.*end"),
            (HEADER + "E001,2026-10-01,work,09:00:00,10:00\n", r"line 2:.*start"),
        ):
            with self.subTest(content=content):
                with self.assertRaisesRegex(ValueError, message):
                    monthly_work_hours(self.fixture(content))
