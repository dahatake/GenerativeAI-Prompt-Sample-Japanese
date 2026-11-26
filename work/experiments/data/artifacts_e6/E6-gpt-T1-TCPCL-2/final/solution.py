import csv
import re
from collections import defaultdict
from datetime import datetime, timedelta


_JST_OFFSET = timedelta(hours=9)
_TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])"
)
_INTEGER = re.compile(r"[+-]?[0-9]+")


def _field(row, index):
    return row[index].strip() if index < len(row) else ""


def _jst_month(value):
    if not _TIMESTAMP.fullmatch(value):
        raise ValueError("expected an ISO 8601 timestamp with an offset")
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    date = datetime.fromisoformat(value)
    # Apply the offset difference directly so no intermediate UTC date can overflow.
    date = date.replace(tzinfo=None) + (_JST_OFFSET - date.utcoffset())
    return date.year * 12 + date.month - 1


def _month_key(index):
    year, month = divmod(index, 12)
    return f"{year:04d}-{month + 1:02d}"


def _net_amount(gross):
    # Divide by 1.1 exactly, then round the magnitude before restoring the sign.
    amount, remainder = divmod(abs(gross) * 10, 11)
    if 2 * remainder >= 11:
        amount += 1
    return -amount if gross < 0 else amount


def monthly_sales(path):
    """Return tax-exclusive sales by JST month, including intervening empty months."""
    totals = defaultdict(int)
    with open(path, encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source, strict=True)
        rows = (row for row in reader if row)
        try:
            header = next(rows, [])
            required = ("ordered_at", "amount_incl_tax", "status")
            if any(name not in header for name in required):
                raise ValueError("CSV requires ordered_at, amount_incl_tax and status columns")
            date_column, amount_column, status_column = map(header.index, required)

            for row in rows:
                status = _field(row, status_column)
                if not status:
                    raise ValueError(f"CSV line {reader.line_num}: missing status")
                if status != "completed":
                    continue

                ordered_at = _field(row, date_column)
                amount = _field(row, amount_column)
                try:
                    month = _jst_month(ordered_at)
                except (ValueError, OverflowError) as error:
                    raise ValueError(f"CSV line {reader.line_num}: invalid ordered_at") from error
                if not _INTEGER.fullmatch(amount):
                    raise ValueError(f"CSV line {reader.line_num}: invalid amount_incl_tax")
                totals[month] += int(amount)
        except csv.Error as error:
            raise ValueError(f"CSV line {reader.line_num}: invalid CSV") from error

    if not totals:
        return {}
    return {
        _month_key(month): _net_amount(totals.get(month, 0))
        for month in range(min(totals), max(totals) + 1)
    }
