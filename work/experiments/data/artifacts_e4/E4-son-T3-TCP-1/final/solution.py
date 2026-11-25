import re

_PATTERN = re.compile(r"INV-(20(?:2[0-9]|[3-9][0-9]))(0[1-9]|1[0-2])-([0-9]{4})")


def validate_invoice_id(value) -> bool:
    if not isinstance(value, str):
        return False
    m = _PATTERN.fullmatch(value)
    return m is not None and m.group(3) != "0000"
