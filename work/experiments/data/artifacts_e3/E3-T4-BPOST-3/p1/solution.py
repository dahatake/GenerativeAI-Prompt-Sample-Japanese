import csv
from collections import defaultdict

WORK_TYPE = "work"
MINUTES_PER_DAY = 24 * 60


def _to_minutes(value, line_no):
    parts = value.strip().split(":")
    if len(parts) not in (2, 3):
        raise ValueError(f"line {line_no}: invalid time {value!r}")
    try:
        h, m = int(parts[0]), int(parts[1])
        s = int(parts[2]) if len(parts) == 3 else 0
    except ValueError:
        raise ValueError(f"line {line_no}: invalid time {value!r}") from None
    if not (0 <= h <= 24 and 0 <= m < 60 and 0 <= s < 60) or (h == 24 and (m or s)):
        raise ValueError(f"line {line_no}: invalid time {value!r}")
    return h * 60 + m + s / 60


def monthly_work_hours(path, month=None):
    """Sum worked hours per employee from a shift CSV.

    Columns: employee, date, type, start, end. Only rows with type "work"
    are counted; an end time at or before the start time is treated as a
    shift that crosses midnight. If ``month`` ("YYYY-MM") is given, only
    shifts whose start date falls in that month are counted.
    """
    minutes = defaultdict(float)
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
            emp = row.get("employee", "")
            if not emp:
                continue
            if month is not None and not row.get("date", "").startswith(month):
                continue
            minutes.setdefault(emp, 0.0)
            if row.get("type", "").lower() != WORK_TYPE:
                continue
            start, end = row.get("start", ""), row.get("end", "")
            if not start or not end:
                raise ValueError(f"line {line_no}: work row missing start/end")
            duration = _to_minutes(end, line_no) - _to_minutes(start, line_no)
            if duration <= 0:
                duration += MINUTES_PER_DAY
            minutes[emp] += duration
    return {emp: m / 60 for emp, m in minutes.items()}
