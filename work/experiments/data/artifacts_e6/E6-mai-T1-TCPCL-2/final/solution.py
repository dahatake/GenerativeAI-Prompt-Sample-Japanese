import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


JST = timezone(timedelta(hours=9))
TAX_DIVISOR = Decimal("1.1")
ONE = Decimal("1")


def _month_after_jst(value):
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(JST).strftime("%Y-%m")


def _month_index(year_month):
    year, month = map(int, year_month.split("-"))
    return year * 12 + month - 1


def _index_month(index):
    year, month0 = divmod(index, 12)
    return f"{year:04d}-{month0 + 1:02d}"


def monthly_sales(path):
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {"ordered_at", "amount_incl_tax", "status"}
        if reader.fieldnames is None:
            raise ValueError("CSV header is missing")

        missing_headers = required.difference(reader.fieldnames)
        if missing_headers:
            raise ValueError(
                "Missing required CSV columns: " + ", ".join(sorted(missing_headers))
            )

        for row in reader:
            if any(row.get(column) is None or not row[column].strip()
                   for column in required):
                continue

            status = row["status"].strip().lower()
            if status == "cancelled":
                continue

            try:
                month = _month_after_jst(row["ordered_at"])
                amount = Decimal(row["amount_incl_tax"].strip())
                if not amount.is_finite():
                    raise InvalidOperation
                tax_exclusive = (amount / TAX_DIVISOR).quantize(
                    ONE, rounding=ROUND_HALF_UP
                )
            except (ValueError, InvalidOperation) as exc:
                raise ValueError("Invalid date or amount in CSV row") from exc
            totals[month] = totals.get(month, 0) + int(tax_exclusive)

    if not totals:
        return {}

    first = _month_index(min(totals))
    last = _month_index(max(totals))
    return {
        _index_month(index): totals.get(_index_month(index), 0)
        for index in range(first, last + 1)
    }

