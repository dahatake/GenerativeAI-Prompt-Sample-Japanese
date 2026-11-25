import re


_INVOICE_ID_PATTERN = re.compile(r"INV-[0-9]{4}([0-9]{2})-[0-9]{4}\Z")


def validate_invoice_id(value):
    """Return whether value has the supported invoice ID format."""
    if not isinstance(value, str):
        return False

    match = _INVOICE_ID_PATTERN.fullmatch(value)
    if match is None:
        return False

    month = int(match.group(1))
    if month < 1 or month > 12:
        return False

    sequence = value.rsplit("-", 1)[1]
    return sequence != "0000"

