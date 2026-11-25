import re

_INVOICE_ID_PATTERN = re.compile(r"INV-([0-9]{4})(0[1-9]|1[0-2])-([0-9]{4})")


def validate_invoice_id(value) -> bool:
    """Return True if value is an invoice ID of the form INV-YYYYMM-NNNN."""
    if not isinstance(value, str):
        return False
    match = _INVOICE_ID_PATTERN.fullmatch(value)
    if match is None:
        return False
    return match.group(3) != "0000"
