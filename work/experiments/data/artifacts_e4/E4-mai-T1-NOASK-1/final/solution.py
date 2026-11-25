import csv
from datetime import datetime, timezone


def monthly_sales(path):
    """Return completed-sales totals grouped by UTC month."""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            status = (row["status"] or "").strip().lower()
            if status != "completed":
                continue

            timestamp_text = (row["ordered_at"] or "").strip()
            if timestamp_text.endswith(("Z", "z")):
                timestamp_text = timestamp_text[:-1] + "+00:00"

            ordered_at = datetime.fromisoformat(timestamp_text)
            if ordered_at.tzinfo is None:
                ordered_at = ordered_at.replace(tzinfo=timezone.utc)
            else:
                ordered_at = ordered_at.astimezone(timezone.utc)

            month = ordered_at.strftime("%Y-%m")
            amount = int((row["amount_incl_tax"] or "").strip())
            totals[month] = totals.get(month, 0) + amount

    return totals
