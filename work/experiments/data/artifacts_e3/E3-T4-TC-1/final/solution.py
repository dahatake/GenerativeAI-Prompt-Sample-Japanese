"""Aggregate monthly working hours per employee from a shift CSV."""

import csv
import re
from datetime import date

REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")

BREAK_THRESHOLD_MINUTES = 6 * 60
BREAK_MINUTES = 60
ROUNDING_UNIT_MINUTES = 15
PAID_LEAVE_MINUTES = 450  # 7.5h

_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})$")


def _parse_minutes(value, field, line_no):
    match = _TIME_RE.match((value or "").strip())
    if not match:
        raise ValueError(f"line {line_no}: invalid {field} time {value!r}")
    hours, minutes = int(match.group(1)), int(match.group(2))
    if hours > 23 or minutes > 59:
        raise ValueError(f"line {line_no}: invalid {field} time {value!r}")
    return hours * 60 + minutes


def _work_minutes(start, end, line_no):
    start_min = _parse_minutes(start, "start", line_no)
    end_min = _parse_minutes(end, "end", line_no)
    duration = end_min - start_min
    if duration < 0:
        duration += 24 * 60  # shift ends on the next day
    if duration > BREAK_THRESHOLD_MINUTES:
        duration -= BREAK_MINUTES
    return duration - duration % ROUNDING_UNIT_MINUTES


def monthly_work_hours(path):
    """Return {employee_id: hours} summed over all rows of the shift CSV.

    - work: (end - start, +24h if end < start), minus 60 min if over 6h,
      floored to 15-minute units.
    - paid_leave: 7.5h.
    - other types: 0h (employee is still listed).
    Malformed rows raise ValueError.
    """
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header = [h.strip() for h in (reader.fieldnames or [])]
        missing = [c for c in REQUIRED_COLUMNS if c not in header]
        if reader.fieldnames is not None and missing:
            raise ValueError(f"missing required columns: {missing}")
        reader.fieldnames = header

        for row in reader:
            line_no = reader.line_num
            employee = (row.get("employee") or "").strip()
            if not employee:
                raise ValueError(f"line {line_no}: empty employee")
            raw_date = (row.get("date") or "").strip()
            try:
                date.fromisoformat(raw_date)
            except ValueError:
                raise ValueError(f"line {line_no}: invalid date {raw_date!r}") from None

            kind = (row.get("type") or "").strip()
            if kind == "work":
                minutes = _work_minutes(row.get("start"), row.get("end"), line_no)
            elif kind == "paid_leave":
                minutes = PAID_LEAVE_MINUTES
            else:
                minutes = 0
            totals[employee] = totals.get(employee, 0) + minutes

    return {emp: minutes / 60 for emp, minutes in totals.items()}
