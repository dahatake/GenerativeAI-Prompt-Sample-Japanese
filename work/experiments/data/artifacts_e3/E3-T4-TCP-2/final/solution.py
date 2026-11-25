import csv
from datetime import datetime

REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")
BREAK_THRESHOLD_MIN = 6 * 60
BREAK_MIN = 60
PAID_LEAVE_MIN = 7 * 60 + 30
ROUND_UNIT_MIN = 15


def _parse_minutes(value, line_no, field):
    try:
        t = datetime.strptime(value, "%H:%M")
    except ValueError:
        raise ValueError(f"line {line_no}: invalid {field} time {value!r}") from None
    return t.hour * 60 + t.minute


def _work_minutes(start, end, line_no):
    if not start or not end:
        raise ValueError(f"line {line_no}: work row requires start and end")
    s = _parse_minutes(start, line_no, "start")
    e = _parse_minutes(end, line_no, "end")
    if s == e:
        raise ValueError(f"line {line_no}: start equals end ({start})")
    span = e - s if e > s else e + 24 * 60 - s  # end < start: ends next day
    if span > BREAK_THRESHOLD_MIN:
        span -= BREAK_MIN
    return span - span % ROUND_UNIT_MIN


def monthly_work_hours(path):
    """Return {employee_id: monthly work hours (float)} aggregated from a shift CSV."""
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = [h.strip() for h in (reader.fieldnames or [])]
        missing = [c for c in REQUIRED_COLUMNS if c not in header]
        if missing:
            raise ValueError(f"missing columns: {missing}")
        reader.fieldnames = header
        for row in reader:
            line_no = reader.line_num
            row = {k: (v or "").strip() for k, v in row.items() if k is not None}
            if not any(row.values()):
                continue
            emp = row["employee"]
            if not emp:
                raise ValueError(f"line {line_no}: empty employee")
            try:
                datetime.strptime(row["date"], "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"line {line_no}: invalid date {row['date']!r}") from None
            kind = row["type"]
            if kind == "work":
                minutes = _work_minutes(row["start"], row["end"], line_no)
            elif kind == "paid_leave":
                minutes = PAID_LEAVE_MIN
            else:
                raise ValueError(f"line {line_no}: unknown type {kind!r}")
            totals[emp] = totals.get(emp, 0) + minutes
    return {emp: m / 60.0 for emp, m in totals.items()}
