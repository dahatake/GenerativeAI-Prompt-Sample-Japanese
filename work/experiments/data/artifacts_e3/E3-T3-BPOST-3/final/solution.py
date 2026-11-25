import re

_INVOICE_ID_PATTERN = re.compile(r"INV-(20[2-9][0-9])(0[1-9]|1[0-2])-([0-9]{4})")


def validate_invoice_id(value) -> bool:
    """請求書番号 (INV-YYYYMM-NNNN) として正しい形式なら True を返す。"""
    if not isinstance(value, str):
        return False
    match = _INVOICE_ID_PATTERN.fullmatch(value)
    if match is None:
        return False
    return int(match.group(3)) != 0
