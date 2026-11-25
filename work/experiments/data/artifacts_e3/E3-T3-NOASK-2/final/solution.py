import re

# INV-YYYYMM-NNNN (ASCII digits only; [0-9] instead of \d to reject non-ASCII digits)
_INVOICE_ID_RE = re.compile(r"INV-([0-9]{4})([0-9]{2})-([0-9]{4})")


def validate_invoice_id(value) -> bool:
    """Return True if value is a well-formed invoice ID like 'INV-202601-0001'.

    Rules: exact format INV-YYYYMM-NNNN, month 01-12, sequence 0001-9999.
    Non-str input returns False; no normalization (case/whitespace) is applied.
    """
    if not isinstance(value, str):
        return False
    match = _INVOICE_ID_RE.fullmatch(value)
    if match is None:
        return False
    _year, month, seq = match.groups()
    return 1 <= int(month) <= 12 and int(seq) >= 1
