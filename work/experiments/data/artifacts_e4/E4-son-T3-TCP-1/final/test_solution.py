import pathlib
import unittest

from solution import validate_invoice_id as v


class T(unittest.TestCase):
    def test_samples_true(self):
        lines = pathlib.Path("samples.txt").read_text(encoding="utf-8").splitlines()
        ids = [l for l in lines if l.startswith("INV-")]
        self.assertEqual(len(ids), 4)
        for i in ids:
            self.assertIs(v(i), True, i)

    def test_year_month_range(self):
        for ok in ["INV-202001-0001", "INV-209912-9999", "INV-202412-0001"]:
            self.assertIs(v(ok), True, ok)
        for ng in ["INV-201912-0001", "INV-200001-0001", "INV-210001-0001",
                   "INV-202600-0001", "INV-202613-0001", "INV-202601-0000"]:
            self.assertIs(v(ng), False, ng)

    def test_sequence(self):
        self.assertIs(v("INV-202601-9999"), True)
        for ng in ["INV-202601-000", "INV-202601-00001", "INV-202601-0000"]:
            self.assertIs(v(ng), False, ng)

    def test_strict_format(self):
        for ng in ["INX-202601-0001", "INV202601-0001", "INV-202601_0001", "INV-2026010001",
                   "inv-202601-0001", "INV-202601-0001\n", " INV-202601-0001",
                   "INV-202601-0001 ", "INV-２０２６０１-０００１", "INV-202601-000a", ""]:
            self.assertIs(v(ng), False, repr(ng))

    def test_non_str(self):
        for x in [None, 202601, 1.5, b"INV-202601-0001", [], ("INV-202601-0001",), object()]:
            self.assertIs(v(x), False, repr(x))


if __name__ == "__main__":
    unittest.main(verbosity=2)
