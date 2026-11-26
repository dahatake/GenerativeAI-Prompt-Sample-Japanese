import csv
from datetime import datetime, timedelta
from typing import Dict, Union


EmployeeId = Union[str, int]
PAID_LEAVE_HOURS = 7.5
QUARTER_HOUR_SECONDS = 15 * 60


def _normalize_header(name):
    return str(name).strip().lower().replace(" ", "").replace("_", "").replace("-", "")


def _pick(row, names):
    normalized_names = {_normalize_header(name) for name in names}
    for name, value in row.items():
        if _normalize_header(name) in normalized_names:
            return value
    return None


def _parse_time(value):
    if value is None:
        raise ValueError("start/end time is missing")
    text = str(value).strip()
    if not text:
        raise ValueError("start/end time is missing")

    if text in ("24:00", "24:00:00"):
        return datetime(1900, 1, 1, 0, 0)

    for fmt in ("%H:%M:%S", "%H:%M", "%H%M"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass

    try:
        return datetime.strptime(text.upper(), "%I:%M %p")
    except ValueError:
        pass

    raise ValueError("invalid time: %r" % value)


def _floor_to_quarter_hour(seconds):
    return (int(seconds) // QUARTER_HOUR_SECONDS) * QUARTER_HOUR_SECONDS / 3600.0


def monthly_work_hours(path) -> Dict[EmployeeId, float]:
    """Aggregate work-shift durations by employee ID for the CSV period."""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            return totals

        for raw_row in reader:
            row = {str(key).strip(): value for key, value in raw_row.items() if key is not None}

            employee_value = _pick(row, (
                "employee_id", "employee", "employeeid", "staff_id", "worker_id",
                "user_id", "従業員ID", "社員ID", "従業員",
            ))
            if employee_value is None:
                raise KeyError("employee ID column is missing")

            employee = str(employee_value).strip()
            if not employee:
                continue
            totals.setdefault(employee, 0.0)

            type_value = _pick(row, ("type", "shift_type", "work_type", "勤務区分", "種類"))
            shift_type = "" if type_value is None else str(type_value).strip().lower().replace("_", "").replace("-", "").replace(" ", "")

            if shift_type == "paidleave":
                totals[employee] += PAID_LEAVE_HOURS
                continue

            if shift_type:
                work_types = {"work", "working", "勤務", "出勤", "シフト", "shift"}
                if shift_type not in work_types:
                    continue

            duration_value = _pick(row, ("hours", "duration", "duration_hours", "work_hours", "労働時間"))
            if duration_value is not None and str(duration_value).strip():
                hours = float(str(duration_value).strip())
                if hours < 0:
                    raise ValueError("work duration cannot be negative")
                totals[employee] += _floor_to_quarter_hour(hours * 3600.0)
                continue

            start_value = _pick(row, ("start", "start_time", "clock_in", "開始", "開始時刻", "出勤時刻"))
            end_value = _pick(row, ("end", "end_time", "clock_out", "終了", "終了時刻", "退勤時刻"))
            if start_value is None or end_value is None:
                continue

            start_text = str(start_value).strip()
            end_text = str(end_value).strip()
            if not start_text or not end_text:
                continue

            start = _parse_time(start_text)
            end = _parse_time(end_text)
            end_is_24 = end_text in ("24:00", "24:00:00")

            if end < start or (end == start and end_is_24):
                end += timedelta(days=1)

            elapsed_seconds = (end - start).total_seconds()
            if elapsed_seconds > 6 * 3600:
                elapsed_seconds -= 3600

            totals[employee] += _floor_to_quarter_hour(elapsed_seconds)

    return totals


