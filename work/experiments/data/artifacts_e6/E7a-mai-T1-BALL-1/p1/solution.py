import csv
import re


def monthly_sales(path):
    """Return completed sales totals grouped by month in YYYY-MM format."""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {"ordered_at", "amount_incl_tax", "status"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError("Missing required CSV column(s): " + ", ".join(sorted(missing)))

        for row in reader:
            if (row.get("status") or "").strip().lower() != "completed":
                continue

            ordered_at = (row.get("ordered_at") or "").strip()
            match = re.match(r"^(\d{4})-(\d{2})-(\d{2})(?:T|\s|$)", ordered_at)
            if not match:
                raise ValueError("Invalid ordered_at value: " + repr(ordered_at))

            year, month, day = map(int, match.groups())
            if month < 1 or month > 12:
                raise ValueError("Invalid ordered_at value: " + repr(ordered_at))

            month_key = f"{year:04d}-{month:02d}"
            amount = int((row.get("amount_incl_tax") or "").strip())
            totals[month_key] = totals.get(month_key, 0) + amount

    return dict(sorted(totals.items()))
