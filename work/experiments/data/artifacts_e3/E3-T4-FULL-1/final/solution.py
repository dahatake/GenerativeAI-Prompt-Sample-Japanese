import csv
from collections import defaultdict

BREAK_THRESHOLD_MIN = 6 * 60
BREAK_MIN = 60
ROUND_UNIT_MIN = 15
PAID_LEAVE_MIN = 450  # 7.5 hours


def _to_minutes(value):
    parts = value.strip().split(":")
    hours, minutes = int(parts[0]), int(parts[1])
    seconds = int(parts[2]) if len(parts) > 2 else 0
    return hours * 60 + minutes + seconds / 60


def _shift_minutes(start, end):
    start_min = _to_minutes(start)
    end_min = _to_minutes(end)
    if end_min < start_min:
        end_min += 24 * 60
    duration = end_min - start_min
    if duration > BREAK_THRESHOLD_MIN:
        duration -= BREAK_MIN
    return int(duration // ROUND_UNIT_MIN) * ROUND_UNIT_MIN


def monthly_work_hours(path):
    totals = defaultdict(int)
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            employee = (row.get("employee") or "").strip()
            if not employee:
                continue
            row_type = (row.get("type") or "").strip().lower()
            if row_type == "paid_leave":
                totals[employee] += PAID_LEAVE_MIN
            elif row_type == "work":
                totals[employee] += _shift_minutes(row["start"], row["end"])
    return {employee: minutes / 60 for employee, minutes in totals.items()}
