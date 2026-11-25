import re


_INVOICE_ID = re.compile(r"INV-(?P<year>[0-9]{4})(?:0[1-9]|1[0-2])-(?P<sequence>[0-9]{4})")


def validate_invoice_id(value: object) -> bool:
    """Return whether value is an invoice ID in the approved format."""
    if not isinstance(value, str):
        return False

    match = _INVOICE_ID.fullmatch(value)
    return (
        match is not None
        and match.group("year") != "0000"
        and match.group("sequence") != "0000"
    )
