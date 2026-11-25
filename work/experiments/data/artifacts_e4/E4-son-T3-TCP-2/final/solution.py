import re

_INVOICE_ID = re.compile(r"INV-20[2-9][0-9](?:0[1-9]|1[0-2])-(?!0000)[0-9]{4}")


def validate_invoice_id(value) -> bool:
    """INV-YYYYMM-NNNN（YYYY=2020〜2099, MM=01〜12, NNNN=0001〜9999）か判定する。"""
    if not isinstance(value, str):
        return False
    return _INVOICE_ID.fullmatch(value) is not None
