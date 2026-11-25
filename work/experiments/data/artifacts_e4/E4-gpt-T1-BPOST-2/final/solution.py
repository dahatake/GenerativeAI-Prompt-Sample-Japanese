import csv
from datetime import datetime, timedelta, timezone


JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """Sum completed sales for every JST month in the order period."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as sales_file:
        for row in csv.DictReader(sales_file):
            timestamp = row["ordered_at"]
            if timestamp.endswith("Z"):
                timestamp = timestamp[:-1] + "+00:00"
            ordered_at = datetime.fromisoformat(timestamp)
            if ordered_at.tzinfo is None:
                raise ValueError("ordered_at must include a time zone offset")
            local_date = ordered_at.astimezone(JST).date()
            month = local_date.year * 12 + local_date.month - 1
            totals.setdefault(month, 0)
            if row["status"] == "completed":
                totals[month] += int(row["amount_incl_tax"])

    monthly = {}
    if totals:
        for month in range(min(totals), max(totals) + 1):
            year, month_index = divmod(month, 12)
            monthly[f"{year:04d}-{month_index + 1:02d}"] = totals.get(month, 0)
    return monthly
