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
    - 最初の月から最後の月まで、注文がない月も 0 で含める
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

    if not totals:
        return {}

    # 最初の月〜最後の月の間は、注文がない月も 0 で含める
    first, last = min(totals), max(totals)
    y, m = int(first[:4]), int(first[5:])
    months = []
    while f"{y:04d}-{m:02d}" <= last:
        months.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)

    divisor = 100 + tax_rate_percent
    result = {}
    for month in months:
        gross = totals.get(month, 0)
        if tax_rate_percent:
            num = gross * 100
            q, r = divmod(abs(num), divisor)
            q += 1 if r * 2 >= divisor else 0
            result[month] = q if gross >= 0 else -q
        else:
            result[month] = gross
    return result
