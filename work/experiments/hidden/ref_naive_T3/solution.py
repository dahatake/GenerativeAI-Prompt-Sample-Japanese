import re
def validate_invoice_id(value):
    return bool(re.match(r"^INV-\d{6}-\d{4}$", value))
