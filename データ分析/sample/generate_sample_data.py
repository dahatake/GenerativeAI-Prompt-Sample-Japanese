"""研修用の架空サンプルデータ(CSV)を決定論的に生成する。

実行: python generate_sample_data.py
乱数シードは固定のため、再実行しても同じファイルができる。
各CSVには、対応する *_サンプルデータ.md に書かれた「品質メモ」と同種の
欠損・重複・表記ゆれを意図的に混ぜている。
"""
import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)


def write(name, header, rows):
    with open(OUT / name, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


def month_iter(start, n):
    y, m = start
    for _ in range(n):
        yield date(y, m, 1)
        m += 1
        if m > 12:
            y, m = y + 1, 1


# ---------------------------------------------------------------- 1 PedalGo
def pedalgo():
    r = random.Random(101)
    cities = [("東京都港区", "東京都", "ST"), ("東京都渋谷区", "東京都", "ST"), ("大阪市北区", "大阪府", "OS"),
              ("横浜市西区", "神奈川県", "YK"), ("名古屋市中区", "愛知県", "NG"), ("福岡市博多区", "福岡県", "FK"),
              ("札幌市中央区", "北海道", "SP"), ("京都市中京区", "京都府", "KY"), ("仙台市青葉区", "宮城県", "SD")]
    plans = ["Light", "Standard", "Premium"]
    occupations = ["会社員"] * 7 + ["パート", "アルバイト", "学生", "主婦", "無職"]
    tiers = ["Bronze"] * 4 + ["Silver"] * 3 + ["Gold"] * 2 + ["Platinum"]
    households = ["単身"] * 4 + ["夫婦のみ"] * 3 + ["子育て世帯"] * 3
    contacts = ["email", "app", "sms"]
    n_cust = 420
    sn = "山川田村佐伯村上小池石原高木鈴木中尾岩井長瀬遠藤渡辺柴田倉田今井新田"
    masters, cust_info = [], {}
    for i in range(1, n_cust + 1):
        cid = f"C{i:04d}"
        city, pref, code = r.choice(cities)
        age = int(min(70, max(18, r.gauss(36, 10))))
        occ = r.choice(occupations)
        if occ == "学生":
            age = r.randint(18, 25)
        inc = 0 if occ == "無職" else int(max(300, r.gauss(4800, 2000)) // 100 * 100)
        if occ in ("学生", "アルバイト", "パート", "主婦"):
            inc = int(inc * 0.35 // 100 * 100)
        reg = date(2023, 6, 1) + timedelta(days=r.randint(0, 1000))
        cust_info[cid] = (city, code, r.choice(plans))
        masters.append([cid, reg.isoformat(), age, r.choice(["女性", "男性", "回答なし"]), pref, occ, inc,
                        r.choice(households), r.choice(tiers), int(r.random() < 0.7),
                        f"{r.choice(sn)}{r.choice('ABCDEFGHIJKLMNOPQRST')}**", r.choice(contacts)])
    # 利用実績は存在するがマスター未登録のID(約5%)をマスターから除外、未使用の登録だけの顧客を追加
    orphan_ids = set(r.sample(sorted(cust_info), 22))
    master_rows = [m for m in masters if m[0] not in orphan_ids]
    for k in range(5):
        master_rows.append([f"C{9001 + k}", "2026-02-01", r.randint(25, 60), "男性", "東京都", "無職", 0, "単身",
                            "Bronze", 0, f"未使用{'ABCDE'[k]}**", "none"])
    comments_pos = ["朝の通勤で便利だった", "ポートが近くて助かる", "料金が手頃で続けやすい", "アプリが使いやすい",
                    "価格改定後も使うつもり", "休日のサイクリングに最適", "バッテリー残量表示が見やすい"]
    comments_neg = ["解錠に時間がかかった", "雨の日はサドルが濡れていた", "返却ポートが満車だった",
                    "アプリのログインが重い", "支払いの引き落とし日が分かりにくい", "価格改定が不満"]
    usage = []
    start = date(2026, 4, 1)
    for cid, (city, code, plan) in cust_info.items():
        active = r.random() < 0.9
        n_days = max(1, int(r.gauss(9 if active else 2, 4)))
        for d in sorted(r.sample(range(91), min(n_days, 91))):
            ud = start + timedelta(days=d)
            fails = int(r.random() < 0.12) + int(r.random() < 0.03)
            cm = ""
            if r.random() < 0.25:
                cm = r.choice(comments_neg if fails or r.random() < 0.25 else comments_pos)
            usage.append([cid, ud.isoformat(), city, plan, r.randint(1, 4), int(max(5, r.gauss(19, 7))), fails,
                          int(r.random() < 0.04), cm, r.choice(["3.8.1", "3.8.1", "3.8.2", "3.7.9"]),
                          f"{code}-{r.randint(1, 12):02d}"])
    dups = r.sample(usage, 25)
    usage.extend([list(x) for x in dups])
    usage.sort(key=lambda x: (x[0], x[1]))
    h1 = ["Customer ID", "usage_date", "city", "plan_type", "ride_count", "avg_minutes", "unlock_failures",
          "payment_delay_flag", "comment_jp", "app_version", "station_code"]
    h2 = ["Customer ID", "registered_at", "age", "gender", "prefecture", "occupation", "annual_income_k",
          "household_type", "loyalty_tier", "consent_email", "customer_name_masked", "preferred_contact"]
    write("pedalgo_usage_2026Q2.csv", h1, usage)
    write("pedalgo_customers.csv", h2, sorted(master_rows))


# ---------------------------------------------------------------- 2 与信
def loan():
    r = random.Random(202)
    emps = [("正社員", 0.55), ("契約社員", 0.12), ("派遣社員", 0.06), ("自営業", 0.10), ("学生", 0.04),
            ("アルバイト", 0.08), ("無職", 0.05)]
    ew = [e[1] for e in emps]
    en = [e[0] for e in emps]
    risk_base = {"正社員": -0.5, "契約社員": 0.3, "派遣社員": 0.5, "自営業": 0.2, "学生": 0.4, "アルバイト": 0.7, "無職": 1.2}
    notes_ok = ["安定就業", "問題なし", "長期安定顧客", "給与振込口座あり"]
    notes_bad = ["過去に軽微延滞", "直近転職", "収入証明画像不鮮明", "連絡不通履歴あり", "多重申込の疑い"]
    notes_neu = ["税金納付月", "賞与月前", ""]
    regions = ["KT", "KS", "CB", "TH", "KY"]
    header = ["applicant_id_hash", "application_month", "age", "employment_type", "annual_income_k",
              "debt_to_income_pct", "months_with_bank", "late_payments_12m", "credit_limit_k", "utilization_pct",
              "inquiries_6m", "region_code", "branch_code", "preferred_channel", "marital_status", "household_size",
              "device_type", "fraud_alert_flag", "collection_note"]

    def make(i, prefix, month):
        emp = r.choices(en, ew)[0]
        age = int(min(75, max(18, r.gauss(40, 12))))
        if emp == "学生":
            age = r.randint(18, 24)
        inc = int(max(0, r.gauss(4800, 1900)) // 100 * 100)
        if emp in ("アルバイト", "学生"):
            inc = int(inc * 0.3 // 100 * 100)
        if emp == "無職":
            inc = int(inc * 0.1 // 100 * 100)
        dti = round(min(95, max(3, r.gauss(32, 15) + (12 if emp in ("アルバイト", "無職") else 0))), 1)
        mwb = max(0, int(r.gauss(40, 30)))
        late = min(6, int(r.expovariate(1.6)))
        limit = int(max(100, r.gauss(800, 400)) // 10 * 10)
        util = round(min(99.9, max(0, r.gauss(45, 24) + late * 6)), 1)
        inq = min(9, int(r.expovariate(0.8)))
        fraud = int(r.random() < 0.02)
        z = (-2.9 + risk_base[emp] + 0.045 * (dti - 32) + 0.35 * late + 0.02 * (util - 45) + 0.18 * inq
             - 0.006 * (mwb - 40) - 0.0001 * (inc - 4800) + 1.2 * fraud)
        p = 1 / (1 + math.exp(-z))
        y = int(r.random() < p)
        note = r.choice(notes_bad if (y and r.random() < 0.6) else notes_ok if not y and r.random() < 0.5 else notes_neu)
        row = [f"{prefix}{i:04d}", month, age, emp, inc, dti, mwb, late, limit, util, inq, r.choice(regions),
               f"B{r.randint(1, 40):03d}", r.choice(["Web", "Web", "店頭", "代理店", "紹介"]),
               r.choice(["未婚", "既婚", "既婚"]), r.randint(1, 5), r.choice(["iPhone", "Android", "PC"]), fraud, note]
        if r.random() < 0.04:
            row[4] = ""
            row[18] = "年収データ欠損"
        return row, y

    rows = []
    months = [m.strftime("%Y-%m") for m in month_iter((2026, 1), 7)]
    for i in range(1, 2401):
        row, y = make(i, "AH", months[(i - 1) % 7])
        rows.append(row + [y])
    dup = [list(x) for x in r.sample(rows, 12)]
    rows.extend(dup)
    write("credit_applications_train.csv", header + ["default_flag"], rows)
    new = [make(i, "NEW", "2026-08")[0] for i in range(901, 931)]
    new.append(list(new[1]))
    write("credit_applications_new.csv", header, new)
    print("default rate:", round(sum(x[-1] for x in rows) / len(rows), 3))


# ---------------------------------------------------------------- 3 アンケート
def survey():
    r = random.Random(303)
    pos = {
        "講師": ["畠山さんの説明が具体的で分かりやすかったです。", "講師の実演が実務に近く参考になった。",
                 "質問への回答が丁寧で、その場で解決できた。", "講師の進め方にメリハリがあった。"],
        "演習": ["演習用ファイルが事前配布されていて助かりました。", "ハンズオンで実際に手を動かせたのが良かった。",
                 "演習の題材が自部署の業務に近かった。", "演習の時間配分がちょうど良かった。"],
        "内容": ["Copilotの使い方が整理できた。", "プロンプトの型を学べたので明日から使える。",
                 "セキュリティの注意点が具体例付きで理解できた。", "ChatGPTとCopilotの違いが分かって良かった。"],
        "運営": ["資料が事前に共有されていて予習できた。", "録画が後日見られるのがありがたい。",
                 "会場が見やすく運営もスムーズだった。"],
    }
    neg = {
        "インフラ": ["午後にネットワークが弱くて実演が止まりました。", "音声が途切れて聞き取りづらかった。",
                     "画面共有が重くて演習が進まなかった。", "Wi-Fiが不安定で何度か切断された。"],
        "難易度": ["演習が難しく、初心者には置いていかれる場面があった。", "前提知識がないと厳しい内容だった。",
                   "応用編は速度が速くてついていけなかった。"],
        "時間": ["質疑の時間が足りなかった。",
                 "演習の時間が短すぎる。", "休憩が少なく集中が切れた。"],
        "資料": ["配布資料の文字が小さくて読みにくい。", "資料と画面の内容が一部違っていた。"],
        "内容": ["自部署の業務に当てはめるイメージが湧かなかった。", "もっと事例を増やしてほしい。",
                 "CopilotとChatGPTのどちらを使うべきか結論が曖昧だった。"],
    }
    sessions = [("基礎編A", date(2026, 7, 3)), ("応用編B", date(2026, 7, 4)), ("管理職向けC", date(2026, 7, 5))]
    offices = ["東京", "東京", "東京", "大阪", "大阪", "名古屋", "福岡", "札幌", "仙台"]
    ages = ["20代", "30代", "30代", "40代", "40代", "50代"]
    rows = []
    for i in range(1, 321):
        sname, d = sessions[(i - 1) % 3 if r.random() < 0.3 else r.choice([0, 0, 1, 2])]
        ts = f"{d.isoformat()} {r.randint(17, 20):02d}:{r.randint(0, 59):02d}"
        score = r.choices([1, 2, 3, 4, 5], [0.03, 0.12, 0.2, 0.35, 0.30])[0]
        parts = []
        if score >= 4:
            parts.append(r.choice(pos[r.choice(list(pos))]))
            if r.random() < 0.3:
                parts.append(r.choice(neg[r.choice(list(neg))]))
        elif score == 3:
            parts.append(r.choice(pos[r.choice(list(pos))]))
            parts.append(r.choice(neg[r.choice(list(neg))]))
        else:
            parts.append(r.choice(neg[r.choice(list(neg))]))
            if r.random() < 0.5:
                parts.append(r.choice(neg[r.choice(list(neg))]))
        if sname == "応用編B" and score <= 3 and r.random() < 0.5:
            parts.append(r.choice(neg["難易度"]))
        rows.append([f"R{i:03d}", ts, sname, r.choice(offices), f"HX-{i:03d}**", r.choice(ages), score,
                     "".join(dict.fromkeys(parts))])
    for i in r.sample(range(len(rows)), 9):
        rows[i][7] = ""
    for i in r.sample(range(len(rows) - 1), 4):  # 連続の重複送信
        rows[i + 1][3:8] = rows[i][3:8]
    rows.sort(key=lambda x: x[1])
    for n, row in enumerate(rows, 1):
        row[0] = f"R{n:03d}"
    write("training_survey_comments.csv",
          ["response_id", "submitted_at", "session_name", "office", "employee_id_masked", "age_band",
           "satisfaction_score", "free_comment"], rows)


# ---------------------------------------------------------------- 4 商談
def opportunities():
    r = random.Random(404)
    prefs = [("東京都", "D001", 3), ("神奈川県", "D005", 2), ("大阪府", "D014", 3), ("愛知県", "D021", 2),
             ("福岡県", "D028", 2), ("北海道", "D033", 1), ("宮城県", "D036", 1), ("広島県", "D040", 1)]
    pw = [p[2] for p in prefs]
    comps = ["Eagle-e", "Eagle-e", "Lumo Compact", "Lumocompact", "Kaze Lite EV", "KAZE-lite", "競合なし"]
    loss = ["駐車場サイズが不安", "競合の納期が早い", "充電設備の設置が難しい", "価格が予算を超える", "航続距離が不安",
            "補助金の見通しが立たない", "家族の同意が得られなかった"]
    delay_note = ["半導体", "輸送", "仕様変更", "部品待ち", "部品待"]
    rows = []
    for i in range(1, 1201):
        d = date(2026, 4, 1) + timedelta(days=r.randint(0, 152))
        pref, dealer, _ = r.choices(prefs, pw)[0]
        dealer = f"D{int(dealer[1:]) + r.randint(0, 4):03d}"
        age = r.choice(["20代", "30代", "30代", "40代", "40代", "50代", "60代"])
        hh = r.choice(["単身", "夫婦のみ", "子育て世帯", "子育て世帯"])
        td = int(r.random() < 0.55)
        quote = int(r.gauss(2480000, 90000) // 10000 * 10000)
        disc = int(max(0, r.gauss(184000, 55000)) // 10000 * 10000)
        sub = 0 if r.random() < 0.3 else r.choice([120000, 150000, 200000, 250000])
        lead = r.choice(["Web広告", "比較サイト", "店頭", "紹介", "イベント"])
        comp = r.choice(comps)
        days = int(max(20, r.gauss(71, 18)))
        p = 0.18 + 0.2 * td + 0.00000012 * disc - 0.0025 * max(0, days - 60)
        won = r.random() < p
        reason = ""
        if not won and r.random() > 0.2:
            reason = r.choice(loss)
            if days > 80 and r.random() < 0.5:
                reason = "競合の納期が早い"
        rows.append([f"OP-{d:%y%m}{i:04d}", d.isoformat(), pref, dealer, age, hh, "Aster Mini", td, quote, disc, sub,
                     lead, comp, reason, days, f"rep{int(dealer[1:]) % 40:02d}***", "成約" if won else "失注"])
    write("aster_mini_opportunities_2026.csv",
          ["opportunity_id", "created_date", "prefecture", "dealer_code", "customer_age_band", "household_type",
           "vehicle_interest", "test_drive_flag", "quote_amount", "discount_jpy", "subsidy_expected_jpy",
           "lead_source", "competitor_vehicle", "loss_reason_text", "expected_delivery_days", "sales_rep_masked",
           "outcome"], rows)


# ---------------------------------------------------------------- 5 デリバリー月次
def delivery():
    r = random.Random(505)
    regions = [("首都圏", 8400, "TK"), ("関西", 5100, "OS"), ("中部", 3300, "NG"), ("九州", 2100, "FK"), ("北海道", 1200, "SP")]
    segs = [("共働き世帯", 1.0, 31), ("単身若年層", 0.8, 27), ("シニア世帯", 0.45, 29)]
    rows = []
    for mi, m in enumerate(month_iter((2025, 10), 12)):
        for reg, base, code in regions:
            for seg, sw, gm in segs:
                orders = int(base * sw * (1 + 0.012 * mi) * r.gauss(1, 0.03))
                uniq = int(orders * r.uniform(0.72, 0.85))
                newc = int(uniq * r.uniform(0.09, 0.15))
                churn = round(r.gauss(4.2, 0.5) + (0.35 * mi if reg == "関西" and mi >= 3 else 0.12 * mi), 1)
                ad = int(orders * r.gauss(600, 40))
                rev = int(orders * r.gauss(3850, 120))
                cc = code + ("-02" if (mi >= 7 and reg == "首都圏") else "-01")
                camp = ["AUT25", "AUT25", "AUT25", "WIN25", "WIN25", "WIN25", "SPRING26", "SPRING26", "SPRING26",
                        "SUM26", "SUM26", "AUT26"][mi]
                rows.append([m.isoformat(), reg, seg, orders, uniq, newc, round(r.gauss(55, 6), 1), churn, rev,
                             round(r.gauss(gm, 1.5), 1), ad, int(orders * r.uniform(0.005, 0.009)),
                             round(abs(r.gauss(3.2, 0.8)) + (3 if reg == "関西" and mi in (3, 4, 5) else 0), 1), camp, cc,
                             f"ops_{code.lower()}+dummy@hokushin.example", ""])
    for row in rows:
        if row[0] == "2026-04-01" and row[13] == "SPRING26" and r.random() < 0.3:
            row[13] = "Spring-26"
        if row[0] == "2026-08-01" and row[1] == "首都圏":
            row[9] = ""
            row[16] = "ERP更新遅延で粗利率欠損"
        if row[0] == "2026-09-01" and row[1] == "関西":
            row[11] = ""
            row[16] = "complaints欠損・CS集計遅延"
        if row[0] == "2026-07-01" and row[1] == "北海道" and row[2] == "共働き世帯":
            row[3] = int(row[3] * 2.4)
            row[8] = int(row[8] * 2.4)
            row[16] = "法人まとめ買い(単発案件)"
        if row[0] in ("2026-01-01", "2026-02-01", "2026-03-01") and row[1] == "関西":
            row[16] = "配送委託先変更・アプリ障害"
    rows.append(list(next(x for x in rows if x[0] == "2026-04-01" and x[1] == "関西")))
    write("delivery_monthly_2025-10_2026-09.csv",
          ["month", "region", "segment", "orders", "unique_customers", "new_customers", "repeat_rate_pct",
           "churn_rate_pct", "revenue_jpy", "gross_margin_pct", "ad_spend_jpy", "complaints", "delay_rate_pct",
           "campaign_code", "center_code", "analyst_contact_masked", "note"], rows)


# ---------------------------------------------------------------- 6 訪日外客
def visitors():
    r = random.Random(606)
    countries = [("韓国", 600000, 118000, "LCC増便"), ("台湾", 400000, 146000, ""), ("中国", 270000, 193000, ""),
                 ("香港", 200000, 180000, ""), ("米国", 190000, 280000, ""), ("タイ", 130000, 160000, ""),
                 ("豪州", 90000, 260000, ""), ("英国", 40000, 270000, ""), ("ドイツ", 22000, 250000, ""),
                 ("フランス", 26000, 255000, "")]
    share = {"韓国": (78, 11, 6, 5), "台湾": (83, 8, 5, 4), "中国": (70, 13, 11, 6), "香港": (81, 8, 5, 6),
             "米国": (62, 24, 6, 8), "タイ": (74, 10, 8, 8), "豪州": (80, 8, 7, 5), "英国": (65, 22, 7, 6),
             "ドイツ": (64, 24, 6, 6), "フランス": (72, 17, 6, 5)}
    season = [0.85, 0.9, 1.1, 1.15, 1.0, 0.95, 1.05, 1.1, 0.95, 1.1, 1.05, 1.0]
    purposes = ["観光", "商用", "親族・知人訪問", "その他"]
    rows = []
    for mi, m in enumerate(month_iter((2024, 10), 24)):
        for ci, (c, base, spend, note) in enumerate(countries):
            q = "中" if c == "中国" else "高"
            g = 1 + 0.01 * mi
            mult = season[m.month - 1] * g
            if c == "中国" and m.month == 2 and m.year == 2026:
                mult *= 1.6
            for pi, p in enumerate(purposes):
                v = int(base * share[c][pi] / 100 * mult * r.gauss(1, 0.04))
                sp = int(spend * (1.5 if p == "商用" else 1.0) * r.gauss(1, 0.03) // 100 * 100)
                rows.append([m.isoformat(), c, p, v, sp, round(r.gauss(38 if p != "観光" else 33, 5), 1),
                             round(min(99.9, r.gauss(97, 1.2)), 1), "通常", q])
    for row in rows:
        if row[0] == "2026-03-01" and row[1] == "タイ" and row[2] == "観光":
            row[4] = ""
        if row[1] == "中国" and r.random() < 0.05:
            row[7] = "推計値含む"
    rows.append(list(next(x for x in rows if x[0] == "2026-03-01" and x[1] == "中国" and x[2] == "観光")))
    write("inbound_visitors_by_country_purpose.csv",
          ["month", "country", "purpose", "visitors", "avg_spend_jpy", "repeat_visit_pct", "airport_share_pct",
           "visa_note", "source_quality"], rows)


if __name__ == "__main__":
    pedalgo(); loan(); survey(); opportunities(); delivery(); visitors()
