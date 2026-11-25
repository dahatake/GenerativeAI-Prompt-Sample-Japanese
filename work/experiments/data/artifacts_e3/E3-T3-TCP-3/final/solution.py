import re

# INV-YYYYMM-NNNN: year 2020-2099, month 01-12, ASCII digits only ([0-9], not \d).
_INVOICE_ID_RE = re.compile(r"INV-20[2-9][0-9](?:0[1-9]|1[0-2])-([0-9]{4})")


def validate_invoice_id(value) -> bool:
    if not isinstance(value, str):
        return False
    match = _INVOICE_ID_RE.fullmatch(value)
    if match is None:
        return False
    return match.group(1) != "0000"
