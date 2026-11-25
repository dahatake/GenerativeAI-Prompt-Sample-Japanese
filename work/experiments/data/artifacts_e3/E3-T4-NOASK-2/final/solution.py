import csv
from datetime import datetime

_KNOWN_TYPES = {"work", "paid_leave"}


def _parse_minutes(value, line_no):
    try:
        t = datetime.strptime(value.strip(), "%H:%M")
    except (ValueError, AttributeError):
        raise ValueError(f"line {line_no}: invalid time {value!r}") from None
    return t.hour * 60 + t.minute


def monthly_work_hours(path):
    """Return {employee_id: worked hours (float)} for a single-month shift CSV.

    - Only ``work`` rows count; ``paid_leave`` contributes 0h.
    - No break deduction is applied.
    - ``end <= start`` means the shift ends the next day (+24h) and is
      attributed to the month of ``date`` (the start date).
    - Raises ValueError for multiple months, unknown types or malformed rows.
    """
    totals = {}
    months = set()
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"employee", "date", "type", "start", "end"}
        if reader.fieldnames is None:
            return {}
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"missing columns: {sorted(missing)}")

        for line_no, row in enumerate(reader, start=2):
            emp = (row["employee"] or "").strip()
            if not emp:
                raise ValueError(f"line {line_no}: empty employee")
            try:
                day = datetime.strptime((row["date"] or "").strip(), "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"line {line_no}: invalid date {row['date']!r}") from None
            months.add((day.year, day.month))
            if len(months) > 1:
                raise ValueError(f"multiple months in file: {sorted(months)}")

            kind = (row["type"] or "").strip()
            if kind not in _KNOWN_TYPES:
                raise ValueError(f"line {line_no}: unknown type {kind!r}")

            totals.setdefault(emp, 0.0)
            if kind != "work":
                continue

            start = _parse_minutes(row["start"], line_no)
            end = _parse_minutes(row["end"], line_no)
            minutes = end - start
            if minutes <= 0:
                minutes += 24 * 60
            totals[emp] += minutes / 60.0

    return totals
