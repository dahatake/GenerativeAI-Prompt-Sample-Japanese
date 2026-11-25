import csv
import re
from datetime import datetime, timedelta, timezone


_REQUIRED_COLUMNS = ("ordered_at", "amount_incl_tax", "status")
_UTC_TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")
_AMOUNT = re.compile(r"-?[0-9]+")
_JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """Sum completed sales by JST month, filling interior gaps with zero."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        try:
            columns = reader.fieldnames or []
            if any(columns.count(name) != 1 for name in _REQUIRED_COLUMNS):
                raise ValueError("Missing or duplicate required CSV columns")

            for row in reader:
                timestamp = row["ordered_at"] or ""
                amount = row["amount_incl_tax"] or ""
                status = row["status"]
                if (
                    not _UTC_TIMESTAMP.fullmatch(timestamp)
                    or not _AMOUNT.fullmatch(amount)
                    or status not in ("completed", "cancelled")
                ):
                    raise ValueError(f"Invalid sales fields on CSV line {reader.line_num}")

                try:
                    ordered_at = datetime.fromisoformat(timestamp[:-1] + "+00:00")
                    value = int(amount)
                    if status == "cancelled":
                        continue
                    local_date = ordered_at.astimezone(_JST)
                except (ValueError, OverflowError) as error:
                    raise ValueError(f"Invalid sales fields on CSV line {reader.line_num}") from error

                month = local_date.year * 12 + local_date.month - 1
                totals[month] = totals.get(month, 0) + value
        except csv.Error as error:
            raise ValueError(f"Invalid CSV near line {reader.line_num}") from error

    result = {}
    if totals:
        for month in range(min(totals), max(totals) + 1):
            year, month_in_year = divmod(month, 12)
            result[f"{year:04d}-{month_in_year + 1:02d}"] = totals.get(month, 0)
    return result
