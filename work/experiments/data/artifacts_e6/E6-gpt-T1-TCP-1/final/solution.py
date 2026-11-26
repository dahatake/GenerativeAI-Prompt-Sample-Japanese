import csv
import re
from collections import defaultdict
from datetime import datetime, timedelta


_REQUIRED_COLUMNS = ("order_id", "ordered_at", "amount_incl_tax", "status")
_UTC_TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
_INTEGER = re.compile(r"[+-]?[0-9]+")
_JST = timedelta(hours=9)
_JDT = timedelta(hours=10)
# Asia/Tokyo's UTC transitions, kept local so no system tz database is required.
_TOKYO_TRANSITIONS = (
    (datetime(1887, 12, 31, 15), _JST),
    (datetime(1948, 5, 1, 15), _JDT),
    (datetime(1948, 9, 11, 15), _JST),
    (datetime(1949, 4, 2, 15), _JDT),
    (datetime(1949, 9, 10, 15), _JST),
    (datetime(1950, 5, 6, 15), _JDT),
    (datetime(1950, 9, 9, 15), _JST),
    (datetime(1951, 5, 5, 15), _JDT),
    (datetime(1951, 9, 8, 15), _JST),
)


def _tokyo_month(utc):
    for starts_at, offset in reversed(_TOKYO_TRANSITIONS):
        if utc >= starts_at:
            break
    else:
        offset = timedelta(hours=9, minutes=18, seconds=59)
    try:
        local = utc + offset
    except OverflowError as error:
        raise ValueError("ordered_at is outside the representable Tokyo date range") from error
    return local.year * 12 + local.month - 1


def _exclude_tax(gross):
    rounded, remainder = divmod(abs(gross) * 10, 11)
    if remainder * 2 >= 11:
        rounded += 1
    return -rounded if gross < 0 else rounded


def monthly_sales(path):
    """Return tax-exclusive monthly totals for completed orders in Tokyo time."""
    totals = defaultdict(int)
    with open(path, encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source, strict=True)
        try:
            header = next(reader, [])
            if any(header.count(name) != 1 for name in _REQUIRED_COLUMNS):
                raise ValueError("CSV must contain each required column exactly once")
            indices = [header.index(name) for name in _REQUIRED_COLUMNS]
            last_required_index = max(indices)
            for row in reader:
                if not row:
                    continue
                if len(row) <= last_required_index:
                    raise ValueError(f"line {reader.line_num}: missing required value")
                order_id, ordered_at, amount, status = (row[index] for index in indices)
                if not order_id.strip() or not status.strip():
                    raise ValueError(f"line {reader.line_num}: missing order_id or status")
                if not _UTC_TIMESTAMP.fullmatch(ordered_at):
                    raise ValueError(f"line {reader.line_num}: invalid ordered_at")
                if not _INTEGER.fullmatch(amount):
                    raise ValueError(f"line {reader.line_num}: invalid amount_incl_tax")
                utc = datetime.fromisoformat(ordered_at[:-1])
                gross = int(amount)
                if status == "completed":
                    totals[_tokyo_month(utc)] += gross
        except csv.Error as error:
            raise ValueError(f"line {reader.line_num}: invalid CSV") from error

    result = {}
    if totals:
        for month_index in range(min(totals), max(totals) + 1):
            year, month = divmod(month_index, 12)
            result[f"{year:04d}-{month + 1:02d}"] = _exclude_tax(totals.get(month_index, 0))
    return result
