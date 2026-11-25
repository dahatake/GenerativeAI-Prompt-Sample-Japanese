import csv
from datetime import datetime, timedelta, timezone


JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """Sum completed sales by calendar month in Japan Standard Time."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as sales_file:
        for row in csv.DictReader(sales_file):
            if row["status"] != "completed":
                continue
            timestamp = row["ordered_at"]
            if timestamp.endswith("Z"):
                timestamp = timestamp[:-1] + "+00:00"
            ordered_at = datetime.fromisoformat(timestamp)
            if ordered_at.tzinfo is None:
                raise ValueError("ordered_at must include a time zone offset")
            local_date = ordered_at.astimezone(JST).date()
            month = f"{local_date.year:04d}-{local_date.month:02d}"
            totals[month] = totals.get(month, 0) + int(row["amount_incl_tax"])
    return totals
