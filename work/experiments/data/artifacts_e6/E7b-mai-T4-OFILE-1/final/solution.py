import csv
import re


PAID_LEAVE_HOURS = 7.5


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


def _normalize_type(value):
    raw = str(value or "").strip().lower()
    return re.sub(r"[\s\-]+", "_", raw)


def _is_paid_leave(row, type_column):
    if type_column is None:
        return False

    kind = _normalize_type(row.get(type_column, ""))
    return kind in {
        "paid_leave", "paidleave", "annual_leave", "annualleave",
        "有給休暇", "有給", "有休"
    }


def _is_work_row(row, type_column):
    if type_column is None:
        return True

    raw = str(row.get(type_column, "")).strip().lower()
    if not raw:
        return True

    non_work = {
        "leave", "paid_leave", "unpaid_leave", "holiday", "off",
        "absence", "absent", "休暇", "有給休暇", "休み", "欠勤", "休日"
    }
    return raw not in non_work


def monthly_work_hours(path):
    """Aggregate CSV shift durations for each employee, in hours."""
    totals_seconds = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        employee_column = _find_column(reader.fieldnames, (
            "employee", "employee_id", "employeeid", "employee_no", "employee_number",
            "worker_id", "workerid", "staff_id", "staff", "user_id", "id",
            "社員番号", "社員id", "従業員番号", "従業員id", "従業員"
        ))
        start_column = _find_column(reader.fieldnames, (
            "start", "start_time", "starttime", "clock_in", "clockin",
            "in", "check_in", "開始時刻", "出勤時刻", "開始", "出勤"
        ))
        end_column = _find_column(reader.fieldnames, (
            "end", "end_time", "endtime", "clock_out", "clockout",
            "out", "check_out", "終了時刻", "退勤時刻", "終了", "退勤"
        ))
        type_column = _find_column(reader.fieldnames, (
            "type", "shift_type", "record_type", "category", "status", "種別", "勤務区分"
        ))

        if employee_column is None:
            raise ValueError("CSV must contain an employee ID column")
        if start_column is None or end_column is None:
            raise ValueError("CSV must contain shift start and end columns")

        for row in reader:
            employee = str(row.get(employee_column, "")).strip()
            if not employee:
                continue

            totals_seconds.setdefault(employee, 0)

            if _is_paid_leave(row, type_column):
                totals_seconds[employee] += PAID_LEAVE_HOURS * 3600
                continue

            if not _is_work_row(row, type_column):
                continue

            start = _parse_clock(row.get(start_column))
            end = _parse_clock(row.get(end_column))
            if start is None or end is None:
                continue

            duration = end - start
            if duration <= 0:
                duration += 24 * 3600
            totals_seconds[employee] += duration

    return {
        employee: seconds / 3600.0
        for employee, seconds in totals_seconds.items()
    }
