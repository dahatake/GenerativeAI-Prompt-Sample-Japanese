"""E9 (H28): per-requirement pass rates of B-type vs TC-type outputs, stratified by the blind cue classification.

Units (existing v1-v3 data, re-scored with the pre-registered hidden tests):
  B      : v1 B (final), v2/v3 B-POST Phase 1 snapshot (= B output before answers)
  TC     : v1/v2 TC (final), v2/v3 TC+ (final)   ["TC-type"]
  NOASK  : v2/v3 NOASK (final)  (reported for reference)
Usage: python analyze_e9.py [rater_A.json rater_B.json]
Writes data/e9_req_pass.csv and, when rater files are given, data/e9_classification.csv and prints the stratified table.
"""
import collections, csv, glob, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
TESTS = {"T1": "hidden_tests.py", "T2": "hidden_tests.py", "T3": "hidden_tests.py", "T4": "hidden_tests_v2.py",
         "T5": "hidden_tests_v2.py", "T6": "hidden_tests_v3.py"}
NREQ = {"T1": 4, "T2": 4, "T3": 4, "T4": 4, "T5": 6, "T6": 10}


def hidden(task, d):
    if not os.path.exists(os.path.join(d, "solution.py")):
        return None
    p = subprocess.run([sys.executable, "-B", os.path.join(HERE, "hidden", TESTS[task]), task, d], capture_output=True,
                       text=True, encoding="utf-8", timeout=300)
    lines = p.stdout.strip().splitlines()
    return json.loads(lines[-1]) if lines else None


def units():
    for d in sorted(glob.glob(os.path.join(DATA, "artifacts", "T[123]-*-*"))):
        m = re.match(r"(T\d)-(B|TC)-(\d)$", os.path.basename(d))
        if m:
            yield "v1", "opus-default", m.group(1), {"B": "B", "TC": "TC"}[m.group(2)], d
    for d in sorted(glob.glob(os.path.join(DATA, "artifacts_e3", "E3-T*-*-*"))):
        m = re.match(r"E3-(T\d)-(BPOST|TC|TCP|NOASK)-(\d)$", os.path.basename(d))
        if not m:
            continue
        t, c = m.group(1), m.group(2)
        if c == "BPOST":
            yield "v2", "opus-default", t, "B", os.path.join(d, "p1")
        else:
            yield "v2", "opus-default", t, {"TC": "TC", "TCP": "TC", "NOASK": "NOASK"}[c], os.path.join(d, "final")
    for d in sorted(glob.glob(os.path.join(DATA, "artifacts_e4", "E[45]-*"))):
        b = os.path.basename(d)
        m = re.match(r"E4-(mai|son|gpt)-(T\d)-(BPOST|TCP|NOASK)-(\d)$", b) or re.match(r"E5-(T6)-(BPOST|TCP|NOASK)-(\d)$", b)
        if not m:
            continue
        if b.startswith("E5"):
            model, t, c = "opus-default", m.group(1), m.group(2)
        else:
            model, t, c = m.group(1), m.group(2), m.group(3)
        if c == "BPOST":
            yield "v3", model, t, "B", os.path.join(d, "p1")
        else:
            yield "v3", model, t, {"TCP": "TC", "NOASK": "NOASK"}[c], os.path.join(d, "final")


def main():
    rows = []
    for ver, model, t, grp, d in units():
        f = hidden(t, d)
        if f is None:
            rows.append({"version": ver, "model": model, "task": t, "group": grp, "dir": os.path.relpath(d, DATA), "req": "", "pass": "",
                         "note": "no solution.py"})
            continue
        for i in range(1, NREQ[t] + 1):
            rows.append({"version": ver, "model": model, "task": t, "group": grp, "dir": os.path.relpath(d, DATA),
                         "req": f"{t}-R{i}", "pass": int(bool(f.get(f"R{i}"))), "note": ""})
    with open(os.path.join(DATA, "e9_req_pass.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("units:", collections.Counter((r["version"], r["group"]) for r in rows if r["req"].endswith("R1")))
    print("missing:", [r["dir"] for r in rows if r["note"]])
    if len(sys.argv) < 3:
        return
    ra = {x["id"]: x for x in json.load(open(sys.argv[1], encoding="utf-8"))}
    rb = {x["id"]: x for x in json.load(open(sys.argv[2], encoding="utf-8"))}
    ids = sorted(ra, key=lambda s: (s.split("-")[0], int(s.split("R")[1])))
    agree_cue = sum(ra[i]["cue"] == rb[i]["cue"] for i in ids)
    agree_val = sum(ra[i]["value"] == rb[i]["value"] for i in ids)
    with open(os.path.join(DATA, "e9_classification.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "cue_A", "value_A", "cue_B", "value_B", "evidence_A", "evidence_B"])
        for i in ids:
            w.writerow([i, ra[i]["cue"], ra[i]["value"], rb[i]["cue"], rb[i]["value"], ra[i]["evidence"], rb[i]["evidence"]])
    print(f"agreement cue {agree_cue}/{len(ids)}, value {agree_val}/{len(ids)}")
    for label, keep in (("rater A (primary)", lambda i: True), ("agreed only (sensitivity)", lambda i: ra[i]["cue"] == rb[i]["cue"])):
        print(f"\n== {label}")
        for axis in ("cue", "value"):
            agg = collections.defaultdict(lambda: [0, 0])
            for r in rows:
                if not r["req"] or r["req"] not in ra or not keep(r["req"]):
                    continue
                k = (ra[r["req"]][axis], r["group"])
                agg[k][0] += r["pass"]
                agg[k][1] += 1
            for lvl in ("yes", "no"):
                cells = []
                for g in ("B", "NOASK", "TC"):
                    p, n = agg[(lvl, g)]
                    cells.append(f"{g} {p}/{n}={p / n:.1%}" if n else f"{g} -")
                nreq = len({i for i in ids if ra[i][axis] == lvl and keep(i)})
                print(f"{axis}={lvl} (reqs={nreq}): " + "  ".join(cells))


if __name__ == "__main__":
    main()
