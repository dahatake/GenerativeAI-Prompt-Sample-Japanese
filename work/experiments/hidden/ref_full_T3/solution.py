import re
def validate_invoice_id(value):
    if not isinstance(value, str):
        return False
    m = re.fullmatch(r"INV-(\d{4})(\d{2})-(\d{4})", value)
    if not m:
        return False
    y, mo, n = int(m[1]), int(m[2]), m[3]
    return 2020 <= y <= 2099 and 1 <= mo <= 12 and n != "0000"
