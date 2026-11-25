import unittest
from pathlib import Path

from solution import validate_invoice_id


class ValidateInvoiceIdTests(unittest.TestCase):
    def test_imported_function_is_callable(self):
        self.assertTrue(callable(validate_invoice_id))

    def test_issued_samples_return_true(self):
        path = Path(__file__).with_name("samples.txt")
        values = path.read_text(encoding="utf-8-sig").splitlines()[1:]
        self.assertEqual(len(values), 4)
        for value in values:
            with self.subTest(value=value):
                self.assertIs(validate_invoice_id(value), True)

    def test_valid_range_endpoints_return_true(self):
        for value in ("INV-000101-0001", "INV-999912-9999"):
            with self.subTest(value=value):
                self.assertIs(validate_invoice_id(value), True)

    def test_invalid_inputs_return_false(self):
        for value in (
            "INV-000001-0001",
            "INV-202600-0001",
            "INV-202613-0001",
            "INV-202601-0000",
            "INV-202601-001",
            "INV-202601-10000",
            "ABC-202601-0001",
            "INV_202601-0001",
            "INV-２０２６０１-0001",
            "inv-202601-0001",
            " INV-202601-0001 ",
            "INV-202601-0001\n",
            "",
            None,
            123,
        ):
            with self.subTest(value=value):
                self.assertIs(validate_invoice_id(value), False)


if __name__ == "__main__":
    unittest.main()
