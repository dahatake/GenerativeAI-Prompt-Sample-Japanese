import unittest
from pathlib import Path

from solution import validate_invoice_id

SAMPLES = [
    line.strip()
    for line in Path(__file__).with_name("samples.txt").read_text(encoding="utf-8").splitlines()
    if line.startswith("INV-")
]

INVALID = [
    "",
    "INV-202601-001",
    "INV-202601-00001",
    "INV-202613-0001",
    "INV-202600-0001",
    "inv-202601-0001",
    " INV-202601-0001",
    "INV-202601-0001 ",
    "INV-202601-0001\n",
    "INV-２０２６０１-０００１",
    "INV202601-0001",
]


class ValidateInvoiceId(unittest.TestCase):
    def test_dod1_samples_valid(self):
        self.assertEqual(len(SAMPLES), 4)
        for s in SAMPLES:
            self.assertIs(validate_invoice_id(s), True, s)

    def test_dod2_invalid_strings(self):
        for s in INVALID:
            self.assertIs(validate_invoice_id(s), False, repr(s))

    def test_dod3_non_str_no_exception(self):
        for v in (None, 123, b"INV-202601-0001", ["INV-202601-0001"]):
            self.assertIs(validate_invoice_id(v), False, repr(v))

    def test_dod4_returns_bool(self):
        for v in SAMPLES + INVALID + [None]:
            self.assertIsInstance(validate_invoice_id(v), bool)

    def test_boundaries(self):
        for m in range(1, 13):
            self.assertIs(validate_invoice_id(f"INV-2026{m:02d}-0000"), True)
        self.assertIs(validate_invoice_id("INV-209912-9999"), True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
