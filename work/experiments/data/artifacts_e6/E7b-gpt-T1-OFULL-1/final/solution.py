import csv
from datetime import datetime, timedelta, timezone


_JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """Return monthly sales totals before tax, grouped by Japan Standard Time."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as sales_file:
        for row in csv.DictReader(sales_file):
            if row["status"] == "cancelled":
                continue

            ordered_at = row["ordered_at"]
            if ordered_at.endswith("Z"):
                ordered_at = ordered_at[:-1] + "+00:00"
            timestamp = datetime.fromisoformat(ordered_at)
            if timestamp.tzinfo is None:
                raise ValueError("ordered_at must include a timezone")

            month = timestamp.astimezone(_JST).date().replace(day=1)
            totals[month] = totals.get(month, 0) + int(row["amount_incl_tax"])
    if not totals:
        return {}

    result = {}
    month, last_month = min(totals), max(totals)
    while True:
        gross = totals.get(month, 0)
        net = abs(gross) * 10 // 11
        result[month.isoformat()[:7]] = -net if gross < 0 else net
        if month == last_month:
            return result
        if month.month == 12:
            month = month.replace(year=month.year + 1, month=1)
        else:
            month = month.replace(month=month.month + 1)
