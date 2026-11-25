import csv
from datetime import datetime, timedelta, timezone

# JST は夏時間がないため固定オフセットで足りる（tzdata 非依存）
JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """sales.csv を JST 基準で月次集計し {"YYYY-MM": 税込金額(int)} を返す。

    cancelled は除外し、負の金額（返金）は差し引く。注文のない月は含めない。
    """
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["status"].strip().lower() == "cancelled":
                continue
            ordered = datetime.fromisoformat(row["ordered_at"].strip().replace("Z", "+00:00"))
            if ordered.tzinfo is None:
                ordered = ordered.replace(tzinfo=timezone.utc)
            key = ordered.astimezone(JST).strftime("%Y-%m")
            totals[key] = totals.get(key, 0) + int(row["amount_incl_tax"])
    return dict(sorted(totals.items()))
