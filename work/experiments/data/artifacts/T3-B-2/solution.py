import re

_INVOICE_ID_PATTERN = re.compile(r"INV-([0-9]{4})([0-9]{2})-([0-9]{4})")


def validate_invoice_id(value) -> bool:
    """請求書番号が INV-YYYYMM-NNNN 形式で妥当かを判定する。"""
    if not isinstance(value, str):
        return False
    match = _INVOICE_ID_PATTERN.fullmatch(value)
    if match is None:
        return False
    _year, month, serial = match.groups()
    if not 1 <= int(month) <= 12:
        return False
    return int(serial) >= 1

