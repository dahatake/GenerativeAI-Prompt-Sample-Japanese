import re


_INVOICE_ID = re.compile(r"INV-(?P<year>[0-9]{4})(?:0[1-9]|1[0-2])-(?P<serial>[0-9]{4})")


def validate_invoice_id(value) -> bool:
    if not isinstance(value, str):
        return False

    match = _INVOICE_ID.fullmatch(value)
    return (
        match is not None
        and 2020 <= int(match["year"]) <= 2099
        and match["serial"] != "0000"
    )
