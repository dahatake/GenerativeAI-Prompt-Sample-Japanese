import csv
from datetime import datetime, timedelta, timezone


JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """Return sales totals grouped by month in JST."""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            return totals

        columns = {
            name.strip(): name
            for name in reader.fieldnames
            if name is not None
        }
        required = ("ordered_at", "amount_incl_tax", "status")
        missing = [name for name in required if name not in columns]
        if missing:
            raise ValueError("Missing required CSV column(s): " + ", ".join(missing))

        for row in reader:
            status = (row.get(columns["status"]) or "").strip().lower()
            if status == "cancelled":
                continue

            ordered_at = (row.get(columns["ordered_at"]) or "").strip()
            if not ordered_at:
                raise ValueError("Invalid ordered_at: " + repr(ordered_at))

            iso_timestamp = ordered_at[:-1] + "+00:00" if ordered_at.endswith(("Z", "z")) else ordered_at
            try:
                ordered_datetime = datetime.fromisoformat(iso_timestamp)
            except ValueError as exc:
                raise ValueError("Invalid ordered_at: " + repr(ordered_at)) from exc

            if ordered_datetime.tzinfo is None:
                ordered_datetime = ordered_datetime.replace(tzinfo=timezone.utc)
            month = ordered_datetime.astimezone(JST).strftime("%Y-%m")

            amount_text = (row.get(columns["amount_incl_tax"]) or "").strip()
            amount = int(amount_text)
            totals[month] = totals.get(month, 0) + amount

    return totals
