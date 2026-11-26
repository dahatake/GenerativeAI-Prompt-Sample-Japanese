import csv
import re
from datetime import date


_REQUIRED_COLUMNS = {"employee", "date", "type", "start", "end"}
_MINUTES_PER_DAY = 24 * 60
_BREAK_THRESHOLD_MINUTES = 6 * 60
_BREAK_MINUTES = 60
_PAID_LEAVE_MINUTES = 7 * 60 + 30
_ROUNDING_MINUTES = 15


def _clock_minutes(value, line, field):
    if re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", value) is None:
        raise ValueError(f"Line {line}: {field} must be a time in HH:MM format")
    hours, minutes = map(int, value.split(":"))
    return hours * 60 + minutes


def monthly_work_hours(path):
    """Return credited hours per employee for shifts starting in one month."""
    totals = {}
    month = None
    with open(path, encoding="utf-8-sig", newline="") as source:
        rows = csv.reader(source, strict=True)
        header = next(rows, None)
        if header is None:
            return {}
        if not _REQUIRED_COLUMNS.issubset(header) or len(set(header)) != len(header):
            raise ValueError("CSV header must contain distinct employee,date,type,start,end columns")

        for values in rows:
            if not values:
                continue
            line = rows.line_num
            if len(values) != len(header):
                raise ValueError(f"Line {line}: field count does not match header")
            row = dict(zip(header, (value.strip() for value in values)))
            employee = row["employee"]
            if not employee:
                raise ValueError(f"Line {line}: employee ID is required")
            try:
                day = date.fromisoformat(row["date"])
            except ValueError as exc:
                raise ValueError(f"Line {line}: date must be in YYYY-MM-DD format") from exc
            if day.isoformat() != row["date"]:
                raise ValueError(f"Line {line}: date must be in YYYY-MM-DD format")
            row_month = (day.year, day.month)
            if month is None:
                month = row_month
            elif row_month != month:
                raise ValueError(f"Line {line}: shift dates span multiple months")

            if row["type"] == "paid_leave":
                duration = _PAID_LEAVE_MINUTES
            elif row["type"] == "work":
                start = _clock_minutes(row["start"], line, "start")
                end = _clock_minutes(row["end"], line, "end")
                duration = (end - start) % _MINUTES_PER_DAY
                if duration > _BREAK_THRESHOLD_MINUTES:
                    duration -= _BREAK_MINUTES
                duration -= duration % _ROUNDING_MINUTES
            else:
                raise ValueError(f"Line {line}: unsupported shift type {row['type']!r}")
            totals[employee] = totals.get(employee, 0) + duration

    return {employee: minutes / 60 for employee, minutes in totals.items()}
