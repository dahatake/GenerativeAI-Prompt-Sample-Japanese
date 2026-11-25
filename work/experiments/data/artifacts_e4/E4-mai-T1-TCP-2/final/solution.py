import csv
import re
from datetime import datetime, timedelta, timezone


_JST = timezone(timedelta(hours=9))
_INTEGER = re.compile(r"^[+-]?\d+$")
_REQUIRED_COLUMNS = {"ordered_at", "amount_incl_tax", "status"}


def _parse_utc(value):
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"

    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _month_key(value):
    return _parse_utc(value).astimezone(_JST).strftime("%Y-%m")


def _month_number(key):
    year, month = (int(part) for part in key.split("-"))
    return year * 12 + month - 1


def _key_from_month_number(number):
    year, month_index = divmod(number, 12)
    return f"{year:04d}-{month_index + 1:02d}"


def monthly_sales(path):
    """Aggregate completed sales by JST month; cancelled orders are excluded."""
    totals = {}
    first_month = None
    last_month = None

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("CSV header is missing")

        missing = _REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            raise ValueError("Missing required CSV columns: " + ", ".join(sorted(missing)))

        for row in reader:
            status = (row.get("status") or "").strip().lower()
            if status not in {"completed", "cancelled"}:
                continue

            ordered_at = row.get("ordered_at") or ""
            month = _month_key(ordered_at)
            month_number = _month_number(month)

            if first_month is None or month_number < first_month:
                first_month = month_number
            if last_month is None or month_number > last_month:
                last_month = month_number

            if status == "cancelled":
                continue

            amount_text = (row.get("amount_incl_tax") or "").strip()
            if not _INTEGER.fullmatch(amount_text):
                raise ValueError(f"Invalid integer amount: {amount_text!r}")
            totals[month] = totals.get(month, 0) + int(amount_text)

    if first_month is None:
        return {}

    result = {}
    for month_number in range(first_month, last_month + 1):
        month = _key_from_month_number(month_number)
        result[month] = totals.get(month, 0)
    return result
