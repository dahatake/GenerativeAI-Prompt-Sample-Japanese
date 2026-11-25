import re

_PATTERN = re.compile(r"INV-(\d{4})(\d{2})-(\d{4})", re.ASCII)


def validate_invoice_id(value) -> bool:
    """Return True if value is a well-formed invoice number: INV-YYYYMM-NNNN."""
    if not isinstance(value, str):
        return False
    m = _PATTERN.fullmatch(value)
    if not m:
        return False
    year, month, seq = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return year >= 1 and 1 <= month <= 12 and seq >= 1
