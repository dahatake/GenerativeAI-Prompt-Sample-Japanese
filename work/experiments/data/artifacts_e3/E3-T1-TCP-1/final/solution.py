import csv
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

JST = timezone(timedelta(hours=9))
REQUIRED_COLUMNS = ("ordered_at", "amount_incl_tax", "status")


def _parse_month(value, line_no):
    try:
        dt = datetime.fromisoformat(value.strip())
    except (AttributeError, ValueError) as e:
        raise ValueError(f"line {line_no}: invalid ordered_at: {value!r}") from e
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    jst = dt.astimezone(JST)
    return jst.year, jst.month


def _parse_amount(value, line_no):
    try:
        return int(value.strip())
    except (AttributeError, ValueError) as e:
        raise ValueError(f"line {line_no}: invalid amount_incl_tax: {value!r}") from e


def _excl_tax(total_incl):
    # 税込合計 ÷ 1.1 を、整数演算で厳密に計算して四捨五入する（0.5 は 0 から遠い方へ）
    return int((Decimal(total_incl) * 10 / 11).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def monthly_sales(path):
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing columns: {missing}")
        for row in reader:
            line_no = reader.line_num
            status = (row["status"] or "").strip().lower()
            if status == "cancelled":
                continue
            ym = _parse_month(row["ordered_at"], line_no)
            amount = _parse_amount(row["amount_incl_tax"], line_no)
            totals[ym] = totals.get(ym, 0) + amount

    if not totals:
        return {}

    result = {}
    year, month = min(totals)
    last = max(totals)
    while (year, month) <= last:
        result[f"{year:04d}-{month:02d}"] = _excl_tax(totals.get((year, month), 0))
        month += 1
        if month == 13:
            year, month = year + 1, 1
    return result
