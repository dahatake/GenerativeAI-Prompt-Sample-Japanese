import csv
import re
from collections import defaultdict
from datetime import date


_REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")


def _clock_minutes(value: str) -> int:
    match = re.fullmatch(r"([0-9]{2}):([0-9]{2})", value)
    if match is None:
        raise ValueError(f"Invalid time: {value!r}")
    hour, minute = map(int, match.groups())
    if hour > 23 or minute > 59:
        raise ValueError(f"Invalid time: {value!r}")
    return hour * 60 + minute


def _work_minutes(start: str, end: str) -> int:
    elapsed = _clock_minutes(end) - _clock_minutes(start)
    if elapsed < 0:
        elapsed += 24 * 60
    net = elapsed - 60 if elapsed > 360 else elapsed
    return (net // 15) * 15


def monthly_work_hours(path) -> dict[str, float]:
    """Return hours by employee for the single start-date month in the CSV."""
    totals = defaultdict(int)
    month = None
    try:
        with open(path, encoding="utf-8-sig", newline="") as source:
            rows = csv.reader(source, strict=True)
            header = next((row for row in rows if row), [])
            if not set(_REQUIRED_COLUMNS).issubset(header) or len(set(header)) != len(header):
                raise ValueError("Missing or duplicate CSV column names")
            indexes = [header.index(column) for column in _REQUIRED_COLUMNS]

            for row in rows:
                if not row:
                    continue
                if len(row) != len(header):
                    raise ValueError(f"Line {rows.line_num}: wrong column count")
                employee, day, kind, start, end = (row[i].strip() for i in indexes)
                if not employee:
                    raise ValueError(f"Line {rows.line_num}: missing employee ID")
                start_date = date.fromisoformat(day)
                if start_date.isoformat() != day:
                    raise ValueError(f"Line {rows.line_num}: expected YYYY-MM-DD")
                if kind == "work":
                    minutes = _work_minutes(start, end)
                elif kind == "paid_leave":
                    minutes = 450
                else:
                    raise ValueError(f"Line {rows.line_num}: unknown shift type {kind!r}")

                row_month = (start_date.year, start_date.month)
                if month is None:
                    month = row_month
                elif row_month != month:
                    raise ValueError("CSV contains multiple start-date months")
                totals[employee] += minutes
    except csv.Error as error:
        raise ValueError(f"Invalid CSV: {error}") from error

    return {employee: totals[employee] / 60 for employee in sorted(totals)}
