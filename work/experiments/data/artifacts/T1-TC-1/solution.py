import csv
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
REQUIRED_COLUMNS = {"ordered_at", "amount_incl_tax", "status"}
COUNTED_STATUSES = {"completed"}
EXCLUDED_STATUSES = {"cancelled"}


def _to_tax_excluded(amount_incl_tax):
    # 1注文ごとに内税額 (税込×10/110) を1円未満切り捨てし、税込から差し引く。負の金額も絶対値で同じ規則を適用する。
    sign = -1 if amount_incl_tax < 0 else 1
    magnitude = abs(amount_incl_tax)
    tax = magnitude * 10 // 110
    return sign * (magnitude - tax)


def _parse_month(value, line_no):
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as e:
        raise ValueError(f"line {line_no}: invalid ordered_at {value!r}") from e
    if dt.tzinfo is None:
        raise ValueError(f"line {line_no}: ordered_at has no timezone {value!r}")
    local = dt.astimezone(JST)
    return local.year, local.month


def _parse_amount(value, line_no):
    try:
        return int(value.strip())
    except ValueError as e:
        raise ValueError(f"line {line_no}: invalid amount_incl_tax {value!r}") from e


def monthly_sales(path):
    """JST の月ごとに税抜売上を集計し {"YYYY-MM": int} を返す（注文のない月は 0）。"""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing columns: {sorted(missing)}")
        for row in reader:
            line_no = reader.line_num
            if None in row or any(row.get(c) is None for c in REQUIRED_COLUMNS):
                raise ValueError(f"line {line_no}: wrong number of fields")
            status = row["status"].strip()
            if status not in COUNTED_STATUSES | EXCLUDED_STATUSES:
                raise ValueError(f"line {line_no}: unexpected status {status!r}")
            month = _parse_month(row["ordered_at"], line_no)
            amount = _parse_amount(row["amount_incl_tax"], line_no)
            totals.setdefault(month, 0)
            if status in COUNTED_STATUSES:
                totals[month] += _to_tax_excluded(amount)

    if not totals:
        return {}

    result = {}
    year, month = min(totals)
    last = max(totals)
    while (year, month) <= last:
        result[f"{year:04d}-{month:02d}"] = totals.get((year, month), 0)
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return result
