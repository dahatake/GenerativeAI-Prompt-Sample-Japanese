import re

_INVOICE_ID_PATTERN = re.compile(
    r"INV-"
    r"20[2-9][0-9]"        # year 2020-2099
    r"(?:0[1-9]|1[0-2])"   # month 01-12
    r"-"
    r"(?!0000)[0-9]{4}"    # sequence 0001-9999
)


def validate_invoice_id(value) -> bool:
    """Return True if value is a valid invoice ID of the form INV-YYYYMM-NNNN."""
    if not isinstance(value, str):
        return False
    return _INVOICE_ID_PATTERN.fullmatch(value) is not None
