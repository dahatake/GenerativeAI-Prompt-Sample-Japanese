import csv
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

JST = timezone(timedelta(hours=9))
TAX_RATE = Decimal("0.10")


def _month_range(first, last):
    y, m = map(int, first.split("-"))
    while f"{y:04d}-{m:02d}" <= last:
        yield f"{y:04d}-{m:02d}"
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def monthly_sales(path, tz=JST, exclude_statuses=("cancelled",)):
    """sales.csv を月次集計し {"YYYY-MM": 税抜金額(int)} を返す。

    - 月の判定は ordered_at(UTC) を tz（既定: JST）に変換して行う
    - status が exclude_statuses に含まれる行（既定: cancelled）は除外
    - 金額は amount_incl_tax（税込10%）を月ごとに合算し、税込 / 1.1 を四捨五入して整数化
    - 負値（返金等）も合算する
    - 最初の月から最後の月まで、注文のない月も 0 で含める
    """
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["status"].strip() in exclude_statuses:
                continue
            ts = datetime.fromisoformat(row["ordered_at"].strip().replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            key = ts.astimezone(tz).strftime("%Y-%m")
            totals[key] = totals.get(key, 0) + int(row["amount_incl_tax"].strip())
    if not totals:
        return {}
    return {
        month: int((Decimal(totals.get(month, 0)) / (1 + TAX_RATE)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        for month in _month_range(min(totals), max(totals))
    }
