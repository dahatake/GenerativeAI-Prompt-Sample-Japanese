import unittest
from pathlib import Path

from solution import validate_invoice_id


class TestInvoiceId(unittest.TestCase):
    def check_cases(self, condition, cases):
        for value, expected in cases:
            with self.subTest(value=value):
                actual = validate_invoice_id(value)
                print(f"{condition} {ascii(value)}: expected={expected}, "
                      f"actual={actual}, type={type(actual).__name__}")
                self.assertIs(type(actual), bool)
                self.assertIs(actual, expected)

    def test_d1_all_published_examples(self):
        samples = Path(__file__).with_name("samples.txt")
        values = samples.read_text(encoding="utf-8-sig").splitlines()[1:]
        self.assertEqual(len(values), 4)
        self.check_cases("D1", [(value, True) for value in values])

    def test_d2_independent_range_boundaries(self):
        self.check_cases("D2", [
            ("INV-201906-1234", False),
            ("INV-202006-1234", True),
            ("INV-209906-1234", True),
            ("INV-210006-1234", False),
            ("INV-202600-1234", False),
            ("INV-202601-1234", True),
            ("INV-202612-1234", True),
            ("INV-202613-1234", False),
            ("INV-202606-0000", False),
            ("INV-202606-0001", True),
            ("INV-202606-9999", True),
        ])

    def test_d3_rejects_malformed_and_non_string_values(self):
        invalid = [
            "INV-20261-0001", "INV-2026001-0001",
            "INV-202601-001", "INV-202601-10000",
            "BIL-202601-0001", "inv-202601-0001", "InV-202601-0001",
            "INV/202601-0001", "INV-202601\u20100001",
            "INV-\uff1202601-0001",
            "INV-202601-000\u0661",
            " INV-202601-0001", "INV-202601-0001\t", "INV-202601-0001\n",
            "INV-202601-00 1", "", None, 202601, b"INV-202601-0001",
        ]
        self.check_cases("D3", [(value, False) for value in invalid])
