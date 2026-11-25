import csv
from datetime import datetime, timedelta, timezone


_JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """Return monthly totals of completed sales, grouped by Japan Standard Time."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as sales_file:
        for row in csv.DictReader(sales_file):
            if row["status"] != "completed":
                continue

            ordered_at = row["ordered_at"]
            if ordered_at.endswith("Z"):
                ordered_at = ordered_at[:-1] + "+00:00"
            timestamp = datetime.fromisoformat(ordered_at)
            if timestamp.tzinfo is None:
                raise ValueError("ordered_at must include a timezone")

            month = timestamp.astimezone(_JST).date().isoformat()[:7]
            totals[month] = totals.get(month, 0) + int(row["amount_incl_tax"])
    return totals
