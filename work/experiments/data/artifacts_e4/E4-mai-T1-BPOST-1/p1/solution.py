import csv


def monthly_sales(path):
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["status"].strip().lower() != "completed":
                continue

            ordered_at = row["ordered_at"].strip()
            if len(ordered_at) < 7:
                raise ValueError(f"Invalid ordered_at value: {ordered_at}")

            month = ordered_at[:7]
            try:
                year, month_number = map(int, month.split("-"))
                if not (1000 <= year <= 9999 and 1 <= month_number <= 12):
                    raise ValueError
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid YYYY-MM date: {ordered_at}")

            amount = int(row["amount_incl_tax"].strip())
            totals[month] = totals.get(month, 0) + amount

    return totals
