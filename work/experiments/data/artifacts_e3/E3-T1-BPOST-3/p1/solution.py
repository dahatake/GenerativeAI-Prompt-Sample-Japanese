import csv
from collections import defaultdict
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9), "JST")


def monthly_sales(path, tz=JST, exclude_statuses=("cancelled",)):
    """sales.csv を月次集計し {"YYYY-MM": 金額(int)} を返す。

    - ordered_at (UTC の ISO8601) を tz (既定: JST) に変換して月を決める
    - status が exclude_statuses に含まれる行は除外 (既定: cancelled)
    - 金額は amount_incl_tax (税込) をそのまま合算。負値 (返金等) も含める
    """
    excluded = {s.strip().lower() for s in exclude_statuses}
    totals = defaultdict(int)
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if (row.get("status") or "").strip().lower() in excluded:
                continue
            ts = datetime.fromisoformat(row["ordered_at"].strip().replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            month = ts.astimezone(tz).strftime("%Y-%m")
            totals[month] += int(row["amount_incl_tax"].strip())
    return dict(sorted(totals.items()))
