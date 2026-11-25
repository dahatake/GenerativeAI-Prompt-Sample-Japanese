import re


_INVOICE_ID_PATTERN = re.compile(r"INV-[0-9]{4}(0[1-9]|1[0-2])-[0-9]{4}\Z")


def validate_invoice_id(value) -> bool:
    """Return True when value is a valid invoice ID; otherwise False."""
    if not isinstance(value, str):
        return False
    return _INVOICE_ID_PATTERN.fullmatch(value) is not None
