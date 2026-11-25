import csv
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))


def _excl_tax(amount_incl, rate_num=11, rate_den=10):
    # 税込 / 1.1 を整数演算で行い、四捨五入(0から遠い側へ丸め)する
    num = amount_incl * rate_den
    q, r = divmod(abs(num), rate_num)
    if r * 2 >= rate_num:
        q += 1
    return q if num >= 0 else -q


def monthly_sales(path, tz=JST, excluded_statuses=("cancelled",)):
    """sales.csv を月次集計し {"YYYY-MM": 税抜金額(int)} を返す。

    - 月の判定は ordered_at (ISO8601, UTC) を tz (既定 JST) に変換した暦月
    - status が excluded_statuses の行は除外、返金(負額)は加算する
    - 金額は amount_incl_tax (税込10%) を注文ごとに /1.1 して整数化した税抜額
    - 最初の月から最後の月まで、注文のない月も 0 で含める
    """
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if (row["status"] or "").strip().lower() in excluded_statuses:
                continue
            ts = datetime.fromisoformat(row["ordered_at"].strip().replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            local = ts.astimezone(tz)
            key = (local.year, local.month)
            totals[key] = totals.get(key, 0) + _excl_tax(int(row["amount_incl_tax"]))
    if not totals:
        return {}

    y, m = min(totals)
    last = max(totals)
    result = {}
    while (y, m) <= last:
        result[f"{y:04d}-{m:02d}"] = totals.get((y, m), 0)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return result
