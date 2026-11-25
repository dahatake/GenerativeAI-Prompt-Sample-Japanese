import re

_INVOICE_ID_PATTERN = re.compile(r"INV-([0-9]{4})([0-9]{2})-([0-9]{4})")


def validate_invoice_id(value):
    """Return True if value is a valid invoice ID of the form INV-YYYYMM-NNNN."""
    if not isinstance(value, str):
        return False
    match = _INVOICE_ID_PATTERN.fullmatch(value)
    if match is None:
        return False
    _year, month, sequence = match.groups()
    return 1 <= int(month) <= 12 and int(sequence) >= 1
