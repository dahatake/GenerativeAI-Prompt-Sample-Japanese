"""Post-hoc add-on to analyze_ladder.py (v1.5, deviation D-v1.5-1; kept separate so that analyze_ladder.py stays byte-identical to the version recorded in the gist).

Adds, to data/ladder_summary.json, the surfacing rate by condition according to the independent rater.
Usage (after `python analyze_ladder.py data/mechanism_rater.json`):  python analyze_ladder_rater_by_condition.py data/mechanism_rater.json
"""
import collections, json, os, sys

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
key = json.load(open(os.path.join(DATA, "mechanism_packet_key.json"), encoding="utf-8"))
rater = json.load(open(sys.argv[1], encoding="utf-8"))
sr = collections.defaultdict(lambda: [0, 0])
for aid, marks in rater.items():
    cond = key[aid].split("|")[1]
    for v in marks.values():
        sr[cond][0] += int(bool(v))
        sr[cond][1] += 1
path = os.path.join(DATA, "ladder_summary.json")
out = json.load(open(path, encoding="utf-8"))
out["surfacing_rate_by_condition_rater"] = {c: round(a / n, 3) for c, (a, n) in sorted(sr.items())}
json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(out["surfacing_rate_by_condition_rater"])
