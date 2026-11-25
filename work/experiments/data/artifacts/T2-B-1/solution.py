from datetime import datetime, timezone

_OLDEST = datetime.min.replace(tzinfo=timezone.utc)


def _email_key(record):
    email = record.get("email")
    if not isinstance(email, str):
        return None
    key = email.strip().lower()
    return key or None


def _updated_at(record):
    value = record.get("updated_at")
    if not isinstance(value, str):
        return _OLDEST
    try:
        dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return _OLDEST
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def dedupe(records):
    """Remove duplicate member records.

    Records are considered duplicates when their email matches after trimming
    whitespace and lowercasing. Among duplicates, the record with the latest
    ``updated_at`` is kept (ties keep the earlier one). Records without a usable
    email cannot be identified and are all kept. Output order follows the first
    appearance of each group; the original dicts are returned unmodified.
    """
    result = []
    index_by_key = {}
    for record in records:
        key = _email_key(record)
        if key is None:
            result.append(record)
            continue
        if key not in index_by_key:
            index_by_key[key] = len(result)
            result.append(record)
            continue
        i = index_by_key[key]
        if _updated_at(record) > _updated_at(result[i]):
            result[i] = record
    return result


if __name__ == "__main__":
    import json
    import sys
    from pathlib import Path

    path = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).with_name("members.json"))
    data = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(dedupe(data), ensure_ascii=False, indent=2))
