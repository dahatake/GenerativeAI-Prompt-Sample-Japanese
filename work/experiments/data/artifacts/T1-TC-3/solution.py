import csv
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
REQUIRED_COLUMNS = ("ordered_at", "amount_incl_tax", "status")


def _to_tax_excluded(amount_incl_tax):
    # Round amount * 10 / 11 to the nearest integer; ties cannot occur because 11 is odd.
    quotient, remainder = divmod(amount_incl_tax * 10, 11)
    return quotient + 1 if remainder * 2 > 11 else quotient


def _next_month(year, month):
    return (year + 1, 1) if month == 12 else (year, month + 1)


def monthly_sales(path):
    """Return {"YYYY-MM": tax-excluded sales} per JST month for completed orders."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing columns: {missing}")
        for row in reader:
            line = reader.line_num
            try:
                ordered_at = datetime.fromisoformat(row["ordered_at"].strip())
                amount = int(row["amount_incl_tax"].strip())
                status = row["status"].strip()
            except (AttributeError, ValueError) as e:
                raise ValueError(f"line {line}: invalid row {row!r}: {e}") from e
            if ordered_at.tzinfo is None:
                raise ValueError(f"line {line}: ordered_at has no timezone: {row['ordered_at']!r}")
            local = ordered_at.astimezone(JST)
            key = (local.year, local.month)
            totals.setdefault(key, 0)
            if status == "completed":
                totals[key] += amount

    if not totals:
        return {}

    result = {}
    current, last = min(totals), max(totals)
    while current <= last:
        result[f"{current[0]:04d}-{current[1]:02d}"] = _to_tax_excluded(totals.get(current, 0))
        current = _next_month(*current)
    return result
