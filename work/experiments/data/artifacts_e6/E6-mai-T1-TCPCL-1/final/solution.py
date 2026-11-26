import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal


JST = timezone(timedelta(hours=9), name="JST")


def _parse_datetime(value):
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(JST)


def _month_key(dt):
    return dt.strftime("%Y-%m")


def _month_index(month_key):
    year, month = (int(part) for part in month_key.split("-"))
    return year * 12 + month


def _month_keys(start, end):
    current = _month_index(start)
    final = _month_index(end)
    result = []
    while current <= final:
        year, month_zero = divmod(current, 12)
        month = month_zero
        if month == 0:
            year -= 1
            month = 12
        result.append(f"{year:04d}-{month:02d}")
        current += 1
    return result


def monthly_sales(path):
    totals = {}
    all_months = []

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {"ordered_at", "amount_incl_tax", "status"}
        if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
            raise ValueError("CSV must contain ordered_at, amount_incl_tax, and status columns")

        for line_number, row in enumerate(reader, start=2):
            ordered_at = row.get("ordered_at")
            if not ordered_at or not ordered_at.strip():
                raise ValueError(f"Missing ordered_at at CSV line {line_number}")

            try:
                month = _month_key(_parse_datetime(ordered_at))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid ordered_at at CSV line {line_number}: {ordered_at}") from exc

            all_months.append(month)

            status = (row.get("status") or "").strip().lower()
            if status != "completed":
                continue

            amount_text = row.get("amount_incl_tax")
            if amount_text is None or not amount_text.strip():
                raise ValueError(f"Missing amount_incl_tax at CSV line {line_number}")

            try:
                amount_incl_tax = int(amount_text.strip())
            except ValueError as exc:
                raise ValueError(f"Invalid amount_incl_tax at CSV line {line_number}: {amount_text}") from exc

            amount_excl_tax = int(Decimal(amount_incl_tax) / Decimal("1.1"))
            totals[month] = totals.get(month, 0) + amount_excl_tax

    if not all_months:
        return {}

    start = min(all_months)
    end = max(all_months)
    return {month: totals.get(month, 0) for month in _month_keys(start, end)}
