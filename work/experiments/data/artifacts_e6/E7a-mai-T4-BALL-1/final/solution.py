import csv
from datetime import datetime, time
from pathlib import Path


_EMPLOYEE_COLUMNS = (
    "employee_id", "employee", "employeeid", "emp_id", "staff_id", "worker_id",
    "従業員ID", "従業員id", "従業員", "employee id",
)
_TYPE_COLUMNS = ("type", "shift_type", "status", "attendance_type", "区分", "勤務区分")
_START_COLUMNS = ("start", "start_time", "clock_in", "starttime", "開始", "出勤")
_END_COLUMNS = ("end", "end_time", "clock_out", "endtime", "終了", "退勤")


def _normalized(name):
    return "" if name is None else str(name).strip().lower().replace("-", "_").replace(" ", "_")


def _find_column(fieldnames, candidates):
    normalized = {_normalized(name): name for name in fieldnames if name is not None}
    for candidate in candidates:
        if _normalized(candidate) in normalized:
            return normalized[_normalized(candidate)]
    return None


def _parse_clock(value):
    text = "" if value is None else str(value).strip()
    if not text:
        return None

    try:
        parsed = datetime.fromisoformat(text)
        return time(parsed.hour, parsed.minute, parsed.second)
    except ValueError:
        pass

    parts = text.split(":")
    if len(parts) not in (2, 3):
        return None
    try:
        hour = int(parts[0])
        minute = int(parts[1])
        second = int(parts[2]) if len(parts) == 3 else 0
    except ValueError:
        return None
    if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
        return None
    return time(hour, minute, second)


def _elapsed_seconds(start_value, end_value):
    start = _parse_clock(start_value)
    end = _parse_clock(end_value)
    if start is None or end is None:
        return None

    start_seconds = start.hour * 3600 + start.minute * 60 + start.second
    end_seconds = end.hour * 3600 + end.minute * 60 + end.second
    if end_seconds < start_seconds:
        end_seconds += 24 * 3600
    return max(0, end_seconds - start_seconds)


def _shift_type(row, type_column):
    if type_column is None:
        return "work"
    return _normalized(row.get(type_column, "") or "")


def _truncated_shift_hours(elapsed_seconds):
    if elapsed_seconds > 6 * 3600:
        elapsed_seconds -= 60 * 60
    elapsed_seconds = max(0, elapsed_seconds)
    elapsed_seconds -= elapsed_seconds % (15 * 60)
    return elapsed_seconds / 3600.0


def monthly_work_hours(path):
    """Aggregate work hours for each employee in a monthly shifts CSV."""
    csv_path = Path(path)
    totals = {}

    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            return totals

        employee_column = _find_column(reader.fieldnames, _EMPLOYEE_COLUMNS)
        type_column = _find_column(reader.fieldnames, _TYPE_COLUMNS)
        start_column = _find_column(reader.fieldnames, _START_COLUMNS)
        end_column = _find_column(reader.fieldnames, _END_COLUMNS)

        if employee_column is None:
            raise ValueError("CSVに従業員ID列がありません")

        for row in reader:
            employee_id = str(row.get(employee_column, "") or "").strip()
            if not employee_id:
                continue
            totals.setdefault(employee_id, 0.0)

            shift_type = _shift_type(row, type_column)
            if shift_type == "paid_leave":
                totals[employee_id] += 7.5
                continue

            if shift_type not in ("work", "worked", "working", "shift", "出勤", "勤務"):
                continue
            if start_column is None or end_column is None:
                continue

            elapsed_seconds = _elapsed_seconds(row.get(start_column), row.get(end_column))
            if elapsed_seconds is None:
                continue

            totals[employee_id] += _truncated_shift_hours(elapsed_seconds)

    return totals
