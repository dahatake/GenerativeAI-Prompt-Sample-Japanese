import re

# 形式: INV-YYYYMM-NNNN（例: INV-202601-0001）
_INVOICE_ID_PATTERN = re.compile(r"INV-([0-9]{4})(0[1-9]|1[0-2])-([0-9]{4})")


def validate_invoice_id(value) -> bool:
    """請求書番号が INV-YYYYMM-NNNN 形式として正しければ True を返す。"""
    if not isinstance(value, str):
        return False
    match = _INVOICE_ID_PATTERN.fullmatch(value)
    if match is None:
        return False
    # 連番 0000 は発行されない前提
    return match.group(3) != "0000"
