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
            month_index = local_date.year * 12 + local_date.month - 1
            totals[month_index] = totals.get(month_index, 0) + int(row["amount_incl_tax"])

    if not totals:
        return {}

    monthly_totals = {}
    for month_index in range(min(totals), max(totals) + 1):
        year, month_offset = divmod(month_index, 12)
        gross = totals.get(month_index, 0)
        net = abs(gross) * 10 // 11
        monthly_totals[f"{year:04d}-{month_offset + 1:02d}"] = -net if gross < 0 else net
    return monthly_totals
