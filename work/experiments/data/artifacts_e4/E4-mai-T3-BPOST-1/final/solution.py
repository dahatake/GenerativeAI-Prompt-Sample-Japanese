import re


_INVOICE_ID_RE = re.compile(r"^INV-(20[0-9]{2})(0[1-9]|1[0-2])-([0-9]{4})$")


def validate_invoice_id(value) -> bool:
    """Return True only for an invoice ID in the form INV-YYYYMM-NNNN."""
    if not isinstance(value, str):
        return False

    return _INVOICE_ID_RE.fullmatch(value) is not None
