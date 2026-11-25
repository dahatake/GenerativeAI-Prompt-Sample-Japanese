import re

_INVOICE_ID_RE = re.compile(r"INV-[0-9]{4}(?:0[1-9]|1[0-2])-[0-9]{4}")


def validate_invoice_id(value) -> bool:
    if not isinstance(value, str):
        return False
    return _INVOICE_ID_RE.fullmatch(value) is not None
