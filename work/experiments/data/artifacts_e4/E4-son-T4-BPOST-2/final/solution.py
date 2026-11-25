import csv
from datetime import datetime


PAID_LEAVE_HOURS = 7.5
BREAK_THRESHOLD_MIN = 6 * 60  # 拘束時間がこれを超えたら休憩控除
BREAK_MIN = 60
ROUND_MIN = 15  # シフトごとの実労働時間を切り捨てる単位


def _minutes(s):
    t = datetime.strptime(s.strip(), "%H:%M")
    return t.hour * 60 + t.minute


def monthly_work_hours(path, month=None):
    """従業員ごとの労働時間(時間, float)を集計して {従業員ID: 時間} を返す。

    work 行: 拘束時間が6時間超なら休憩60分を控除し、実労働時間を15分単位で切り捨てて加算。
    paid_leave 行: 所定労働時間 7.5h を加算。
    終了が開始以前の場合は日跨ぎ勤務として +24h。
    month="YYYY-MM" を指定するとその月(開始日基準)の行だけを対象にする。
    """
    result = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            emp = row.get("employee")
            if not emp:
                continue
            if month and not row.get("date", "").startswith(month):
                continue
            result.setdefault(emp, 0.0)
            kind = row.get("type", "").lower()
            if kind == "paid_leave":
                result[emp] += PAID_LEAVE_HOURS
                continue
            if kind != "work":
                continue
            if not row.get("start") or not row.get("end"):
                continue
            start, end = _minutes(row["start"]), _minutes(row["end"])
            if end < start:
                end += 24 * 60
            span = end - start
            if span > BREAK_THRESHOLD_MIN:
                span -= BREAK_MIN
            span -= span % ROUND_MIN
            result[emp] += span / 60.0
    return result
