import csv
from collections import defaultdict

WORK_TYPE = "work"


def _to_minutes(value):
    hh, mm = value.strip().split(":")
    h, m = int(hh), int(mm)
    if not (0 <= h <= 24 and 0 <= m < 60) or (h == 24 and m != 0):
        raise ValueError(f"invalid time: {value!r}")
    return h * 60 + m


def monthly_work_hours(path, month=None):
    """Aggregate working hours per employee from an attendance CSV.

    Columns: employee,date,type,start,end (HH:MM). Only ``type == "work"`` rows
    are counted. If end < start the shift is treated as crossing midnight and is
    attributed to the month of ``date``. ``month`` ("YYYY-MM") optionally
    restricts aggregation to that month.
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
            if (row.get("type") or "").strip().lower() != WORK_TYPE:
                continue
            start, end = (row.get("start") or "").strip(), (row.get("end") or "").strip()
            if not start or not end:
                raise ValueError(f"work row without start/end: {row}")
            minutes = _to_minutes(end) - _to_minutes(start)
            if minutes < 0:
                minutes += 24 * 60
            totals[emp] += minutes / 60
    return dict(totals)
