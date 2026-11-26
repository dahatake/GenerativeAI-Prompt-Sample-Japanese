import csv
from datetime import datetime, timedelta, timezone


def monthly_sales(path):
    """Aggregate tax-excluded sales by month in Japanese time."""
    totals = {}
    months = []

    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            status = (row.get("status") or "").strip().lower()
            if status == "cancelled":
                continue

            ordered_at = (row.get("ordered_at") or "").strip()
            if not ordered_at:
                continue

            try:
                parsed = datetime.fromisoformat(ordered_at.replace("Z", "+00:00"))
            except ValueError:
                continue

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            month = parsed.astimezone(timezone(timedelta(hours=9))).strftime("%Y-%m")

            try:
                amount = int((row.get("amount_incl_tax") or "").strip())
            except (TypeError, ValueError):
                continue

            if amount < 0:
                continue

            tax_excluded = (amount * 10) // 11
            totals[month] = totals.get(month, 0) + tax_excluded
            months.append(month)

    if not months:
        return {}

    months.sort()
    first_year, first_month = map(int, months[0].split("-"))
    last_year, last_month = map(int, months[-1].split("-"))

    filled = {}
    year, month = first_year, first_month
    while (year, month) <= (last_year, last_month):
        key = f"{year:04d}-{month:02d}"
        filled[key] = totals.get(key, 0)
        month += 1
        if month == 13:
            year += 1
            month = 1

    return filled
