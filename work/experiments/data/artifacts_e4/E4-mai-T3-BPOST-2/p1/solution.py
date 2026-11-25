import re


_INVOICE_ID_RE = re.compile(r"^INV-(\d{4})(\d{2})-(\d{4})$")


def validate_invoice_id(value):
    """Return True when value has the INV-YYYYMM-NNNN invoice format."""
    if not isinstance(value, str):
        return False

    match = _INVOICE_ID_RE.fullmatch(value)
    if match is None:
        return False

    year, month, sequence = match.groups()
    if not 1 <= int(month) <= 12:
        return False
    if int(sequence) == 0:
        return False

    return True
