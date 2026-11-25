import csv
from datetime import datetime, timedelta

WORK_TYPE = "work"


def _parse_time(value):
    value = value.strip()
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise ValueError(f"invalid time: {value!r}")


def _shift_hours(start, end):
    s = _parse_time(start)
    e = _parse_time(end)
    if e < s:
        # Overnight shift (e.g. 22:00-06:00): end is on the next day.
        e += timedelta(days=1)
    return (e - s).total_seconds() / 3600.0


def monthly_work_hours(path, month=None):
    """Sum work hours per employee from a shifts CSV.

    month: optional "YYYY-MM" filter; shifts are attributed to the month of
    their start date. If omitted, all rows are aggregated.
    """
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            emp = (row.get("employee") or "").strip()
            if not emp:
                continue
            date = (row.get("date") or "").strip()
            if month is not None and not date.startswith(month):
                continue
            totals.setdefault(emp, 0.0)
            if (row.get("type") or "").strip().lower() != WORK_TYPE:
                continue
            start = (row.get("start") or "").strip()
            end = (row.get("end") or "").strip()
            if not start or not end:
                continue
            totals[emp] += _shift_hours(start, end)
    return totals
