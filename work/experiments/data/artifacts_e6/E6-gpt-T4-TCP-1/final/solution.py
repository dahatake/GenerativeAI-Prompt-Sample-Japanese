import csv
import re
from datetime import date

_REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_TIME = re.compile(r"([01][0-9]|2[0-3]):([0-5][0-9])")


def _minute_of_day(value: str | None) -> int:
    match = _TIME.fullmatch(value) if value is not None else None
    if match is None:
        raise ValueError(f"expected an HH:MM time, got {value!r}")
    return 60 * int(match[1]) + int(match[2])


def _elapsed_minutes(start: str | None, end: str | None) -> int:
    return (_minute_of_day(end) - _minute_of_day(start)) % (24 * 60)


def _work_minutes(elapsed: int) -> int:
    return elapsed - 60 if elapsed > 360 else elapsed


def monthly_work_hours(path) -> dict[str, float]:
    """Return hours by employee for a CSV containing one calendar month."""
    totals: dict[str, int] = {}
    month = None
    with open(path, encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        try:
            columns = reader.fieldnames
            if columns is None or any(columns.count(name) != 1 for name in _REQUIRED_COLUMNS):
                raise ValueError("CSV must contain one of each required column: employee,date,type,start,end")
            for row in reader:
                try:
                    if None in row:
                        raise ValueError("more fields than in the header")
                    employee = row["employee"]
                    if not employee or not employee.strip():
                        raise ValueError("employee ID is missing or blank")
                    raw_date = row["date"]
                    if not raw_date or not _DATE.fullmatch(raw_date):
                        raise ValueError("date must have format YYYY-MM-DD")
                    day = date.fromisoformat(raw_date)
                    row_month = (day.year, day.month)
                    if month is None:
                        month = row_month
                    elif row_month != month:
                        raise ValueError("dates must be in one calendar month")

                    kind = row["type"]
                    if kind == "work":
                        minutes = _work_minutes(_elapsed_minutes(row["start"], row["end"]))
                    elif kind == "paid_leave":
                        minutes = 450
                    else:
                        raise ValueError(f"unknown shift type: {kind!r}")
                    totals[employee] = totals.get(employee, 0) + (minutes // 15) * 15
                except ValueError as exc:
                    raise ValueError(f"CSV line {reader.line_num}: {exc}") from exc
        except csv.Error as exc:
            raise ValueError(f"invalid CSV near line {reader.line_num}: {exc}") from exc
    return {employee: minutes / 60 for employee, minutes in totals.items()}
