import csv
from datetime import date, time


_REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")


def _minutes_since_midnight(value: str) -> int:
    parsed = time.fromisoformat(value)
    if parsed.isoformat(timespec="minutes") != value:
        raise ValueError(f"expected HH:MM, got {value!r}")
    return parsed.hour * 60 + parsed.minute


def _parse_shift(row, columns):
    employee, date_text, kind, start, end = (row[index] for index in columns)
    if not employee.strip():
        raise ValueError("employee ID is required")

    work_date = date.fromisoformat(date_text)
    if work_date.isoformat() != date_text:
        raise ValueError(f"expected YYYY-MM-DD, got {date_text!r}")

    if kind == "work":
        duration = _minutes_since_midnight(end) - _minutes_since_midnight(start)
        if duration < 0:
            duration += 24 * 60
    elif kind == "paid_leave":
        duration = 0
    else:
        raise ValueError(f"unknown shift type: {kind!r}")

    return employee, (work_date.year, work_date.month), duration


def monthly_work_hours(path) -> dict[str, float]:
    """Return hours per employee for a single month, assigning shifts to their start date."""
    minutes_by_employee = {}
    month = None

    with open(path, encoding="utf-8-sig", newline="") as source:
        rows = csv.reader(source, strict=True)
        try:
            header = next(rows, [])
            if len(set(header)) != len(header):
                raise ValueError("CSV header contains duplicate columns")
            if not set(_REQUIRED_COLUMNS).issubset(header):
                raise ValueError(f"CSV header must contain {', '.join(_REQUIRED_COLUMNS)}")
            columns = [header.index(name) for name in _REQUIRED_COLUMNS]

            for row in rows:
                if not row:
                    continue
                try:
                    if len(row) != len(header):
                        raise ValueError("row does not match the header column count")
                    employee, shift_month, duration = _parse_shift(row, columns)
                    if month is not None and shift_month != month:
                        raise ValueError("CSV contains multiple calendar months")
                except ValueError as exc:
                    raise ValueError(f"line {rows.line_num}: {exc}") from exc

                month = shift_month
                minutes_by_employee[employee] = minutes_by_employee.get(employee, 0) + duration
        except csv.Error as exc:
            raise ValueError(f"line {rows.line_num}: invalid CSV: {exc}") from exc

    return {employee: minutes / 60 for employee, minutes in minutes_by_employee.items()}
