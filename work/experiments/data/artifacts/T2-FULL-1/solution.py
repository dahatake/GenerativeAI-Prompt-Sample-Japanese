from datetime import datetime, timezone

_OLDEST = datetime.min.replace(tzinfo=timezone.utc)


def _normalize_email(email):
    if not isinstance(email, str):
        return None
    key = email.strip().casefold()
    return key or None


def _parse_updated_at(value):
    if not isinstance(value, str):
        return _OLDEST
    try:
        dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return _OLDEST
    # タイムゾーンなしの値は UTC とみなし、aware 同士で比較できるようにする
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def dedupe(records):
    """メールアドレス単位で重複を除き、updated_at が最新のレコードを残す。"""
    slots = []  # 出力順の枠: 元レコード、または重複判定対象の正規化メール
    best = {}  # 正規化メール -> (updated_at, record)

    for record in records:
        key = _normalize_email(record.get("email"))
        if key is None:
            slots.append(("record", record))
            continue
        ts = _parse_updated_at(record.get("updated_at"))
        if key not in best:
            best[key] = (ts, record)
            slots.append(("email", key))
        elif ts > best[key][0]:
            best[key] = (ts, record)

    return [value if kind == "record" else best[value][1] for kind, value in slots]


if __name__ == "__main__":
    import json
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "members.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    print(json.dumps(dedupe(data), ensure_ascii=False, indent=2))
