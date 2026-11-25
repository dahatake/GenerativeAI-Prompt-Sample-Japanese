import csv
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))


def monthly_sales(path, tz=JST, excluded_statuses=("cancelled",)):
    """sales.csv を月次集計し {"YYYY-MM": 金額(int)} を返す。

    - 月の判定は ordered_at (ISO8601, UTC) を tz (既定 JST) に変換した暦月
    - status が excluded_statuses の行は除外、返金(負額)は加算する
    - 金額は amount_incl_tax (税込) をそのまま合計する
    """
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if (row["status"] or "").strip().lower() in excluded_statuses:
                continue
            ts = datetime.fromisoformat(row["ordered_at"].strip().replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            key = ts.astimezone(tz).strftime("%Y-%m")
            totals[key] = totals.get(key, 0) + int(row["amount_incl_tax"])
    return dict(sorted(totals.items()))
