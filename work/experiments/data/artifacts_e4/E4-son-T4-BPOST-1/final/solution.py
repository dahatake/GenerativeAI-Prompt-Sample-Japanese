import csv

WORK_TYPES = {"work"}
PAID_LEAVE_TYPES = {"paid_leave"}
PAID_LEAVE_HOURS = 7.5
BREAK_THRESHOLD_MIN = 6 * 60
BREAK_MIN = 60


def _parse_time(s):
    h, m = s.strip().split(":")[:2]
    return int(h) * 60 + int(m)


def monthly_work_hours(path, month=None):
    """勤怠CSVから従業員ごとの労働時間(時間, float)を集計する。

    month: "YYYY-MM" を指定するとその月(開始日基準)のみ集計。None なら全行。
    type が work の行は拘束時間を加算し、6時間超なら一律60分の休憩を控除する。
    paid_leave は所定7.5時間として加算。終了 < 開始 は日跨ぎ(翌日終了)として扱う。
    """
    totals = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            emp = row.get("employee", "")
            if not emp:
                continue
            totals.setdefault(emp, 0.0)
            kind = row.get("type", "").lower()
            if month and not row.get("date", "").startswith(month):
                continue
            if kind in PAID_LEAVE_TYPES:
                totals[emp] += PAID_LEAVE_HOURS
                continue
            if kind not in WORK_TYPES:
                continue
            if not row.get("start") or not row.get("end"):
                continue
            minutes = _parse_time(row["end"]) - _parse_time(row["start"])
            if minutes < 0:
                minutes += 24 * 60
            if minutes > BREAK_THRESHOLD_MIN:
                minutes -= BREAK_MIN
            totals[emp] += minutes / 60.0
    return totals
