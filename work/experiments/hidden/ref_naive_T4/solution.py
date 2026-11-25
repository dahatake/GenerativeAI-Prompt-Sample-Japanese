import csv
from datetime import datetime
def monthly_work_hours(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["type"] != "work":
                continue
            s = datetime.strptime(r["start"], "%H:%M"); t = datetime.strptime(r["end"], "%H:%M")
            out[r["employee"]] = out.get(r["employee"], 0.0) + (t - s).total_seconds() / 3600
    return out
