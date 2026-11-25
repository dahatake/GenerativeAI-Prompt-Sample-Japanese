import csv
from datetime import datetime, timezone


_REQUIRED_FIELDS = {"order_id", "ordered_at", "amount_incl_tax", "status"}


def _parse_month(value):
    if value is None:
        raise ValueError("ordered_at is required")

    text = value.strip()
    if not text:
        raise ValueError("ordered_at is required")

    iso_text = text[:-1] + "+00:00" if text.endswith(("Z", "z")) else text
    try:
        parsed = datetime.fromisoformat(iso_text)
    except ValueError as exc:
        raise ValueError("invalid ordered_at: %s" % text) from exc

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc)
    return parsed.year, parsed.month


def monthly_sales(path):
    monthly = {}
    first = None
    last = None

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("CSV header is missing")

        fieldnames = set(reader.fieldnames)
        missing = _REQUIRED_FIELDS - fieldnames
        if missing:
            raise ValueError("missing required CSV header(s): %s" % ", ".join(sorted(missing)))

        for line_number, row in enumerate(reader, start=2):
            year, month = _parse_month(row.get("ordered_at"))

            amount_text = row.get("amount_incl_tax")
            if amount_text is None or not amount_text.strip():
                raise ValueError("invalid amount_incl_tax at line %d" % line_number)
            try:
                amount = int(amount_text.strip())
            except ValueError as exc:
                raise ValueError("invalid amount_incl_tax at line %d: %s" % (line_number, amount_text)) from exc

            month_index = year * 12 + month - 1
            if first is None or month_index < first:
                first = month_index
            if last is None or month_index > last:
                last = month_index

            if row.get("status") == "completed":
                key = "%04d-%02d" % (year, month)
                monthly[key] = monthly.get(key, 0) + amount

    if first is None:
        return {}

    result = {}
    current = first
    while current <= last:
        year, month_zero_based = divmod(current, 12)
        key = "%04d-%02d" % (year, month_zero_based + 1)
        result[key] = monthly.get(key, 0)
        current += 1
    return result
