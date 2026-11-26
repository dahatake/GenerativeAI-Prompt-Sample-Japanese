import csv
import re


_TIME_PATTERN = re.compile(r"^([01][0-9]|2[0-3]):([0-5][0-9])$")


def _minutes(value: str, row_number: int, column: str) -> int:
    if value is None:
        raise ValueError(f"row {row_number}: missing {column}")
    match = _TIME_PATTERN.fullmatch(value.strip())
    if not match:
        raise ValueError(f"row {row_number}: invalid {column} time {value!r}")
    return int(match.group(1)) * 60 + int(match.group(2))


def monthly_work_hours(path):
    """Aggregate work and paid-leave hours per employee from a shift CSV."""
    totals = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("missing CSV header")

        required = {"employee", "type", "start", "end"}
        missing = sorted(required.difference(reader.fieldnames))
        if missing:
            raise ValueError("missing required columns: " + ", ".join(missing))

        for row_number, row in enumerate(reader, start=2):
            employee = row.get("employee")
            shift_type = row.get("type")

            if employee is None or not employee.strip():
                raise ValueError(f"row {row_number}: missing employee")
            if shift_type is None or not shift_type.strip():
                raise ValueError(f"row {row_number}: missing type")

            employee = employee.strip()
            shift_type = shift_type.strip()

            if shift_type == "paid_leave":
                totals[employee] = totals.get(employee, 0.0) + 450
                continue

            if shift_type != "work":
                continue

            start = _minutes(row.get("start"), row_number, "start")
            end = _minutes(row.get("end"), row_number, "end")

            duration = end - start
            if duration < 0:
                duration += 24 * 60

            if duration > 360:
                duration -= 60

            duration = (duration // 15) * 15
            totals[employee] = totals.get(employee, 0.0) + duration

    return {employee: minutes / 60.0 for employee, minutes in totals.items()}
