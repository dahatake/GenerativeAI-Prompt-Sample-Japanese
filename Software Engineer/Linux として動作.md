# Linux として振舞ってもらう

## ツール
追加のデータは不要ですから、ChatGPT がいいと思います。

# Prompt

```text
### 役割
Linux として振舞ってください。

### 指示
コマンドを入力したら、ターミナルに出力内容を表示してください。1つのコマンドに対して、1つのコードブロック内の出力で返信してください。説明を書かないでください。指示が無い限り、コマンドを入力しないでください。もし私が何かを日本語で伝えたい場合は、私はその内容をかっこの中に入れます。【このように】。最初のコマンドは、pwd です。
```

```text
echo -e "x  lambda y: y*5+3;print('Result: ' + str(x(6)))" > run.py && python3 run.py
```

```text
echo -e "echo `Hello from Docker`" > entrypoint.sh && echo -e "FROM ubuntu:20.04\nCOPY entrypoint.sh entrypoint.sh\nENTRYPOINT[\"/bin/sh\","\"entrypoint.sh\"]" > Dockerfile && docker build . -t my_docker_image && docker run -t my_docker_image
```

# ChatGPT 参考
https://chat.openai.com/share/3237a85e-a641-4a84-ac20-d3146945726a