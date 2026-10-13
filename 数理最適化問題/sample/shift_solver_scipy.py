"""シフトスケジュール問題サンプルの検証と参考解の生成。

実行: python shift_solver_scipy.py
  1. shift_employees.csv / shift_demand.csv を読み込む
  2. サンプルMDに載せている「作成されたシフトスケジュール表」のハード制約違反を数える
  3. scipy.optimize.milp でハード制約を満たす参考解を求め shift_solution_example.csv に出力する
必要: pandas, scipy (>=1.9)
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp

BASE = Path(__file__).parent
DAYS = ["月", "火", "水", "木", "金", "土", "日"]
EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SHIFTS = ["M", "D", "N"]

emp = pd.read_csv(BASE / "shift_employees.csv", encoding="utf-8").fillna("")
dem = pd.read_csv(BASE / "shift_demand.csv", encoding="utf-8").set_index("day")
E = list(emp.employee)
night_ok = dict(zip(emp.employee, emp.night_ok))
leader_ok = dict(zip(emp.employee, emp.leader_ok))
pref = dict(zip(emp.employee, emp.preferred_shift))
off_req = {e: DAYS.index(d) for e, d in zip(emp.employee, emp.days_off_request) if d}

# MDの「5. 解決策の妥当性確認 用」に載っている表
MD_TABLE = """A M D O O M O M
B D O D M O D O
C N O N O N O M
D M M O O D M O
E O D O D D O N
F O N O N O N O
G M O M D O M O
H D M D O M O D
I O D M D O O D
J N O O N O O N"""


def check(table):
    sched = {l.split()[0]: l.split()[1:] for l in table.strip().splitlines()}
    v = []
    for e, row in sched.items():
        work = [i for i, s in enumerate(row) if s != "O"]
        if len(work) > 5:
            v.append(f"{e}: 週{len(work)}勤務(上限5)")
        if e in off_req and row[off_req[e]] != "O":
            v.append(f"{e}: 希望休({DAYS[off_req[e]]})に勤務({row[off_req[e]]})")
        for i, s in enumerate(row):
            if s == "N" and not night_ok[e]:
                v.append(f"{e}: 夜番不可なのに{DAYS[i]}に夜番")
            if s == "N" and i < 6 and row[i + 1] != "O":
                v.append(f"{e}: {DAYS[i]}夜番の翌日({DAYS[i+1]})が休日でない")
    for i, d in enumerate(DAYS):
        for s in SHIFTS:
            n = sum(1 for e in sched if sched[e][i] == s)
            if n != dem.loc[d, s]:
                v.append(f"{d}{s}: {n}名(必要{dem.loc[d, s]})")
        if not any(sched[e][i] in ("M", "D") and leader_ok[e] for e in sched):
            v.append(f"{d}: 朝番・昼番にリーダー不在")
    return v


def solve():
    ne, nd, ns = len(E), 7, 3
    idx = lambda e, d, s: (e * nd + d) * ns + s
    nx = ne * nd * ns
    # 追加変数: 土日勤務数の最大/最小, 4連勤以上の違反(各e,開始日0..3)
    iw_max, iw_min = nx, nx + 1
    iv = lambda e, w: nx + 2 + e * 4 + w
    n = nx + 2 + ne * 4
    rows, lo, hi = [], [], []

    def add(coefs, l, u):
        r = np.zeros(n)
        for k, c in coefs:
            r[k] += c
        rows.append(r), lo.append(l), hi.append(u)

    for e in range(ne):
        ename = E[e]
        for d in range(nd):
            add([(idx(e, d, s), 1) for s in range(ns)], 0, 1)
            if not night_ok[ename]:
                add([(idx(e, d, 2), 1)], 0, 0)
            if d < 6:
                add([(idx(e, d, 2), 1)] + [(idx(e, d + 1, s), 1) for s in range(ns)], 0, 1)
        add([(idx(e, d, s), 1) for d in range(nd) for s in range(ns)], 0, 5)
        if ename in off_req:
            add([(idx(e, off_req[ename], s), 1) for s in range(ns)], 0, 0)
        for w in range(4):
            add([(idx(e, d, s), 1) for d in range(w, w + 4) for s in range(ns)] + [(iv(e, w), -1)], -np.inf, 3)
        wk = [(idx(e, d, s), 1) for d in (5, 6) for s in range(ns)]
        add(wk + [(iw_max, -1)], -np.inf, 0)
        add(wk + [(iw_min, -1)], 0, np.inf)
    for d in range(nd):
        for s in range(ns):
            need = dem.iloc[d][SHIFTS[s]]
            add([(idx(e, d, s), 1) for e in range(ne)], need, need)
        add([(idx(e, d, s), 1) for e in range(ne) if leader_ok[E[e]] for s in (0, 1)], 1, np.inf)
    c = np.zeros(n)
    for e in range(ne):
        for d in range(nd):
            for s in range(ns):
                if pref[E[e]] != SHIFTS[s]:
                    c[idx(e, d, s)] += 1  # 希望外シフトのペナルティ
    c[iw_max], c[iw_min] = 3, -3
    for e in range(ne):
        for w in range(4):
            c[iv(e, w)] = 5
    integrality = np.ones(n)
    ub = np.ones(n)
    ub[[iw_max, iw_min]] = 7
    res = milp(c, constraints=LinearConstraint(np.array(rows), lo, hi), integrality=integrality,
               bounds=Bounds(np.zeros(n), ub))
    return res, idx


if __name__ == "__main__":
    print("== MDの表のハード制約違反 ==")
    for line in check(MD_TABLE) or ["違反なし"]:
        print(" -", line)
    res, idx = solve()
    print("== ソルバー ==", res.message)
    if res.x is not None:
        out = []
        for e, name in enumerate(E):
            row = []
            for d in range(7):
                s = [k for k in range(3) if res.x[idx(e, d, k)] > 0.5]
                row.append(SHIFTS[s[0]] if s else "O")
            out.append([name] + row)
        table = pd.DataFrame(out, columns=["Worker"] + EN)
        table["TotalShifts"] = (table[EN] != "O").sum(axis=1)
        table["WeekendShifts"] = (table[["Sat", "Sun"]] != "O").sum(axis=1)
        table["PreferredMatched"] = [sum(1 for x in r[1:8] if x == pref[r[0]]) for r in out]
        table.to_csv(BASE / "shift_solution_example.csv", index=False, encoding="utf-8")
        print(table.to_string(index=False))
        print("ハード制約違反:", check("\n".join(" ".join(r) for r in out)) or "なし")
