import csv
from datetime import datetime

PAID_LEAVE_MINUTES = 450
BREAK_THRESHOLD_MINUTES = 360
BREAK_MINUTES = 60
ROUND_UNIT_MINUTES = 15


def _to_minutes(value):
    t = datetime.strptime(value.strip(), "%H:%M")
    return t.hour * 60 + t.minute


def _shift_minutes(start, end):
    try:
        s, e = _to_minutes(start), _to_minutes(end)
    except (ValueError, AttributeError):
        return 0
    if e < s:
        e += 24 * 60
    span = e - s
    if span > BREAK_THRESHOLD_MINUTES:
        span -= BREAK_MINUTES
    return span // ROUND_UNIT_MINUTES * ROUND_UNIT_MINUTES


def monthly_work_hours(path):
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            emp = (row.get("employee") or "").strip()
            if not emp:
                continue
            kind = (row.get("type") or "").strip()
            if kind == "work":
                minutes = _shift_minutes(row.get("start") or "", row.get("end") or "")
            elif kind == "paid_leave":
                minutes = PAID_LEAVE_MINUTES
            else:
                minutes = 0
            totals[emp] = totals.get(emp, 0) + minutes
    return {emp: m / 60 for emp, m in totals.items()}
