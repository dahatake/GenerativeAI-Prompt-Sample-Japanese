import csv
import re
from datetime import date


_REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")


def _csv_rows(stream):
    reader = csv.reader(stream, strict=True)
    while True:
        line_number = reader.line_num + 1
        try:
            row = next(reader)
        except StopIteration:
            return
        except csv.Error as error:
            raise ValueError(f"CSV line {line_number}: {error}") from error
        if row:
            yield line_number, row


def _shift_month(value, line_number):
    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            raise ValueError
        shift_date = date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"CSV line {line_number}: invalid date {value!r}") from None
    return shift_date.year, shift_date.month


def _time_in_minutes(value, field, line_number):
    if re.fullmatch(r"[0-9]{2}:[0-9]{2}", value):
        hour, minute = map(int, value.split(":"))
        if hour < 24 and minute < 60:
            return hour * 60 + minute
    raise ValueError(f"CSV line {line_number}: invalid {field} time {value!r}")


def monthly_work_hours(path):
    """Return hours by employee for the single start-date month in the CSV."""
    totals = {}
    month = None
    with open(path, encoding="utf-8-sig", newline="") as stream:
        rows = _csv_rows(stream)
        _, header = next(rows, (0, ()))
        if any(header.count(name) != 1 for name in _REQUIRED_COLUMNS):
            raise ValueError("CSV header must contain employee, date, type, start and end exactly once")
        employee_col, date_col, type_col, start_col, end_col = map(header.index, _REQUIRED_COLUMNS)

        for line_number, row in rows:
            if len(row) != len(header):
                raise ValueError(f"CSV line {line_number}: wrong number of columns")
            kind = row[type_col].strip()
            if not kind:
                raise ValueError(f"CSV line {line_number}: missing type")
            if kind not in {"work", "paid_leave"}:
                continue

            employee = row[employee_col].strip()
            if not employee:
                raise ValueError(f"CSV line {line_number}: missing employee ID")
            shift_month = _shift_month(row[date_col], line_number)
            if month is None:
                month = shift_month
            elif month != shift_month:
                raise ValueError(f"CSV line {line_number}: expected a single calendar month")

            if kind == "paid_leave":
                minutes = 450
            else:
                start = _time_in_minutes(row[start_col], "start", line_number)
                end = _time_in_minutes(row[end_col], "end", line_number)
                gross_minutes = (end - start) % (24 * 60)
                break_minutes = 60 if gross_minutes > 360 else 0
                net_minutes = max(0, gross_minutes - break_minutes)
                minutes = net_minutes - net_minutes % 15
            totals[employee] = totals.get(employee, 0) + minutes

    return {employee: totals[employee] / 60 for employee in sorted(totals)}
