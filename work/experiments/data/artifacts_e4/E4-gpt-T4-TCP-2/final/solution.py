import csv
import re
from datetime import date


_REQUIRED_COLUMNS = {"employee", "date", "type", "start", "end"}
_TIME_FORMAT = re.compile(r"([0-9]{2}):([0-9]{2})")


def _minute_of_day(value: str | None, column: str, line: int) -> int:
    match = _TIME_FORMAT.fullmatch(value or "")
    if match:
        hour, minute = map(int, match.groups())
        if hour < 24 and minute < 60:
            return hour * 60 + minute
    raise ValueError(f"line {line}: {column} must be a time in HH:MM format")


def monthly_work_hours(path) -> dict[str, float]:
    """Return hours per employee for the single start-date month in the CSV."""
    minutes_by_employee: dict[str, int] = {}
    month: tuple[int, int] | None = None

    with open(path, encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source, strict=True)
        rows = (fields for fields in reader if fields)
        try:
            header = next(rows, [])
            missing = _REQUIRED_COLUMNS.difference(header)
            if missing:
                raise ValueError(f"missing CSV columns: {', '.join(sorted(missing))}")

            for fields in rows:
                line = reader.line_num
                row = dict(zip(header, fields))
                employee = row.get("employee")
                if employee is None or not employee.strip():
                    raise ValueError(f"line {line}: employee ID is required")

                raw_date = row.get("date") or ""
                try:
                    start_date = date.fromisoformat(raw_date)
                except ValueError as exc:
                    raise ValueError(f"line {line}: invalid date {raw_date!r}") from exc
                if start_date.isoformat() != raw_date:
                    raise ValueError(f"line {line}: date must use YYYY-MM-DD format")

                row_month = (start_date.year, start_date.month)
                if month is not None and row_month != month:
                    raise ValueError(f"line {line}: CSV contains more than one month")
                month = row_month

                shift_type = row.get("type")
                if shift_type == "paid_leave":
                    minutes = 450
                elif shift_type == "work":
                    start = _minute_of_day(row.get("start"), "start", line)
                    end = _minute_of_day(row.get("end"), "end", line)
                    elapsed = (end - start) % (24 * 60)
                    worked = elapsed - 60 if elapsed > 360 else elapsed
                    minutes = worked // 15 * 15
                else:
                    raise ValueError(f"line {line}: unknown shift type {shift_type!r}")

                minutes_by_employee[employee] = minutes_by_employee.get(employee, 0) + minutes
        except csv.Error as exc:
            raise ValueError(f"invalid CSV: {exc}") from exc

    return {employee: minutes / 60 for employee, minutes in minutes_by_employee.items()}
