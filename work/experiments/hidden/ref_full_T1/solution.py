import csv
from datetime import datetime, timedelta, timezone
JST = timezone(timedelta(hours=9))
def monthly_sales(path):
    tot = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["status"].strip().lower() == "cancelled":
                continue
            dt = datetime.fromisoformat(r["ordered_at"].replace("Z", "+00:00")).astimezone(JST)
            k = (dt.year, dt.month)
            tot[k] = tot.get(k, 0) + int(r["amount_incl_tax"])
    if not tot:
        return {}
    (y, m), end = min(tot), max(tot)
    out = {}
    while (y, m) <= end:
        out[f"{y:04d}-{m:02d}"] = int(tot.get((y, m), 0) * 10 // 11)
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out
