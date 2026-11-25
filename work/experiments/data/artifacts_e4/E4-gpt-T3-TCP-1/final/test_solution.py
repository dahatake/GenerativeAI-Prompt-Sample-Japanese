from pathlib import Path
import unittest
from unittest.mock import Mock

from solution import validate_invoice_id


class TestInvoiceId(unittest.TestCase):
    def assert_validation_cases(self, cases):
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertIs(validate_invoice_id(value), expected)

    def test_accepts_all_four_sample_ids(self):
        lines = Path(__file__).with_name("samples.txt").read_text(encoding="utf-8-sig")
        _, *samples = lines.splitlines()
        self.assertEqual(len(samples), 4)
        self.assert_validation_cases((sample, True) for sample in samples)

    def test_rejects_non_strings_without_coercion(self):
        values = (None, 2026010001, b"INV-202601-0001", Mock(spec=str))
        self.assert_validation_cases((value, False) for value in values)

    def test_rejects_malformed_ids(self):
        values = (
            "", "INV-20261-0001", "INV-2026001-0001",
            "INV-202601-001", "INV-202601-00001", "INV-202601/0001",
            "INV-202601\u20130001", "INV-\uff1202601-0001", "INV-202601-\uff10001",
            "INV-202601-0001\n", "INV-202601- 001", "BIL-202601-0001",
        )
        self.assert_validation_cases((value, False) for value in values)

    def test_prefix_is_case_sensitive_and_whitespace_is_not_trimmed(self):
        values = (
            "inv-202601-0001", "Inv-202601-0001", " INV-202601-0001",
            "INV-202601-0001 ", "\tINV-202601-0001", "INV-202601-0001\t",
        )
        self.assert_validation_cases((value, False) for value in values)

    def test_year_and_month_boundaries(self):
        self.assert_validation_cases((
            ("INV-202001-0010", True), ("INV-209912-0010", True),
            ("INV-000001-0001", False), ("INV-199912-0001", False),
            ("INV-201912-0001", False), ("INV-210001-0001", False),
            ("INV-202600-0001", False), ("INV-202613-0001", False),
        ))

    def test_serial_number_boundaries(self):
        self.assert_validation_cases((
            ("INV-202601-0000", False), ("INV-202601-0001", True),
            ("INV-202601-9999", True),
        ))
