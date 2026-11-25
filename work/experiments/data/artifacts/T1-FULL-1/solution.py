import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_DOWN

JST = timezone(timedelta(hours=9))
TAX_RATE = Decimal("1.1")


def _parse_utc(value):
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _next_month(year, month):
    return (year + 1, 1) if month == 12 else (year, month + 1)


def monthly_sales(path):
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if (row.get("status") or "").strip().lower() == "cancelled":
                continue
            jst = _parse_utc(row["ordered_at"]).astimezone(JST)
            key = (jst.year, jst.month)
            totals[key] = totals.get(key, Decimal(0)) + Decimal(row["amount_incl_tax"].strip())

    if not totals:
        return {}

    result = {}
    current, last = min(totals), max(totals)
    while current <= last:
        incl = totals.get(current, Decimal(0))
        # Decimal avoids float error (e.g. 11000 / 1.1 == 9999.999... in float)
        excl = int((incl / TAX_RATE).quantize(Decimal(1), rounding=ROUND_DOWN))
        result[f"{current[0]:04d}-{current[1]:02d}"] = excl
        current = _next_month(*current)
    return result


if __name__ == "__main__":
    print(monthly_sales("sales.csv"))
