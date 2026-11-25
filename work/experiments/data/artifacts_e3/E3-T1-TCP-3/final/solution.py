import csv
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
REQUIRED_COLUMNS = ("order_id", "ordered_at", "amount_incl_tax", "status")
INCLUDED_STATUS = "completed"


def _to_jst_month(value, line_no):
    try:
        dt = datetime.fromisoformat(value.strip())
    except (AttributeError, ValueError) as e:
        raise ValueError(f"line {line_no}: invalid ordered_at {value!r}") from e
    if dt.tzinfo is None:
        # ordered_at is recorded in UTC
        dt = dt.replace(tzinfo=timezone.utc)
    jst = dt.astimezone(JST)
    return jst.year, jst.month


def _to_int_amount(value, line_no):
    try:
        return int(value.strip())
    except (AttributeError, ValueError) as e:
        raise ValueError(f"line {line_no}: invalid amount_incl_tax {value!r}") from e


def _excl_tax(amount_incl_tax):
    # 10% tax, truncated toward zero per row; integer math avoids float errors (3300/1.1)
    sign = -1 if amount_incl_tax < 0 else 1
    return sign * (abs(amount_incl_tax) * 10 // 11)


def _next_month(year, month):
    return (year + 1, 1) if month == 12 else (year, month + 1)


def monthly_sales(path):
    """Return tax-excluded sales of completed orders per JST month as {"YYYY-MM": int}.

    Months between the first and last month with completed orders are filled with 0.
    """
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in header]
        if missing:
            raise ValueError(f"missing required columns: {missing}")
        for row in reader:
            line_no = reader.line_num
            if any(row.get(c) is None for c in REQUIRED_COLUMNS):
                raise ValueError(f"line {line_no}: missing required values")
            ym = _to_jst_month(row["ordered_at"], line_no)
            amount = _to_int_amount(row["amount_incl_tax"], line_no)
            if row["status"].strip() != INCLUDED_STATUS:
                continue
            totals[ym] = totals.get(ym, 0) + _excl_tax(amount)

    if not totals:
        return {}

    result = {}
    current, last = min(totals), max(totals)
    while current <= last:
        result[f"{current[0]:04d}-{current[1]:02d}"] = totals.get(current, 0)
        current = _next_month(*current)
    return result
