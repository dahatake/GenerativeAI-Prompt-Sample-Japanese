import csv
import re
from datetime import datetime, timedelta, timezone
from os import PathLike

_JST = timezone(timedelta(hours=9))
_REQUIRED_FIELDS = {"ordered_at", "amount_incl_tax", "status"}
_UTC_TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
_INTEGER = re.compile(r"[+-]?[0-9]+")


def monthly_sales(path: str | PathLike[str]) -> dict[str, int]:
    """Return completed sales totals by calendar month in Japan time."""
    totals: dict[str, int] = {}
    with open(path, encoding="utf-8-sig", newline="") as source:
        rows = csv.DictReader(source)
        missing = _REQUIRED_FIELDS.difference(rows.fieldnames or ())
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        for row in rows:
            if row["status"] != "completed":
                continue

            ordered_at = row["ordered_at"]
            if ordered_at is None or not _UTC_TIMESTAMP.fullmatch(ordered_at):
                raise ValueError(f"Invalid ordered_at on CSV line {rows.line_num}")
            try:
                local_time = datetime.fromisoformat(ordered_at[:-1] + "+00:00").astimezone(_JST)
            except (ValueError, OverflowError) as error:
                raise ValueError(f"Invalid ordered_at on CSV line {rows.line_num}") from error

            amount = row["amount_incl_tax"]
            if amount is None or not _INTEGER.fullmatch(amount):
                raise ValueError(f"Invalid amount_incl_tax on CSV line {rows.line_num}")

            month = f"{local_time.year:04d}-{local_time.month:02d}"
            totals[month] = totals.get(month, 0) + int(amount)
    return totals
