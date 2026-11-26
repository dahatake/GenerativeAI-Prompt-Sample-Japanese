import csv
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from os import PathLike

_REQUIRED_COLUMNS = {"ordered_at", "amount_incl_tax", "status"}
_UTC_TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
_INTEGER_AMOUNT = re.compile(r"[+-]?[0-9]+")
_JST = timezone(timedelta(hours=9))


def monthly_sales(path: str | PathLike[str]) -> dict[str, int]:
    """Return monthly net sales for completed orders, grouped by JST month."""
    gross_by_month: dict[int, int] = defaultdict(int)
    with open(path, encoding="utf-8-sig", newline="") as source:
        rows = csv.DictReader(source)
        missing = _REQUIRED_COLUMNS.difference(rows.fieldnames or ())
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        for row in rows:
            status = row["status"]
            if status is None or not status.strip():
                raise ValueError(f"Missing status at CSV line {rows.line_num}")
            if status != "completed":
                continue

            timestamp = row["ordered_at"]
            amount = row["amount_incl_tax"]
            if timestamp is None or not _UTC_TIMESTAMP.fullmatch(timestamp):
                raise ValueError(f"Invalid ordered_at at CSV line {rows.line_num}")
            if amount is None or not _INTEGER_AMOUNT.fullmatch(amount):
                raise ValueError(f"Invalid amount_incl_tax at CSV line {rows.line_num}")
            try:
                local_date = datetime.fromisoformat(timestamp[:-1] + "+00:00").astimezone(_JST)
            except (ValueError, OverflowError) as error:
                raise ValueError(f"Invalid ordered_at at CSV line {rows.line_num}") from error

            month = (local_date.year - 1) * 12 + local_date.month - 1
            gross_by_month[month] += int(amount)

    if not gross_by_month:
        return {}

    result: dict[str, int] = {}
    for month in range(min(gross_by_month), max(gross_by_month) + 1):
        year, month_in_year = divmod(month, 12)
        gross = gross_by_month.get(month, 0)
        # Divide the magnitude so negative totals are truncated toward zero too.
        net = abs(gross) * 10 // 11
        result[f"{year + 1:04d}-{month_in_year + 1:02d}"] = -net if gross < 0 else net
    return result
