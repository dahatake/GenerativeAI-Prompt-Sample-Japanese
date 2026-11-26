import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal


def monthly_sales(path):
    """Return monthly tax-excluded sales for all except cancelled orders."""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            status = (row.get("status") or "").strip().lower()
            if status == "cancelled":
                continue

            ordered_at = (row.get("ordered_at") or "").strip()
            if ordered_at.endswith(("Z", "z")):
                ordered_at = ordered_at[:-1] + "+00:00"

            try:
                timestamp = datetime.fromisoformat(ordered_at)
            except ValueError as exc:
                raise ValueError("invalid ordered_at: {!r}".format(ordered_at)) from exc

            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)

            jst = timestamp.astimezone(timezone(timedelta(hours=9)))
            month = jst.strftime("%Y-%m")

            amount_text = (row.get("amount_incl_tax") or "").strip()
            amount_incl_tax = int(amount_text)
            amount_excl_tax = int(Decimal(amount_incl_tax) / Decimal("1.1"))
            totals[month] = totals.get(month, 0) + amount_excl_tax

    if not totals:
        return {}

    first_year, first_month = map(int, min(totals).split("-"))
    last_year, last_month = map(int, max(totals).split("-"))

    year, month = first_year, first_month
    while (year, month) <= (last_year, last_month):
        key = "{:04d}-{:02d}".format(year, month)
        totals.setdefault(key, 0)
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

    return dict(sorted(totals.items()))
