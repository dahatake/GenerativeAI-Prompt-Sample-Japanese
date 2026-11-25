import re


_INVOICE_ID = re.compile(r"INV-([0-9]{4})([0-9]{2})-([0-9]{4})")


def validate_invoice_id(value: object) -> bool:
    if not isinstance(value, str):
        return False

    match = _INVOICE_ID.fullmatch(value)
    if match is None:
        return False

    year, month, sequence = match.groups()
    return 2020 <= int(year) <= 2099 and 1 <= int(month) <= 12 and sequence != "0000"
