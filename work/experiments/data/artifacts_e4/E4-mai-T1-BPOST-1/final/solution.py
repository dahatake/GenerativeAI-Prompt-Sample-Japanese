import csv
from datetime import datetime, timedelta, timezone


JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["status"].strip().lower() != "completed":
                continue

            ordered_at = row["ordered_at"].strip()
            iso_value = ordered_at[:-1] + "+00:00" if ordered_at.endswith(("Z", "z")) else ordered_at
            try:
                timestamp = datetime.fromisoformat(iso_value)
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                month = timestamp.astimezone(timezone.utc).astimezone(JST).strftime("%Y-%m")
            except ValueError:
                raise ValueError(f"Invalid ordered_at value: {ordered_at}")

            amount = int(row["amount_incl_tax"].strip())
            totals[month] = totals.get(month, 0) + amount

    return totals
