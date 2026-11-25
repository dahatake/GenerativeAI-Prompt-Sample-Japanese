import csv
from datetime import datetime, timedelta
def monthly_work_hours(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            e = r["employee"]
            if r["type"] == "paid_leave":
                h = 7.5
            else:
                s = datetime.strptime(r["start"], "%H:%M"); t = datetime.strptime(r["end"], "%H:%M")
                if t < s:
                    t += timedelta(days=1)
                m = int((t - s).total_seconds() // 60)
                if m > 360:
                    m -= 60
                m = m // 15 * 15
                h = m / 60
            out[e] = out.get(e, 0.0) + h
    return out
