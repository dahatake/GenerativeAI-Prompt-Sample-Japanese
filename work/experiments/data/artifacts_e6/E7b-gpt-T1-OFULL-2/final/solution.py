import csv
from datetime import datetime, timedelta, timezone


JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """Return pre-tax sales by calendar month in Japan Standard Time."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as sales_file:
        for row in csv.DictReader(sales_file):
            if row["status"] == "cancelled":
                continue
            timestamp = row["ordered_at"]
            if timestamp.endswith("Z"):
                timestamp = timestamp[:-1] + "+00:00"
            ordered_at = datetime.fromisoformat(timestamp)
            if ordered_at.tzinfo is None:
                raise ValueError("ordered_at must include a time zone offset")
            local_date = ordered_at.astimezone(JST).date()
            month = (local_date.year, local_date.month)
            totals[month] = totals.get(month, 0) + int(row["amount_incl_tax"])

    if not totals:
        return {}

    monthly = {}
    year, month = min(totals)
    last_month = max(totals)
    while (year, month) <= last_month:
        gross = totals.get((year, month), 0)
        net = abs(gross) * 10 // 11
        monthly[f"{year:04d}-{month:02d}"] = -net if gross < 0 else net
        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1
    return monthly
