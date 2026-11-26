import csv


def monthly_sales(path):
    """Aggregate completed sales in a CSV file by month."""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            if (row.get("status") or "").strip() != "completed":
                continue

            ordered_at = (row.get("ordered_at") or "").strip()
            if len(ordered_at) < 7:
                continue

            month = ordered_at[:7]
            if len(month) != 7 or month[4] != "-":
                continue

            totals[month] = totals.get(month, 0) + int(row["amount_incl_tax"].strip())

    return totals
