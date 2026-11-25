import csv
from collections import defaultdict

WORK_TYPE = "work"
PAID_LEAVE_TYPE = "paid_leave"
MINUTES_PER_DAY = 24 * 60
PAID_LEAVE_MINUTES = 7.5 * 60
BREAK_THRESHOLD_MINUTES = 6 * 60
BREAK_MINUTES = 60
ROUNDING_UNIT_MINUTES = 15


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

    Columns: employee, date, type, start, end.
    - "work": end at or before start means the shift crosses midnight.
      Shifts longer than 6 hours get a 60-minute break deducted, then the
      result is floored to 15-minute units.
    - "paid_leave": counted as 7.5 hours.
    - Other types are ignored.
    If ``month`` ("YYYY-MM") is given, only rows whose date falls in that
    month are counted.
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
            row_type = row.get("type", "").lower()
            if row_type == PAID_LEAVE_TYPE:
                minutes[emp] += PAID_LEAVE_MINUTES
                continue
            if row_type != WORK_TYPE:
                continue
            start, end = row.get("start", ""), row.get("end", "")
            if not start or not end:
                raise ValueError(f"line {line_no}: work row missing start/end")
            duration = _to_minutes(end, line_no) - _to_minutes(start, line_no)
            if duration <= 0:
                duration += MINUTES_PER_DAY
            if duration > BREAK_THRESHOLD_MINUTES:
                duration -= BREAK_MINUTES
            duration = (duration // ROUNDING_UNIT_MINUTES) * ROUNDING_UNIT_MINUTES
            minutes[emp] += duration
    return {emp: m / 60 for emp, m in minutes.items()}
