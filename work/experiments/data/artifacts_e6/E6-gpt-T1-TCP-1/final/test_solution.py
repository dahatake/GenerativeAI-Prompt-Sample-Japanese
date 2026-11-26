import unittest
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from solution import monthly_sales


HEADER = 'order_id,ordered_at,amount_incl_tax,status\n'


@contextmanager
def fixture(text, encoding='utf-8'):
    path = Path(f'.monthly-sales-{uuid4().hex}.csv')
    with path.open('x', encoding=encoding, newline='') as stream:
        stream.write(text)
    try:
        yield path
    finally:
        path.unlink()


class MonthlySalesTests(unittest.TestCase):
    def test_dod1_sample_dictionary_and_types(self):
        expected = {
            '2026-01': 15000, '2026-02': 10000, '2026-03': 0,
            '2026-04': 17000, '2026-05': 7000,
        }
        result = monthly_sales('sales.csv')
        self.assertIs(type(result), dict)
        self.assertEqual(result, expected)
        for month, amount in result.items():
            self.assertIs(type(month), str)
            self.assertIs(type(amount), int)

    def test_dod2_jst_boundary_status_and_gap(self):
        text = HEADER + (
            'A,2025-12-30T00:00:00Z,1100,cancelled\n'
            'B,2026-01-31T14:59:59Z,110,completed\n'
            'C,2026-01-31T15:00:00Z,220,completed\n'
            'D,2026-02-14T11:11:00Z,-110,completed\n'
            'E,2026-03-10T00:00:00Z,1100,cancelled\n'
            'F,2026-04-30T15:30:00Z,330,completed\n'
            'G,2026-06-05T00:00:00Z,1100,cancelled\n'
        )
        with fixture(text) as path:
            self.assertEqual(monthly_sales(path), {
                '2026-01': 100, '2026-02': 100, '2026-03': 0,
                '2026-04': 0, '2026-05': 300,
            })

    def test_dod2_historical_tokyo_month_boundaries(self):
        for utc, month in [
            ('1887-12-31T14:45:00Z', '1888-01'),
            ('1951-05-31T14:30:00Z', '1951-06'),
        ]:
            with self.subTest(utc=utc), fixture(HEADER + f'A,{utc},11,completed\n') as path:
                self.assertEqual(monthly_sales(path), {month: 10})

    def test_dod3_rounds_signed_month_sums_exactly(self):
        text = HEADER + (
            'A,2026-01-01T00:00:00Z,6,completed\n'
            'B,2026-01-02T00:00:00Z,6,completed\n'
            'C,2026-02-01T00:00:00Z,-6,completed\n'
            'D,2026-02-02T00:00:00Z,-6,completed\n'
            'E,2026-03-01T00:00:00Z,-6,completed\n'
            f'F,2026-04-01T00:00:00Z,{11 * 10**31 + 6},completed\n'
        )
        with fixture(text) as path:
            self.assertEqual(monthly_sales(path), {
                '2026-01': 11, '2026-02': -11, '2026-03': -5,
                '2026-04': 10**32 + 5,
            })

    def test_dod4_header_only_and_filtered_out(self):
        for text in [HEADER, HEADER + 'A,2026-01-01T00:00:00Z,1100,cancelled\n']:
            with self.subTest(text=text), fixture(text) as path:
                self.assertEqual(monthly_sales(path), {})

    def test_dod4_retains_zero_sum_month(self):
        text = HEADER + 'A,2026-01-01T00:00:00Z,6,completed\nB,2026-01-02T00:00:00Z,-6,completed\n'
        with fixture(text) as path:
            self.assertEqual(monthly_sales(path), {'2026-01': 0})

    def test_dod5_malformed_inputs_raise_value_error(self):
        cases = {
            'missing header': 'order_id,ordered_at,amount_incl_tax\n',
            'duplicate required header': HEADER.strip() + ',status\n',
            'missing field': HEADER + 'A,2026-01-01T00:00:00Z,6\n',
            'empty field': HEADER + 'A,2026-01-01T00:00:00Z,,completed\n',
            'impossible date in excluded row': HEADER + 'A,2026-02-30T00:00:00Z,6,cancelled\n',
            'noncanonical timestamp': HEADER + 'A,2026-01-01T00:00:00+00:00,6,completed\n',
            'date outside JST range': HEADER + 'A,9999-12-31T15:00:00Z,6,completed\n',
            'decimal amount': HEADER + 'A,2026-01-01T00:00:00Z,1.5,completed\n',
            'malformed quoting': HEADER + '"A,2026-01-01T00:00:00Z,6,completed\n',
        }
        for case, text in cases.items():
            with self.subTest(case=case), fixture(text) as path:
                with self.assertRaises(ValueError):
                    monthly_sales(path)

    def test_dod5_bom_column_order_and_repeated_order(self):
        text = (
            'status,ordered_at,extra,amount_incl_tax,order_id\n'
            'completed,2026-01-01T00:00:00Z,"extra, ignored",+11,A\n\n'
            'completed,2026-01-01T00:00:00Z,"extra, ignored",+11,A\n'
        )
        with fixture(text, encoding='utf-8-sig') as path:
            self.assertEqual(monthly_sales(path), {'2026-01': 20})

    def test_dod5_sample_csv_is_unchanged(self):
        path = Path('sales.csv')
        before = path.read_bytes()
        mtime_before = path.stat().st_mtime_ns
        monthly_sales(path)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(path.stat().st_mtime_ns, mtime_before)
        self.assertEqual(sha256(before).hexdigest(),
                         'c6d43f26291c5523e093222ef4167efc5f3e1cd037d5852e3da0b4edb9bd94ea')
