import csv
from datetime import datetime, timedelta
from typing import Dict, Union


EmployeeId = Union[str, int]


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
        return datetime(1, 1, 2, 0, 0)

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
            if type_value is not None:
                shift_type = str(type_value).strip().lower()
                work_types = {"work", "working", "勤務", "出勤", "シフト", "shift"}
                if shift_type not in work_types:
                    continue

            duration_value = _pick(row, ("hours", "duration", "duration_hours", "work_hours", "労働時間"))
            if duration_value is not None and str(duration_value).strip():
                hours = float(str(duration_value).strip())
                if hours < 0:
                    raise ValueError("work duration cannot be negative")
                totals[employee] += hours
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
            if end < start:
                end += timedelta(days=1)

            totals[employee] += (end - start).total_seconds() / 3600.0

    return totals
