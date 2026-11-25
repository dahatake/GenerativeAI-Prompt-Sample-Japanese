import csv
from datetime import datetime, timedelta, timezone

# Japan has no DST, so a fixed offset is equivalent to Asia/Tokyo and avoids a tzdata dependency.
JST = timezone(timedelta(hours=9), "JST")

REQUIRED_COLUMNS = ("order_id", "ordered_at", "amount_incl_tax", "status")
INCLUDED_STATUSES = {"completed"}
KNOWN_STATUSES = {"completed", "cancelled"}


def _parse_month(value, line_no):
    try:
        ts = datetime.fromisoformat(value.strip())
    except ValueError as e:
        raise ValueError(f"line {line_no}: invalid ordered_at {value!r}") from e
    if ts.tzinfo is None:
        raise ValueError(f"line {line_no}: ordered_at has no timezone: {value!r}")
    return ts.astimezone(JST).strftime("%Y-%m")


def _parse_amount(value, line_no):
    try:
        return int(value.strip())
    except ValueError as e:
        raise ValueError(f"line {line_no}: invalid amount_incl_tax {value!r}") from e


def monthly_sales(path):
    """Sum tax-included amounts of completed orders per JST month: {"YYYY-MM": int}."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing columns: {missing}")
        for row in reader:
            line_no = reader.line_num
            if any(row.get(c) is None for c in REQUIRED_COLUMNS) or None in row:
                raise ValueError(f"line {line_no}: wrong number of fields")
            status = row["status"].strip()
            if status not in KNOWN_STATUSES:
                raise ValueError(f"line {line_no}: unknown status {status!r}")
            month = _parse_month(row["ordered_at"], line_no)
            amount = _parse_amount(row["amount_incl_tax"], line_no)
            if status in INCLUDED_STATUSES:
                totals[month] = totals.get(month, 0) + amount
    return dict(sorted(totals.items()))
