import csv
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

JST = timezone(timedelta(hours=9), "JST")
TAX_RATE = Decimal("0.10")


def _to_tax_excluded(amount_incl_tax):
    return int((Decimal(amount_incl_tax) / (1 + TAX_RATE)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _month_range(first, last):
    y, m = map(int, first.split("-"))
    while f"{y:04d}-{m:02d}" <= last:
        yield f"{y:04d}-{m:02d}"
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def monthly_sales(path, tz=JST, exclude_statuses=("cancelled",)):
    """sales.csv を月次集計し {"YYYY-MM": 税抜金額(int)} を返す。

    - ordered_at (UTC の ISO8601) を tz (既定: JST) に変換して月を決める
    - status が exclude_statuses に含まれる行は除外 (既定: cancelled)
    - amount_incl_tax (税込10%) を月ごとに合算し、税抜 (÷1.1, 四捨五入) に換算
    - 負値 (返金) も含めて差し引く
    - 最初の月から最後の月まで、注文がない月も 0 で出力する
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
    if not totals:
        return {}
    return {
        month: _to_tax_excluded(totals.get(month, 0))
        for month in _month_range(min(totals), max(totals))
    }
