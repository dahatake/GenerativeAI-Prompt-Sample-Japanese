"""CW1 scorer: scores the Cowork runs returned by the user (protocol: data/preregistration_cowork_cw1.md).

Usage: python cowork/score_cowork.py <results_root>        (the folder that holds run-01 .. run-06, e.g. the unzipped CW1_results.zip)
For each run it
  1. verifies manifest.sha256.txt when present,
  2. decodes final_dict.json (the dict Cowork reported) against the 16 requirement combinations (score_e12.decode),
  3. finds monthly_sales code (generated .py files in the run folder first, then fenced code in conversation.txt), checks it with an AST
     allowlist (no network, no process, no file writes), runs it in a subprocess on the real sales.csv and on a held-out sales file, and decodes both,
  4. reads meta.txt (the user's observations).
Statuses are kept apart: "not started" (no files), "undecidable" (returned, but no decodable dict / code), "multiple candidates" (flagged for manual review).
Writes <results_root>/cowork_scores.csv. The primary score is agreement of the REPORTED dict on the supplied sales.csv; the held-out score checks that code is not hard-coded.
"""
import ast, csv, hashlib, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
sys.path.insert(0, EXP)
import score_e12  # noqa: E402

SALES = os.path.join(EXP, "tasks", "T1_sales", "sales.csv")
HELDOUT = os.path.join(HERE, "heldout_sales.csv")
RUNS = ["run-01", "run-02", "run-03", "run-04", "run-05", "run-06"]
ALLOWED_IMPORTS = {"csv", "datetime", "json", "math", "collections", "decimal", "itertools", "re", "typing", "statistics", "calendar",
                   "functools", "dataclasses", "pathlib", "io", "fractions", "operator", "sys", "os", "__future__", "zoneinfo", "enum", "copy"}
BANNED_NAMES = {"eval", "exec", "compile", "__import__", "input", "breakpoint", "globals", "locals", "setattr", "delattr"}
BANNED_ATTRS = {"system", "popen", "unlink", "rmdir", "rmtree", "rename", "write_text", "write_bytes", "mkdir", "makedirs",
                "urlopen", "request", "socket", "run", "call", "Popen", "walk", "listdir", "scandir", "environ", "getenv", "chdir"}
KEY = re.compile(r"^\d{4}-\d{2}$")


def read(path):
    return open(path, encoding="utf-8-sig", errors="replace").read() if os.path.exists(path) else None


def is_result_dict(d):
    return isinstance(d, dict) and d and all(isinstance(k, str) and KEY.match(k) and isinstance(v, int) and not isinstance(v, bool) for k, v in d.items())


def parse_dict(text):
    """Return (dict, status, n_candidates). Candidates are dicts whose keys are YYYY-MM; template examples like {"YYYY-MM": 0} never match."""
    if text is None:
        return None, "missing", 0
    t = text.strip()
    if not t or t.lower() == "null":
        return None, "none reported", 0
    found = []
    for c in [t] + re.findall(r"\{[^{}]*\}", t, re.S):
        for loader in (json.loads, ast.literal_eval):
            try:
                d = loader(c)
            except Exception:
                continue
            if is_result_dict(d) and d not in found:
                found.append(d)
            break
    if not found:
        return None, "no {YYYY-MM: int} dict found", 0
    return found[-1], ("ok" if len(found) == 1 else "multiple candidates (last used; check final_dict.json)"), len(found)


def unsafe_reason(code):
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"syntax error: {e.msg}"
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name.split(".")[0] not in ALLOWED_IMPORTS:
                    return f"import {a.name}"
        elif isinstance(n, ast.ImportFrom):
            if (n.module or "").split(".")[0] not in ALLOWED_IMPORTS:
                return f"from {n.module} import"
        elif isinstance(n, ast.Name) and n.id in BANNED_NAMES:
            return f"name {n.id}"
        elif isinstance(n, ast.Attribute) and n.attr in BANNED_ATTRS:
            return f"attribute .{n.attr}"
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "open":
            mode = None
            if len(n.args) > 1 and isinstance(n.args[1], ast.Constant):
                mode = str(n.args[1].value)
            for kw in n.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    mode = str(kw.value.value)
            if mode and any(c in mode for c in "wax+"):
                return "open() for writing"
    return None


def collect_codes(run_dir, conv):
    codes = []
    for f in sorted(os.listdir(run_dir)) if os.path.isdir(run_dir) else []:
        if re.search(r"\.py(\.txt)?$", f):
            c = read(os.path.join(run_dir, f))
            if c and "def monthly_sales" in c:
                codes.append((f, c))
    for i, c in enumerate(re.findall(r"```(?:python|py)?\s*\n(.*?)```", conv or "", re.S)):
        if "def monthly_sales" in c:
            codes.append((f"conversation block {i + 1}", c))
    return codes


RUNNER = "import json,sys\nns={}\nexec(open(sys.argv[1],encoding='utf-8').read(),ns)\nprint(json.dumps(ns['monthly_sales'](sys.argv[2])))\n"


def execute(code, data):
    with tempfile.TemporaryDirectory() as td:
        cp = os.path.join(td, "code.py")
        open(cp, "w", encoding="utf-8").write(code)
        try:
            p = subprocess.run([sys.executable, "-I", "-c", RUNNER, cp, data], capture_output=True, text=True, timeout=30, cwd=td)
        except subprocess.TimeoutExpired:
            return None, "timeout"
    if p.returncode != 0:
        return None, "error: " + (p.stderr.strip().splitlines() or ["?"])[-1][:120]
    try:
        return {k: int(v) for k, v in json.loads(p.stdout.strip().splitlines()[-1]).items()}, "ok"
    except Exception as e:  # noqa: BLE001
        return None, f"bad output: {e}"


def run_code(run_dir, conv):
    codes = collect_codes(run_dir, conv)
    if not codes:
        return None, None, "no monthly_sales code", ""
    files = [x for x in codes if not x[0].startswith("conversation")]
    src, code = (files or codes)[-1]  # a generated file is the finished artifact; otherwise the last block shown
    bad = unsafe_reason(code)
    if bad:
        return None, None, f"not executed: {bad} (manual review: {src})", src
    r1, w1 = execute(code, SALES)
    r2, _ = execute(code, HELDOUT)
    return r1, r2, ("ok" if r1 is not None else w1), src


def describe(hits):
    if not hits:
        return None, ""
    h = hits[0]
    n = sum(bool(h[k]) for k in ("R1", "R2", "R3", "R4"))
    return n, ",".join(k for k in ("R1", "R2", "R3", "R4") if not h[k])


def decode_heldout(result):
    if result is None:
        return None, ""
    saved = score_e12.ROWS
    score_e12.ROWS = list(csv.DictReader(open(HELDOUT, encoding="utf-8")))
    try:
        return describe(score_e12.decode(result))
    finally:
        score_e12.ROWS = saved


def meta(path):
    out = {}
    for line in (read(path) or "").splitlines():
        m = re.match(r"^([a-z0-9_]+)\s*(?:\([^)]*\))?\s*:\s*(.*)$", line.strip())
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def verify_manifest(root):
    mf = os.path.join(root, "manifest.sha256.txt")
    if not os.path.exists(mf):
        return "no manifest"
    bad = n = 0
    for line in read(mf).splitlines():
        if not line.strip():
            continue
        h, rel = line.split("  ", 1)
        p = os.path.join(root, rel.strip())
        n += 1
        if not os.path.exists(p) or hashlib.sha256(open(p, "rb").read()).hexdigest().upper() != h.upper():
            bad += 1
    return f"{n - bad}/{n} files match"


def main():
    root = sys.argv[1]
    rows = []
    print("manifest:", verify_manifest(root))
    for r in RUNS:
        d = os.path.join(root, r)
        m = meta(os.path.join(d, "meta.txt"))
        conv = read(os.path.join(d, "conversation.txt"))
        fd = read(os.path.join(d, "final_dict.json"))
        started = conv is not None or fd is not None
        rep, why, ncand = parse_dict(fd)
        hits = score_e12.decode(rep) if rep else []
        score, miss = describe(hits)
        c1, c2, cwhy, src = run_code(d, conv) if started else (None, None, "not started", "")
        cs, cm = describe(score_e12.decode(c1)) if c1 else (None, "")
        hs, hm = decode_heldout(c2)
        attempts = (len([x for x in os.listdir(d) if re.match(r"try\d+$", x)]) + 1) if (os.path.isdir(d) and started) else 0
        und = "undecidable" if started else ""
        rows.append({
            "run": r, "arm": m.get("arm", ""), "status": "returned" if started else "not started", "attempts": attempts,
            "reported_dict": json.dumps(rep, ensure_ascii=False) if rep else "",
            "reported_status": (("decoded" + (" - " + why if ncand > 1 else "")) if hits else (why if not rep else "no match among the 16 combinations")) if started else "not started",
            "reported_candidates": ncand,
            "reported_score": (score if score is not None else "undecidable") if started else "not started", "reported_missing": miss,
            "code_source": src, "code_status": cwhy,
            "code_score_supplied_data": cs if cs is not None else und, "code_missing": cm,
            "code_score_heldout": hs if hs is not None else und, "heldout_missing": hm,
            "code_equals_reported": (c1 == rep) if (c1 and rep) else "",
            **{k: m.get(k, "") for k in ("cowork_executed_code", "cowork_asked_questions", "topics_answered", "stopped_after_phase1", "phase2_same_task", "approval_prompts_shown", "external_effect_requested", "start_time", "end_time", "deviations")},
        })
    out = os.path.join(root, "cowork_scores.csv")
    with open(out, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("wrote", out)
    for x in rows:
        print(x["run"], x["arm"], x["status"], "| reported:", x["reported_score"], x["reported_missing"], f"({x['reported_status']})", "| code:", x["code_score_supplied_data"], x["code_missing"], "heldout:", x["code_score_heldout"], x["heldout_missing"], f"({x['code_status']})", "| asked:", x["cowork_asked_questions"], "| stopped:", x["stopped_after_phase1"])
    for arm in ("B", "TCP"):
        sc = [x["reported_score"] for x in rows if x["arm"] == arm]
        dec = [s for s in sc if isinstance(s, int)]
        print(f"{arm}: decided {len(dec)}/{len(sc)}, scores {sc}" + (f", mean {sum(dec) / len(dec):.2f}" if dec else ""))


if __name__ == "__main__":
    main()
