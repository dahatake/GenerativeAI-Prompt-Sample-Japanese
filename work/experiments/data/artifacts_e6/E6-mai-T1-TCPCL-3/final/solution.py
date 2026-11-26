import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


JST = timezone(timedelta(hours=9))
ONE_TENTH = Decimal("1.10")
ONE = Decimal("1")


def _parse_datetime(value: str) -> datetime:
    if value is None:
        raise ValueError("ordered_at is missing")
    text = value.strip()
    if not text:
        raise ValueError("ordered_at is missing")

    if text.endswith("Z") or text.endswith("z"):
        text = text[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError("invalid ordered_at") from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(JST)


def _tax_exclusive(value: str) -> int:
    if value is None:
        raise ValueError("amount_incl_tax is missing")
    text = value.strip()
    if not text:
        raise ValueError("amount_incl_tax is missing")

    try:
        amount = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError("invalid amount_incl_tax") from exc
    if not amount.is_finite():
        raise ValueError("invalid amount_incl_tax")

    return int((amount / ONE_TENTH).quantize(ONE, rounding=ROUND_HALF_UP))


def monthly_sales(path):
    totals = {}
    all_months = set()

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {"ordered_at", "amount_incl_tax", "status"}
        if reader.fieldnames is None:
            raise ValueError("missing CSV header")
        missing = required.difference(reader.fieldnames)
        if missing:
            raise ValueError("missing required CSV columns")

        for row in reader:
            status = row["status"]
            if status is None or not status.strip():
                raise ValueError("status is missing")

            ordered_jst = _parse_datetime(row["ordered_at"])
            month = ordered_jst.strftime("%Y-%m")
            all_months.add(month)

            tax_exclusive = _tax_exclusive(row["amount_incl_tax"])
            if status.strip() == "completed":
                totals[month] = totals.get(month, 0) + tax_exclusive

    if not all_months:
        return {}

    first = min(all_months)
    last = max(all_months)

    first_year, first_month = (int(part) for part in first.split("-"))
    last_year, last_month = (int(part) for part in last.split("-"))

    result = {}
    year, month = first_year, first_month
    while (year, month) <= (last_year, last_month):
        key = f"{year:04d}-{month:02d}"
        result[key] = totals.get(key, 0)
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    return result
