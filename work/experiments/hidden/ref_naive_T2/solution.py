def dedupe(records):
    seen, out = set(), []
    for r in records:
        if r["email"] in seen: continue
        seen.add(r["email"]); out.append(r)
    return out
