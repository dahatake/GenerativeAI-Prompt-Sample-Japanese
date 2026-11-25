import csv
import re


def _find_column(fieldnames, candidates):
    normalized = {str(name).strip().lower(): name for name in (fieldnames or [])}
    for candidate in candidates:
        key = candidate.lower()
        if key in normalized:
            return normalized[key]
    return None


def _parse_clock(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    match = re.search(r"(?<!\d)(\d{1,2}):(\d{2})(?::(\d{2}))?(?!\d)", text)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        second = int(match.group(3) or 0)
        if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59:
            return hour * 3600 + minute * 60 + second
    return None


def monthly_work_hours(path):
    """Aggregate CSV shift durations for each employee, in hours."""
    totals_seconds = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        employee_column = _find_column(reader.fieldnames, (
            "employee", "employee_id", "employeeid", "employee_no",
            "worker_id", "workerid", "staff_id", "staff", "user_id", "id",
            "社員番号", "従業員id", "従業員"
        ))
        start_column = _find_column(reader.fieldnames, (
            "start", "start_time", "starttime", "clock_in", "clockin",
            "in", "check_in", "開始時刻", "出勤時刻"
        ))
        end_column = _find_column(reader.fieldnames, (
            "end", "end_time", "endtime", "clock_out", "clockout",
            "out", "check_out", "終了時刻", "退勤時刻"
        ))
        type_column = _find_column(reader.fieldnames, (
            "type", "shift_type", "record_type", "category", "status"
        ))

        if employee_column is None:
            raise ValueError("CSV must contain an employee ID column")
        for row in reader:
            employee = str(row.get(employee_column, "")).strip()
            if not employee:
                continue

            totals_seconds.setdefault(employee, 0)

            row_type = ""
            if type_column is not None:
                row_type = str(row.get(type_column, "")).strip().lower()

            if row_type == "paid_leave":
                totals_seconds[employee] += int(7.5 * 3600)
                continue

            if row_type in {
                "leave", "unpaid_leave", "holiday", "off", "absence",
                "absent", "休暇", "有給休暇", "休み", "欠勤", "休日"
            }:
                continue

            if start_column is None or end_column is None:
                continue

            start = _parse_clock(row.get(start_column))
            end = _parse_clock(row.get(end_column))
            if start is None or end is None:
                continue

            duration = end - start
            if duration < 0:
                duration += 24 * 3600
            totals_seconds[employee] += duration

    return {
        employee: seconds / 3600.0
        for employee, seconds in totals_seconds.items()
    }


