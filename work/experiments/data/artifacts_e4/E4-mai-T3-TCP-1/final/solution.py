import re


_INVOICE_ID_PATTERN = re.compile(r"INV-([0-9]{4})([0-9]{2})-([0-9]{4})\Z")


def validate_invoice_id(value):
    """Return True when value follows the approved invoice identifier format."""
    if not isinstance(value, str):
        return False

    match = _INVOICE_ID_PATTERN.fullmatch(value)
    if match is None:
        return False

    year = int(match.group(1))
    month = int(match.group(2))
    serial = int(match.group(3))

    return bool(2020 <= year <= 2099 and 1 <= month <= 12 and 1 <= serial <= 9999)
