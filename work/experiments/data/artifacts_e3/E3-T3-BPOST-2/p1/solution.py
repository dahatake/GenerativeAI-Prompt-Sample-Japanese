import re

_INVOICE_ID_PATTERN = re.compile(r"INV-([0-9]{4})([0-9]{2})-([0-9]{4})")


def validate_invoice_id(value) -> bool:
    """Return True if value is a valid invoice ID of the form INV-YYYYMM-NNNN."""
    if not isinstance(value, str):
        return False
    match = _INVOICE_ID_PATTERN.fullmatch(value)
    if match is None:
        return False
    year, month, serial = (int(g) for g in match.groups())
    return year >= 1000 and 1 <= month <= 12 and serial >= 1
