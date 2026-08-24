# Excelマクロの保守・理解支援 — 研修用サンプルデータ

> **注意**：このファイルに記載する自治体名、部署名、伝票番号、金額、業務ルールはすべて研修用の架空データです。実在の個人・団体・業務とは関係ありません。VBAコードは説明演習用であり、本サンプル以外の実ファイルでは実行しないでください。

## サンプルExcelファイル

- [Excelマクロの保守・理解支援.xlsm](./Excelマクロの保守・理解支援.xlsm)
- Excelで開き、`Alt` + `F11` から標準モジュール `MonthlySummary` を確認してください。
- マクロを実行する場合は、研修環境であることを確認してから「入力データ」シートの「月次集計を実行」ボタンを使用してください。

## 業務の概要

- **業務名**：各課消耗品費の月次集計
- **自治体名**：みどり野市（架空）
- **利用者**：財政課予算管理係の担当職員
- **実行時期**：毎月第3開庁日まで
- **目的**：各課から提出された支出データのうち集計対象となる行を、所属・節ごとに集計し、月次の確認表を作成する。
- **現在の運用**：担当者が各課のデータを「入力データ」シートへ貼り付け、セル `K2` に対象年月を入力してから「月次集計」ボタンを押す。
- **成果物**：「集計結果」シートをPDF化し、課内確認後に共有フォルダーへ保存する。

## シート・列・項目の説明

### 「入力データ」シート

- `K2`：対象年月。文字列で `2026/07` のように入力する運用。
- 2行目以降が明細。

| 列 | 項目名 | 内容 |
|---|---|---|
| A | 集計対象 | `○` の行だけ集計する。空欄は集計しない。 |
| B | 所属コード | 3桁の部署コード。 |
| C | 所属名 | 部署の表示名。 |
| D | 支出日 | 原則として `yyyy/mm/dd` 形式。 |
| E | 伝票番号 | 各課が採番した番号。 |
| F | 節コード | 「科目マスタ」シートのコード。 |
| G | 品名 | 購入した物品等の名称。 |
| H | 税込金額 | 円単位の数値。 |
| I | 備考 | 返品、差額調整などの補足。 |

研修用の入力例：

| 集計対象 | 所属コード | 所属名 | 支出日 | 伝票番号 | 節コード | 品名 | 税込金額 | 備考 |
|---|---|---|---|---|---|---|---:|---|
| ○ | 101 | 総務課 | 2026/07/03 | A-260703-01 | 10 | コピー用紙 | 19,800 |  |
| ○ | 102 | 市民課 | 2026/07/05 | A-260705-03 | 11 | 窓口用封筒 | 13,200 |  |
| ○ | 101 | 総務課 | 2026/07/11 | A-260711-02 |  | ラベルシール | 4,400 | 節コード未入力 |
| ○ | 103 | 福祉課 | 2026/07/18 | A-260718-08 | 20 | プリンター | 38,500 | 係内共用 |
| ○ | 101 | 総務課 | 2026/06/30 | A-260630-12 | 10 | ファイル用品 | 8,800 | 前月分 |
|  | 102 | 市民課 | 2026/07/20 | A-260720-04 | 10 | 付箋 | 2,750 | 集計対象欄が空欄 |
| ○ | 104 | 教育総務課 | 日付未定 | A-260722-07 | 10 | ホワイトボード用品 | 6,600 | 日付を確認中 |
| ○ | 102 | 市民課 | 2026/07/25 | A-260725-09 | 99 | 卓上用品 | 3,300 | 新しいコードとの申し送りあり |
| ○ | 101 | 総務課 | 2026/07/28 | A-260728-10 | 10 | 文具一式 | 12,000円 | 金額が文字列 |
| ○ | 101 | 総務課 | 2026/07/29 | A-260729-11 | 10 | 返品分 | -2,200 | 前月購入分の返品 |

### 「科目マスタ」シート

| 列 | 項目名 | 内容 |
|---|---|---|
| A | 節コード | 入力データと照合するコード。 |
| B | 節名称 | 集計結果に表示する名称。 |
| C | 使用可否 | `可` のコードだけ集計する。 |

研修用のマスタ例：

| 節コード | 節名称 | 使用可否 |
|---|---|---|
| 10 | 需用費（消耗品費） | 可 |
| 11 | 需用費（印刷製本費） | 可 |
| 20 | 備品購入費 | 不可 |

### 「集計結果」シート

| 列 | 項目名 |
|---|---|
| A | 所属コード |
| B | 所属名 |
| C | 節コード |
| D | 節名称 |
| E | 件数 |
| F | 合計金額 |

### 「エラーログ」シート

| 列 | 項目名 |
|---|---|
| A | 入力データの行番号 |
| B | 伝票番号 |
| C | エラー内容 |
| D | 確認対象の値 |

## VBAコード

```vb
Option Explicit

Public Sub CreateMonthlySummary()
    Const INPUT_SHEET As String = "入力データ"
    Const MASTER_SHEET As String = "科目マスタ"
    Const OUTPUT_SHEET As String = "集計結果"
    Const ERROR_SHEET As String = "エラーログ"

    Dim wsInput As Worksheet
    Dim wsMaster As Worksheet
    Dim wsOutput As Worksheet
    Dim wsError As Worksheet
    Dim totals As Object
    Dim counts As Object
    Dim departmentNames As Object
    Dim lastRow As Long
    Dim rowNo As Long
    Dim outputRow As Long
    Dim errorRow As Long
    Dim targetMonth As String
    Dim departmentCode As String
    Dim departmentName As String
    Dim accountCode As String
    Dim voucherNo As String
    Dim key As String
    Dim parts As Variant
    Dim amount As Double
    Dim accountName As Variant
    Dim enabled As Variant
    Dim item As Variant

    On Error GoTo ErrorHandler

    Application.ScreenUpdating = False

    Set wsInput = ThisWorkbook.Worksheets(INPUT_SHEET)
    Set wsMaster = ThisWorkbook.Worksheets(MASTER_SHEET)
    Set wsOutput = ThisWorkbook.Worksheets(OUTPUT_SHEET)
    Set wsError = ThisWorkbook.Worksheets(ERROR_SHEET)

    Set totals = CreateObject("Scripting.Dictionary")
    Set counts = CreateObject("Scripting.Dictionary")
    Set departmentNames = CreateObject("Scripting.Dictionary")

    targetMonth = Trim$(CStr(wsInput.Range("K2").Value))
    If targetMonth = "" Then
        MsgBox "対象年月を入力してください。", vbExclamation
        GoTo Finally
    End If

    wsOutput.Range("A2:F1000").ClearContents
    wsError.Range("A2:D1000").ClearContents
    outputRow = 2
    errorRow = 2

    lastRow = wsInput.Cells(wsInput.Rows.Count, "A").End(xlUp).Row

    For rowNo = 2 To lastRow
        If Trim$(CStr(wsInput.Cells(rowNo, "A").Value)) = "○" Then
            departmentCode = Trim$(CStr(wsInput.Cells(rowNo, "B").Value))
            departmentName = Trim$(CStr(wsInput.Cells(rowNo, "C").Value))
            voucherNo = Trim$(CStr(wsInput.Cells(rowNo, "E").Value))
            accountCode = Trim$(CStr(wsInput.Cells(rowNo, "F").Value))

            If Not IsDate(wsInput.Cells(rowNo, "D").Value) Then
                WriteError wsError, errorRow, rowNo, voucherNo, _
                    "支出日を日付として読み取れません", wsInput.Cells(rowNo, "D").Text
            ElseIf Format$(CDate(wsInput.Cells(rowNo, "D").Value), "yyyy/mm") <> targetMonth Then
                ' 対象月以外の明細は何も記録せず読み飛ばす
            ElseIf departmentCode = "" Or departmentName = "" Then
                WriteError wsError, errorRow, rowNo, voucherNo, _
                    "所属コードまたは所属名が未入力です", departmentCode & " / " & departmentName
            ElseIf accountCode = "" Then
                WriteError wsError, errorRow, rowNo, voucherNo, _
                    "節コードが未入力です", ""
            ElseIf Not IsNumeric(wsInput.Cells(rowNo, "H").Value) Then
                WriteError wsError, errorRow, rowNo, voucherNo, _
                    "税込金額が数値ではありません", wsInput.Cells(rowNo, "H").Text
            Else
                accountName = Application.VLookup(accountCode, wsMaster.Range("A:C"), 2, False)
                enabled = Application.VLookup(accountCode, wsMaster.Range("A:C"), 3, False)

                If IsError(accountName) Or IsError(enabled) Then
                    WriteError wsError, errorRow, rowNo, voucherNo, _
                        "節コードが科目マスタにありません", accountCode
                ElseIf CStr(enabled) <> "可" Then
                    WriteError wsError, errorRow, rowNo, voucherNo, _
                        "現在は使用できない節コードです", accountCode
                Else
                    amount = CDbl(wsInput.Cells(rowNo, "H").Value)
                    key = departmentCode & "|" & accountCode

                    If totals.Exists(key) Then
                        totals(key) = CDbl(totals(key)) + amount
                        counts(key) = CLng(counts(key)) + 1
                    Else
                        totals.Add key, amount
                        counts.Add key, 1
                    End If

                    If Not departmentNames.Exists(departmentCode) Then
                        departmentNames.Add departmentCode, departmentName
                    End If
                End If
            End If
        End If
    Next rowNo

    For Each item In totals.Keys
        parts = Split(CStr(item), "|")
        accountName = Application.VLookup(parts(1), wsMaster.Range("A:C"), 2, False)

        wsOutput.Cells(outputRow, "A").Value = parts(0)
        wsOutput.Cells(outputRow, "B").Value = departmentNames(parts(0))
        wsOutput.Cells(outputRow, "C").Value = parts(1)
        wsOutput.Cells(outputRow, "D").Value = accountName
        wsOutput.Cells(outputRow, "E").Value = counts(item)
        wsOutput.Cells(outputRow, "F").Value = totals(item)
        outputRow = outputRow + 1
    Next item

    If outputRow > 2 Then
        wsOutput.Range("A1:F" & outputRow - 1).Sort _
            Key1:=wsOutput.Range("A2"), Order1:=xlAscending, _
            Key2:=wsOutput.Range("C2"), Order2:=xlAscending, Header:=xlYes
    End If

    wsOutput.Range("H2").Value = "対象年月"
    wsOutput.Range("I2").Value = targetMonth
    wsOutput.Range("H3").Value = "作成日時"
    wsOutput.Range("I3").Value = Now

    MsgBox "月次集計が完了しました。エラーログも確認してください。", vbInformation

Finally:
    Application.ScreenUpdating = True
    Exit Sub

ErrorHandler:
    MsgBox "処理を中止しました。" & vbCrLf & _
        "エラー番号: " & Err.Number & vbCrLf & _
        "内容: " & Err.Description, vbCritical
    Resume Finally
End Sub

Private Sub WriteError(ByVal ws As Worksheet, ByRef errorRow As Long, _
                       ByVal sourceRow As Long, ByVal voucherNo As String, _
                       ByVal message As String, ByVal targetValue As String)
    ws.Cells(errorRow, "A").Value = sourceRow
    ws.Cells(errorRow, "B").Value = voucherNo
    ws.Cells(errorRow, "C").Value = message
    ws.Cells(errorRow, "D").Value = targetValue
    errorRow = errorRow + 1
End Sub
```

## 過去の引継ぎメモ

- 「集計結果」シートの見出し行と印刷設定は変更しないこと。
- 年度初めに「科目マスタ」を更新するが、誰が使用可否を決めるかは資料に記載がない。
- 負の金額は返品時に入力することがあるが、集計へ含めるかどうかは前任者によって扱いが異なっていた。
- `K2` は文字列で入力している。日付形式で入力した場合の挙動は確認していない。
- エラーログに出た明細を修正した後、マクロを再実行する運用と聞いている。
- 集計結果が1,000行を超えた実績はない。
- マクロの設計書とテスト記録は見つかっていない。
