import csv
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))


def _excl_tax(amount_incl_tax):
    # 税込 / 1.1 を整数演算で四捨五入（0.5 は +∞ 方向へ切り上げ）
    return (20 * amount_incl_tax + 11) // 22


def monthly_sales(path):
    totals = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["status"].strip() != "completed":
                continue
            ts = datetime.fromisoformat(row["ordered_at"].strip().replace("Z", "+00:00"))
            local = ts.astimezone(JST)
            key = (local.year, local.month)
            totals[key] = totals.get(key, 0) + _excl_tax(int(row["amount_incl_tax"]))

    if not totals:
        return {}

    year, month = min(totals)
    last = max(totals)
    result = {}
    while (year, month) <= last:
        result[f"{year:04d}-{month:02d}"] = totals.get((year, month), 0)
        month += 1
        if month > 12:
            year, month = year + 1, 1
    return result
