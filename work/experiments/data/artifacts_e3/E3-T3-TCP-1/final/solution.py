import re

_INVOICE_ID_RE = re.compile(r"INV-(20[2-9][0-9])(0[1-9]|1[0-2])-([0-9]{4})")


def validate_invoice_id(value) -> bool:
    """Return True if value is an invoice ID of the form INV-YYYYMM-NNNN.

    YYYY: 2020-2099, MM: 01-12, NNNN: 0001-9999 (ASCII digits only, exact match).
    """
    if not isinstance(value, str):
        return False
    match = _INVOICE_ID_RE.fullmatch(value)
    if match is None:
        return False
    return match.group(3) != "0000"
