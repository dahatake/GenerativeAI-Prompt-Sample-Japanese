import re


_INVOICE_ID_RE = re.compile(r"^INV-([0-9]{4})(0[1-9]|1[0-2])-([0-9]{4})$")


def validate_invoice_id(value) -> bool:
    """Return True only for an invoice ID in the form INV-YYYYMM-NNNN."""
    if not isinstance(value, str):
        return False

    match = _INVOICE_ID_RE.fullmatch(value)
    if match is None:
        return False

    year = int(match.group(1))
    return year != 0
