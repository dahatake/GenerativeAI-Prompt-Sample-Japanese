import csv
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))


def monthly_sales(path, tz=JST, include_statuses=("completed",)):
    """sales.csv を月次集計し {"YYYY-MM": 金額(int)} を返す。

    - 月の判定は ordered_at (UTC) を tz (既定: JST) に変換して行う
    - status が include_statuses に含まれる行のみ集計 (既定: completed のみ)
    - amount_incl_tax (税込) をそのまま合算し、負の値 (返金等) も含める
    """
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["status"].strip() not in include_statuses:
                continue
            ordered_at = datetime.fromisoformat(row["ordered_at"].strip().replace("Z", "+00:00"))
            if ordered_at.tzinfo is None:
                ordered_at = ordered_at.replace(tzinfo=timezone.utc)
            month = ordered_at.astimezone(tz).strftime("%Y-%m")
            totals[month] = totals.get(month, 0) + int(row["amount_incl_tax"].strip())
    return dict(sorted(totals.items()))
