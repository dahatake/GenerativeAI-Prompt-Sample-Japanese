import csv
import re
from datetime import date, time

_REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")


def _shift_date(value: str) -> date:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("date must use YYYY-MM-DD")
    return date.fromisoformat(value)


def _clock_minutes(value: str) -> int:
    if not re.fullmatch(r"[0-9]{2}:[0-9]{2}", value):
        raise ValueError("work times must use HH:MM")
    clock = time.fromisoformat(value)
    return clock.hour * 60 + clock.minute


def _credited_minutes(kind: str, start: str, end: str) -> int:
    if kind == "paid_leave":
        return 450
    if kind != "work":
        raise ValueError("type must be work or paid_leave")

    duration = _clock_minutes(end) - _clock_minutes(start)
    if duration < 0:
        duration += 24 * 60
    net_minutes = duration - 60 if duration > 360 else duration
    return (net_minutes // 15) * 15


def monthly_work_hours(path) -> dict[str, float]:
    """Return hours by employee for one month, using each shift's start date."""
    totals: dict[str, int] = {}
    target_month = None

    try:
        with open(path, encoding="utf-8-sig", newline="") as source:
            rows = csv.reader(source, strict=True)
            header = next((fields for fields in rows if fields), [])
            if len(set(header)) != len(header):
                raise ValueError("duplicate CSV column names")
            if not set(_REQUIRED_COLUMNS).issubset(header):
                raise ValueError("missing required CSV columns")
            indexes = [header.index(column) for column in _REQUIRED_COLUMNS]

            for fields in rows:
                if not fields:
                    continue
                if len(fields) != len(header):
                    raise ValueError(f"wrong number of columns on line {rows.line_num}")
                employee, date_text, kind, start, end = (fields[index].strip() for index in indexes)
                if not employee:
                    raise ValueError(f"missing employee on line {rows.line_num}")

                shift_date = _shift_date(date_text)
                month = shift_date.year, shift_date.month
                if target_month is None:
                    target_month = month
                elif month != target_month:
                    raise ValueError("CSV contains shifts from more than one month")

                minutes = _credited_minutes(kind, start, end)
                totals[employee] = totals.get(employee, 0) + minutes
    except csv.Error as error:
        raise ValueError(f"invalid CSV: {error}") from error

    return {employee: totals[employee] / 60 for employee in sorted(totals)}
