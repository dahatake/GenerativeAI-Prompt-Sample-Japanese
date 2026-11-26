import csv
from datetime import datetime


def _find_column(fieldnames, candidates):
    names = {name.strip().lower(): name for name in fieldnames if name is not None}
    for candidate in candidates:
        if candidate in names:
            return names[candidate]
    return None


def _parse_clock(value):
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None


def monthly_work_hours(path):
    """Aggregate work hours per employee from a shifts CSV file."""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            return totals

        employee_column = _find_column(
            reader.fieldnames,
            ("employee", "employee_id", "employeeid", "staff_id", "staff",
             "worker_id", "worker", "従業員id", "社員番号"),
        )
        start_column = _find_column(
            reader.fieldnames,
            ("start", "start_time", "clock_in", "check_in", "開始", "開始時刻"),
        )
        end_column = _find_column(
            reader.fieldnames,
            ("end", "end_time", "clock_out", "check_out", "終了", "終了時刻"),
        )
        type_column = _find_column(
            reader.fieldnames,
            ("type", "shift_type", "category", "区分", "種類"),
        )
        hours_column = _find_column(
            reader.fieldnames,
            ("hours", "work_hours", "duration", "duration_hours", "労働時間"),
        )

        if employee_column is None:
            raise KeyError("CSV must contain an employee ID column")

        for row in reader:
            employee = (row.get(employee_column) or "").strip()
            if not employee:
                continue

            shift_type = ""
            if type_column is not None:
                shift_type = (row.get(type_column) or "").strip().lower()

            if shift_type == "paid_leave":
                totals[employee] = totals.get(employee, 0.0) + 7.5
                continue

            if shift_type not in ("", "work", "working", "shift", "勤務"):
                continue

            hours = None
            if hours_column is not None:
                raw_hours = (row.get(hours_column) or "").strip()
                if raw_hours:
                    try:
                        hours = float(raw_hours)
                    except ValueError:
                        hours = None

            if hours is None and start_column is not None and end_column is not None:
                start = _parse_clock(row.get(start_column))
                end = _parse_clock(row.get(end_column))
                if start is not None and end is not None:
                    seconds = (end.hour * 3600 + end.minute * 60 + end.second)
                    seconds -= (start.hour * 3600 + start.minute * 60 + start.second)
                    if seconds < 0:
                        seconds += 24 * 3600
                    hours = seconds / 3600.0

            if hours is not None and hours >= 0:
                totals[employee] = totals.get(employee, 0.0) + float(hours)

    return totals
