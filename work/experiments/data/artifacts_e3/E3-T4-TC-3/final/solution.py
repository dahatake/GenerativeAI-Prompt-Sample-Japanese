import csv
from datetime import date, datetime

REQUIRED_COLUMNS = ("employee", "date", "type", "start", "end")
BREAK_THRESHOLD_MINUTES = 6 * 60
BREAK_MINUTES = 60
ROUNDING_UNIT_MINUTES = 15
PAID_LEAVE_MINUTES = 450  # 所定労働時間 7.5h


def _parse_time(value, line_no, column):
    try:
        t = datetime.strptime(value.strip(), "%H:%M")
    except ValueError:
        raise ValueError(f"line {line_no}: invalid {column} time {value!r}") from None
    return t.hour * 60 + t.minute


def _work_minutes(start, end):
    gross = end - start
    if gross < 0:
        gross += 24 * 60
    # 休憩判定は丸め前の拘束時間で行う
    net = gross - BREAK_MINUTES if gross > BREAK_THRESHOLD_MINUTES else gross
    return net // ROUNDING_UNIT_MINUTES * ROUNDING_UNIT_MINUTES


def monthly_work_hours(path):
    totals = {}
    months = set()
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing required columns: {missing}")
        for line_no, row in enumerate(reader, start=2):
            employee = (row["employee"] or "").strip()
            if not employee:
                raise ValueError(f"line {line_no}: empty employee")
            try:
                day = date.fromisoformat((row["date"] or "").strip())
            except ValueError:
                raise ValueError(f"line {line_no}: invalid date {row['date']!r}") from None
            months.add((day.year, day.month))
            if len(months) > 1:
                raise ValueError(f"line {line_no}: multiple months in one file")

            kind = (row["type"] or "").strip()
            if kind == "work":
                start = _parse_time(row["start"] or "", line_no, "start")
                end = _parse_time(row["end"] or "", line_no, "end")
                minutes = _work_minutes(start, end)
            elif kind == "paid_leave":
                minutes = PAID_LEAVE_MINUTES
            else:
                raise ValueError(f"line {line_no}: unknown type {kind!r}")
            totals[employee] = totals.get(employee, 0) + minutes

    return {emp: minutes / 60 for emp, minutes in totals.items()}
