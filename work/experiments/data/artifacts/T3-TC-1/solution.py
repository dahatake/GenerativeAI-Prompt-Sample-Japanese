import re
from datetime import datetime, timedelta, timezone

_JST = timezone(timedelta(hours=9))
_MIN_YEAR = 2000
_PATTERN = re.compile(r"INV-([0-9]{4})([0-9]{2})-([0-9]{4})")


def _now_utc():
    return datetime.now(timezone.utc)


def validate_invoice_id(value, *, today=None):
    """請求書番号 INV-YYYYMM-NNNN が正しければ True を返す。

    today を省略した場合は日本時間 (UTC+9) の現在日付を基準に「未来の年月」を判定する。
    """
    if not isinstance(value, str):
        return False
    match = _PATTERN.fullmatch(value)
    if match is None:
        return False

    year, month, serial = (int(group) for group in match.groups())
    if not 1 <= month <= 12:
        return False
    if year < _MIN_YEAR:
        return False
    if serial == 0:
        return False

    if today is None:
        today = _now_utc().astimezone(_JST).date()
    return (year, month) <= (today.year, today.month)
