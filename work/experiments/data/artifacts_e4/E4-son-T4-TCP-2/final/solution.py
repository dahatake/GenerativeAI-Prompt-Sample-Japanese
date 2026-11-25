import csv
from datetime import date, datetime

BREAK_THRESHOLD_MIN = 360
BREAK_MIN = 60
ROUND_UNIT_MIN = 15
PAID_LEAVE_MIN = 450
REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")


def _parse_minutes(value, lineno, name):
    try:
        t = datetime.strptime((value or "").strip(), "%H:%M")
    except ValueError:
        raise ValueError(f"line {lineno}: invalid {name} time: {value!r}") from None
    return t.hour * 60 + t.minute


def _shift_minutes(start, end):
    span = (end - start) % (24 * 60)
    if span > BREAK_THRESHOLD_MIN:
        span -= BREAK_MIN
    return span // ROUND_UNIT_MIN * ROUND_UNIT_MIN


def monthly_work_hours(path):
    """勤怠CSVから従業員ごとの労働時間(時間, float)を集計する。"""
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing columns: {missing}")
        for row in reader:
            lineno = reader.line_num
            if not any((v or "").strip() for v in row.values() if isinstance(v, str)):
                continue
            emp = (row["employee"] or "").strip()
            if not emp:
                raise ValueError(f"line {lineno}: empty employee")
            try:
                date.fromisoformat((row["date"] or "").strip())
            except ValueError:
                raise ValueError(f"line {lineno}: invalid date: {row['date']!r}") from None
            kind = (row["type"] or "").strip()
            if kind == "work":
                start = _parse_minutes(row["start"], lineno, "start")
                end = _parse_minutes(row["end"], lineno, "end")
                minutes = _shift_minutes(start, end)
            elif kind == "paid_leave":
                minutes = PAID_LEAVE_MIN
            else:
                raise ValueError(f"line {lineno}: unknown type: {row['type']!r}")
            totals[emp] = totals.get(emp, 0) + minutes
    return {emp: m / 60 for emp, m in totals.items()}
