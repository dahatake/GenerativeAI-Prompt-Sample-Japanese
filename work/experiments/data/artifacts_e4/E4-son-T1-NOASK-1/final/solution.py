import csv
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))


def monthly_sales(path):
    """completed のみを JST の月で集計する（税込金額の合計）。"""
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["status"].strip() != "completed":
                continue
            ordered_at = datetime.fromisoformat(row["ordered_at"].strip().replace("Z", "+00:00"))
            key = ordered_at.astimezone(JST).strftime("%Y-%m")
            totals[key] = totals.get(key, 0) + int(row["amount_incl_tax"])
    return dict(sorted(totals.items()))
