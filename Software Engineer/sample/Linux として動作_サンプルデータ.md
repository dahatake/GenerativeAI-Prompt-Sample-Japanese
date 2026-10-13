対応Prompt: [../Linux として動作.md](../Linux%20として動作.md)

※以下はすべて架空のサンプルデータです。実在の企業・個人・環境・識別子とは無関係です。

# セッション前提
- 使い捨ての Ubuntu 22.04.5 LTS コンテナーを想定
- `python3 --version` は `Python 3.10.12`(Ubuntu 22.04 標準)
- `docker --version` は `Docker version 26.1.4`
- 作業ディレクトリは `/home/demo/lab`
- 重要: どのコマンドも学習用の隔離環境でのみ実行し、本番環境では実行しない

## 1. 役割Promptの直後に送る最初の入力
```text
pwd
```

## 2. Python 実行確認向けの追加入力
```text
# 期待する事前状態
- `/home/demo/lab` は空ディレクトリ
- 標準出力に `Result: 33` が出れば成功
- ネットワークアクセス不要

# 送信するコマンド
echo -e "x = lambda y: y*5+3\nprint('Result: ' + str(x(6)))" > run.py && python3 run.py
```

## 3. Docker 動作確認向けの追加入力
```text
# 期待する事前状態
- Docker daemon 起動済み
- ビルドコンテキストは `/home/demo/lab`
- 作成イメージは学習用で永続利用しない

# 送信するコマンド
echo -e "echo Hello from Docker" > entrypoint.sh && echo -e "FROM ubuntu:20.04\nCOPY entrypoint.sh entrypoint.sh\nENTRYPOINT [\"/bin/sh\", \"entrypoint.sh\"]" > Dockerfile && docker build . -t sample_lab_image && docker run --rm -t sample_lab_image
```

## 4. 期待する出力の目安（模擬結果の確認用）
- 1: `/home/demo/lab`
- 2: `Result: 33`（`6*5+3`）
- 3: `docker build` のビルドログ(`FROM ubuntu:20.04` の取得、`COPY`、`ENTRYPOINT` の各ステップと `sample_lab_image` のタグ付け)のあと、`Hello from Docker` が表示される
- 各出力は1コマンド1コードブロックで、日本語の補足は【】内だけに入っていること

## 5. 追加で試せる入力（ファイル状態の追跡確認）
```text
ls -l
```
```text
cat run.py
```
期待: `ls -l` に `run.py` `entrypoint.sh` `Dockerfile` が現れ、`cat run.py` は `x = lambda y: y*5+3` と `print('Result: ' + str(x(6)))` の2行を返す。
