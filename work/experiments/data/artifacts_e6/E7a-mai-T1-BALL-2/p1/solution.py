import csv
from datetime import date


def monthly_sales(path):
    """Return completed sales totals grouped by ISO month."""
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
            if status != "completed":
                continue

            ordered_at = (row.get(columns["ordered_at"]) or "").strip()
            if len(ordered_at) < 10:
                raise ValueError("Invalid ordered_at: " + repr(ordered_at))

            date_text = ordered_at[:10]
            parsed_date = date.fromisoformat(date_text)
            month = parsed_date.strftime("%Y-%m")

            amount_text = (row.get(columns["amount_incl_tax"]) or "").strip()
            amount = int(amount_text)
            totals[month] = totals.get(month, 0) + amount

    return totals
