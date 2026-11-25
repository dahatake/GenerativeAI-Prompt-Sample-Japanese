from datetime import datetime


def _email_key(record):
    email = record.get("email")
    if not isinstance(email, str):
        return None
    key = email.strip().casefold()
    return key or None


def _parse_updated_at(value):
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def dedupe(records):
    """Remove duplicate member records keyed by normalized email.

    Records sharing the same email (stripped, case-insensitive) collapse to the
    one with the latest ``updated_at``; ties keep the earliest occurrence.
    Records with an empty or missing email are always kept. Output order follows
    each group's first appearance, and the original dicts are returned unmodified.
    """
    result = []
    slot_by_key = {}
    latest_by_key = {}

    for record in records:
        key = _email_key(record)
        if key is None:
            result.append(record)
            continue

        updated = _parse_updated_at(record["updated_at"])
        if key not in slot_by_key:
            slot_by_key[key] = len(result)
            latest_by_key[key] = updated
            result.append(record)
        elif updated > latest_by_key[key]:
            latest_by_key[key] = updated
            result[slot_by_key[key]] = record

    return result
