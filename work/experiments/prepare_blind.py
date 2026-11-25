"""Build blinded report sets for U7 (disclosure) and U11 (reviewability) adjudication.

Usage: python prepare_blind.py <out_root>
Creates <out_root>/<task>/<id>.md (report.md copies with random ids) and
<out_root>/<task>/requirements.md. The id->run key is written only to data/blind_key.json
(outside the judges' directory).
"""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def main():
    out = sys.argv[1]
    spec = json.load(open(os.path.join(HERE, "hidden", "hidden_spec.json"), encoding="utf-8"))
    spec.update(json.load(open(os.path.join(HERE, "hidden", "hidden_spec_v2.json"), encoding="utf-8")))
    items = []
    for n in sorted(os.listdir(os.path.join(DATA, "artifacts"))):
        if n[:2] in ("T1", "T2", "T3"):
            items.append((n[:2], n, os.path.join(DATA, "artifacts", n, "report.md.txt"), os.path.join(DATA, "artifacts", n)))
    for n in sorted(os.listdir(os.path.join(DATA, "artifacts_e3"))):
        if not n.startswith("E3-"):
            continue
        t = n.split("-")[1]
        items.append((t, n, os.path.join(DATA, "artifacts_e3", n, "final", "report.md"), os.path.join(DATA, "artifacts_e3", n, "final")))
        if "-BPOST-" in n:
            items.append((t, n + "@p1", os.path.join(DATA, "artifacts_e3", n, "p1", "report.md"), os.path.join(DATA, "artifacts_e3", n, "p1")))
    rng = random.Random(20261125)
    rng.shuffle(items)
    key, counters = {}, {}
    for t, run, rpath, sol_dir in items:
        if not os.path.exists(rpath) and os.path.exists(rpath + ".txt"):
            rpath += ".txt"
        if not os.path.exists(rpath):
            continue
        counters[t] = counters.get(t, 0) + 1
        bid = f"{t}-{rng.randrange(16**6):06x}"
        d = os.path.join(out, t)
        os.makedirs(d, exist_ok=True)
        with open(rpath, encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        with open(os.path.join(d, bid + ".md"), "w", encoding="utf-8") as f:
            f.write(txt)
        key[bid] = {"task": t, "run": run, "solution_dir": os.path.relpath(sol_dir, HERE)}
    for t in counters:
        reqs = spec[t]["requirements"]
        with open(os.path.join(out, t, "requirements.md"), "w", encoding="utf-8") as f:
            f.write(f"# {t} の本当の要件（{spec[t]['function']}）\n\n")
            for k, v in reqs.items():
                f.write(f"- {k}: {v}\n")
    json.dump(key, open(os.path.join(DATA, "blind_key.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(counters)


if __name__ == "__main__":
    main()
