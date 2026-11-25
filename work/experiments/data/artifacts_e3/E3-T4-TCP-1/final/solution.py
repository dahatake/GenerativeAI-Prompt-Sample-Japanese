import csv
import re

REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")
BREAK_THRESHOLD_MINUTES = 6 * 60
BREAK_MINUTES = 60
PAID_LEAVE_MINUTES = 450  # 7.5 hours
ROUND_DOWN_UNIT_MINUTES = 15

_TIME_RE = re.compile(r"^(\d{2}):(\d{2})$")


def _parse_minutes(value, line_no):
    match = _TIME_RE.match(value)
    if not match:
        raise ValueError(f"line {line_no}: invalid time {value!r}")
    hours, minutes = int(match.group(1)), int(match.group(2))
    if hours > 23 or minutes > 59:
        raise ValueError(f"line {line_no}: invalid time {value!r}")
    return hours * 60 + minutes


def _work_minutes(start, end, line_no):
    start_min = _parse_minutes(start, line_no)
    end_min = _parse_minutes(end, line_no)
    span = end_min - start_min
    if span < 0:
        span += 24 * 60  # ends on the next day
    if span > BREAK_THRESHOLD_MINUTES:
        span -= BREAK_MINUTES
    return span - span % ROUND_DOWN_UNIT_MINUTES


def monthly_work_hours(path):
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = [name.strip() for name in (reader.fieldnames or [])]
        missing = [c for c in REQUIRED_COLUMNS if c not in fields]
        if reader.fieldnames is not None and missing:
            raise ValueError(f"missing columns: {missing}")
        reader.fieldnames = fields

        for row in reader:
            line_no = reader.line_num
            values = {k: (row.get(k) or "").strip() for k in REQUIRED_COLUMNS}
            if not any(values.values()):
                continue
            employee = values["employee"]
            if not employee:
                raise ValueError(f"line {line_no}: empty employee")
            kind = values["type"]
            if kind == "work":
                if not values["start"] or not values["end"]:
                    raise ValueError(f"line {line_no}: work row needs start and end")
                minutes = _work_minutes(values["start"], values["end"], line_no)
            elif kind == "paid_leave":
                minutes = PAID_LEAVE_MINUTES
            else:
                raise ValueError(f"line {line_no}: unknown type {kind!r}")
            totals[employee] = totals.get(employee, 0) + minutes

    return {emp: minutes / 60.0 for emp, minutes in totals.items()}
