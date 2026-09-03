対応Prompt: [..\zipファイルのサマリー.md](..\zipファイルのサマリー.md)

> このファイルの内容はすべて研修用の架空データです。実在のソースコード・顧客情報・画像・ログとは関係ありません。ファイル構成・エンコーディング・代表内容を定義し、同じ内容の実ZIPも用意しています。

# 想定する zip 名

- `factory-copilot-demo-2026-09.zip`
- [実際にアップロードできるサンプルZIP](./factory-copilot-demo-2026-09.zip)

# 貼り付け用Prompt

```text
このzipファイルを展開してください。それぞれのファイルの内容を読み取って、要約の文章を作成してください。
```

# 1. 期待するアーカイブの目的

- 題材: `Factory Copilot Kickoff` 向けのデモアプリ一式
- 中身: Pythonアプリ、CSVデータ、設計メモ、日本語メモ、テスト、ログ、画像、壊れたJSON、ゼロバイトファイル
- 目的: Code Interpreter に「読めるテキスト」「バイナリ」「文字コード差」「壊れたファイル」を混在させたときの挙動確認

# 2. ファイルマニフェスト

| パス | 種別 | 文字コード/形式 | 期待する扱い | 備考 |
|---|---|---|---|---|
| `README_overview.txt` | text | UTF-8 | 要約対象 | 全体概要 |
| `docs\requirements.md` | markdown | UTF-8 | 要約対象 | 要件定義 |
| `docs\release_notes_ja.txt` | text | UTF-8 | 要約対象 | 日本語リリースノート |
| `data\customers_sample.csv` | csv | UTF-8 | 要約対象 | 顧客サンプル |
| `data\maintenance_logs_2026-08.csv` | csv | UTF-8 | 要約対象 | 欠損・異常値あり |
| `data\pricing_sjis.csv` | csv | Shift_JIS | 文字化け可否を確認して要約 | `¥`、全角カナあり |
| `src\app.py` | python | UTF-8 | 要約対象 | CLI入口 |
| `src\report_builder.py` | python | UTF-8 | 要約対象 | レポート生成 |
| `src\utils\cleaning.py` | python | UTF-8 | 要約対象 | データ整形 |
| `tests\test_report_builder.py` | python | UTF-8 | 要約対象 | 単体テスト |
| `logs\app.log` | log | UTF-8 | 主要エラー中心に要約 | 冗長ログ |
| `notes\todo_日本語メモ.txt` | text | UTF-8 | 要約対象 | 口語・箇条書き混在 |
| `configs\settings.dev.json` | json | UTF-8 | 要約対象 | 開発設定 |
| `configs\broken.json` | json | UTF-8(壊れ) | 読み取り失敗を明記 | カンマ欠落 |
| `assets\architecture.png` | binary image | PNG | 中身読取不可として扱う | 図版 |
| `assets\workshop_logo.ai` | binary design | Adobe Illustrator | 中身読取不可として扱う | ベクターロゴ |
| `archive\legacy_spec.bin` | binary | 独自形式 | 読み取り失敗を明記 | 旧仕様書のダミーバイナリ |
| `tmp\empty_placeholder.txt` | empty | 0 bytes | 空ファイルとして扱う | 意図的な空 |

# 3. 代表内容

## 3-1. `README_overview.txt`

```text
Factory Copilot Demo Package
Version: 0.9-beta

This package contains a small reporting demo used in internal workshops.
It reads customer and maintenance CSV files, normalizes inconsistent values,
and creates a weekly summary for customer success managers.

Known limitations:
- Japanese Shift_JIS pricing data may require explicit decoding.
- The demo does not send email; it only writes markdown output.
- Some files are intentionally broken or binary-only for workshop testing.
```

## 3-2. `docs\requirements.md`

```text
# Requirements

## Goal
Generate a weekly customer-facing draft summary from workshop sample data.

## Functional requirements
1. Load customer master data.
2. Load maintenance logs.
3. Normalize plant codes and priority labels.
4. Aggregate open issues by customer and severity.
5. Output markdown summaries with "Facts / Risks / Next Actions".

## Non-functional requirements
- Run locally with Python 3.11
- Complete under 30 seconds for 5,000 rows
- Never expose real personal data

## Open questions
- Should pricing ranges be displayed to customers or internal users only?
- How should unreadable files be reported in the final summary?
```

## 3-3. `docs\release_notes_ja.txt`

```text
2026-09-01 リリースノート（抜粋）

- 週次サマリーの見出しを「Facts / Risks / Next Actions」に統一
- 顧客優先度 `High`, `HIGH`, `高` を同一視する前処理を追加
- 工場コードが `plt-01` と `PLT-001` で混在する問題に暫定対応
- 既知の不具合: Shift_JIS の価格CSVを読み込むと、一部の通貨記号が欠落することがある
```

## 3-4. `data\customers_sample.csv`

```csv
customer_id,customer_name,segment,plant_code,priority,cs_owner
C001,{A社},Enterprise,PLT-001,High,owner_01
C002,{B社},Mid,plt-02,HIGH,owner_02
C003,{C社},SMB,PLT-003,高,owner_03
C004,{D社},Enterprise,PLT_004,Medium,owner_02
```

## 3-5. `data\maintenance_logs_2026-08.csv`

```csv
log_id,customer_id,opened_at,severity,response_minutes,status,issue_type,notes
M001,C001,2026-08-03 09:14,Critical,18,Open,MailError,wrong recipients reported
M002,C001,2026-08-05 13:02,Major,47,Closed,Latency,storage queue spike
M003,C002,2026-08-11 08:41,Major,,Open,Encoding,CSV export mojibake
M004,C003,2026-08-14 18:25,Minor,12,Closed,Training,operator confusion
M005,C004,2026-08-28 07:55,Critical,9999,Open,Auth,abnormal value for response time
```

## 3-6. `data\pricing_sjis.csv`

```text
plan,price_range,notes
QuickStart,45万円前後,初回導入向け
Standard Launch,120万円前後,複数拠点向け
Premium Success,260万円前後,教育含む
```

### 文字コードメモ

- 実ファイル化するときは Shift_JIS で保存
- `万円`、全角スペース、機種依存しやすい `¥` 記号を含めてもよい

## 3-7. `src\app.py`

```python
from report_builder import build_weekly_report

def main():
    report = build_weekly_report(
        customer_csv="data/customers_sample.csv",
        log_csv="data/maintenance_logs_2026-08.csv"
    )
    with open("output/latest_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("report generated")

if __name__ == "__main__":
    main()
```

## 3-8. `src\report_builder.py`

```python
import csv
from utils.cleaning import normalize_plant_code, normalize_priority

def build_weekly_report(customer_csv, log_csv):
    customers = {}
    with open(customer_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["plant_code"] = normalize_plant_code(row["plant_code"])
            row["priority"] = normalize_priority(row["priority"])
            customers[row["customer_id"]] = row

    issues = []
    with open(log_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            issues.append(row)

    lines = ["# Weekly Summary", ""]
    for issue in issues:
        customer = customers.get(issue["customer_id"], {"customer_name": "{Unknown}"})
        lines.append(f"- {customer['customer_name']}: {issue['issue_type']} / {issue['status']}")
    return "\n".join(lines)
```

## 3-9. `src\utils\cleaning.py`

```python
def normalize_plant_code(value: str) -> str:
    value = value.strip().upper().replace("_", "-")
    if value.startswith("PLT-") and len(value) == 6:
        return value[:4] + "0" + value[4:]
    return value

def normalize_priority(value: str) -> str:
    mapping = {
        "HIGH": "High",
        "高": "High",
        "MEDIUM": "Medium",
        "LOW": "Low"
    }
    key = value.strip().upper() if value else ""
    return mapping.get(key, value.title() if value else "Unknown")
```

## 3-10. `tests\test_report_builder.py`

```python
from src.utils.cleaning import normalize_plant_code, normalize_priority

def test_normalize_plant_code():
    assert normalize_plant_code("plt-02") == "PLT-002"

def test_normalize_priority():
    assert normalize_priority("高") == "High"
```

## 3-11. `logs\app.log`

```text
2026-08-28 07:55:12 INFO start job weekly-report
2026-08-28 07:55:14 WARN missing response_minutes log_id=M003
2026-08-28 07:55:15 ERROR decode failed file=data/pricing_sjis.csv codec=utf-8
2026-08-28 07:55:18 INFO fallback summary generated without pricing data
2026-08-28 07:55:19 WARN abnormal response_minutes log_id=M005 value=9999
2026-08-28 07:55:20 INFO end job weekly-report
```

## 3-12. `notes\todo_日本語メモ.txt`

```text
- A社向けの週次ドラフト、Next Actions が弱い
- FAQデモ用データをあと18件ほしい
- pricing_sjis.csv は文字コードを決め打ちしないほうがよいかも
- broken.json はわざと壊してあるので、失敗時メッセージ確認に使う
- 画像ファイルは中身が読めない前提で、ファイル名だけでも触れてほしい
```

## 3-13. `configs\settings.dev.json`

```json
{
  "environment": "dev",
  "report_output": "output/latest_report.md",
  "include_pricing": false,
  "max_rows_preview": 20
}
```

## 3-14. `configs\broken.json`

```json
{
  "environment": "dev"
  "include_pricing": true,
  "max_rows_preview": 20
}
```

## 3-15. バイナリ/空ファイル系の扱い

```text
assets\architecture.png
- 工場データ連携図のPNG。画像そのもののOCRは不要。

assets\workshop_logo.ai
- イベントロゴのベクターデータ。読み取り不能で正常。

archive\legacy_spec.bin
- 旧仕様書を模した独自形式のダミーバイナリ。「バイナリのため詳細未確認」でよい。

tmp\empty_placeholder.txt
- 0 bytes。空ファイルとして扱う。
```

# 4. 期待する要約の出力要件

- ファイルごとに 1-3文で要約
- 読み取れないファイルは「読み取れない理由」を明記
- 文字化け/壊れたJSON/異常値/欠損は見落とさない
- 最後に「アーカイブ全体の目的」「気になる品質リスク」「次に確認すべきこと」を3点ずつ整理

# 5. 実ZIPの検証ポイント

- `data\pricing_sjis.csv` は本当に Shift_JIS 保存にする
- `tmp\empty_placeholder.txt` は 0 byte のままにする
- `assets\architecture.png` と `assets\workshop_logo.ai` はダミーでもバイナリ実体を置く
- `configs\broken.json` は壊したままにする
- 展開後のマニフェストが本ファイルの一覧と一致することを確認する
