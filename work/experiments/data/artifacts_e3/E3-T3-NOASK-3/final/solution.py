import re

_INVOICE_ID_PATTERN = re.compile(r"INV-([0-9]{4})([0-9]{2})-([0-9]{4})")


def validate_invoice_id(value) -> bool:
    """Return True if value is a valid invoice ID of the form INV-YYYYMM-NNNN.

    Month must be 01-12 and the serial must be 0001-9999. Non-str input returns False.
    """
    if not isinstance(value, str):
        return False
    match = _INVOICE_ID_PATTERN.fullmatch(value)
    if match is None:
        return False
    _year, month, serial = match.groups()
    return 1 <= int(month) <= 12 and int(serial) >= 1
