import csv
from datetime import datetime, timezone


def monthly_sales(path):
    """Return completed sales totals by UTC calendar month."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as sales_file:
        rows = csv.DictReader(sales_file, strict=True)
        required_columns = {"ordered_at", "amount_incl_tax", "status"}
        if not required_columns.issubset(rows.fieldnames or ()):
            raise ValueError("CSV must include ordered_at, amount_incl_tax, and status")

        for row in rows:
            if any(row[column] is None for column in required_columns):
                raise ValueError(f"Missing field on CSV line {rows.line_num}")
            if row["status"] != "completed":
                continue

            timestamp = row["ordered_at"]
            if timestamp.endswith("Z"):
                timestamp = timestamp[:-1] + "+00:00"
            ordered_at = datetime.fromisoformat(timestamp)
            if ordered_at.tzinfo is None:
                raise ValueError(f"Missing time zone on CSV line {rows.line_num}")
            utc = ordered_at.astimezone(timezone.utc)
            month = f"{utc.year:04d}-{utc.month:02d}"
            totals[month] = totals.get(month, 0) + int(row["amount_incl_tax"], 10)

    return dict(sorted(totals.items()))
