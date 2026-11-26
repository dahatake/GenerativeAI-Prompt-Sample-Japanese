"""Cross-version ladder: what makes a Task Contract prompt work compared with a conventional prompt.

Re-scores every run of v1-v4 with the pre-registered hidden tests (per requirement), then
  1) compares adjacent conditions on a ladder within matched (model, task) strata (one-sided permutation tests), and
  2) decomposes answered conditions by whether each hidden requirement surfaced in the answers (data/surfacing_rules.json).
Usage: python analyze_ladder.py            -> data/ladder_req.csv, data/ladder_summary.json, data/mechanism_packet.md.txt
       python analyze_ladder.py <rater.json>  -> also compares the keyword rule with an independent rater
Conditions: B (conventional short request; v1 B, and the Phase 1 snapshot of B-POST), FULL (all rules given), NOASK (contract
structure, plan and self-tests, no answers), TC (questions + answers), TCP (TC+, value options + one follow-up), TCPCL (TC+ with
an aspect checklist), BPOST (B, then answers to report.md and a fix), BALL (B-POST with "list all assumptions"), BALL_p1,
OFULL / OFILE (v4 E7b; Phase 1 copied from v3 B-POST, so not counted again as B).
"""
import collections, csv, glob, hashlib, json, os, random, re, subprocess, sys
from analyze_e3 import perm_test

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
TESTS = {"T1": "hidden_tests.py", "T2": "hidden_tests.py", "T3": "hidden_tests.py", "T4": "hidden_tests_v2.py",
         "T5": "hidden_tests_v2.py", "T6": "hidden_tests_v3.py"}
NREQ = {"T1": 4, "T2": 4, "T3": 4, "T4": 4, "T5": 6, "T6": 10}
MODEL = {"mai": "mai-code-2-flash", "son": "claude-sonnet-5.5", "gpt": "gpt-6.2-sol"}
DEFAULT = "claude-opus-5.5"


def read(p):
    for q in (p, p + ".txt"):
        if os.path.exists(q):
            return open(q, encoding="utf-8", errors="ignore").read()
    return ""


def hidden(task, d):
    if not os.path.exists(os.path.join(d, "solution.py")):
        return None
    p = subprocess.run([sys.executable, "-B", os.path.join(HERE, "hidden", TESTS[task]), task, d], capture_output=True,
                       text=True, encoding="utf-8", timeout=300)
    lines = p.stdout.strip().splitlines()
    return json.loads(lines[-1]) if lines else None


def units():
    """Yield (version, model, task, cond, run_id, dir, answers_text or None)."""
    v1 = {r["run_id"]: r["answers_verbatim"] for r in json.load(open(os.path.join(DATA, "oracle_log.json"), encoding="utf-8"))}
    for d in sorted(glob.glob(os.path.join(DATA, "artifacts", "T[123]-*-*"))):
        m = re.match(r"(T\d)-(B|TC|FULL)-(\d)$", os.path.basename(d))
        if m:
            rid = os.path.basename(d)
            yield "v1", DEFAULT, m[1], m[2], rid, d, v1.get(rid) if m[2] == "TC" else None
    for root, ver in (("artifacts_e3", "v2"), ("artifacts_e4", "v3"), ("artifacts_e6", "v4")):
        for d in sorted(glob.glob(os.path.join(DATA, root, "E*"))):
            rid = os.path.basename(d)
            m = (re.match(r"E3-(T\d)-(BPOST|TC|TCP|NOASK|FULL)-(\d)$", rid) or
                 re.match(r"E5-(T6)-(BPOST|TCP|NOASK|FULL)-(\d)$", rid))
            model = DEFAULT
            if not m:
                m2 = re.match(r"E(?:4|6|7a|7b)-(mai|son|gpt)-(T\d)-(BPOST|TCP|TCPCL|NOASK|BALL|OFULL|OFILE)-(\d)$", rid)
                if not m2:
                    continue
                model, task, cond = MODEL[m2[1]], m2[2], m2[3]
            else:
                task, cond = m[1], m[2]
            fin = os.path.join(d, "final")
            ans = (read(os.path.join(fin, "answers.md")) + "\n" + read(os.path.join(fin, "answers2.md"))).strip() or None
            if cond in ("BPOST", "BALL"):
                yield ver, model, task, "B" if cond == "BPOST" else "BALL_p1", rid, os.path.join(d, "p1"), None
            yield ver, model, task, cond, rid, fin, ans if cond not in ("NOASK", "FULL") else None


def surfaced(rules, task, answers):
    out = {}
    sents = [s for s in re.split(r"[。\n]", answers or "") if s.strip() and "特に指定" not in s]
    for req, pat in rules[task].items():
        out[req] = any(re.search(pat, s, re.I) for s in sents)
    return out


def score(xs):
    return round(sum(xs) / len(xs), 3) if xs else None


def main():
    rules = json.load(open(os.path.join(DATA, "surfacing_rules.json"), encoding="utf-8"))
    rows, runs = [], []
    for ver, model, task, cond, rid, d, ans in units():
        f = hidden(task, d)
        if f is None:
            continue
        reqs = [f"R{i}" for i in range(1, NREQ[task] + 1)]
        sf = surfaced(rules, task, ans) if ans is not None else {}
        for r in reqs:
            rows.append({"version": ver, "model": model, "task": task, "condition": cond, "run_id": rid, "req": f"{task}-{r}",
                         "pass": int(bool(f.get(r))), "answered": int(ans is not None),
                         "surfaced_kw": int(sf.get(r, False)) if ans is not None else ""})
        runs.append({"version": ver, "model": model, "task": task, "cond": cond, "run_id": rid, "answers": ans,
                     "score": sum(bool(f.get(r)) for r in reqs) / len(reqs)})
    with open(os.path.join(DATA, "ladder_req.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    def strata(cond, tasks=None, models=None):
        g = {}
        for r in runs:
            if r["cond"] in cond and (tasks is None or r["task"] in tasks) and (models is None or r["model"] in models):
                g.setdefault(f'{r["model"]}|{r["task"]}', []).append(r["score"])
        return g

    def comp(a, b, label, step):
        ga, gb = strata(a), strata(b)
        common = sorted(set(ga) & set(gb))
        ga = {k: ga[k] for k in common}
        gb = {k: gb[k] for k in common}
        obs, p, meth, n = perm_test(ga, gb)
        return {"step": step, "comparison": label, "strata": common, "n_a": sum(map(len, ga.values())),
                "n_b": sum(map(len, gb.values())), "mean_a": score([x for v in ga.values() for x in v]),
                "mean_b": score([x for v in gb.values() for x in v]), "diff": round(obs, 3), "p_one_sided": round(p, 4), "method": meth}

    ladder = [
        comp(["NOASK"], ["B"], "NOASK - B", "1 contract structure, plan and self-tests without answers"),
        comp(["TC", "TCP"], ["NOASK"], "TC/TC+ - NOASK", "2 answers to the agent's questions"),
        comp(["TCP"], ["TC"], "TC+ - TC", "3 options written as concrete values (+1 follow-up)"),
        comp(["TCPCL"], ["TCP"], "TC+CL - TC+", "4 aspect checklist in Spec Mode"),
        comp(["BPOST"], ["B"], "B-POST - B", "post-hoc answers to report.md and a fix"),
        comp(["BALL"], ["BPOST"], "BALL - B-POST", "list all assumptions before post-hoc answers"),
        comp(["OFULL"], ["OFILE"], "OFULL - OFILE", "answerer reads the whole report"),
        comp(["TCP", "TCPCL"], ["BPOST", "BALL"], "Spec Mode (TC+/TC+CL) - post-hoc (B-POST/BALL)", "timing: before vs after implementation"),
        comp(["TC", "TCP", "TCPCL"], ["B"], "TC family - B", "overall: Task Contract prompt vs conventional prompt"),
        comp(["FULL"], ["B"], "FULL - B", "reference: all rules written in the request"),
    ]
    cells = collections.defaultdict(list)
    for r in runs:
        cells[r["cond"]].append(r["score"])
    # mechanism: answered conditions, pass by surfacing
    mech = collections.defaultdict(lambda: [0, 0])
    for x in rows:
        if x["answered"]:
            k = (x["condition"], x["surfaced_kw"])
            mech[k][0] += x["pass"]
            mech[k][1] += 1
    allm = collections.defaultdict(lambda: [0, 0])
    for (c, s), (p, n) in mech.items():
        allm[s][0] += p
        allm[s][1] += n
    base = collections.defaultdict(lambda: [0, 0])  # same requirements in B (no answers)
    for x in rows:
        if x["condition"] == "B":
            base[x["req"]][0] += x["pass"]
            base[x["req"]][1] += 1
    out = {"conditions": {c: {"n_runs": len(v), "mean": score(v)} for c, v in sorted(cells.items())},
           "ladder": ladder,
           "mechanism_by_condition": {f"{c}|surfaced={s}": {"pass": p, "n": n, "rate": round(p / n, 3)} for (c, s), (p, n) in sorted(mech.items())},
           "mechanism_all_answered": {f"surfaced={s}": {"pass": p, "n": n, "rate": round(p / n, 3)} for s, (p, n) in sorted(allm.items())},
           "surfacing_rate_by_condition": {c: round(sum(n for (cc, s), (p, n) in mech.items() if cc == c and s == 1) /
                                                 sum(n for (cc, s), (p, n) in mech.items() if cc == c), 3)
                                           for c in sorted({c for c, _ in mech})}}
    # requirements that failed in B: are they fixed when surfaced?
    fixed = collections.defaultdict(lambda: [0, 0])
    for x in rows:
        if x["answered"] and base[x["req"]][1] and base[x["req"]][0] / base[x["req"]][1] < 0.5:
            fixed[x["surfaced_kw"]][0] += x["pass"]
            fixed[x["surfaced_kw"]][1] += 1
    out["mechanism_on_requirements_B_usually_fails"] = {f"surfaced={s}": {"pass": p, "n": n, "rate": round(p / n, 3)} for s, (p, n) in sorted(fixed.items())}
    # anonymized packet for the independent rater (no scores, no conditions)
    spec = {}
    for f in ("hidden_spec.json", "hidden_spec_v2.json", "hidden_spec_v3.json"):
        spec.update(json.load(open(os.path.join(HERE, "hidden", f), encoding="utf-8")))
    answered = [r for r in runs if r["answers"]]
    rnd = random.Random(20261126)
    rnd.shuffle(answered)
    key, lines = {}, ["# 回答の内容の判定用資料", "",
                      "各項目について、「依頼者が AI に渡した回答」が、列挙した各要件を AI に伝えている（訂正している、または AI の仮定を正しいと確認している）かを判定してください。", ""]
    for i, r in enumerate(answered, 1):
        aid = f"A{i:03d}"
        key[aid] = r["run_id"] + "|" + r["cond"]
        lines += [f"## {aid}（課題 {r['task']}）", "", "要件:"]
        lines += [f"- {r['task']}-{k}: {v}" for k, v in spec[r["task"]]["requirements"].items()]
        lines += ["", "回答:", "", "```text", r["answers"].strip(), "```", ""]
    open(os.path.join(DATA, "mechanism_packet.md.txt"), "w", encoding="utf-8").write("\n".join(lines))
    json.dump(key, open(os.path.join(DATA, "mechanism_packet_key.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    out["packet_sha256"] = hashlib.sha256(open(os.path.join(DATA, "mechanism_packet.md.txt"), "rb").read()).hexdigest()
    if len(sys.argv) > 1:
        rater = json.load(open(sys.argv[1], encoding="utf-8"))  # {"A001": {"T1-R1": 1, ...}, ...}
        kw = {(x["run_id"] + "|" + x["condition"], x["req"]): x for x in rows if x["answered"]}
        agree = tot = 0
        rm = collections.defaultdict(lambda: [0, 0])
        rf = collections.defaultdict(lambda: [0, 0])
        for aid, marks in rater.items():
            for req, v in marks.items():
                x = kw.get((key[aid], req))
                if not x:
                    continue
                tot += 1
                agree += int(bool(v)) == x["surfaced_kw"]
                rm[int(bool(v))][0] += x["pass"]
                rm[int(bool(v))][1] += 1
                if base[req][1] and base[req][0] / base[req][1] < 0.5:
                    rf[int(bool(v))][0] += x["pass"]
                    rf[int(bool(v))][1] += 1
        out["rater_agreement"] = {"agree": agree, "n": tot, "rate": round(agree / tot, 3) if tot else None}
        out["mechanism_all_answered_rater"] = {f"surfaced={s}": {"pass": p, "n": n, "rate": round(p / n, 3)} for s, (p, n) in sorted(rm.items())}
        out["mechanism_on_requirements_B_usually_fails_rater"] = {f"surfaced={s}": {"pass": p, "n": n, "rate": round(p / n, 3)} for s, (p, n) in sorted(rf.items())}
        # added after the protocol was fixed (output only): surfacing rate by condition with the rater's classification
        sr = collections.defaultdict(lambda: [0, 0])
        for aid, marks in rater.items():
            cond = key[aid].split("|")[1]
            for v in marks.values():
                sr[cond][0] += int(bool(v))
                sr[cond][1] += 1
        out["surfacing_rate_by_condition_rater"] = {c: round(a / n, 3) for c, (a, n) in sorted(sr.items())}
    json.dump(out, open(os.path.join(DATA, "ladder_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in out if k not in ("ladder",)}, ensure_ascii=False, indent=1))
    for l in ladder:
        print(l["step"], "|", l["comparison"], l["mean_a"], l["mean_b"], l["diff"], "p=", l["p_one_sided"], "n", l["n_a"], l["n_b"], "strata", len(l["strata"]))


if __name__ == "__main__":
    main()
