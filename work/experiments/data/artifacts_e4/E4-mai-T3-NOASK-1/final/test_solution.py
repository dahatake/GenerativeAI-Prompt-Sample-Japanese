import unittest

from solution import validate_invoice_id


class ValidateInvoiceIdTests(unittest.TestCase):
    def test_samples(self):
        samples = (
            "INV-202601-0001",
            "INV-202601-0002",
            "INV-202512-0347",
            "INV-202603-1200",
        )
        for value in samples:
            with self.subTest(value=value):
                self.assertIs(validate_invoice_id(value), True)

    def test_valid_boundaries(self):
        for value in ("INV-000001-0001", "INV-999912-9999"):
            with self.subTest(value=value):
                self.assertIs(validate_invoice_id(value), True)

    def test_invalid_months(self):
        for value in ("INV-202600-0001", "INV-202613-0001", "INV-2026A1-0001"):
            with self.subTest(value=value):
                self.assertIs(validate_invoice_id(value), False)

    def test_invalid_sequence(self):
        for value in ("INV-202601-0000", "INV-202601-10000", "INV-202601-１２３４"):
            with self.subTest(value=value):
                self.assertIs(validate_invoice_id(value), False)

    def test_invalid_format(self):
        for value in (
            "inv-202601-0001",
            "INV-2026-01-0001",
            "INV-2026010001",
            "INV-202601-0001-",
            "INV-２０２６０１-0001",
            " INV-202601-0001",
            "INV-202601-0001 ",
            "INV-202601-0001\n",
        ):
            with self.subTest(value=value):
                self.assertIs(validate_invoice_id(value), False)

    def test_invalid_types(self):
        for value in (None, 2026010001, 2026010001.0, True, ["INV-202601-0001"]):
            with self.subTest(value=value):
                self.assertIs(validate_invoice_id(value), False)


if __name__ == "__main__":
    unittest.main()
