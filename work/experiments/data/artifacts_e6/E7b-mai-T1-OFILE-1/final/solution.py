import csv
from datetime import datetime, timedelta, timezone


JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            status = (row.get("status") or "").strip().lower()
            if status != "completed":
                continue

            ordered_at = (row.get("ordered_at") or "").strip()
            try:
                iso_value = ordered_at[:-1] + "+00:00" if ordered_at.upper().endswith("Z") else ordered_at
                parsed = datetime.fromisoformat(iso_value)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                month = parsed.astimezone(JST).strftime("%Y-%m")
            except (TypeError, ValueError):
                raise ValueError(f"Invalid ordered_at value: {ordered_at}")

            try:
                amount = int((row.get("amount_incl_tax") or "").strip())
            except (TypeError, ValueError):
                raise ValueError(f"Invalid amount_incl_tax value: {row.get('amount_incl_tax')}")

            totals[month] = totals.get(month, 0) + amount

    return totals
