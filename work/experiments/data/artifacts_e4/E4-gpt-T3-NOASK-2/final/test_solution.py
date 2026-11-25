import unittest
from pathlib import Path

from solution import validate_invoice_id


class Stringifiable:
    def __str__(self):
        return "INV-202601-0001"

    def __repr__(self):
        return "Stringifiable()"


class InvoiceIdTests(unittest.TestCase):
    def assert_validity(self, values, expected):
        for value in values:
            with self.subTest(value=value):
                actual = validate_invoice_id(value)
                self.assertIs(actual, expected)
                print(f"{ascii(value)}: expected={expected}, actual={actual}")

    def test_examples(self):
        lines = Path(__file__).with_name("samples.txt").read_text(encoding="utf-8-sig").splitlines()
        _, *samples = lines
        self.assertEqual(len(samples), 4)
        self.assert_validity(samples, True)

    def test_valid_boundaries_not_in_examples(self):
        self.assert_validity(("INV-000101-0001", "INV-999912-9999"), True)

    def test_invalid_calendar_and_sequence_values(self):
        self.assert_validity(
            ("INV-202600-0001", "INV-202613-0001", "INV-000001-0001", "INV-202601-0000"),
            False,
        )

    def test_noncanonical_spellings(self):
        self.assert_validity(
            (
                "INV-20261-0001",
                "INV-2026010-0001",
                "INV-202601-001",
                "INV-202601-00001",
                "INV-202601_0001",
                "inv-202601-0001",
                "INV-２０２６０１-0001",
                "INV-202601-０００１",
                " INV-202601-0001",
                "INV-202601-0001 ",
                "INV-202601-0001\n",
                "",
            ),
            False,
        )

    def test_non_strings_are_not_coerced(self):
        self.assert_validity((None, 2026010001, True, b"INV-202601-0001", Stringifiable()), False)
