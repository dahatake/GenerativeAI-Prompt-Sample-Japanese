import csv
from datetime import datetime

BREAK_THRESHOLD_MINUTES = 6 * 60
BREAK_MINUTES = 60
ROUNDING_UNIT_MINUTES = 15
PAID_LEAVE_MINUTES = 7 * 60 + 30
MINUTES_PER_DAY = 24 * 60


def _parse_minutes(value, field, line_no):
    text = (value or "").strip()
    try:
        t = datetime.strptime(text, "%H:%M")
    except ValueError:
        raise ValueError(f"line {line_no}: invalid {field} time {value!r} (expected HH:MM)") from None
    return t.hour * 60 + t.minute


def _shift_minutes(start, end, line_no):
    start_min = _parse_minutes(start, "start", line_no)
    end_min = _parse_minutes(end, "end", line_no)
    duration = end_min - start_min
    if duration < 0:
        # end before start: the shift ends on the following day
        duration += MINUTES_PER_DAY
    if duration > BREAK_THRESHOLD_MINUTES:
        duration -= BREAK_MINUTES
    return duration // ROUNDING_UNIT_MINUTES * ROUNDING_UNIT_MINUTES


def monthly_work_hours(path):
    """Return {employee_id: work hours (float)} aggregated over all rows of the CSV.

    - work: (end - start) [+24h if end < start], minus 60 min if over 6h,
      then floored to 15-minute units per shift.
    - paid_leave: 7.5h per row.
    - other types: 0h (the employee still appears in the result).
    """
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):
            employee = (row.get("employee") or "").strip()
            if not employee:
                raise ValueError(f"line {line_no}: missing employee")
            kind = (row.get("type") or "").strip()
            if kind == "work":
                minutes = _shift_minutes(row.get("start"), row.get("end"), line_no)
            elif kind == "paid_leave":
                minutes = PAID_LEAVE_MINUTES
            else:
                minutes = 0
            totals[employee] = totals.get(employee, 0) + minutes
    return {employee: minutes / 60 for employee, minutes in totals.items()}
