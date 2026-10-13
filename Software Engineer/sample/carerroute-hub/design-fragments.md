# CareRoute Hub 設計断片(架空)

研修用の架空データです。「添付のER図」「添付のデプロイ図」として Issue に添付、またはリポジトリの `docs/` に置いて使います。

## ER図(抜粋)

```mermaid
erDiagram
    patient ||--o{ visit_plan : "訪問予定"
    nurse ||--o{ visit_plan : "担当"
    visit_plan ||--o| visit_record : "実績"
    visit_record ||--o{ insurance_claim : "請求(1:N)"
    visit_record ||--o{ record_audit_log : "閲覧/更新履歴"

    patient {
        uuid patient_id PK
        string name_enc "暗号化"
        string address_enc "暗号化"
        string insurance_no_enc "暗号化"
    }
    visit_plan {
        uuid plan_id PK
        uuid patient_id FK
        uuid nurse_id FK
        datetime planned_at
    }
    visit_record {
        uuid record_id PK
        uuid plan_id FK
        text nursing_note
        datetime recorded_at
    }
    insurance_claim {
        uuid claim_id PK
        uuid record_id FK
        string claim_month
        string status
    }
    record_audit_log {
        uuid log_id PK
        uuid record_id FK
        string action "view/update"
        string actor_id
        datetime occurred_at
    }
```

## デプロイ図(抜粋)

```mermaid
flowchart LR
    subgraph JE["Japan East (本番)"]
        APIM[API Management] --> BFF[BFF .NET 8]
        BFF --> RSV[予約サービス]
        BFF --> REC[記録サービス]
        BFF --> BIL[請求サービス]
        RSV & REC & BIL --> SQL[(Azure SQL Hyperscale)]
        BFF --> REDIS[(Redis)]
        REC --> BLOB[(Blob 帳票PDF)]
        BIL --> SB{{Service Bus}}
        FN[Azure Functions v4 Timer/Queue] --> SQL
        FN --> SB
    end
    subgraph JW["Japan West (DR)"]
        SQL2[(SQL geo-replica)]
        BLOB2[(Blob GRS)]
    end
    SQL -. 非同期レプリケーション .-> SQL2
    BLOB -.-> BLOB2
    APP[Application Insights / Log Analytics] --- BFF
```

## 監査ログ設計書(未完成のドラフト)

| 項目 | 内容 |
| --- | --- |
| 対象 | 看護記録の閲覧/更新 |
| 保持 | 7年 |
| 出力先 | Log Analytics カスタムテーブル `CareAudit_CL`(列定義は未確定) |
| 確定済み列 | `TimeGenerated`, `ActorId`, `Action`, `RecordId` |
| 未確定 | 患者識別子のマスキング方式、アーカイブ先(Basic Logs / Storage)、取り込み遅延の許容値 |
