import csv
import re
from datetime import datetime, timedelta, timezone


_JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """Return completed orders' tax-inclusive totals by calendar month in JST."""
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

            month = f"{local_date.year:04d}-{local_date.month:02d}"
            totals[month] = totals.get(month, 0) + value
    return dict(sorted(totals.items()))
