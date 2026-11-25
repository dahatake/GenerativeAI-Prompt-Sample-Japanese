import re

MIN_YEAR = 2000
MAX_YEAR = 2099

# [0-9] instead of \d so that non-ASCII digits (e.g. full-width) are rejected.
_INVOICE_ID_PATTERN = re.compile(r"INV-([0-9]{4})(0[1-9]|1[0-2])-([0-9]{4})")


def validate_invoice_id(value) -> bool:
    """Return True if value is a valid invoice ID such as 'INV-202601-0001'.

    Format: 'INV-' + YYYYMM + '-' + 4-digit serial (0001-9999).
    The year must be within MIN_YEAR..MAX_YEAR; future months are not rejected.
    Non-string input returns False.
    """
    if not isinstance(value, str):
        return False
    match = _INVOICE_ID_PATTERN.fullmatch(value)
    if match is None:
        return False
    year = int(match.group(1))
    serial = match.group(3)
    return MIN_YEAR <= year <= MAX_YEAR and serial != "0000"
