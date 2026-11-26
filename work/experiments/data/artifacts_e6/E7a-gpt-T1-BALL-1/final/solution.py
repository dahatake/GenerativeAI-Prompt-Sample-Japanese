import csv
from datetime import datetime, timedelta, timezone


JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """Return tax-exclusive sales totals by JST month, excluding cancelled orders."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as sales_file:
        rows = csv.DictReader(sales_file, strict=True)
        required_columns = {"ordered_at", "amount_incl_tax", "status"}
        if not required_columns.issubset(rows.fieldnames or ()):
            raise ValueError("CSV must include ordered_at, amount_incl_tax, and status")

        for row in rows:
            if any(row[column] is None for column in required_columns):
                raise ValueError(f"Missing field on CSV line {rows.line_num}")
            if row["status"] == "cancelled":
                continue

            timestamp = row["ordered_at"]
            if timestamp.endswith("Z"):
                timestamp = timestamp[:-1] + "+00:00"
            ordered_at = datetime.fromisoformat(timestamp)
            if ordered_at.tzinfo is None:
                raise ValueError(f"Missing time zone on CSV line {rows.line_num}")
            local_time = ordered_at.astimezone(JST)
            month_index = local_time.year * 12 + local_time.month - 1
            totals[month_index] = totals.get(month_index, 0) + int(row["amount_incl_tax"], 10)

    result = {}
    if totals:
        for month_index in range(min(totals), max(totals) + 1):
            year, month = divmod(month_index, 12)
            gross = totals.get(month_index, 0)
            # Divide by 1.1 exactly, truncating towards zero.
            net = abs(gross) * 10 // 11
            result[f"{year:04d}-{month + 1:02d}"] = -net if gross < 0 else net
    return result
