import re

_INVOICE_ID = re.compile(r"INV-[0-9]{4}(?:0[1-9]|1[0-2])-([0-9]{4})")


def validate_invoice_id(value) -> bool:
    """INV-YYYYMM-NNNN 形式（MM は 01-12、NNNN は 0001-9999）なら True。"""
    if type(value) is not str:
        return False
    m = _INVOICE_ID.fullmatch(value)
    return m is not None and m.group(1) != "0000"
