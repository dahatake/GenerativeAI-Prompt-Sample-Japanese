import re
from typing import cast


_INVOICE_ID_PATTERN = re.compile(
    r"INV-(?!0000)[0-9]{4}(?:0[1-9]|1[0-2])-(?!0000)[0-9]{4}"
)


def validate_invoice_id(value: object) -> bool:
    """Return whether value has a valid invoice ID format, regardless of issuance."""
    if not issubclass(type(value), str):
        return False
    return _INVOICE_ID_PATTERN.fullmatch(cast(str, value)) is not None
