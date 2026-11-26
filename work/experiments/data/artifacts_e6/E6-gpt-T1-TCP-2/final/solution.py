import csv
import re
from datetime import datetime, timedelta, timezone


_JST = timezone(timedelta(hours=9))
_TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
_AMOUNT = re.compile(r"[+-]?[0-9]+")
_REQUIRED_COLUMNS = ("ordered_at", "amount_incl_tax", "status")


def monthly_sales(path):
    """Sum completed orders by JST month, filling interior gaps with zero."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as source:
        rows = csv.reader(source, strict=True)
        try:
            header = next((row for row in rows if row), [])
            if not set(_REQUIRED_COLUMNS).issubset(header):
                raise ValueError("Missing required CSV columns")
            if len(set(header)) != len(header):
                raise ValueError("Duplicate CSV column names")
            date_col, amount_col, status_col = map(header.index, _REQUIRED_COLUMNS)

            for row in rows:
                if not row:
                    continue
                if len(row) != len(header):
                    raise ValueError(f"Wrong number of columns on line {rows.line_num}")
                status = row[status_col]
                if status not in {"completed", "cancelled"}:
                    raise ValueError(f"Unknown status on line {rows.line_num}")
                timestamp, amount = row[date_col], row[amount_col]
                if not _TIMESTAMP.fullmatch(timestamp) or not _AMOUNT.fullmatch(amount):
                    raise ValueError(f"Invalid timestamp or amount on line {rows.line_num}")
                try:
                    utc = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(
                        tzinfo=timezone.utc
                    )
                    local = utc.astimezone(_JST)
                    value = int(amount)
                except (ValueError, OverflowError) as error:
                    raise ValueError(f"Invalid timestamp or amount on line {rows.line_num}") from error
                if status == "completed":
                    month = local.year * 12 + local.month - 1
                    totals[month] = totals.get(month, 0) + value
        except csv.Error as error:
            raise ValueError(f"Invalid CSV on line {rows.line_num}") from error

    if not totals:
        return {}

    result = {}
    for month in range(min(totals), max(totals) + 1):
        year, month_index = divmod(month, 12)
        result[f"{year:04d}-{month_index + 1:02d}"] = totals.get(month, 0)
    return result
