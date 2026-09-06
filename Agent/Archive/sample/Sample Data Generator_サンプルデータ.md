> 対応Prompt: ../Sample Data Generator.md

# Sample Data Generator — サンプルデータ

> 注意: このファイルに記載する会社名、設備名、数値、コメント、日付、異常条件はすべて架空です。実在データではありません。

## 共通シナリオ

- 依頼元: 空色モバイル株式会社
- 用途: 研修、分析検証、ダッシュボード試作
- 共通制約:
  - 個人情報や実顧客情報は禁止
  - CSV化しやすい列構成にする
  - 日本語コメントは感情が偏りすぎないよう肯定・否定・中立を混在させる

## 1. サンプルデータ生成エージェントに渡す案件ブリーフ

```text
業務検証用のサンプルデータを作成してください。ダウンロードできる想定で、表形式の先頭5件も表示してください。

# 共通仕様
- 日付列を必ず含める
- 正規分布に近い列と、偏りがある列を両方入れる
- 列名は英語
- コメント列がある場合、コメントは日本語
- 2026年のデータとして作る

# 今回よく使うテーマ
- コールセンター問い合わせ
- 工場設備監視

# 追加要望
- 欠損値が少数混ざる現実的なデータにする
- 明らかな異常値は全件の3%未満
```

## 2. Starter Prompt 例1として使う入力

```text
コールセンターのサンプルデータを100件作成してください。フリーコメント欄のデータも作成してください。

# 条件
- 会社: 空色モバイル株式会社
- 期間: 2026-07-01 〜 2026-09-15
- 列: TicketID, Date, Product, ContactChannel, WaitMinutes, ResolutionDays, CSScore, Comments
- ContactChannel は phone / chat / email
- WaitMinutes は平均12分前後の分布にしつつ、一部40分超の偏りを入れる
- Comments は日本語で、OS更新、配送遅延、初期設定、修理対応への言及を混ぜる
```

## 3. Starter Prompt 例2として使う入力

```text
工場の設備の監視のサンプルデータを1,000件作成してください。

# 条件
- 工場: 空色モバイル株式会社 甲南工場
- 期間: 2026-08-01 〜 2026-08-31
- 設備: SMT-01, SMT-02, Press-03, Oven-01, Inspect-07
- 列: RecordID, Date, EquipmentID, TemperatureC, VibrationMm, PowerKw, ErrorCode, DowntimeMinutes, OperatorComment
- TemperatureC は設備ごとの基準値を持たせる
- ErrorCode は大半が NONE、一部に E201, E315, W010 を混在
- OperatorComment は日本語、夜勤引継ぎらしい短文も混ぜる
- 異常停止は1,000件中20件前後
```
