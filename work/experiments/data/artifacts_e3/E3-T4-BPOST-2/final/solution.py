import csv
from collections import defaultdict

WORK_TYPE = "work"
PAID_LEAVE_TYPE = "paid_leave"
PAID_LEAVE_MINUTES = 450  # 所定労働時間 7.5h
BREAK_THRESHOLD_MINUTES = 360  # 拘束 6h を「超える」場合に休憩を控除
BREAK_MINUTES = 60
ROUNDING_UNIT_MINUTES = 15


def _to_minutes(value):
    hh, mm = value.strip().split(":")
    h, m = int(hh), int(mm)
    if not (0 <= h <= 24 and 0 <= m < 60) or (h == 24 and m != 0):
        raise ValueError(f"invalid time: {value!r}")
    return h * 60 + m


def monthly_work_hours(path, month=None):
    """Aggregate working hours per employee from an attendance CSV.

    Columns: employee,date,type,start,end (HH:MM).
    - ``work``: end - start (end < start means the shift crosses midnight and is
      attributed to the month of ``date``); 60 min break is deducted when the
      span exceeds 6h; the result is floored to 15-minute units.
    - ``paid_leave``: counted as 7.5h.
    - other types: 0h.
    ``month`` ("YYYY-MM") optionally restricts aggregation to that month.
    """
    totals = defaultdict(float)
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            emp = (row.get("employee") or "").strip()
            if not emp:
                continue
            date = (row.get("date") or "").strip()
            if month is not None and not date.startswith(month):
                continue
            totals[emp] += 0.0
            row_type = (row.get("type") or "").strip().lower()
            if row_type == PAID_LEAVE_TYPE:
                totals[emp] += PAID_LEAVE_MINUTES / 60
                continue
            if row_type != WORK_TYPE:
                continue
            start, end = (row.get("start") or "").strip(), (row.get("end") or "").strip()
            if not start or not end:
                raise ValueError(f"work row without start/end: {row}")
            minutes = _to_minutes(end) - _to_minutes(start)
            if minutes < 0:
                minutes += 24 * 60
            if minutes > BREAK_THRESHOLD_MINUTES:
                minutes -= BREAK_MINUTES
            minutes -= minutes % ROUNDING_UNIT_MINUTES
            totals[emp] += minutes / 60
    return dict(totals)
