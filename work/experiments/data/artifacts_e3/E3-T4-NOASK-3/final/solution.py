"""Aggregate monthly working hours per employee from a shift CSV.

Rules (see contract.md):
- Breaks are not deducted; a shift counts as ``end - start``.
- If ``end <= start`` the shift is treated as ending on the next day.
- Only ``type == "work"`` rows count; other types contribute 0.0 hours
  but the employee still appears in the result.
- The file must cover a single month (by ``date``); otherwise ValueError.
  Overnight shifts are attributed entirely to the start date's month.
- Hours are not rounded.
"""

import csv
from datetime import datetime

REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")
_MINUTES_PER_DAY = 24 * 60


def _parse_minutes(value, line_no, field):
    try:
        t = datetime.strptime(value, "%H:%M")
    except ValueError:
        raise ValueError(
            f"line {line_no}: invalid {field} time {value!r} (expected HH:MM)"
        ) from None
    return t.hour * 60 + t.minute


def _shift_minutes(start, end, line_no):
    start_min = _parse_minutes(start, line_no, "start")
    end_min = _parse_minutes(end, line_no, "end")
    if end_min <= start_min:
        end_min += _MINUTES_PER_DAY
    return end_min - start_min


def monthly_work_hours(path):
    """Return ``{employee_id: hours}`` for the single month covered by ``path``."""
    minutes = {}
    months = set()

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header = [h.strip() for h in (reader.fieldnames or [])]
        missing = [c for c in REQUIRED_COLUMNS if c not in header]
        if missing:
            raise ValueError(f"missing required columns: {missing}")
        reader.fieldnames = header

        for row in reader:
            line_no = reader.line_num
            values = {k: (row.get(k) or "").strip() for k in REQUIRED_COLUMNS}
            if not any(values.values()):
                continue

            employee = values["employee"]
            if not employee:
                raise ValueError(f"line {line_no}: empty employee")

            try:
                date = datetime.strptime(values["date"], "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    f"line {line_no}: invalid date {values['date']!r} "
                    "(expected YYYY-MM-DD)"
                ) from None
            months.add((date.year, date.month))

            minutes.setdefault(employee, 0)
            if values["type"].lower() == "work":
                minutes[employee] += _shift_minutes(
                    values["start"], values["end"], line_no
                )

    if len(months) > 1:
        found = ", ".join(f"{y:04d}-{m:02d}" for y, m in sorted(months))
        raise ValueError(f"file contains multiple months: {found}")

    return {emp: m / 60.0 for emp, m in minutes.items()}
