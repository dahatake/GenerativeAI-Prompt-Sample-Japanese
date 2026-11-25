import re

MIN_YEAR = 2000
MAX_YEAR = 2099

# [0-9] instead of \d so that non-ASCII digits (e.g. full-width) are rejected.
_INVOICE_ID_PATTERN = re.compile(r"INV-([0-9]{4})([0-9]{2})-([0-9]{4})")


def validate_invoice_id(value) -> bool:
    """Return True if value is a valid invoice ID of the form INV-YYYYMM-NNNN.

    Rules: exact match (no normalization), YYYY in MIN_YEAR..MAX_YEAR,
    MM in 01..12, NNNN in 0001..9999. Non-str input returns False.
    """
    if not isinstance(value, str):
        return False
    match = _INVOICE_ID_PATTERN.fullmatch(value)
    if match is None:
        return False
    year, month, serial = (int(group) for group in match.groups())
    return MIN_YEAR <= year <= MAX_YEAR and 1 <= month <= 12 and serial >= 1
