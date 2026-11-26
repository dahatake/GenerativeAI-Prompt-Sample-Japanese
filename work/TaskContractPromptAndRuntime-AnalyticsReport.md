# Task Contract Prompt と Runtime の分析レポート

**対象**: 通常の Prompt と Task Contract Prompt の違い、Microsoft公式のRuntime用語、GitHub Copilot / Copilot Cowork / Microsoft 365 Copilot / Microsoft Copilot Studio / Microsoft Foundry の実装度  
**調査日**: 2026-11-26  
**結論の要約**: `Harness Loop` は Microsoft または GitHub が公式に定義した製品名ではない。実務上の分析名として使うなら、計画・実行・観察・検証・修正・再試行・停止・承認を含む複合Loopである。Microsoft Learnでは「Microsoft Copilot harness」と「agentic loop」、GitHub DocsではSDKの「agent loop」「tool-use loop」、Microsoft Foundryでは「Agent Runtime」と「agents / conversations / responses」、Foundry hosted agentsでは「resilient execution / multi-turn chain」が正式な用語として確認できる。

---

## 1. エグゼクティブサマリー

### 1.1 結論

1. **Task Contract Promptは、通常のPromptを単なる指示文ではなく、Agentとの間の委任契約として作る形式**である。通常のPromptが成果物の依頼、条件、出力形式を一度に書くのに対し、Task Contract Promptは、実行前に仮定・不足情報・選択肢・停止点・完了条件・証拠・承認範囲を人間とAgentが往復できる形にする。
2. **効果の中心は、Promptの文章量ではなく、人間にしか分からない既定値を人間の前に出させ、回答で置き換えること**だった。本リポジトリの横断分析では、TC系対Bで充足率が約+32ポイント、回答の段で約+40.3ポイントの差が出た。回答に現れた要件の合格率は99.5%（440/442）、現れなかった要件は55.4%（62/112）だった。
3. **「Harness Loop」は公式名称ではない。** Microsoft公式の正式名称は、Copilot Studioでは「Microsoft Copilot harness」と「agentic loop」、GitHub SDKでは「agent loop」「tool-use loop」、Microsoft Foundryでは「Agent Runtime」「agents / conversations / responses」「resilient execution」「multi-turn chain」である。
4. **GitHub Copilotは、最も明確なagent loop実装の一つ**である。CLIが会話履歴を更新し、LLMのtool requestを実行し、結果を次のターンへ戻すtool-use loopを公式に説明している。Agent modeではファイル編集、terminal、反復修正、hooks、session completion eventを使える。
5. **Copilot Coworkは、計画・段階実行・承認・停止・再開・ファイル出力を持つが、bounded retryと失敗テスト修正の閉ループはCW1だけでは未検証**である。Task Contract PromptのTC+はCW1で3回とも4/4だったが、n=3の探索的実験であり、製品効果の一般化ではない。
6. **Microsoft 365 Copilotは、製品・表面・提供データが異なるため、Copilot ChatとCoworkを同一Runtimeとして扱えない。** M365 Copilotは業務データの検索、引用、会話、承認、Work IQの統合を持つが、この記事でいうコードテスト・失敗修正Loopは、承認ゲートを含めて製品ごとの実測が必要である。
7. **Microsoft Copilot Studioは、Microsoft Copilot harnessとagentic loopの設計機能が公式に最も具体的**である。retry上限、完了基準、human approval、hook、sandbox、tool handoff、traceを設計できる。インフラとしては強いが、利用するagentによって実装度は設定依存で、選択した機能が自動的に有効になるとは限らない。
8. **Microsoft Foundryは、Agent Runtime、conversation、response、long-running resilience、HITL suspend/resumeを公式に備える。** 特にhosted agentはprocess loss recovery、lease、checkpoint参照、multi-turn chain、human approvalを持つ。しかしretry上限、テストループ、完了検証はアプリケーション側の設計に依存する。

### 実装度スコア

| Runtime / surface | 計画 | 人間への質問・承認 | Tool / file / sandbox | 検証・test | 修正・retry | 永続停止・再開 |
|---|---|---|---|---|---|---|
| GitHub Copilot Agent mode / SDK | Full | Full/環境依存 | Full | Full/設定依存 | Full/設定依存 | Full |
| GitHub Copilot CLI | Full | Full | Full | Full/設定依存 | Full/設定依存 | Full |
| Copilot Cowork | Partial-Full | Full for sensitive actions; Spec Modeはprompt | Partial-Full | Partial（CW1ではテスト自己申告） | Unverified | Partial-Full |
| Microsoft 365 Copilot Chat | Partial | Partial-Full | Partial（実行環境に依存） | Partial | Unverified | Partial |
| Microsoft Copilot Studio | Partial-Full/設定でFull | Partial-Full/設定でFull | Partial-Full/公式component；実行は設定依存 | Partial-Full/設計可能・run未実施 | Partial-Full/設計可能・run未実施 | Partial-Full/公式状態遷移；HITLは設定依存 |
| Microsoft Foundry Agent Service | Full/managed runtime | Partial-Full/アプリでdesign | Full/公式runtime；hosted agentで実行度選択 | Partial-Full/観測可能；DoDはアプリ設計・run未実施 | Partial-Full/hosted recovery；retry budgetはアプリ設計。全crash recoveryはstored resilient background Responsesに限定 | Partial-Full/公式state/resume；全resume・全deterministic replayは保証しない |

スコアの意味:

- **Full**: 公式機能または公式APIが存在し、実測または設定可能なrunで確認できる。
- **Partial-Full**: 公式機能が存在するが、設計・設定・製品表面ごとの実装が必要。
- **設定でFull**: Runtimeが必要なprimitiveを提供するが、agent設定・workflow・hook・アプリロジックなしに一律動作するとは限らない。
- **Unverified**: 公式資料では可能性が示されても、Task Contractの本タスクで実証されていない。
- **Partial**: 能力の一部が確認できるが、完全なループを構成するための証拠が不足している。

---

## 2. Task Contract Promptとは何か

### 2.1 定義

**Task Contract Prompt**は、AI Agentに大きなタスクを任せるために、以下を実行前に合意可能な形で書くPromptである。

- **Outcome**: 達成する状態
- **Scope / Out of scope**: Agentの作業範囲
- **Inputs / sources**: 参照する資料・ファイル・権限
- **Clarifications**: Agentが尋ねるべき質問と、選択肢・推奨案
- **Assumptions**: 人間が答えないときに進む既定案
- **Definition of Done（DoD）**: 完了とみなす測定可能な条件
- **Evidence**: DoDを証明する出力、ログ、テスト、引用
- **Approval boundaries**: 承認が必要な操作
- **Stop / resume**: 停止して人間に聞く条件と、再開手順
- **Error handling**: 証拠不足、失敗、曖昧な状態での停止方法

Task Contractは、単一の文章ではなく、RuntimeがAgentを止め・進めるための信号を含む。

**Task Contract Promptは本レポートで定義する分析用の格式であり、Microsoft、GitHub、Foundryが標準スキーマとして認定した製品名ではない。** PromptだけはRuntimeを停止・承認・再試行させられない。Runtimeが提示された契約を解釈し、human responseを待ち、completion checkを実行し、approvalやretryの境界を強制する必要がある。

### 2.2 通常のPromptとの比較

| 観点 | 通常のPrompt | Task Contract Prompt |
|---|---|---|
| 主語 | 「何を作るか」 | 「何を達成し、何を根拠に、何を完了とし、どこまで実行するか」 |
| 曖昧な既定値 | Agentが黙って埋める | 質問・選択肢・推奨案として人間の前に出す |
| 作業前の停止 | 通常はない、または任意 | Spec Modeで停止し、回答を待つ |
| 完了条件 | 文章的・主観的であることが多い | DoDとテスト・証拠に分解する |
| 人間の承認 | 外部操作の前後で場当たり的 | 承認ゲート、権限、不可逆操作を先に定義する |
| 手戻り | 成果物を作ってから発見する | 境界と既定値を実装前に確認する |
| 再試行 | Agent任せ | 修正可能な失敗、試行上限、証拠不足の停止を分ける |
| 成功の判定 | Agentの自己申告になりやすい | 隠しテスト・機械採点・実行ログ・人間の承認で判定する |
| 小さな可逆タスク | 通常のPromptで十分なことがある | 必要性は低い |
| 大きい不可逆タスク | 既定値と副作用のリスクが大きい | 明確な効果が期待できる |

通常のPromptは、依頼者に分かりきっているルールを省略できる。Task Contract Promptは、省略してよいルールを省略せず、依頼者にしか分からない値を人間に戻す。

### 2.3 通常Promptとの実証差

既存のv1-v4横断分析では、TC系とB（従来型）を同じモデル×課題の層で比較した。

| 比較 | 従来型 | Task Contract系 | 差 |
|---|---:|---:|---:|
| TC系-B | 62.1% | 94.1% | +32.0ポイント、片側p<0.001 |
| TC/TC+-NOASK | 53.5% | 93.9% | +40.3ポイント、片側p<0.001 |
| TC+-TC | 93.8% | 100% | +6.2ポイント、片側p=0.05 |
| TC+CL-TC+ | 84.4% | 97.9% | +13.5ポイント、片側p=0.0071 |
| FULL-B | 68.1% | 100% | +31.9ポイント、片側p=0.0013 |

仕組みの検証では、回答を受けた125回・554要件のうち、回答に現れた要件の合格率は99.5%（440/442）、現れなかった要件は55.4%（62/112）だった。独立判定者との一致は98.0%（543/554）だった。

したがって、Task Contract Promptの差は「契約の体裁」ではなく、人間の回答をエンジンへ渡すための停止・質問・更新・検証で説明できる。

---

## 3. 公式用語とRuntime

### 3.1 Microsoft Copilot harness

Microsoft Learnの正式名称は **Microsoft Copilot harness**である。

公式ドキュメントは、Microsoft Copilot harnessを次の要素で構成する:

- Instructions
- Knowledge
- Tools
- Skills
- Memory
- Agent sandbox
- Connected agents
- Channels / analytics / evaluations / governance

公式資料は「Nothing is committed in advance」として、Harnessが実行時に前の結果と文脈から次のステップを選ぶことを説明する。Microsoft Copilot Studioでも、**agentic loop**という正式な表現を、ツール失敗時に続ける・別経路を試す・停止する・人間に尋ねるためのループとして説明する。

公式のagentic loopガイドで要求される制御は:

- retry上限とattemptの定義
- retry前の事前状態検証
- terminal failureでの停止
- human approval
- completion criteriaとevidence
- ambiguous resultでのstate verification
- traceによるroute/retry/stopの監査
- original input/tool resultの保存

このガイドは、Microsoft Copilot harnessを使うCopilot Studio Agent向けであり、すべてのCopilot製品に同じretryポリシーがデフォルトで実装されたという資料ではない。

### 3.2 GitHub Copilotの「agent loop」「tool-use loop」

GitHub Docsの正式名称は、主に次である。

- **Agent mode**
- **agent loop**
- **tool-use loop**
- **session.idle**
- **session.task_complete**
- **hooks**

SDK文書は、CLIがconversation historyをLLMに送るターンを繰り返し、tool requestを実行して結果を次のターンに戻す処理を、agent loop / tool-use loopと明確に説明する。modelがtoolsを要求し続ける限りループし、tool requestがない場合にloopを終了する。

重要な終了signalは次のとおり。

| Signal | 性質 |
|---|---|
| `session.idle` | 常に、tool-use loop終了時に発行される機械的な完了/停止signal |
| `session.task_complete` | modelがtask completeを明示した場合に発行される意味的な完了 |
| `session.error` | timeout/errorと併用して処理する |

Autopilotでは、`task_complete`がない場合にCLIが継続を促す。Interactive modeでは、モデルがテキストで止まればtask_completeを出さずに`session.idle`だけで終わることがある。

Hooksは正式なRuntime制御機能である。

- `sessionStart`
- `userPromptSubmitted`
- `preToolUse`
- `postToolUse`
- `errorOccurred`
- `sessionEnd`
- `agentStop`
- `subagentStop`

`preToolUse`はtool実行をapprove/denyできる。`postToolUse`は失敗を含む実行結果を記録できる。ただし、Copilot cloud agentではhook eventの一部だけが対応し、VS CodeやCLIと同一ではない。

### 3.3 Microsoft 365 Copilot Cowork

Coworkの公式用語は、アプリケーションカードでは **agentic system**、**multi-step task execution**、**action approval**、**conversation controls**、**side panel**である。公式資料からは「Harness Loop」という固有の名称は確認できない。

公式に確認できる機能は:

- 複数ステップのTaskを分解し、一つずつ実行
- 進行を会話に表示
- interrupt/steer/pause/resume/cancel
- sensitive actionsの前にapproval
- file/work context/skills/plugins
- completed/paused/canceledのtask status

公式資料では、失敗したtestを検知して修正するretry、retry上限、sandbox内の完了判定、タスク完了の機械的なDoD信号は確認できない。

CW1では、TC+がPhase 1で止まり、同じ会話で回答を受けてPhase 2へ進む挙動を確認した。Bは質問せずに完了した。承認ゲートは6回とも表示されず、外部への作用もなかった。この観察からは、Spec Modeの停止と回答の往復は確認できるが、bounded retryやfailed-test repairは確認できない。

### 3.4 Microsoft 365 Copilot Chat

Microsoft 365 Copilot Chatは、Work IQ経由で業務データを検索し、引用を付け、質問して回答を反映できる。E12では課題T1を実行し、TC+で3回止まり、Bで同じ既定値に戻る傾向を観察した。

ただし、Chatはcodeとファイルの再現可能なループをWork IQ経由で完全に持つ製品として確認できない。

- 元データの保持が不十分だった
- Phase 2の会話で元CSVを貼り付けなかった
- 示されたコードを著者が手元で再実行した
- 作業範囲のファイルに対するtest-fail-fix loopは未確認

したがって、Chatは「回答と引用のLoop」は持つが、Task Contract Promptが要求する完全なexecution/verification loopを自動で持つとは断定できない。

### 3.5 Microsoft Copilot Studio

正式なRuntime名称は、Microsoft Copilot harnessである。

公式に確認できる構成:

- Instructions
- Knowledge
- Tools/MCP/connector/workflow
- Skills
- Memory
- Agent sandbox
- Connected agents
- Human approval workflow
- trace/analytics/evaluation

agentic loopガイドは、次の制御を明示する。

- retry上限
- retry対象とterminal failureの区分
- prior stateの検証
- completion criteria
- missing evidenceでのincomplete報告
- runtime hookによるtool/route/stopの強制
- irreversible action前のhuman approval
- traceによるrepeated calls/route changesの監査

Copilot Studioは、Task Contract Promptに必要なruntime機能を**最も明確に設計できる**環境の一つである。ただし、設定したagentが各制御を実装するかは、agentの作成方式・tool・workflow・hookに依存する。

### 3.6 Microsoft Foundry Agent Service

Microsoft Foundryの正式なRuntime名称は **Foundry Agent Service / Agent Runtime**である。

公式のRuntime componentsは:

- **Agent**: reusable model/instructions/tools
- **Conversation**: server-side persisted history
- **Response**: one unit of execution

Foundry Agent typesは:

- Prompt agents
- Voice-based prompt agents
- Hosted agents

Hosted agentsは、Agent Framework、LangGraph、OpenAI Agents SDK、Anthropic Agent SDK、Copilot SDK、custom codeをcontainerまたはsourceとしてデプロイできる。Foundryがmanaged endpoint、scaling、identity、session-level state、observabilityを提供する。

長時間実行では、次を公式に提供する。

- durable work identity
- persisted input
- lease-based recovery
- stream replay
- response checkpoints
- upstream framework checkpoint
- pause/suspend/resume for human approval
- cancellation and steering
- side-effect watermark

これは、Task Contract Promptで必要な「停止・承認・再開・progress preservation」を最もRuntimeレベルで構築しやすい環境である。

ただし、retry上限、failure-to-fix、completion test、Task Contractの質問回答は、Agentまたはアプリケーション側で設定する必要がある。Foundryが自動的にTask Contract Promptを解釈するわけではない。

---

## 4. Harness capability matrix

### 4.1 6能力 × 5 Runtime

| 能力 | GitHub Copilot | Copilot Cowork | M365 Copilot Chat | Copilot Studio | Microsoft Foundry |
|---|---|---|---|---|---|
| Plan | Agent modeはファイル選択、step、tool requestを繰り返す | 複数ステップを表示し、CW1ではPhase 1で停止 | 読み取りと調査を行うが、code test loopは限定的 | Harnessとworkflowsで明示設計可 | Agent/hosted agent/frameworkで設計可 |
| Human clarification | terminal/approvalとopen questionはmode設定に依存 | Skipで自動既定案へ進み、TC Promptでは回答を待つことも可能 | 質問して同じ会話で反映した実績あり | topics、approval、agentic loopのhuman reviewを設計可 | multi_turn_task、tool approval、checkpointsで設計可 |
| Tool / file / sandbox | Full | M365 action/fileを実行。isolated code sandboxは公式だけでは未確認 | OneDrive/Graph/Officeを扱える。code/file isolationは未確認 | Tools/MCP/workflow/sandbox/connected agentsが公式機能 | toolboxes、code interpreter、MCP、container/identity、sandboxを公式機能として設計可 |
| Verify / DoD | test/lint/buildをhookやAgent loopで実行可能 | CW1では自己申告のtest出力。run-02だけ外部再実行あり | one-shot code executionと引用照合。repeated test loopは未確認 | completion criteria、evidence、evaluation、traceを設計可 | observability/evaluation/checkpointer/response checkpointsを設計可 |
| Fail/retry | tool failureをpostToolUse/error hookで記録可能。Agent Mergeは特定failureを修復 | failure/retryのCW1実測なし | 未確認 | agentic loop guideでretry limit/terminal failureを設計可 | process loss recoveryとretryを区別し、retry budgetはアプリ側で設計可 |
| Stop/pause/resume | session.idle、task_complete、steering、cancel、HITL approval | pause/resume/cancel、Skip、task status | 会話単位で停止・再送は可能だがdurable task identityは未確認 | stopping condition、terminal state、human approvalを設計可 | suspended/ resumed multi-turn chain、lease recovery、stream replayを公式に提供 |

### 4.2 Task Contractに必要な機能の優先度

| 優先度 | 必要機能 | 理由 |
|---|---|---|
| 必須 | 人間の回答を待つ停止 | 人間にしか分からない値を置き換えるため |
| 必須 | 回答を契約へ反映し再開するidentity | 質問と実装フェーズをつなぐため |
| 必須 | 完了条件と証拠 | Agentの自己申告だけを採用しないため |
| 必須 | tool/作業範囲の権限 | 外部作用とファイル変更を制御するため |
| 強く推奨 | tool failureの分類とretry上限 | 手戻りと副作用の繰り返しを防ぐため |
| 強く推奨 | trace/session record | どのturnでどのtool/testが失敗したかを見るため |
| 強く推奨 | process loss recovery | 長時間タスクで中断を戻せるため |
| 小規模では任意 | 予算・並列sub-agent | task sizeとcostに応じて追加する |

Task Contract Promptを実行できるかを決めるのは、Promptだけではなく、Runtimeが上の機能をどこまで提供するかである。

---

## 5. 通常のPromptとの比較をRuntime側から見る

### 5.1 通常のPrompt

通常のPromptは、次の典型的な形式を持つ。

```text
次の売上データを月次集計するPython関数を書いて。
日本時間で、cancelledは除外、売上はtax抜、欠損月は0埋めしてください。
テストも通してください。
```

このPromptは、依頼者がルールをすべて書けば強い。しかし、次の問題をAgentは自動で解けない。

- Agentにしか分からない不明点を、人間へ戻すか
- 回答前に実装を止めるか
- 回答を契約へ反映するか
- 不可逆な操作の承認ゲートを置くか
- test失敗時に何回まで修正するか
- evidenceが不足した場合に完了扱いをしないか

### 5.2 Task Contract Prompt

Task Contract Promptは、通常のPromptの内容に加え、次を組み込む。

```text
Outcome:
...

Clarifications:
Q1. ...
A: ...

Open questions:
- この仮定で進めます: ...

Stop:
- 実装前にQ1-Q3へ回答を得るまで停止

Definition of Done:
- 隠しテストをすべてpass
- 元データでのdictと一致
- 保留データでも一致

Evidence:
- pytest出力
- tool result
- diff

Approval:
- 外部送信、共有、権限変更は承認が必要

Retry:
- test失敗は最大2回修正
- ambiguityが残る場合は停止
```

この違いは「文章の詳細」ではなく、Runtimeが停止・回答・再開・検証・承認を処理できるかの差として現れる。

---

## 6. 製品別の詳細比較

### 6.1 GitHub Copilot

**公式Loop**:

```text
prompt
→ full conversation historyをLLMへ
→ tool request
→ tool実行
→ tool resultを会話へ
→ 次のLLM call
→ session.idle または session.task_complete
```

**強い点**:

- Agent modeでファイル編集・terminal・反復修正が公式機能
- Copilot CLIで1turnを観測可能
- hooksでtool前後・session開始終了・errorを監視
- Agent Mergeでfailed workflow/merge conflictのtargeted loop
- cloud sandboxes、session continuity、MCP、custom instructions

**弱い点 / 未検証**:

- retry上限はAgent、model、surfaceごとに変わる
- task_completeはbest-effortで、session.idleとの意味が異なる
- Task Contract PromptのGitHub側A/Bは未実行
- file/repoごとの承認設定は表面ごとの確認が必要

**Task Contract Promptとの相性**:

最も相性がよい候補。特に、Spec Modeでのstop、回答、Phase 2への再開、テスト、fix loopを支えるRuntime機能が揃う。ただし、Task Contractの構造はPrompt側で渡す必要があり、Runtimeがそれを標準スキーマとして解釈するわけではない。

### 6.2 Copilot Cowork

**公式Loop**:

```text
task
→ planning / step list
→ skill/tool
→ step progress
→ approval for sensitive action
→ result / file
→ user review
```

**確認できた点**:

- TC+のPhase 1でstop
- 3問と選択肢を出し、回答を受けてimplementationへ進む
- test/resultを自己申告
- pause/resume/cancel
- action approval

**未確認点**:

- failed testからのautomatic fix loop
- retry count
- ambiguous test resultでのstate verification
- sandbox/作業範囲の隔離をCW1だけで完全証明
- 承認ゲート自体の失敗注入

**結論**:

CoworkはTask Contract Promptの「事前に聞く」「止める」「回答して再開する」を実現できる。完全なHarness Loopとしては、失敗修正・retry・DoD evidenceの外部再実行を追加検証する必要がある。

### 6.3 Microsoft 365 Copilot

M365 Copilotには複数の表面がある。

- Copilot Chat / Work IQ
- Copilot Cowork
- Office/Teams/OneDrive上のCopilot

表面ごとにtool、状態、承認、sandboxが異なる。

CW1の結果はCoworkのものであり、M365 Copilot ChatやOffice Copilot全体の実装度を代表しない。

**相性**:

- 業務記録・承認・引用に強い
- Task Contract Promptの情報収集・回答停車に使える
- code/test loopを標準で持つとは断定できない
- 外部への作用は承認ゲートで制御できる

### 6.4 Microsoft Copilot Studio

Copilot Studioは、Microsoft Copilot harnessを使うRuntime環境として公式に定義される。

**強い点**:

- Instructions / knowledge / tools / skills / memory / sandbox
- MCP/connector/workflow
- human approval workflow
- agentic loop with retry limits
- completion verification
- trace/evaluation

**Task Contract向けの実装**:

1. PromptでDoDとOut of scopeを定義
2. Agentに回答待ちのtopicを定義
3. workflowにapproval gateを置く
4. hook/pre/post toolでvalidation
5. retry上限とterminal failureを設定
6. evidenceをagent outputから検証
7. traceからどこで停止/再試行したか記録

### 6.5 Microsoft Foundry Agent Service

Foundryは最も柔軟で、Agent Runtimeをmanagedに提供する。

**強い点**:

- Agent / conversation / response
- Prompt、voice、hosted agent
- server-side multi-turn state
- long-running work identity
- process-loss recovery
- human-in-the-loop suspend/resume
- toolboxes/MCP/code interpreter/observability
- Hosted agents by Agent Framework/LangGraph/OpenAI/Anthropic SDK/Copilot SDK

**Task Contract向けの実装**:

- `@multi_turn_task`でquestion/approvalをsuspend
- `task_id`で回答をresume
- `metadata`にlast completed phase/idempotency key
- external storageにlarge progress/results
- downstream serviceにidempotency
- Agent framework checkpointer
- workflow engineでfan-out/fan-in/timer
- observabilityでevidenceとtool callを記録

**未確認/設計依存**:

- Task Contract schemaの標準解釈
- retry上限の既定値
- test failから修正までの自動loop
- completionのautomatic semantic verification

---

## 7. Runtime機能の実装度

### 7.1 GitHub Copilot

| 機能 | 実装度 | 根拠 |
|---|---|---|
| Agent loop | Full | GitHub SDK「the agent loop」公式文書 |
| Tool request → execute → result | Full | tool-use loop公式文書 |
| session.idle/task_complete | Full | SDK公式文書 |
| hooks | Full/設定依存 | pre/post/error/stop hooks公式文書 |
| human approval | Full/環境依存 | terminal permission、preToolUse |
| retry policy | Partial | autopilotはtask_completeでnudge。汎用retry上限は設定依存 |
| test-fix loop | Full/設定依存 | Agent modeはtest/errorを反復する公式説明。失敗注入試験は未実施 |
| session persistence | Full | resume、session events、cloud session official docs |

### 7.2 Copilot Cowork

| 機能 | 実装度 | 根拠 |
|---|---|---|
| Planning | Full | official docs + CW1 Phase 1 |
| human question | Full/同じtask | CW1で3問、回答後に再開 |
| approval | Partial-Full | 公式にsensitive action approval。CW1にはapproval triggerなし |
| file output | Full | CW1のrun-02でgenerated files |
| test execution | Partial | run-02/04/06で自己申告。独立再実行は一部 |
| retry/failure repair | Unverified | failure injectionなし |
| bounded retry | Unverified | no retry limit observed |
| process recovery | Unverified | CW1ではprocess loss testなし |

### 7.3 M365 Copilot Chat

| 満足度 | 実装度 | 根拠 |
|---|---|---|
| 質問停止・回答反映 | Partial-Full | E12でTC+がPhase 1で止まり、回答を反映 |
| code execution | Partial | E11bでSHA256と素数を実行 |
| test-fail-fix loop | Unverified | file work loop未検証 |
| sandbox | Unverified | 作業範囲隔離未検証 |
| retry | Unverified | E12は再送があったが自動retryではない |

### 7.4 Copilot Studio

| 機能 | 実装度 | 根拠 |
|---|---|---|
| Microsoft Copilot harness | Full/official | Harness overview |
| agentic loop | Full/設計可能 | agentic loops in practice |
| retry limit | Full/設計可能 | guidance + runtime hooks |
| human approval | Full/設計可能 | workflow + human approval |
| completion verification | Full/設計可能 | verify completion |
| test/evaluation | Full/設計可能 | evaluation/trace |
| sandbox | Full/official | isolated Python sandbox |

### 7.5 Microsoft Foundry

| 機能 | 実装度 | 根拠 |
|---|---|---|
| Agent Runtime | Full/official | Foundry overview/runtime components |
| conversation/response | Full/official | runtime components |
| tools/MCP | Full/official | toolboxes, MCP, functions |
| HITL suspend/resume | Full/official | `@multi_turn_task`, `task_id` |
| resilience | Full/official | durable identity, lease, checkpoint |
| retry policy | Partial/アプリ設計 | runtime distinguishes recovery/retry; application defines budget |
| completion test | Partial/アプリ設計 | service/agent framework should validate DoD |
| Task Contract standard | Unverified | service is generic; no standard Task Contract schema |

---

## 8. Task Contract PromptとHarness Loopの関係

Task Contract Promptは、Harness Loopへ渡す**タスク契約**である。逆に、Harness LoopはTask Contract Promptを実行・検証・再試行・停止する**Runtime mechanism**である。

```text
Task Contract Prompt
  = Outcome / Scope / Clarifications / Assumptions / DoD / Evidence / Approval / Retry / Stop

Harness Loop
  = Plan / Act / Observe / Decide / Retry or Stop / Verify / Resume
```

両者が揃うと、次が成立する。

1. Agentは作業前に曖昧な点を質問する。
2. Humanが回答して既定値を置き換える。
3. Agentは回答を契約へ反映して実行する。
4. Runtimeはtool/test/evidenceを実行し、DoDを検証する。
5. testやtoolが失敗した場合、修正可能なら再試行し、terminal failureなら停止する。
6. irreversible actionの前に承認を得る。
7. process lossや会話中断があっても、progressを再開できる。

片方だけでは不十分である。

- Task Contract Promptだけでは、Runtimeが停止やretryやapprovalを持たなければ機能しない。
- Runtimeだけでは、依頼者にしか分からない既定値を人間へ出す契約がない。

---

## 9. 実証データとの結論

### 9.1 Task Contractの実験

| Evidence | 結論 |
|---|---|
| TC系-B | +32.0ポイント、片側p<0.001 |
| TC/TC+-NOASK | 回答の段で+40.3ポイント、片側p<0.001 |
| 回答に現れた要件 | 99.5%合格（440/442） |
| 回答に現れなかった要件 | 55.4%合格（62/112） |
| CW1 B | 3回とも2/4 |
| CW1 TC+ | 3回とも4/4 |
| CW1保留データ | TC+の確認可能コードは4/4。run-02は手動review後の再実行 |

**CW1とE12の比較は、製品効果の直接比較ではない。** E12は、隠し要件に基づくAIオラクルが尋ねられた点だけに答えた。CW1は、隠し要件を知った実行者（AIアシスタント）が固定の回答表から話題を選び、盲検ではなかった。E12はPhase 2を新しい会話で送り、CW1は原則として同じタスクでPhase 2を送った。E12の主指標は、Copilotが示したdictの組み合わせ一致では判定不能2回と再構成データ1回であり、著者が保存されたコードを元のsales.csvで再実行した副次採点では3回とも3/4だった。CW1の主指標は、Coworkが提示したdictを元のsales.csvと照合した結果で、TC+は3回とも4/4だった。E12は個人設定が有効な環境で実行された可能性もあるため、製品と回答方法の違いを分けて読む必要がある。

### 9.2 Harness Loopの実証

CW1は次の能力を確認した。

- Phase 1で実装を止める
- 質問に固定回答を返す
- 同じ会話でPhase 2へ進む
- TC+がtestを実行したと報告する
- final dictを提示する

以下はCW1では確認できなかった。

- failed test -> 修正 -> 再実行
- retry上限
- process crash recovery
- approval trigger
- external action
- 作業ディレクトリの隔離

したがって、Task Contract Promptの効果とHarness Loopの実装度は別の証拠である。

---

## 10. 製品別の推奨

| 用途 | 推奨Runtime | 理由 |
|---|---|---|
| ソフトウェア開発での大きなTask | GitHub Copilot Agent / SDK / CLI | Agent loop、file/test/lint、hooks、session、cloud executionが公式に揃う |
| Microsoft 365業務記録からContractを作る | M365 Copilot Chat/Coworkを表面ごとに分ける | Chatは引用・会話・業務データ検索、Coworkはsensitive action approval・task step・file outputを公式に提供する。どちらにも全coded test loopを一般化しない |
| 業務プロセスを設計し、承認とretryを強制する | Copilot Studio | Harness、workflow、人間承認、trace、evaluation、sandboxを統合できる |
| 独自agent frameworkでdurable HITLを実装する | Microsoft Foundry Agent Service | Agent Runtime、conversation、response、hosted agent、resilience、approvalを公式に提供する |
| 既存のTask Contractを最初に試す | GitHub Copilot Agent mode | 実行・テスト・diff・再試行を最も再現しやすい |
| 複数ステップの業務タスクを承認付きで試す | Copilot Cowork | action approvalとtask stepを公式に提供する |

推奨は、Task Contract Promptの効果を保証するものではない。Runtimeごとの実験を追加する必要がある。

---

## 10A. 正式名称・Preview・適用範囲の注意

1. **Copilot Studioのhooksはpreviewの機能で、同じhook形式をすべてのsurfaceで保証しない。** preToolUse/postToolUse/errorOccurred/sessionEndなどを使えるが、Copilot Studio AgentとGitHub CLI/cloud agentでevent supportは異なる。
2. **FoundryでMicrosoft Copilot harnessを選べる機能はpreviewである。** Foundry prompt agentsは既定のruntimeと、Copilot harnessを選択するmulti-step tool/skill/file/command workflowを区別する。この選択だけでTask Contract Promptの効果を保証しない。
3. **Foundryの完全なcrash recoveryは、stored background Responsesでresilient background executionを有効にした場合に限る。** foreground responseやリカバリ時のdeterministic replayは保証されない。アプリケーションはcheckpoint、side-effect watermark、idempotencyを持つ必要がある。
4. **Copilot Coworkの承認、スキップ、記憶、statusの文はCW1の合成課題と公式のapplication cardを分けて読む。** CW1では承認ゲートが出ず、回答者は固定表を使った。公式資料の承認機能を、CW1の承認ゲートが出なかったから有効でないとは判断しない。
5. **「original input/tool result preservation」はCopilot Studio agentic loopガイドの直接引用ではなく、入出力保存・handoff・traceを組み合わせた報告上の要約として扱う。** Tool resultを保存する保証をCopilot Studioがすべてのagentにデフォルトで持つとは断定しない。
6. **GitHub Copilotのhooksはsurfaceごとの実装差がある。** cloud agentはsubset、CLIはpersonal/repository hooks、VS Codeはpreviewと公式資料で区別されている。

## 11. 未検証事項

1. GitHub Copilot Agent modeで、Task Contract Promptと通常Promptのdirect A/Bを実行していない。
2. Copilot Studioで、HITL/approval/retry/traceを同じTask Contractで実行した実績がない。
3. Microsoft Foundryで、multi-turn human approvalと失敗修正をTask Contractで検証した実績がない。
4. Coworkで、失敗テスト・retry上限・approval failure・process lossを検証していない。
5. M365 Copilot Chatで、作業範囲のファイルに対してtest-fail-fix loopを繰り返す実験をしていない。
6. Microsoft公式資料は製品とサーフェスごとに更新されるため、確認日と版を継続更新する必要がある。

---

## 12. 調査方法

調査は次の順で行った。

1. Task Contractの既存実験レポートとCW1ログを一次資料として読む。
2. Microsoft公式:
   - Microsoft Copilot harness overview
   - Design reliable agentic loops
   - Copilot Cowork overview/application card
   - Foundry Agent Service overview/runtime components
   - Foundry long-running resilience
   - Foundry human-in-the-loop
3. GitHub公式:
   - Agent mode
   - Copilot in the cloud
   - SDK agent loop
   - hooks
   - Agent Merge
4. 公式名称と機能を、計画・実行・検証・retry・approval・stopに分解。
5. CW1のdict/test result/phase1/phase2/メタデータから実測を抽出。
6. Full/Partial/Unverifiedの4段階で実装度を判定。

---

## 13. 参考資料

| R | 資料 | 確認した範囲 | URL |
|---|---|---|---|
| R1 | Microsoft Copilot harness overview | Harness component model、sandbox、tool、memory、skills、connected agents | https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/microsoft-copilot-harness-overview |
| R2 | Design reliable agentic loops | retry、停止、completion verification、HITL、trace | https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/agentic-loops-in-practice |
| R3 | Copilot Cowork overview | task decomposition、approval、pause/resume/cancel、file operations | https://learn.microsoft.com/en-us/copilot/cowork/ |
| R4 | Copilot Cowork application card | agentic characteristics、intended use、limitations、evaluation | https://learn.microsoft.com/en-us/copilot/cowork/responsible-ai/copilot-cowork-application-card |
| R5 | Using agent mode in your IDE | Agent modeのfile edit/command/test/review loop | https://docs.github.com/en/copilot/how-tos/copilot-in-your-ide/use-copilot-agents/use-agent-mode |
| R6 | GitHub Copilot on GitHub.com and GitHub Mobile | cloud/session/sandbox/Agent Merge/Automations | https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-on-github |
| R7 | The agent loop | SDK/CLI tool-use loop、turn、session.idle/task_complete | https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/agent-loop |
| R8 | Hooks for GitHub Copilot | pre/post/error/stop hooks、approval/validation/logging | https://docs.github.com/en/copilot/concepts/customizations/hooks |
| R9 | Getting pull requests ready to merge with Agent Merge | failed workflow/merge conflict修正Loop | https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/watch-and-fix-pull-requests |
| R10 | What is Microsoft Foundry Agent Service? | managed Agent Runtime、prompt/voice/hosted agent、tools、identity、observability | https://learn.microsoft.com/en-us/azure/foundry/agents/overview |
| R11 | Runtime components in Foundry Agent Service | agents/conversations/responses lifecycle | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components |
| R12 | Resilience for long-running Foundry hosted agents | work identity、lease、checkpoint、stream replay、recovery | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/long-running-agent-resilience |
| R13 | Add a human-in-the-loop approval step in Foundry | suspended task、task_id、resumed turn、approval | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/add-human-in-the-loop |
| R14 | Application card: GitHub Copilot Agents | surface distinctions、permission、sandbox、approval、limits | https://docs.github.com/en/copilot/responsible-use/agents |
| R15 | CW1 protocol | 6回の事前登録、回答規則、採点定義 | [./experiments/data/preregistration_cowork_cw1.md](./experiments/data/preregistration_cowork_cw1.md) |
| R16 | CW1 raw records | 6回の会話、回答、dict、test/保留データの記録 | [./experiments/data/cw1/cowork_scores.csv](./experiments/data/cw1/cowork_scores.csv) |
| R17 | The agent loop (GitHub SDK) | SDK/CLIのtool-use loop、turn、session.idle/task_complete、autopilot nudge | https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/agent-loop |
| R18 | Agent Framework / GitHub Copilot harness (Microsoft DevBlog) | Copilot harnessのshell/file/MCP、permission handler、OpenTelemetry、session reuse | https://devblogs.microsoft.com/agent-framework/build-production-ready-agents-with-the-github-copilot-harness-and-agent-framework/ |
| R19 | Add a human-in-the-loop approval step in Foundry | multi_turn_taskのsuspended/resumed、task_id、approval、durable wait。deleting a finished/suspended chainは別に記載 | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/add-human-in-the-loop |
| R20 | Copilot Studio agentic loop guide | retry limit、terminal failure、completion evidence、trace、runtime hook | https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/agentic-loops-in-practice |
| R21 | Microsoft Copilot harness overview (Work IQ/managed MCP) | Microsoft IQ/Work IQがmanaged MCP toolとしてorganizational contextを提供する | https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/microsoft-copilot-harness-overview |

---

## 14. 最終結論

**Task Contract Promptは、通常のPromptに対して「止める、聞く、契約を更新する、証拠を検証する」情報を加える委任形式である。**

**Runtimeとして必要なのは、単なるLLM callではなく、session state、tool/file execution、human approval、DoD verification、failure/retry、停止・再開、observabilityを持つHarnessである。**

**GitHub Copilotは、公式のagent/tool-use loop、hooks、cloud session、test/lint実行、Agent Mergeから、loop機能を最も明確に実装している。**

**Copilot Coworkは、計画・段階実行・質問停止・承認・ファイル出力を持つが、bounded retry、failed-test repair、process recoveryはCW1だけでは確認できない。**

**M365 Copilot Chatは、業務データの検索・引用・質問停止を持つが、code/test loopは製品表面ごとに確認が必要である。**

**Copilot Studioは、Microsoft Copilot harnessとagentic loopガイドを公式に持ち、retry、approval、trace、evaluation、sandbox、human approvalを設計可能である。**

**Microsoft Foundryは、Agent Runtime、Conversation、Response、Hosted agents、HITL suspend/resume、resilient process recoveryを最も明確なRuntime componentsとして持つ。**

したがって、GitHub CopilotでTask Contract Promptが有効だという結論を一般化するには、GitHub Agent modeでのdirect A/Bが必要である。逆に、現在確認できる結論は、Task Contract Promptが回答を得る段で強い効果を示し、GitHub Copilot/Copilot Studio/Foundryはそれを運用可能なRuntime機能を持つという二層の事実である。
