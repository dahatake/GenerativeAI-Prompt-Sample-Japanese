const REPO = "https://github.com/dahatake/GenerativeAI-Prompt-Sample-Japanese/tree/main/";
const link = (folder, label) => ({ label, url: REPO + encodeURI(folder) });

export const COPILOTS = [
  {
    id: "m365",
    name: "Microsoft 365 Copilot",
    emoji: "🧑‍💼",
    color: "#7f85f5",
    color2: "#00b7c3",
    shape: "icosahedron",
    tagline: "Word・Excel・PowerPoint・Outlook・Teams を横断する仕事のパートナー",
    tips: [
      "役割 → 目的 → 文脈 → 出力形式 の順で伝えると、一発で使える答えが返ってきます。",
      "「/」でファイルや会議を参照すると、社内データに基づいた回答になります。",
      "会議後は『決定事項・未決事項・次のアクション』を表にして、と頼むのが定番です。",
      "うまくいかない時は、1つの長い指示より『追加の一言』で育てる方が速いです。"
    ],
    bad: "会議の議事録を作ってください。",
    good: "あなたは経験豊富なPMOです。以下の会議内容から、参加者・議題・決定事項・次回アクションを含む議事録を、担当者と期限付きの表で作成してください。",
    lab: {
      task: "会議メモから議事録を作る",
      parts: {
        role: "あなたは経験豊富なPMOです。",
        goal: "会議内容を、要点を整理した議事録にしてください。",
        context: "対象は2025年7月15日の定例会議（参加者7名）です。内容は <会議内容> タグ内にあります。",
        format: "決定事項・未決事項・次のアクションを表形式で、担当者と期限付きで出力してください。",
        constraints: "推測は書かず、不明点は『要確認』と記載。A4で1枚以内に収めてください。"
      }
    },
    quiz: [
      { q: "Copilot に良い回答を引き出す最初の一歩は？", a: ["とにかく短く依頼する", "役割・目的・文脈を伝える", "何度も同じ依頼を繰り返す", "英語でだけ依頼する"], correct: 1, why: "役割・目的・文脈が揃うほど、意図に沿った出力になります。" },
      { q: "出力が惜しい時、次にやると効果的なのは？", a: ["最初からやり直す", "諦める", "追加の指示で具体的に修正を依頼する", "画面を再読み込みする"], correct: 2, why: "対話で育てるのが Copilot の基本スタイルです。" }
    ],
    links: [link("会議", "会議のサンプル"), link("日々のタスク", "日々のタスク"), link("営業", "営業"), link("管理職", "管理職")]
  },
  {
    id: "github",
    name: "GitHub Copilot",
    emoji: "👩‍💻",
    color: "#3fb950",
    color2: "#58a6ff",
    shape: "octahedron",
    tagline: "コード補完・チャット・エージェントで開発を加速するAIペアプログラマー",
    tips: [
      "コメントや関数名で『やりたいこと』を先に書くと補完の精度が上がります。",
      "チャットでは対象ファイル・言語・制約（ライブラリ、テスト方針）を明示しましょう。",
      "『テストを先に書いて』『エッジケースを列挙して』は強力な定番プロンプトです。",
      "生成コードは必ずレビュー。セキュリティと依存関係は人間が最終確認します。"
    ],
    bad: "ソート書いて",
    good: "TypeScript で、重複を除いて昇順に並べる関数 uniqueSort(numbers: number[]) を書いてください。空配列と負数のテストケースも Jest で付けてください。",
    lab: {
      task: "関数とテストを生成する",
      parts: {
        role: "あなたはシニアTypeScriptエンジニアです。",
        goal: "数値配列から重複を除き、昇順に並べる関数 uniqueSort を実装してください。",
        context: "Node.js 20 / TypeScript 5 のプロジェクトで、外部ライブラリは使えません。",
        format: "関数本体と Jest のテストを別々のコードブロックで出力してください。",
        constraints: "空配列・負数・巨大配列のケースを必ず含め、計算量も一行で説明してください。"
      }
    },
    quiz: [
      { q: "補完の精度を上げるコツは？", a: ["ファイルを空にする", "意図が伝わるコメントや関数名を先に書く", "変数名を a, b, c にする", "常にTabキーを連打する"], correct: 1, why: "文脈（コメント・命名・周辺コード）が補完の手がかりになります。" },
      { q: "生成されたコードの扱いとして正しいのは？", a: ["そのままデプロイ", "テストとレビューで検証する", "コメントを消すだけ", "動いたら何も見ない"], correct: 1, why: "品質とセキュリティの責任は開発者にあります。" }
    ],
    links: [link("Software Engineer", "Software Engineer"), link("Code Interpreter", "Code Interpreter")]
  },
  {
    id: "studio",
    name: "Copilot Studio",
    emoji: "🤖",
    color: "#ff8c00",
    color2: "#ff4fa3",
    shape: "dodecahedron",
    tagline: "ローコードで自分だけのエージェントを作り、業務を自動化",
    tips: [
      "最初に『誰の・どの業務を・どこまで任せるか』を1文で定義しましょう。",
      "指示文（Instructions）は箇条書きで、禁止事項と口調も書くと安定します。",
      "ナレッジは小さく始めて、よく聞かれる質問10個で動作テストします。",
      "権限と承認フローを最初から設計し、重要操作は人の確認を挟みます。"
    ],
    bad: "社内ヘルプのボットを作って",
    good: "新入社員向けIT ヘルプデスク エージェント。対象はPC・VPN・アカウントの質問。ナレッジは IT FAQ のみ参照し、不明なら担当チームの窓口を案内。口調は丁寧で簡潔。",
    lab: {
      task: "社内ヘルプエージェントの指示文を作る",
      parts: {
        role: "あなたは新入社員向けのITヘルプデスク担当エージェントです。",
        goal: "PC・VPN・アカウントに関する質問に、手順付きで答えてください。",
        context: "参照できるのは社内IT FAQナレッジのみです。利用者はITに詳しくありません。",
        format: "結論 → 手順（番号付き）→ 解決しない場合の連絡先 の順で回答してください。",
        constraints: "ナレッジに無い内容は推測せず、担当チームへ案内。個人情報は聞き出さないこと。"
      }
    },
    quiz: [
      { q: "エージェント作成で最初に決めるべきことは？", a: ["アイコンの色", "誰の何の業務をどこまで任せるか", "名前の絵文字", "公開日"], correct: 1, why: "目的と範囲が明確だと、指示文もテストも設計しやすくなります。" },
      { q: "重要な操作（支払い・削除など）はどうする？", a: ["全自動にする", "人の承認を挟む", "ログを無効化する", "全員に権限を渡す"], correct: 1, why: "Human-in-the-loop で安全に自動化します。" }
    ],
    links: [link("Agent", "Agent サンプル")]
  },
  {
    id: "security",
    name: "Security Copilot",
    emoji: "🛡️",
    color: "#e5484d",
    color2: "#8e4ec6",
    shape: "torusknot",
    tagline: "インシデント調査・脅威分析・リスク対策をAIで素早く",
    tips: [
      "アラートID・時間範囲・対象アセットを明示して、調査の範囲を絞ります。",
      "『要約 → 影響範囲 → 推奨対応』の3段階で聞くと意思決定しやすくなります。",
      "Prompt Injection など AI 固有のリスクも学び、入力と出力の両方を疑います。",
      "機密情報は入力しない。結果は必ず一次情報（ログ）で裏取りします。"
    ],
    bad: "このアラートどう思う？",
    good: "アラート ID 1234 について、過去24時間の関連サインインを要約し、影響を受けたユーザーと推奨対応を優先度付きで3つ挙げてください。",
    lab: {
      task: "セキュリティアラートを調査する",
      parts: {
        role: "あなたはSOCのシニアアナリストです。",
        goal: "不審なサインインアラートの原因と影響を調査してください。",
        context: "対象はアラート ID 1234、過去24時間、海外IPからの連続失敗後に成功したログインです。",
        format: "要約・影響範囲・推奨対応（優先度付き3件）の順に出力してください。",
        constraints: "根拠となるログ項目を併記し、断定できない点は仮説として区別してください。"
      }
    },
    quiz: [
      { q: "Prompt Injection とは？", a: ["プロンプトの圧縮技術", "入力で AI に意図しない指示を実行させる攻撃", "高速化の手法", "画像生成の設定"], correct: 1, why: "外部入力に紛れた命令でAIの挙動が乗っ取られるリスクです。" },
      { q: "AI の調査結果はどう扱う？", a: ["そのまま信じる", "ログなど一次情報で裏取りする", "無視する", "公開する"], correct: 1, why: "出力を鵜呑みにしないことが原則です。" }
    ],
    links: [link("Security", "Security サンプル")]
  },
  {
    id: "analyst",
    name: "Researcher & Analyst",
    emoji: "📊",
    color: "#00b7c3",
    color2: "#4f6bed",
    shape: "wire",
    tagline: "調査・データ分析・戦略立案を、根拠付きで深掘りする",
    tips: [
      "『何を決めたいか』を先に言うと、分析の切り口がブレません。",
      "データの列名・期間・単位を渡し、グラフと所見をセットで依頼します。",
      "前提・仮説・リスクを分けて出力させると、レビューしやすくなります。",
      "出典の提示を必ず求め、数字は元データで検証します。"
    ],
    bad: "売上を分析して",
    good: "添付の月次売上CSV（2023-2024）から、前年同月比の増減要因を3つに絞って分析し、折れ線グラフと次月の打ち手を提示してください。",
    lab: {
      task: "売上データから打ち手を導く",
      parts: {
        role: "あなたは事業会社のデータアナリストです。",
        goal: "前年同月比の増減要因を特定し、次月の打ち手を提案してください。",
        context: "添付は月次売上CSV（2023-2024）。列は 月・商品カテゴリ・売上・販売数です。",
        format: "所見3点・折れ線グラフ・打ち手を表で、仮説と事実を分けて出力してください。",
        constraints: "出典となる列名を明記し、データから言えない点は推測と明示してください。"
      }
    },
    quiz: [
      { q: "分析依頼で最初に伝えると良いことは？", a: ["好きな色", "何を決めたいか（意思決定の目的）", "ファイルサイズ", "作成者名"], correct: 1, why: "目的が分析の切り口を決めます。" },
      { q: "数字を含む回答の扱いは？", a: ["全て正しい", "元データで検証する", "丸めて報告", "削除する"], correct: 1, why: "計算ミスや誤読の可能性があるため検証が必要です。" }
    ],
    links: [link("データ分析", "データ分析"), link("ビジネス戦略や分析", "ビジネス戦略や分析"), link("数理最適化問題", "数理最適化問題")]
  },
  {
    id: "creative",
    name: "Designer & Creative",
    emoji: "🎨",
    color: "#ff4fa3",
    color2: "#ffb900",
    shape: "sphere",
    tagline: "画像・文書・プレゼンを、想像から形へ",
    tips: [
      "被写体・スタイル・構図・光・雰囲気をカンマ区切りで足していきます。",
      "カメラワーク（ショット・アングル・動き）を言葉にすると映像表現が一気に洗練されます。",
      "NG要素（文字入れ不可など）も明示すると、やり直しが減ります。",
      "著作権・肖像権・ブランドガイドラインを必ず確認します。"
    ],
    bad: "かっこいい画像",
    good: "ミディアムクローズアップ、ローアングル、ゆっくりしたオービットで、未来的なオフィスで働くロボットを夕景の柔らかい光で。写実的、文字なし。",
    lab: {
      task: "プロモーション画像を指示する",
      parts: {
        role: "あなたは広告制作のアートディレクターです。",
        goal: "新サービスのキービジュアル画像を作ってください。",
        context: "未来的なオフィスで、ロボットと人が協働している夕景のシーンです。",
        format: "16:9、写実的、ミディアムクローズアップ・ローアングルで出力してください。",
        constraints: "画像内に文字やロゴは入れず、実在の人物・ブランドは描かないでください。"
      }
    },
    quiz: [
      { q: "画像の指示で効果的なのは？", a: ["単語1つだけ", "被写体・スタイル・構図・光を具体的に書く", "長い物語だけ", "記号だけ"], correct: 1, why: "具体的な視覚要素が仕上がりを決めます。" },
      { q: "ローアングルが与える印象は？", a: ["客観性", "力強さ・ヒーロー感", "不安定さ", "俯瞰"], correct: 1, why: "下から見上げると威厳や力強さが出ます。" }
    ],
    links: [link("文書・画像作成", "文書・画像作成"), link("DALL-E", "DALL-E")]
  }
];

export const PART_LABELS = {
  role: { label: "役割", icon: "🎭", weight: 15 },
  goal: { label: "目的", icon: "🎯", weight: 25 },
  context: { label: "文脈", icon: "🗂️", weight: 20 },
  format: { label: "出力形式", icon: "📐", weight: 20 },
  constraints: { label: "制約", icon: "🧱", weight: 20 }
};

export const BADGES = [
  { id: "first", icon: "🌱", name: "はじめの一歩", cond: s => s.xp >= 10 },
  { id: "lab", icon: "🧪", name: "プロンプト錬金術師", cond: s => s.labs.length >= 1 },
  { id: "quiz3", icon: "🧠", name: "3連続正解", cond: s => s.bestCombo >= 3 },
  { id: "all", icon: "🏆", name: "全Copilot制覇", cond: s => s.done.length >= COPILOTS.length },
  { id: "orb", icon: "🔮", name: "オーブコレクター", cond: s => s.orbs >= 5 },
  { id: "lib", icon: "📚", name: "Prompt探検家", cond: s => (s.gcats || []).length >= 5 },
  { id: "dir", icon: "🎬", name: "カメラ監督", cond: s => s.cams.length >= 5 },
  { id: "konami", icon: "🌈", name: "秘密のコマンド", cond: s => s.konami }
];

export const SHOTS = { EWS: "Extreme Wide Shot", WS: "Wide Shot", FS: "Full Shot", MS: "Medium Shot", MCU: "Medium Close-Up", CU: "Close-Up", ECU: "Extreme Close-Up" };
export const ANGLES = { eye: "Eye Level", low: "Low Angle", high: "High Angle", bird: "Bird's Eye", worm: "Worm's Eye", dutch: "Dutch Angle", ots: "Over-the-Shoulder", pov: "POV" };
export const MOVES = {
  static: "Static / Locked-off", pan: "Pan", tilt: "Tilt", dollyIn: "Dolly / Push In", dollyOut: "Dolly / Pull Out", truck: "Truck / Tracking",
  pedestal: "Pedestal", orbit: "Orbit / Arc", crane: "Crane / Jib", handheld: "Handheld", gimbal: "Gimbal / Steadicam", whip: "Whip Pan",
  zoom: "Zoom In / Out", dollyZoom: "Dolly Zoom", roll: "Roll", fpv: "FPV / Fly-through"
};
export const CHARS = {
  locked: "Locked", gentle: "Slow / Gentle", smooth: "Smooth", floating: "Floating", organic: "Natural / Organic",
  energetic: "Energetic", snappy: "Snappy", aggressive: "Aggressive", hyper: "Hyperdynamic", impossible: "Impossible"
};

const S = (size, angle, move, char, extra = {}) => ({ size, angle, move, char, ...extra });

export const STYLES = [
  { id: "corporate", name: "Corporate / Keynote", icon: "🏢", goal: "信頼感・安定感・内容への集中", shots: [S("MS", "eye", "dollyIn", "smooth")] },
  { id: "product", name: "Product / Tech Keynote", icon: "💎", goal: "製品をプレミアムに魅せる", shots: [S("CU", "low", "orbit", "floating")] },
  { id: "cinematic", name: "Cinematic / Film", icon: "🎞️", goal: "物語と心理をカメラで補強", shots: [S("MCU", "eye", "dollyIn", "organic")] },
  { id: "documentary", name: "Documentary", icon: "📹", goal: "その場にいる感覚", shots: [S("MS", "eye", "handheld", "organic")] },
  {
    id: "youtube", name: "YouTube", icon: "▶️", goal: "注意を維持しテンポを作る", dur: 2.4,
    shots: [S("MS", "eye", "static", "energetic", { cut: 1 }), S("MCU", "eye", "dollyIn", "snappy", { cut: 1 }), S("MS", "eye", "static", "energetic", { cut: 1 }), S("WS", "high", "truck", "energetic", { cut: 1 }), S("CU", "eye", "static", "snappy", { cut: 1 })]
  },
  { id: "commercial", name: "Commercial / CM", icon: "📺", goal: "短時間で強い印象", shots: [S("ECU", "low", "dollyOut", "energetic")] },
  { id: "mv", name: "Music Video / MV", icon: "🎤", goal: "ビートと映像を同期", shots: [S("MCU", "low", "orbit", "aggressive")] },
  {
    id: "anime", name: "Anime / Stylized 3D", icon: "🌀", goal: "不可能なカメラ", dur: 4.5,
    shots: [S("ECU", "eye", "dollyZoom", "impossible"), S("MS", "dutch", "orbit", "hyper"), S("EWS", "bird", "roll", "impossible")]
  },
  { id: "game", name: "Game Trailer", icon: "🎮", goal: "スケール・速度・没入", shots: [S("WS", "low", "fpv", "hyper")] }
];
