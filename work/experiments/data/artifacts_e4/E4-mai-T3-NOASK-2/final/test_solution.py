import pathlib
import unittest

from solution import validate_invoice_id


class ValidateInvoiceIdTests(unittest.TestCase):
    def test_samples_are_valid(self):
        samples_path = pathlib.Path(__file__).with_name("samples.txt")
        lines = [line.strip() for line in samples_path.read_text(encoding="utf-8").splitlines()]
        samples = [line for line in lines if line and not line.startswith("最近")]
        self.assertEqual(len(samples), 4)
        for value in samples:
            with self.subTest(value=value):
                self.assertIs(validate_invoice_id(value), True)

    def test_invalid_shapes_and_types(self):
        invalid = [
            "",
            "INV-20261-0001",
            "INV-2026010-0001",
            "INV_202601-0001",
            "INV/202601/0001",
            None,
            2026010001,
            " INV-202601-0001",
            "INV-202601-0001 ",
            "inv-202601-0001",
            "ＩＮＶ－２０２６０１－０００１",
        ]
        for value in invalid:
            with self.subTest(value=value):
                self.assertIs(validate_invoice_id(value), False)

    def test_month_boundary_and_tail(self):
        invalid = [
            "INV-202600-0001",
            "INV-202613-0001",
            "INV-202601-000",
            "INV-202601-00010",
            "INV-202601-000x",
            "INV-202601-0001-",
        ]
        for value in invalid:
            with self.subTest(value=value):
                self.assertIs(validate_invoice_id(value), False)

    def test_month_year_and_serial_edges(self):
        valid = [
            "INV-000001-0000",
            "INV-999912-9999",
            "INV-202601-0347",
            "INV-202512-1200",
        ]
        for value in valid:
            with self.subTest(value=value):
                self.assertIs(validate_invoice_id(value), True)

    def test_all_results_are_exact_bool(self):
        values = ["INV-202601-0001", "INV-202600-0001", None, 123]
        for value in values:
            with self.subTest(value=value):
                self.assertIs(type(validate_invoice_id(value)), bool)


if __name__ == "__main__":
    unittest.main(verbosity=2)
