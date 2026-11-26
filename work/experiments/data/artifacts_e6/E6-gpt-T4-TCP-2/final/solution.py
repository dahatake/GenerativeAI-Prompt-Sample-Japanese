import csv
import re
from datetime import date


_REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_TIME = re.compile(r"([01][0-9]|2[0-3]):([0-5][0-9])")


def _clock_minutes(text: str, line: int) -> int:
    match = _TIME.fullmatch(text)
    if match is None:
        raise ValueError(f"Line {line}: invalid time {text!r}; expected HH:MM")
    hour, minute = map(int, match.groups())
    return hour * 60 + minute


def monthly_work_hours(path) -> dict[str, float]:
    """Return hours per employee for a single month of shifts and paid leave."""
    totals: dict[str, int] = {}
    month = None
    with open(path, encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        try:
            headers = reader.fieldnames or []
            if any(headers.count(name) != 1 for name in _REQUIRED_COLUMNS):
                raise ValueError("CSV must contain each required column exactly once")

            for row in reader:
                line = reader.line_num
                if None in row or any(row[name] is None for name in _REQUIRED_COLUMNS):
                    raise ValueError(f"Line {line}: invalid number of fields")

                employee = row["employee"]
                if not employee.strip():
                    raise ValueError(f"Line {line}: employee ID is empty")

                day = row["date"]
                try:
                    if not _DATE.fullmatch(day):
                        raise ValueError("expected YYYY-MM-DD")
                    shift_date = date.fromisoformat(day)
                except ValueError as exc:
                    raise ValueError(f"Line {line}: invalid date {day!r}") from exc
                shift_month = (shift_date.year, shift_date.month)
                if month is None:
                    month = shift_month
                elif shift_month != month:
                    raise ValueError(f"Line {line}: CSV must cover a single month")

                kind = row["type"]
                if kind == "work":
                    start = _clock_minutes(row["start"], line)
                    end = _clock_minutes(row["end"], line)
                    minutes = (end - start) % (24 * 60)
                    if minutes > 360:
                        minutes -= 60
                    minutes -= minutes % 15
                elif kind == "paid_leave":
                    minutes = 450
                else:
                    raise ValueError(f"Line {line}: unknown shift type {kind!r}")

                totals[employee] = totals.get(employee, 0) + minutes
        except csv.Error as exc:
            raise ValueError(f"Malformed CSV near line {reader.line_num}") from exc

    return {employee: minutes / 60 for employee, minutes in totals.items()}
