import csv
import re
from datetime import datetime, timedelta, timezone
from os import PathLike

_JST = timezone(timedelta(hours=9))
_REQUIRED_COLUMNS = {"ordered_at", "amount_incl_tax", "status"}
_UTC_TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
_INTEGER_AMOUNT = re.compile(r"[+-]?[0-9]+")


def monthly_sales(path: str | PathLike[str]) -> dict[str, int]:
    """Sum non-cancelled sales by JST month, including zeros between sales months."""
    totals: dict[tuple[int, int], int] = {}
    with open(path, encoding="utf-8-sig", newline="") as source:
        rows = csv.DictReader(source, strict=True)
        try:
            missing = _REQUIRED_COLUMNS.difference(rows.fieldnames or ())
            if missing:
                raise ValueError(f"Missing CSV columns: {', '.join(sorted(missing))}")

            for row in rows:
                status = row["status"]
                if status is None:
                    raise ValueError(f"CSV line {rows.line_num}: missing status")
                if status == "cancelled":
                    continue

                ordered_at = row["ordered_at"]
                if ordered_at is None or not _UTC_TIMESTAMP.fullmatch(ordered_at):
                    raise ValueError(f"CSV line {rows.line_num}: invalid ordered_at")
                try:
                    local_time = datetime.fromisoformat(ordered_at[:-1] + "+00:00").astimezone(_JST)
                except (ValueError, OverflowError) as exc:
                    raise ValueError(f"CSV line {rows.line_num}: invalid ordered_at") from exc

                amount = row["amount_incl_tax"]
                if amount is None or not _INTEGER_AMOUNT.fullmatch(amount):
                    raise ValueError(f"CSV line {rows.line_num}: invalid amount_incl_tax")
                key = (local_time.year, local_time.month)
                totals[key] = totals.get(key, 0) + int(amount)
        except csv.Error as exc:
            raise ValueError(f"CSV line {rows.line_num}: malformed CSV") from exc

    if not totals:
        return {}

    result: dict[str, int] = {}
    year, month = min(totals)
    last_month = max(totals)
    while (year, month) <= last_month:
        result[f"{year:04d}-{month:02d}"] = totals.get((year, month), 0)
        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1
    return result
