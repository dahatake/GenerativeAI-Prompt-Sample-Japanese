import csv
from datetime import datetime, timedelta, timezone

_JST = timezone(timedelta(hours=9))
_REQUIRED_COLUMNS = {"ordered_at", "amount_incl_tax", "status"}


def monthly_sales(path):
    """Return completed sales totals by month, including zero-sales months."""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = set(reader.fieldnames or [])
        missing = _REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError("missing required columns: " + ", ".join(sorted(missing)))

        for row in reader:
            if (row.get("status") or "").strip() != "completed":
                continue

            ordered_at = (row.get("ordered_at") or "").strip()
            if not ordered_at:
                raise ValueError("ordered_at is empty")

            iso_value = ordered_at[:-1] + "+00:00" if ordered_at.endswith("Z") else ordered_at
            try:
                parsed = datetime.fromisoformat(iso_value)
            except ValueError as exc:
                raise ValueError("invalid ordered_at: " + ordered_at) from exc

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            local_month = parsed.astimezone(_JST)
            key = local_month.strftime("%Y-%m")

            amount_text = (row.get("amount_incl_tax") or "").strip()
            try:
                amount = int(amount_text)
            except (TypeError, ValueError) as exc:
                raise ValueError("invalid amount_incl_tax: " + amount_text) from exc

            totals[key] = totals.get(key, 0) + amount

    if not totals:
        return {}

    first = min(totals)
    last = max(totals)
    year, month = map(int, first.split("-"))
    last_year, last_month = map(int, last.split("-"))

    result = {}
    while (year, month) <= (last_year, last_month):
        key = f"{year:04d}-{month:02d}"
        result[key] = totals.get(key, 0)
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

    return result
