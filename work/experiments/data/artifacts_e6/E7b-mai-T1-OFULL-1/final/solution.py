import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal


def monthly_sales(path):
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            status = row["status"].strip().lower()
            if status == "cancelled":
                continue

            ordered_at = row["ordered_at"].strip()
            try:
                parsed = datetime.fromisoformat(
                    ordered_at[:-1] + "+00:00"
                    if ordered_at.upper().endswith("Z")
                    else ordered_at
                )
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid ordered_at value: {ordered_at}")

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            jst = parsed.astimezone(timezone(timedelta(hours=9)))
            month = f"{jst.year:04d}-{jst.month:02d}"

            amount_incl_tax = Decimal(row["amount_incl_tax"].strip())
            amount_excl_tax = int(amount_incl_tax / Decimal("1.1"))
            totals[month] = totals.get(month, 0) + amount_excl_tax

    return totals
