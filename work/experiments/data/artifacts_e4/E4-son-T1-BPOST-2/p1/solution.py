import csv
from collections import defaultdict
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))


def monthly_sales(path, tz=JST, tax_rate_percent=10, exclude_statuses=("cancelled",)):
    """sales.csv を月次集計し {"YYYY-MM": 税抜売上(int)} を返す。

    - ordered_at (UTC) を tz (既定 JST) に変換して月を決める
    - status が exclude_statuses の行は除外
    - 負の金額 (返金) はそのまま相殺
    - amount_incl_tax は税込なので、月ごとの合計を税率で割って税抜にする (四捨五入)
      tax_rate_percent=0 を渡すと税込のまま集計
    """
    excluded = {s.lower() for s in exclude_statuses}
    totals = defaultdict(int)
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if (row.get("status") or "").strip().lower() in excluded:
                continue
            ts = datetime.fromisoformat(row["ordered_at"].strip().replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            local = ts.astimezone(tz)
            totals[f"{local.year:04d}-{local.month:02d}"] += int(row["amount_incl_tax"])

    divisor = 100 + tax_rate_percent
    result = {}
    for month in sorted(totals):
        gross = totals[month]
        if tax_rate_percent:
            num = gross * 100
            q, r = divmod(abs(num), divisor)
            q += 1 if r * 2 >= divisor else 0
            result[month] = q if gross >= 0 else -q
        else:
            result[month] = gross
    return result
