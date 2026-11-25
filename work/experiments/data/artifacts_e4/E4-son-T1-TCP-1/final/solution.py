import csv
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """completed の税抜売上を JST の月ごとに集計する。注文のない月は 0 で補完する。"""
    totals = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["status"] != "completed":
                continue
            ordered = datetime.fromisoformat(row["ordered_at"].replace("Z", "+00:00"))
            key = ordered.astimezone(JST).strftime("%Y-%m")
            # 税込 / 1.1 を整数演算で行い、行ごとに切り捨てる
            net = int(row["amount_incl_tax"]) * 10 // 11
            totals[key] = totals.get(key, 0) + net

    if not totals:
        return {}

    first, last = min(totals), max(totals)
    year, month = int(first[:4]), int(first[5:])
    result = {}
    while True:
        key = f"{year:04d}-{month:02d}"
        result[key] = totals.get(key, 0)
        if key == last:
            break
        month += 1
        if month > 12:
            year, month = year + 1, 1
    return result
