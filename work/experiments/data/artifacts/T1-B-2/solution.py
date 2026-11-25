import csv
from collections import defaultdict
from datetime import datetime, timedelta, timezone, tzinfo

JST = timezone(timedelta(hours=9), "JST")


def monthly_sales(path, tz: tzinfo = JST, statuses=("completed",)):
    """sales.csv を月次集計し {"YYYY-MM": 金額(int)} を返す。

    - 金額は amount_incl_tax（税込）をそのまま合計する（負値＝返金等も含める）
    - status が statuses に含まれる行のみ集計（既定: completed のみ。cancelled は除外）
    - ordered_at (UTC) を tz（既定: JST）に変換してから月を判定する
    - 売上が無い月はキーに含めない
    """
    totals = defaultdict(int)
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["status"].strip() not in statuses:
                continue
            ordered_at = datetime.fromisoformat(row["ordered_at"].strip().replace("Z", "+00:00"))
            if ordered_at.tzinfo is None:
                ordered_at = ordered_at.replace(tzinfo=timezone.utc)
            month = ordered_at.astimezone(tz).strftime("%Y-%m")
            totals[month] += int(row["amount_incl_tax"].strip())
    return dict(sorted(totals.items()))
