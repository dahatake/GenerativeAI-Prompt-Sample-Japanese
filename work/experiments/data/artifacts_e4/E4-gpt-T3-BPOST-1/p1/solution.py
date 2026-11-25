import re


_INVOICE_ID = re.compile(r"INV-([0-9]{4})(?:0[1-9]|1[0-2])-([0-9]{4})")


def validate_invoice_id(value: object) -> bool:
    if not isinstance(value, str):
        return False

    match = _INVOICE_ID.fullmatch(value)
    return match is not None and match[1] != "0000" and match[2] != "0000"
