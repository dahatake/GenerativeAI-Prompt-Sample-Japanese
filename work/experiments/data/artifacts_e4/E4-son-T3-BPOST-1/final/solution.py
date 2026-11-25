import re

_PATTERN = re.compile(r"INV-(\d{4})(\d{2})-(\d{4})", re.ASCII)


def validate_invoice_id(value) -> bool:
    """INV-YYYYMM-NNNN 形式（年は2020-2099、月は01-12、連番は0001以上）なら True。"""
    if not isinstance(value, str):
        return False
    m = _PATTERN.fullmatch(value)
    if not m:
        return False
    year, month, seq = m.groups()
    return 2020 <= int(year) <= 2099 and 1 <= int(month) <= 12 and int(seq) >= 1
