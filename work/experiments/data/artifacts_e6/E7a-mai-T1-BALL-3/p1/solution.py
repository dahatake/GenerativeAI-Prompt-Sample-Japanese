import csv


def monthly_sales(path):
    """completed sales totalled by YYYY-MM from ordered_at."""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            status = (row.get("status") or "").strip().lower()
            if status != "completed":
                continue

            ordered_at = (row.get("ordered_at") or "").strip()
            month = ordered_at[:7]
            if len(month) != 7 or month[4] != "-":
                raise ValueError("invalid ordered_at: {!r}".format(ordered_at))

            amount_text = (row.get("amount_incl_tax") or "").strip()
            amount = int(amount_text)
            totals[month] = totals.get(month, 0) + amount

    return totals
