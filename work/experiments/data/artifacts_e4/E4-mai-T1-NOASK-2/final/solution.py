import csv
from datetime import datetime, timezone


def monthly_sales(path):
    """Aggregate completed sales amounts by UTC month."""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            status = (row.get("status") or "").strip().lower()
            if status != "completed":
                continue

            ordered_at = (row.get("ordered_at") or "").strip()
            iso_value = ordered_at[:-1] + "+00:00" if ordered_at.upper().endswith("Z") else ordered_at
            ordered = datetime.fromisoformat(iso_value)

            if ordered.tzinfo is None:
                ordered = ordered.replace(tzinfo=timezone.utc)
            else:
                ordered = ordered.astimezone(timezone.utc)

            month = f"{ordered.year:04d}-{ordered.month:02d}"
            amount = int((row.get("amount_incl_tax") or "").strip())
            totals[month] = totals.get(month, 0) + amount

    return totals
