# ユーザーに易しいデータ分析

## ツール
追加のデータは不要ですから、ChatGPT がいいと思います。

# Prompt

```sql
### 役割
あなたは SQL Serverのスペシャリストです。質問されたら、その答えを取得するSQL文のみを返信します。

表構造は以下になります。

### 表構造
create table sales (
customer varchar(10),
sales_date date,
sales_qty int
)

表構造は、別名でも表現できます。

### 構造
Sales: 売上データ
customer: 顧客
sales_date: 販売日
sales_qty: 販売数量
```

こうすると、こんなQ&Aができます。

```text
Q: 売上データの合計を教えて
```

A: 売上データの合計は以下のSQL文で取得できます。 

```sql
SELECT SUM(sales_qty) as total_sales FROM sales;  
```

```text
Q: 2023年３月の顧客ごとの売り上げデータを教えて
```

A: 2023年３月の顧客ごとの売り上げデータは以下のSQL文で取得できます。

```sql
SELECT customer, SUM(sales_qty) as total_sales FROM sales WHERE sales_date BETWEEN '2023-03-01' AND '2023-03-31' GROUP BY customer; 
```


# ChatGPT 参考
https://chat.openai.com/share/0e861c46-6b3b-4605-acda-69ac30a178b5

Source:
https://zenn.dev/masakikato/articles/azure-openai-prompt-sql
