import csv
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

JST = timezone(timedelta(hours=9), "JST")
TAX_RATE = Decimal("0.10")


def _parse_timestamp(value):
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        # Naive timestamps are treated as UTC, consistent with the "Z" suffix in the data.
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _to_tax_excluded(amount_incl_tax):
    # Round half away from zero (四捨五入) so refunds are handled symmetrically.
    value = Decimal(amount_incl_tax) / (1 + TAX_RATE)
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _month_range(first, last):
    year, month = map(int, first.split("-"))
    end = tuple(map(int, last.split("-")))
    while (year, month) <= end:
        yield f"{year:04d}-{month:02d}"
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)


def monthly_sales(path, *, tz=JST, counted_statuses=("completed",)):
    """Aggregate sales.csv by month.

    Returns {"YYYY-MM": tax_excluded_amount(int)}, covering every month from the
    first to the last order month (months without sales are 0). Months are
    determined in ``tz`` (default JST). Only rows whose status is in
    ``counted_statuses`` are summed; negative amounts (refunds) are included.
    Each month's tax-included total is converted to tax-excluded (/1.1, rounded).
    """
    statuses = {s.strip().lower() for s in counted_statuses}
    totals = {}
    order_months = set()
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            month = _parse_timestamp(row["ordered_at"]).astimezone(tz).strftime("%Y-%m")
            order_months.add(month)
            if (row.get("status") or "").strip().lower() not in statuses:
                continue
            amount = int(row["amount_incl_tax"].strip().replace(",", ""))
            totals[month] = totals.get(month, 0) + amount
    if not order_months:
        return {}
    return {
        month: _to_tax_excluded(totals.get(month, 0))
        for month in _month_range(min(order_months), max(order_months))
    }
