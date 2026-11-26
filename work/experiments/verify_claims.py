"""Claims ledger: recompute the key numbers of the whitepaper from the data, and check that the text states the same values.

Usage: python verify_claims.py   -> prints PASS/FAIL per claim and writes data/claims_ledger.csv
Each claim = (id, section, how it is written in the text, value recomputed from the data files).
A claim passes when the recomputed value, formatted as in the text, is found in the whitepaper.
"""
import csv, json, os, re, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
WP = open(os.path.join(HERE, "..", "TaskContractWhitepaper.md"), encoding="utf-8").read()
J = lambda f: json.load(open(os.path.join(DATA, f), encoding="utf-8"))


def pt(x):  # percentage points / percent with one decimal
    return f"{x * 100:.1f}"


def pct(x):
    v = f"{x * 100:.1f}"
    return v[:-2] if v.endswith(".0") else v


def runs(f, cond, tasks, model=None):
    out = []
    for r in csv.DictReader(open(os.path.join(DATA, f), encoding="utf-8")):
        if r["condition"] == cond and r["task"] in tasks and (model is None or r.get("model") == model):
            out.append(int(r["hidden_pass"]) / int(r.get("n_req") or (6 if r["task"] == "T5" else 4)))
    return out


def claims():
    e3, e4, e6, lad = J("summary_e3.json"), J("summary_e4.json"), J("summary_e6.json"), J("ladder_summary.json")
    t3 = e3["tests"]
    c = []
    n_runs = sum(len([d for d in os.listdir(os.path.join(DATA, a)) if os.path.isdir(os.path.join(DATA, a, d))])
                 for a in ("artifacts", "artifacts_e3", "artifacts_e4", "artifacts_e6"))
    c.append(("N-total", "header", "計 {} 回", str(n_runs)))
    tc = runs("scores_e1.csv", "TC", ["T1", "T3"]) + runs("scores_e3.csv", "TC", ["T4", "T5"])
    c.append(("v2-TC", "付録D-1", "TC {}%", pct(statistics.mean(tc))))
    c.append(("v2-NOASK", "付録D-1", "NOASK {}%", pct(statistics.mean(runs("scores_e3.csv", "NOASK", ["T1", "T3", "T4", "T5"])))))
    c.append(("v2-BPOST", "付録D-1", "B-POST は {}%", pct(statistics.mean(runs("scores_e3.csv", "BPOST", ["T1", "T3", "T4", "T5"])))))
    c.append(("H8", "付録D-1", "TC と NOASK の差は {}ポイント", pt(t3["PREREG_H8_TC_vs_NOASK(T1,T3,T4,T5)"]["diff"])))
    c.append(("H8-p", "付録D-1", "片側 p={}", str(t3["PREREG_H8_TC_vs_NOASK(T1,T3,T4,T5)"]["p_one_sided"])))
    c.append(("H7", "付録D-1", "B-POST が {}ポイント高かった", pt(t3["PREREG_H7_BPOST_vs_TC(T1,T3,T4,T5)"]["diff"])))
    c.append(("H8b-p", "付録D-1", "NOASK と B の差は検出されなかった（p={}）", f'{t3["PREREG_H8b_B_vs_NOASK(T1,T3,T4,T5)"]["p_one_sided"]:.2f}'))
    t4 = e4["tests"]
    c.append(("H15", "付録D-7", "\\+{}ポイント、モデルと課題で層別", pt(t4["H15_TCP_vs_NOASK_3models"]["diff"])))
    c.append(("H17", "付録D-8", "TC\\+ が \\+{}ポイント上回った", pt(t4["H17_TCP_vs_BPOST_3models"]["diff"])))
    c.append(("H17-p", "付録D-8", "片側 p={}", f'{t4["H17_TCP_vs_BPOST_3models"]["p_one_sided"]:.4f}'))
    for m, row in e4["per_model"].items():
        if m == "default":
            continue
        c.append((f"T6-{m}-TCP", "表6", "\\| " + m + r" \|[^\n]*" + "{}%", pct(row["TCP"])))
    e5 = e4["E5"]["cells"]
    c.append(("E5-BPOST", "付録D-11", "B-POST は {}%", pct(e5["BPOST"]["mean"])))
    c.append(("E5-NOASK", "付録D-11", "NOASK は {}%", pct(e5["NOASK"]["mean"])))
    t6 = e6["tests"]
    c.append(("H23", "付録D-14", "TC\\+CL は[^\n]*{}%", pct(t6["H23_TCPCL_vs_TCP_v3v4"]["mean_a"])))
    c.append(("H23-ctrl", "付録D-14", "TC\\+ は {}%", pct(t6["H23_TCPCL_vs_TCP_v3v4"]["mean_b"])))
    c.append(("H23-p", "付録D-14", "片側 p={}", f'{t6["H23_TCPCL_vs_TCP_v3v4"]["p_one_sided"]:.3f}'))
    c.append(("H23-v4", "付録D-14", "p={}", f'{t6["H23_TCPCL_vs_TCP_v4_only"]["p_one_sided"]:.3f}'))
    c.append(("H24", "付録D-15", "BALL は {}%", pct(t6["H24_BALL_vs_BPOST_v3"]["mean_a"])))
    c.append(("H24-ctrl", "付録D-15", "B-POST は {}%", pct(t6["H24_BALL_vs_BPOST_v3"]["mean_b"])))
    c.append(("H24-p", "付録D-15", "片側 p={}", f'{t6["H24_BALL_vs_BPOST_v3"]["p_one_sided"]:.4f}'))
    c.append(("H25-p", "付録D-15", "片側 p={}", str(t6["H25_OFULL_vs_OFILE_paired"]["p_one_sided"])))
    e8 = e6["E8"]
    c.append(("E8", "付録D-16", "G {}/5、G\\+TB {}/5、G\\+TB2 {}/5", (e8["G"]["price_leak"], e8["GTB"]["price_leak"], e8["GTB2"]["price_leak"])))
    c.append(("H26-p", "付録D-16", "片側 p={}", f'{t6["H26_GTB2_lt_G_price_leak_fisher"]:.3f}'))
    c.append(("H26-ref", "付録D-16", "p={}", f'{t6["ref_GTB2_lt_GTB_price_leak_fisher"]:.3f}'))
    # E9 and rework (recomputed from the per-requirement files)
    cls = {r["id"]: r for r in csv.DictReader(open(os.path.join(DATA, "e9_classification.csv"), encoding="utf-8"))}
    agg = {}
    for r in csv.DictReader(open(os.path.join(DATA, "e9_req_pass.csv"), encoding="utf-8")):
        if r["req"] and r["group"] == "B":
            k = cls[r["req"]]["cue_A"]
            a = agg.setdefault(k, [0, 0])
            a[0] += int(r["pass"])
            a[1] += 1
    c.append(("E9-cue-yes", "付録D-17", "手がかりあり {}%", pct(agg["yes"][0] / agg["yes"][1])))
    c.append(("E9-cue-no", "付録D-17", "なし {}%", pt(agg["no"][0] / agg["no"][1])))
    rw = list(csv.DictReader(open(os.path.join(DATA, "rework_vs_scale.csv"), encoding="utf-8")))
    c.append(("rework-ratio", "4.20", "{}行（972行", f'{sum(int(x["rework"]) for x in rw) / sum(int(x["p1_failed"]) for x in rw):.1f}'))
    # ladder (v1.5)
    m = lad["mechanism_all_answered"]
    c.append(("mech-surf1", "要旨/5章", "{}%（440/442）", pct(m["surfaced=1"]["rate"])))
    c.append(("mech-surf0", "要旨/5章", "{}%（62/112）", pct(m["surfaced=0"]["rate"])))
    f = lad["mechanism_on_requirements_B_usually_fails"]
    c.append(("mech-fail-surf0", "要旨/5章", "{}/45", str(f["surfaced=0"]["pass"])))
    c.append(("mech-fail-surf1", "5章 表R2", "（{}/207）", str(f["surfaced=1"]["pass"])))
    mr = lad["mechanism_all_answered_rater"]
    c.append(("mech-rater-surf1", "5章 表R2", "{}%（438/439）", pct(mr["surfaced=1"]["rate"])))
    ag = lad["rater_agreement"]
    c.append(("rater-agree", "要旨/5章", "{}%", pct(ag["rate"])))
    c.append(("rater-agree-n", "5章", "554件中{}件", str(ag["agree"])))
    lad_by = {x["comparison"]: x for x in lad["ladder"]}
    req = list(csv.DictReader(open(os.path.join(DATA, "ladder_req.csv"), encoding="utf-8")))

    def surf_count(conds, strata=None):
        r = [x for x in req if x["condition"] in conds and (strata is None or f'{x["model"]}|{x["task"]}' in strata)]
        return f'{sum(int(x["surfaced_kw"]) for x in r)}/{len(r)}'

    s6 = set(lad_by["BALL - B-POST"]["strata"])
    c.append(("surf-BPOST-ballstrata", "5.4節", "B-POST の 31%（{}）", surf_count({"BPOST"}, s6)))
    c.append(("surf-BALL-ballstrata", "5.4節", "BALL は 96%（{}）", surf_count({"BALL"}, s6)))
    c.append(("surf-specmode", "5.5節", "Spec Mode が 94%（{}）", surf_count({"TCP", "TCPCL"})))
    c.append(("surf-posthoc", "5.5節", "事後確認が 71%（{}）", surf_count({"BPOST", "BALL"})))

    def sp(x):  # signed percentage points as written in the ladder table
        v = f"{x * 100:.1f}"
        return ("+" if x > 0 else "−") + v.lstrip("-")

    for comp, label in [("NOASK - B", "段1"), ("TC/TC+ - NOASK", "段2"), ("TC+ - TC", "段3"), ("TC+CL - TC+", "段4"),
                        ("B-POST - B", "段5"), ("BALL - B-POST", "段6"), ("OFULL - OFILE", "段7"),
                        ("Spec Mode (TC+/TC+CL) - post-hoc (B-POST/BALL)", "段8"), ("TC family - B", "段9"), ("FULL - B", "段10")]:
        x = lad_by[comp]
        c.append((f"ladder-{label}", "5章 表R1", "{}% 対 {}% \\|[^\n]*?{}", (pct(x["mean_a"]), pct(x["mean_b"]), sp(x["diff"]))))
    for cond, label in [("TC", "TC"), ("TCP", "TC+"), ("TCPCL", "TC+CL"), ("BPOST", "B-POST"), ("BALL", "BALL"), ("OFILE", "OFILE"), ("OFULL", "OFULL")]:
        c.append((f"surf-{label}", "5章 表R3", "\\| " + re.escape(label) + r" \|[^\n]*?" + "{}% / {}%",
                  (f'{lad["surfacing_rate_by_condition"][cond] * 100:.0f}', f'{lad["surfacing_rate_by_condition_rater"][cond] * 100:.0f}')))
    return c


def main():
    rows, bad = [], 0
    for cid, sec, pat, val in claims():
        vals = val if isinstance(val, tuple) else (val,)
        rx = pat.format(*[re.escape(str(v)) for v in vals])
        ok = re.search(rx, WP) is not None
        bad += not ok
        rows.append({"id": cid, "section": sec, "pattern": rx, "recomputed": "/".join(map(str, vals)), "found_in_text": ok})
        print(("PASS" if ok else "FAIL"), cid, sec, "->", "/".join(map(str, vals)))
    with open(os.path.join(DATA, "claims_ledger.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows) - bad}/{len(rows)} claims match")


if __name__ == "__main__":
    main()
