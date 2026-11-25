import csv
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9), "JST")


def _parse_timestamp(value):
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        # Naive timestamps are treated as UTC, consistent with the "Z" suffix in the data.
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def monthly_sales(path, *, tz=JST, counted_statuses=("completed",)):
    """Aggregate sales.csv by month.

    Returns {"YYYY-MM": total_amount(int)}, sorted by month. Months are
    determined in ``tz`` (default JST). Only rows whose status is in
    ``counted_statuses`` are summed; negative amounts (refunds) are included.
    """
    statuses = {s.strip().lower() for s in counted_statuses}
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if (row.get("status") or "").strip().lower() not in statuses:
                continue
            month = _parse_timestamp(row["ordered_at"]).astimezone(tz).strftime("%Y-%m")
            amount = int(row["amount_incl_tax"].strip().replace(",", ""))
            totals[month] = totals.get(month, 0) + amount
    return dict(sorted(totals.items()))
