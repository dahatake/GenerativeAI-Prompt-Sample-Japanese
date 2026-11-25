import csv
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")
REQUIRED_COLUMNS = ("ordered_at", "amount_incl_tax", "status")
_INT_RE = re.compile(r"[+-]?\d+")


def _to_jst_month(value, line_no):
    text = (value or "").strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        raise ValueError(f"line {line_no}: invalid ordered_at {value!r}") from None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    jst = dt.astimezone(JST)
    return jst.year, jst.month


def _excl_tax(value, line_no):
    text = (value or "").strip()
    if not _INT_RE.fullmatch(text):
        raise ValueError(f"line {line_no}: invalid amount_incl_tax {value!r}")
    amount = int(text)
    # 税込 ÷ 1.1 を整数演算で行い、1 円未満は 0 方向へ切り捨てる
    sign = -1 if amount < 0 else 1
    return sign * (abs(amount) * 10 // 11)


def monthly_sales(path):
    totals = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if reader.fieldnames is not None and missing:
            raise ValueError(f"missing columns: {missing}")
        for row in reader:
            line_no = reader.line_num
            if any(row.get(c) is None for c in REQUIRED_COLUMNS):
                raise ValueError(f"line {line_no}: missing fields")
            month = _to_jst_month(row["ordered_at"], line_no)
            amount = _excl_tax(row["amount_incl_tax"], line_no)
            if row["status"].strip().lower() != "completed":
                continue
            totals[month] = totals.get(month, 0) + amount

    if not totals:
        return {}

    result = {}
    year, month = min(totals)
    last = max(totals)
    while (year, month) <= last:
        result[f"{year:04d}-{month:02d}"] = totals.get((year, month), 0)
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return result
