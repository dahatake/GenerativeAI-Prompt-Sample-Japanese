import csv
import re
from datetime import date, time

_COLUMNS = {"employee", "date", "type", "start", "end"}
_MINUTES_PER_DAY = 24 * 60


def _shift_date(value):
    if not value or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("date must be in YYYY-MM-DD format")
    return date.fromisoformat(value)


def _clock_minutes(value):
    if not value or not re.fullmatch(r"[0-9]{2}:[0-9]{2}", value):
        raise ValueError("time must be in HH:MM format")
    clock = time.fromisoformat(value)
    return clock.hour * 60 + clock.minute


def monthly_work_hours(path) -> dict[str, float]:
    """Sum actual hours per employee for a CSV with a single shift-start month."""
    totals = {}
    month = None

    with open(path, encoding="utf-8-sig", newline="") as source:
        rows = csv.DictReader(source, strict=True)
        try:
            if not _COLUMNS.issubset(rows.fieldnames or ()):
                raise ValueError("CSV requires employee, date, type, start and end columns")

            for row in rows:
                try:
                    employee = row["employee"]
                    if not employee or not employee.strip():
                        raise ValueError("employee must not be empty")

                    shift_date = _shift_date(row["date"])
                    row_month = (shift_date.year, shift_date.month)
                    if month is not None and row_month != month:
                        raise ValueError("CSV contains more than one year-month")
                    month = row_month

                    kind = row["type"]
                    if kind == "work":
                        start = _clock_minutes(row["start"])
                        end = _clock_minutes(row["end"])
                        minutes = (end - start) % _MINUTES_PER_DAY
                    elif kind == "paid_leave":
                        for value in (row["start"], row["end"]):
                            if value:
                                _clock_minutes(value)
                        minutes = 0
                    else:
                        raise ValueError("type must be work or paid_leave")

                    totals[employee] = totals.get(employee, 0) + minutes
                except ValueError as exc:
                    raise ValueError(f"CSV line {rows.line_num}: {exc}") from exc
        except csv.Error as exc:
            raise ValueError(f"Invalid CSV near line {rows.line_num}: {exc}") from exc

    return {employee: minutes / 60 for employee, minutes in totals.items()}
