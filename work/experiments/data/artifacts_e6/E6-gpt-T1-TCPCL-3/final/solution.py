import csv
import re
from collections import defaultdict
from datetime import datetime, timedelta


_JST_OFFSET = timedelta(hours=9)
_REQUIRED = ("ordered_at", "amount_incl_tax", "status")
_TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])"
)
_INTEGER = re.compile(r"[+-]?[0-9]+")


def _jst_month(value: str) -> int:
    if not _TIMESTAMP.fullmatch(value):
        raise ValueError("invalid ordered_at format")
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    offset = stamp.utcoffset()
    assert offset is not None
    # Apply the offset difference directly: an intermediate UTC date may be out of range.
    jst = stamp.replace(tzinfo=None) + (_JST_OFFSET - offset)
    return jst.year * 12 + jst.month - 1


def _net_amount(gross: int) -> int:
    rounded, remainder = divmod(abs(gross) * 10, 11)
    if 2 * remainder >= 11:
        rounded += 1
    return -rounded if gross < 0 else rounded


def monthly_sales(path) -> dict[str, int]:
    """Return rounded net sales by JST month, including interior months at zero."""
    gross_by_month: dict[int, int] = defaultdict(int)
    with open(path, encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source, strict=True)
        try:
            header = next((fields for fields in reader if fields), [])
            if any(header.count(name) != 1 for name in _REQUIRED):
                raise ValueError("expected exactly one of each column: " + ", ".join(_REQUIRED))
            date_col, amount_col, status_col = (header.index(name) for name in _REQUIRED)
            for row in reader:
                if not row:
                    continue
                if len(row) <= max(date_col, amount_col, status_col):
                    raise ValueError(f"line {reader.line_num}: missing required field")
                date, amount, status = (row[i].strip() for i in (date_col, amount_col, status_col))
                if not date or not amount or not status:
                    raise ValueError(f"line {reader.line_num}: blank required field")
                if not _INTEGER.fullmatch(amount):
                    raise ValueError(f"line {reader.line_num}: invalid integer amount")
                try:
                    month = _jst_month(date)
                except (ValueError, OverflowError) as error:
                    raise ValueError(f"line {reader.line_num}: invalid ordered_at") from error
                if status == "completed":
                    gross_by_month[month] += int(amount)
        except csv.Error as error:
            raise ValueError(f"line {reader.line_num}: invalid CSV") from error

    if not gross_by_month:
        return {}

    result: dict[str, int] = {}
    for month in range(min(gross_by_month), max(gross_by_month) + 1):
        year, month_index = divmod(month, 12)
        result[f"{year:04d}-{month_index + 1:02d}"] = _net_amount(gross_by_month.get(month, 0))
    return result
