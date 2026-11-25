import csv
from collections import defaultdict
from datetime import datetime, timedelta, timezone

# JST has no daylight saving time, so a fixed offset is sufficient.
JST = timezone(timedelta(hours=9))


def monthly_sales(path, tz=JST, exclude_statuses=("cancelled",)):
    """sales.csv を月次で集計し {"YYYY-MM": 金額(int)} を返す。

    - 月の判定は ordered_at を tz (既定: JST) に変換して行う
    - status が exclude_statuses に含まれる行は除外する
    - 金額は amount_incl_tax (税込) をそのまま合計する (マイナス値=返金等も含む)
    """
    excluded = {s.strip().lower() for s in exclude_statuses}
    totals = defaultdict(int)
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if (row.get("status") or "").strip().lower() in excluded:
                continue
            ordered_at = datetime.fromisoformat(row["ordered_at"].strip().replace("Z", "+00:00"))
            if ordered_at.tzinfo is None:
                ordered_at = ordered_at.replace(tzinfo=timezone.utc)
            month = ordered_at.astimezone(tz).strftime("%Y-%m")
            totals[month] += int(row["amount_incl_tax"].strip())
    return dict(sorted(totals.items()))
