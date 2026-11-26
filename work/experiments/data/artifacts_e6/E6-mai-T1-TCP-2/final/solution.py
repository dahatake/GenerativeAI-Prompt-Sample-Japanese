import csv
from datetime import datetime, timezone
from os import fspath
from zoneinfo import ZoneInfo


JST = ZoneInfo("Asia/Tokyo")
UTC = timezone.utc
_REQUIRED_COLUMNS = {"ordered_at", "amount_incl_tax", "status"}


def _parse_datetime(value):
    text = value.strip()
    if not text:
        return None
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    try:
        return parsed.astimezone(JST)
    except (OverflowError, ValueError):
        return None


def _month_range(first_month, last_month):
    year, month = first_month
    last_year, last_month_number = last_month
    while (year, month) <= (last_year, last_month_number):
        yield f"{year:04d}-{month:02d}"
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1


def monthly_sales(path):
    """Aggregate completed sales from a CSV file by month in Asia/Tokyo."""
    totals = {}
    first_month = None
    last_month = None

    with open(fspath(path), "r", encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        if reader.fieldnames is None:
            return {}

        normalized_names = {
            name.strip(): name
            for name in reader.fieldnames
            if name is not None
        }
        missing = _REQUIRED_COLUMNS - set(normalized_names)
        if missing:
            raise ValueError("missing required CSV columns: " + ", ".join(sorted(missing)))

        for row in reader:
            status_value = row.get(normalized_names["status"])
            status = status_value.strip().lower() if isinstance(status_value, str) else ""
            if status not in {"completed", "cancelled"}:
                continue

            local_dt = _parse_datetime(row.get(normalized_names["ordered_at"]) or "")
            if local_dt is None:
                continue

            amount_value = row.get(normalized_names["amount_incl_tax"])
            if amount_value is None:
                continue
            try:
                amount = int(amount_value.strip())
            except (AttributeError, ValueError):
                continue

            month = (local_dt.year, local_dt.month)
            if first_month is None or month < first_month:
                first_month = month
            if last_month is None or month > last_month:
                last_month = month

            if status == "completed":
                totals[month] = totals.get(month, 0) + amount

    if first_month is None:
        return {}

    result = {}
    for month_key in _month_range(first_month, last_month):
        year_text, month_text = month_key.split("-")
        month = (int(year_text), int(month_text))
        result[month_key] = totals.get(month, 0)
    return result
