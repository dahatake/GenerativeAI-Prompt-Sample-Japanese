import csv
import re
from datetime import datetime, timedelta, timezone
from fractions import Fraction


_JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """Return completed orders' tax-exclusive totals by calendar month in JST."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as sales_file:
        rows = csv.DictReader(sales_file, strict=True)
        if rows.fieldnames is None:
            return {}
        required = {"ordered_at", "amount_incl_tax", "status"}
        if not required.issubset(rows.fieldnames):
            raise ValueError(f"Missing CSV columns: {', '.join(sorted(required - set(rows.fieldnames)))}")

        for row in rows:
            status = row["status"]
            if not status:
                raise ValueError(f"CSV line {rows.line_num}: missing status")
            if status != "completed":
                continue

            timestamp = row["ordered_at"] or ""
            if timestamp.endswith("Z"):
                timestamp = timestamp[:-1] + "+00:00"
            try:
                ordered_at = datetime.fromisoformat(timestamp)
                if ordered_at.tzinfo is None:
                    raise ValueError("ordered_at must include a time zone")
                local_date = ordered_at.astimezone(_JST)
                amount = (row["amount_incl_tax"] or "").strip()
                if not re.fullmatch(r"[+-]?[0-9]+", amount):
                    raise ValueError("amount_incl_tax must be an integer")
                value = int(amount)
            except (ValueError, OverflowError) as error:
                raise ValueError(f"CSV line {rows.line_num}: {error}") from error

            month_index = local_date.year * 12 + local_date.month - 1
            totals[month_index] = totals.get(month_index, 0) + value

    if not totals:
        return {}

    result = {}
    for month_index in range(min(totals), max(totals) + 1):
        year, month_zero_based = divmod(month_index, 12)
        monthly_total = totals.get(month_index, 0)
        result[f"{year:04d}-{month_zero_based + 1:02d}"] = int(Fraction(monthly_total * 10, 11))
    return result
