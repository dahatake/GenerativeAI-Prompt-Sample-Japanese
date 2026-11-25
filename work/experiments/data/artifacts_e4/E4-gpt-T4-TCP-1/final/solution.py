import csv
import re
from datetime import date


_REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")


def _clock_minutes(value, line):
    if re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", value) is None:
        raise ValueError(f"line {line}: invalid time {value!r}; expected HH:MM")
    return int(value[:2]) * 60 + int(value[3:])


def _work_minutes(start, end, line):
    minutes = _clock_minutes(end, line) - _clock_minutes(start, line)
    if minutes < 0:
        minutes += 24 * 60
    if minutes > 360:
        minutes -= 60
    return minutes // 15 * 15


def monthly_work_hours(path):
    """Return hours by employee for a single month of shifts and paid leave."""
    totals = {}
    month = None
    with open(path, encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source, strict=True)
        try:
            header = next(reader, [])
            missing = set(_REQUIRED_COLUMNS).difference(header)
            if missing:
                raise ValueError(f"missing CSV columns: {', '.join(sorted(missing))}")
            if len(set(header)) != len(header):
                raise ValueError("duplicate CSV column names")
            indexes = [header.index(column) for column in _REQUIRED_COLUMNS]

            for row in reader:
                if not row:
                    continue
                line = reader.line_num
                if len(row) != len(header):
                    raise ValueError(f"line {line}: unexpected number of columns")
                employee, day, kind, start, end = (row[index] for index in indexes)
                if not employee.strip():
                    raise ValueError(f"line {line}: employee ID is required")
                try:
                    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", day) is None:
                        raise ValueError
                    shift_date = date.fromisoformat(day)
                except ValueError as exc:
                    raise ValueError(f"line {line}: invalid date {day!r}; expected YYYY-MM-DD") from exc
                row_month = (shift_date.year, shift_date.month)
                if month is None:
                    month = row_month
                elif row_month != month:
                    raise ValueError(f"line {line}: CSV contains more than one calendar month")

                if kind == "work":
                    minutes = _work_minutes(start, end, line)
                elif kind == "paid_leave":
                    if start or end:
                        raise ValueError(f"line {line}: paid_leave requires blank start and end")
                    minutes = 450
                else:
                    raise ValueError(f"line {line}: unknown shift type {kind!r}")
                totals[employee] = totals.get(employee, 0) + minutes
        except csv.Error as exc:
            raise ValueError(f"line {reader.line_num}: invalid CSV: {exc}") from exc

    return {employee: minutes / 60 for employee, minutes in totals.items()}
