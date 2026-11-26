import csv
import re
from datetime import datetime, timedelta, timezone


JST = timezone(timedelta(hours=9))


def _ordered_at_in_jst(value):
    text = (value or "").strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}(?:$|[Tt ])", text):
        raise ValueError("Invalid ordered_at value: " + repr(text))

    normalized = text[:-1] + "+00:00" if text.upper().endswith("Z") else text
    try:
        ordered_at = datetime.fromisoformat(normalized)
    except ValueError:
        raise ValueError("Invalid ordered_at value: " + repr(text))

    if ordered_at.tzinfo is None:
        ordered_at = ordered_at.replace(tzinfo=timezone.utc)
    else:
        ordered_at = ordered_at.astimezone(timezone.utc)

    return ordered_at.astimezone(JST)


def monthly_sales(path):
    """Return monthly totals of completed sales, including zero-sales months."""
    totals = {}
    first_month = None
    last_month = None

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {"ordered_at", "amount_incl_tax", "status"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError("Missing required CSV column(s): " + ", ".join(sorted(missing)))

        for row in reader:
            local_time = _ordered_at_in_jst(row.get("ordered_at"))
            month_index = local_time.year * 12 + local_time.month - 1
            first_month = month_index if first_month is None else min(first_month, month_index)
            last_month = month_index if last_month is None else max(last_month, month_index)

            if (row.get("status") or "").strip().lower() != "completed":
                continue

            month_key = f"{local_time.year:04d}-{local_time.month:02d}"
            amount = int((row.get("amount_incl_tax") or "").strip())
            totals[month_key] = totals.get(month_key, 0) + amount

    if first_month is None:
        return {}

    result = {}
    for month_index in range(first_month, last_month + 1):
        year, month_zero_based = divmod(month_index, 12)
        month_key = f"{year:04d}-{month_zero_based + 1:02d}"
        result[month_key] = totals.get(month_key, 0)

    return result
