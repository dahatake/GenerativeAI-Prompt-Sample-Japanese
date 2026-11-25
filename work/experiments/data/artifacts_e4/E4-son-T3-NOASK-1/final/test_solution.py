import pathlib
import unittest

from solution import validate_invoice_id

SAMPLES = pathlib.Path(__file__).with_name("samples.txt")


class ValidateInvoiceId(unittest.TestCase):
    def test_dod1_samples_true(self):
        ids = [l.strip() for l in SAMPLES.read_text(encoding="utf-8").splitlines() if l.startswith("INV-")]
        self.assertEqual(len(ids), 4)
        for s in ids:
            self.assertIs(validate_invoice_id(s), True, s)

    def test_dod2_invalid_strings_false(self):
        bad = [
            "INV-202600-0001", "INV-202613-0001", "INV-202601-0000",
            "INV-202601-001", "INV-202601-00001",
            "inv-202601-0001", " INV-202601-0001", "INV-202601-0001 ", "INV-202601-0001\n",
            "INV-２０２６０１-０００１", "INV202601-0001", "INV-2026010001", "",
        ]
        for s in bad:
            self.assertIs(validate_invoice_id(s), False, repr(s))

    def test_dod3_non_str_false_no_exception(self):
        for v in [None, 123, b"INV-202601-0001", [], {}, 1.5, True]:
            self.assertIs(validate_invoice_id(v), False, repr(v))

    def test_dod4_return_type_is_bool(self):
        for v in ["INV-202601-0001", "x", None]:
            self.assertIs(type(validate_invoice_id(v)), bool)

    def test_boundaries_true(self):
        for s in ["INV-202601-9999", "INV-202612-0001", "INV-000001-0001"]:
            self.assertIs(validate_invoice_id(s), True, s)


if __name__ == "__main__":
    unittest.main(verbosity=2)
