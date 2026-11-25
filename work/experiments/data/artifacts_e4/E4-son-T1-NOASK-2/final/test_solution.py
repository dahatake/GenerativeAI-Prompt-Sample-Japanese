import re
import unittest

from solution import monthly_sales

HEADER = "order_id,ordered_at,amount_incl_tax,status\n"


def run(tmp_path, body):
    with open(tmp_path, "w", encoding="utf-8", newline="") as f:
        f.write(HEADER + body)
    return monthly_sales(tmp_path)


class TestMonthlySales(unittest.TestCase):
    def test_expected_values_for_sales_csv(self):
        self.assertEqual(
            monthly_sales("sales.csv"),
            {"2026-01": 16500, "2026-02": 11000, "2026-04": 18700, "2026-05": 7700},
        )

    def test_types_and_key_format(self):
        result = monthly_sales("sales.csv")
        for k, v in result.items():
            self.assertRegex(k, r"^\d{4}-\d{2}$")
            self.assertIs(type(v), int)

    def test_no_empty_month(self):
        self.assertNotIn("2026-03", monthly_sales("sales.csv"))

    def test_cancelled_has_no_effect(self):
        base = "A,2026-01-05T02:15:00Z,1000,completed\n"
        with_cancel = base + "B,2026-01-06T02:15:00Z,99999,cancelled\n"
        self.assertEqual(run("t1.csv", base), run("t2.csv", with_cancel))

    def test_jst_boundary_rows(self):
        r = run("t3.csv", "A,2026-01-31T16:20:00Z,3300,completed\n"
                          "B,2026-04-30T15:30:00Z,7700,completed\n"
                          "C,2026-01-31T14:59:59Z,100,completed\n")
        self.assertEqual(r, {"2026-01": 100, "2026-02": 3300, "2026-05": 7700})

    def test_negative_amount_is_subtracted(self):
        r = run("t4.csv", "A,2026-02-03T05:00:00Z,8800,completed\n"
                          "B,2026-02-14T11:11:00Z,-1100,completed\n")
        self.assertEqual(r, {"2026-02": 7700})

    def test_input_file_unchanged(self):
        with open("sales.csv", "rb") as f:
            before = f.read()
        monthly_sales("sales.csv")
        with open("sales.csv", "rb") as f:
            self.assertEqual(before, f.read())


if __name__ == "__main__":
    unittest.main(verbosity=2)
