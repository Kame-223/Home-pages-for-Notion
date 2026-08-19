# 実装メモ（旧CLAUDE.md引き継ぎ内容）

**このファイルはコード実装の現状記録。「なぜこう作るか」は PHILOSOPHY.md、「何を作るか」は docs/chapter*.md を参照。**

## プロジェクト概要
ADHDの大学生（ICU）の自分専用ホームページ。NotionをDBとして使い、Vercel上で公開。

- **GitHub**: Kame-223/Home-pages-for-Notion
- **Vercel**: https://home-pages-for-notion-n5f9.vercel.app
- **デプロイ**: git push → Vercel自動（1〜2分）
- **メインファイル**: `public/index.html`（全コード1ファイル）
- **APIプロキシ**: `api/notion.js`、`api/fetch-title.js`

## Notion DB
- タスク: `3294c1ec140d838499ae0131fc67976d`
- 振り返り: `76f4c1ec140d8375aa5b81c589f9b247`（タイトルプロパティ名は「名前」）
- プロジェクト: `8584c1ec140d83b29e26019b60fe7a3e`

## 実装済み機能（完成）
- サイドバー・哲学バナー・日時ウィジェット
- 選択モード / 実行モード切替
- 進捗バー（ピン済みタスクのみ）
- 今日やること / IMPORTANT URGENT / important URGENT / PROJECT（箱のみ・後述）
- タスクカード（AREA・SUBJECT・ELA・DEADLINE・LINKS・時間帯・時間見積もり）
- Importantモード（赤背景・確認ダイアログ・締切カウントダウン強化）
- 締切：日時まで設定可・カウントダウン表示・Important時は秒数まで
- クマボタン（リンク一覧・favicon＋タイトル自動取得）
- ＋INBOX → Notion保存
- 次やるフィルター（プロパティ順 / 締切順）
- 振り返り（気分・体調・自動保存・3時リセット・ドラゴン）
- Googleカレンダー（個人＋ICU・色分け・時間帯背景）
- 背景：1日3回切替（6時・12時・18時）
- **Eモード「今日やること」スクロール追従**（完成）

## カラー設定（2026-07 OFFICIAL/PRIVATEへ改称・統合）
### AREAタグ・カードボーダー・グループヘッダー
- OFFICIAL（旧「課題」）→ `#9070C0`（紫）
- PRIVATE（旧「個人」＋「生活」を統合。生活はNotion側で個人へ再割当て済み）→ `#F8D8B0`（ピーチ）※旧ICUを統合

### SUBJECTタグ
- ELA（ER4/S&L4/RCA/ATS4/ARW含む）→ `#A0C8E8`（スカイブルー）
- それ以外のSUBJECT → グレー統一（`tag-gray`）

### カレンダーイベント色（優先順位順）
1. 当日行動（KIND or calName or title）→ `#C4C4C4`（薄いグレー）
2. ELA/ER4/S&L4/RCA/ATS4/ARW → `#A0C8E8`
3. 教育原理/憲法/社会学/PE → `#C0C0E8`
4. calNameに「生活」「寮」を含む → `#C0E0C0`
5. その他（個人カレンダー） → `#F8D8B0`

## タスク分類システム（2026-07 4象限グリッド化）
タスクページ右側のGTD分類UIを、アイゼンハワーマトリクス（重要×緊急）ベースの2×2グリッドに再構築。単一のNotionプロパティ「GTD 種別」（status型）の選択肢を差し替える形で実装（新規プロパティは追加していない）。

### GTD 種別の選択肢（2026-07 装飾なしラベルへ変更）
| 表記 | 意味 | 備考 |
|---|---|---|
| 📥 INBOX | 未分類 | |
| ▶️ IMPORTANT URGENT | 重要×緊急 | 旧`▶️ IU`。メインページの「IMPORTANT URGENT」パネルもこの値を参照 |
| 💫 IMPORTANT urgent | 重要×非緊急 | 旧`💫 Iu` |
| 💨 important URGENT | 非重要×緊急 | 旧`💨 iU`。メインページの「important URGENT」パネルもこの値を参照 |
| 🗑️important urgent | 非重要×非緊急（ゴミ箱） | 旧`🗑 iu`。選択すると自動的に完了扱い |
| 🔥 今すぐやる | 1分以内で片付くタスク | 選択すると自動的に完了扱い |
| 📧 待ち | 対応待ち | グリッド化の対象外、現状維持 |

Notionの選択肢名は装飾（太字・打ち消し線）を持てないため、大文字/小文字だけでは重複扱いになる問題を避けつつ意味を伝えるために、絵文字を残したまま単語をそのまま並べる表記（`IMPORTANT URGENT`など）に変更した。アプリ側の表示（タスク詳細ページの4象限グリッド・メインページのパネル見出し）では、大文字＝該当・小文字＝非該当を太字/打ち消し線（`.gtd-cap`/`.gtd-low`）で視覚的に強調している。

### UI構造
- `.task-gtd-grid`：4象限を2×2 CSS Gridで配置。既存のドラッグ&ドロップ基盤（`GTD_DROP_AREAS`、ポインターイベントベース）をそのまま流用
- `.gtd-area-imasugu`：グリッド下の横長スロット（「🔥 今すぐやる」用）
- `gtd-slot-project`：既存のPROJECTスロットは変更なし、GTD 種別とは無関係の別軸として維持
- `_OVERLAY_SLOTS`/`_OVERLAY_GTD_MAP`/`_overlayListCounts`：展開オーバーレイの表示・ページネーションを5区分（impurg/imp/urg/trash/imasugu）+ projectに対応する形で汎用化

## メインページ 3パネル構成（2026-07 持ち越しパネルの解体）
`chapter5-mainpage.md` 5.5節「持ち越しを持たない」方針に沿って、専用の「🔄 持ち越し」パネルを廃止。期限切れ・前セッションでピンしたまま未完了のタスクは、GTD分類に応じて以下のパネルへ自然に現れる形にした。

- **IMPORTANT URGENT**（旧「▶️ 次やること」パネルを改名。`renderNextList()`）：GTD種別が`▶️ IMPORTANT URGENT`のタスク。デフォルト5件+もっと見る、エリア/科目別グルーピング、プロパティ/締切フィルター切替は既存のまま
- **important URGENT**（新設。`renderNiuList()`）：GTD種別が`💨 important URGENT`のタスク。デフォルト3件+もっと見る、エリア別グルーピング
- **PROJECT**（新設・箱のみ）：ヘッダー表示のみで、マイルストーン連携などのデータ取得ロジックは未実装（下記「未完了・継続中」参照）

完了しなかったままセッションを跨いだタスクの「実行時間帯（朝/昼/夜）自動リセット」処理は、パネル表示とは無関係の判定として`renderAll()`内に残している（持ち越しパネルの有無に関係なく機能する）。

## 未完了・継続中
- カレンダー課題2: Deleteキーでイベント削除（未実装）
- カレンダー課題3: タスクをドラッグしてカレンダーに追加（未実装）
- PROJECTパネル: マイルストーン（`_loadMilestones()`）と紐づけた実データ表示（未実装。現在は見出しのみの箱）

## 選択・実行モードのスケジュールパネル統一（2026-07）
以前は選択モードと実行モードでスケジュールパネルの見た目・挙動が大きく異なっていた（選択モード=30分刻み/20px・画面内に収めてスクロール、実行モード=15分刻み/9px・`contentHeight:'auto'`で全スロットを展開しページ自体が伸びる）。これを次のように統一した。

- スロット刻みは両モードとも15分（`slotDuration:'00:15:00'`）、1スロット9px
- 高さは両モードとも「画面内に収めて内部スクロール」方式（旧・選択モード方式）に統一。`.schedule-col`は常に透明なレイアウト用ラッパー、`.sched-sticky`が常に見た目の箱（背景・枠線・`position:sticky`）を担う
- 横幅は選択モードの中央80px列（朝昼夜の玉）を廃止したことで両モードとも揃った（後述）
- 上記の統一により、旧・実行モード専用の「今日やることパネルがページの長いスクロールに追従する」仕組み（`applyExecFixed()`/`_cacheExecScrollRange()`/`resetExecFixed()`等）は不要になり削除した。実行モード開始時に現在時刻へ合わせる処理は、ページ全体のスクロールではなく`.fc-scroller`の`scrollTop`を直接設定する方式に置き換えた
- レイアウト計算の関数は`applySModeCalLayout()`から`applyCalLayout()`に改名し、モードを問わず呼べるようにした

## 朝昼夜の玉の移動（2026-07）
選択モード中央の玉専用80px列を廃止し、スケジュールパネル左端の時刻軸（`.fc-timegrid-axis`、幅50px→68px）上にオーバーレイ表示する形に変更した（`#s-orb-col`は`.sched-sticky`内、`#fc-container`の兄弟要素）。玉のサイズは62px→40pxに縮小。位置計算（`updateOrbZoneOffsets()`）は新しい15分刻み/9px設定に合わせて再計算するよう修正済み。

## 3パネル（IMPORTANT URGENT / important urgent / PROJECT）の排他表示・巡回チェック（2026-07）
`chapter5-mainpage.md` 5.3〜5.4節の思想を踏襲しつつ、実装は一部異なる判断をしている（詳細は同ファイルの追記を参照）。

- 3パネルのうち常に1つだけ中身が見える（`openGtdSubPanel`、`openGtdPanel()`/`applyGtdPanelVeils()`）。他の2つは完全に隠すベール（`.gtd-veil`）がかかる
- 各パネルには「未確認」を示す黒丸（`.gtd-unseen-dot`）が付き、一度開くと消える。`localStorage`（`gtdPanelSeen`）で永続化し、日次リセットはしない
- important urgentパネルのみ、当日締切のI×Uタスクがある日は黒丸を消した先にもう一段階の確認ボタン（`.niu-gate`、`confirmNiuGate()`）を挟む。この確認は`getFurikaeriDate()`基準の日付キー付き`localStorage`（`niuGateConfirmed_<日付>`）で当日中は再表示しない
- 締切当日判定は`isTaskDeadlineToday()`として独立関数化（旧`renderCard()`内のインラインIIFEを共通化）

## タスク選択時の白枠線バグ修正（2026-07）
`.task-card.confirmed-dim`が`opacity:0.4`を要素全体にかけていたため、`border-color:#fff`も一緒に薄くなっていた。`opacity`をカードの子要素（`.pin-badge`/`.tag-row`/`.card-lower`）側に移し、カード自身の枠線・背景は薄まらないようにした。

## 重要な実装メモ
- `taskState`はlocalStorageに保存（done/pinned/important/jikantai/timeIdx/links）
- 振り返りは3時リセット、frPageIdで重複保存防止
- `day-schedule-content` IDは存在しない→renderAllでnullチェック済み

## 締切タグ表記（2026-07 英語化・色簡略化）
`deadlineTag()`のラベルを英語表記に変更（今日→Today、明日→Tomorrow、期限切れ→Overdue等）。日数が正確な範囲（今日・明日・2〜7日後/前）はそのまま、週・月単位の目安になる範囲（1週間後〜2ヶ月後、期限切れ側の1週間前・2週間前）は「以上」の意味で`+`を付けて表記（例: `1 Week+`, `2 Months+`）。色分けも今日/明日/期限切れ=赤（`tag-red`）・それ以外=グレー（`tag-gray`）の2色に簡略化（`tag-amber`/`tag-blue`はCSS定義のみ残存、未使用）。Importantタスクは従来通り`tag-imp-dl`。

## QNH非表示化（2026-08）
「決めること自体がストレスだった」という理由で、QNH（Quick/Normal/Heavy）関連のUI（タスクカードの時間タイプボタン、集中モードの見積もり選択など）を全て非表示にした。`taskState`の`timeType`等の保存データ・保存処理自体は削除していない（将来の復活・既存データ保護のため）。あわせて、構想のみで実装・設計書ともに存在していなかった「AIが当日の気分を見てQNHをおすすめする」機能は、着手前の時点で不採用と決定した（今後も追加しない）。

## AREAプロパティのTASK/WISH改名とタスク/ウィッシュ分類の再設計（2026-08）
`docs/chapter3-planning.md`・`docs/chapter4-projects.md`の追記（2026-08）も参照。

### Notion側の変更
- 「エリア」プロパティ（select型）の選択肢をOFFICIAL/PRIVATE→TASK/WISHへリネーム。`.claude/skills/notion-api-safety/SKILL.md`の安全手順（新option追加→ページ付け替え→旧option参照0件確認→旧option削除）に従って実施。色（TASK=`#9070C0`紫、WISH=`#F8D8B0`ピーチ）は維持
- 新規プロパティ「WISH 種別」（select型：📥 INBOX/Next/Plan/Dream）を追加。既存の「GTD 種別」とは完全に独立しており、TASK側の自動化ロジック（今すぐやる/ゴミ箱の自動完了など）に影響しない

### TASK画面（既存4象限グリッド）をTASK専用に絞り込み
- 「次やる」（`getNextTasks()`）・「important urgent」（`getNiuTasks()`）・INBOX列・4象限バッジ集計（`gtdCounts`）に、それぞれ`getProp(t,'エリア') !== 'WISH'`のフィルタを追加。エリア未設定のタスクは（明示的にWISHにされない限り）引き続きTASK側に表示される
- 4象限展開オーバーレイの汎用化：`_OVERLAY_GTD_MAP`/`_OVERLAY_PROP`/`_OVERLAY_KEYS`/`_OVERLAY_SLOTS`にWISH側のキー（`wnext`/`wplan`/`wdream`）を追加し、`openOverlay()`/`closeOverlay()`が対象プロパティ（GTD 種別／WISH 種別）に応じてTASK側・WISH側どちらのINBOX列・分類先列を操作するか自動判定するようにした

### WISH画面（新規・#wish-content）
TASK画面と同じ左右分割レイアウト（左：WISH専用INBOX、右：分類先）を採用。分類先は次の3段構成：
1. **Next/Plan/Dreamの逆三角クラスター**（`.wish-tri-grid`）：左上NEXT・右上PLAN・下DREAM（大）の3枚を`clip-path`で三角形に切り抜いたdiv。TASK画面の4象限と同じ「クリックで展開」方式（`openGtdQuadrant('wnext'|'wplan'|'wdream')`）で、普段はラベル＋件数バッジのみ、クリックで該当パネルが列全体に展開しカード一覧を表示する。
   - `clip-path`で切り取った斜め辺には`border`が描画されないCSS上の制約があるため、境界線は`pointer-events:none`の装飾用SVG（`.wish-tri-borders`、対角線2本の`<line>`）で別途描画し、外枠は`.wish-tri-grid`自身の`border`で描く。当たり判定・展開パネルへの差し替えは従来通りdiv自身が担う（`elementFromPoint`ベースの`_dropAreaAtPoint()`はclip-pathで切り取られた領域をヒットしないため、3枚が矩形として重なっていても正しく判別できる）
   - 展開中（`.expand-target`）はclip-pathを解除し列全体に広がるよう`.wish-tri.expand-target`で上書き。装飾用SVGの境界線も`:has()`セレクタで非表示にする
2. **今すぐやる（炎パネル）**：TASK画面と同じ背景画像。ドロップした瞬間に完了扱いにする（`completeWishTask()`、`ステータス`→`完了`）
3. **TASKパネル**：ドロップすると`エリア`を`TASK`に変更し、WISHから完全に外れてTASK画面側へ移る（`moveWishToTask()`）

分類（`setWishKind()`）はGTD側の`setGtdKind()`と独立した専用関数とし、TASK側のような自動完了などの特殊挙動は持たせていない。

### ドラッグ&ドロップ機構の汎用化
従来TASK専用だった「クリックで持ち上げ→クリックで確定」のGTD分類機構（`initGtdDrag()`/`updateGtdDropHighlight()`/`finishGtdDrag()`）を、対象プロパティ（`gtdDragProp`）とドロップ先定義（`gtdDragAreas`）を持ち回る形に一般化。ピックアップ元（`#task-content`/`#wish-content`/`#triage-content`のどのカードか）に応じて`GTD_DROP_AREAS`/`WISH_DROP_AREAS`/`TRIAGE_DROP_AREAS`のいずれかを選択する。ドロップ先の`action`フィールド（`complete`＝即完了、`toTask`＝AREAをTASKへ、`setArea`＝AREAを指定値へ）で、単純なプロパティ差し替え以外の特殊挙動を`finishGtdDrag()`内で分岐させている。

### INBOX仕分け画面（新規・#triage-content、サイドバー「Sort」）
GTD種別=`📥 INBOX`かつエリア未設定のタスクだけを対象に、左にINBOX一覧、右にTASK/WISHの振り分け先（大きな2枚のパネル）を配置。既存のクリック持ち上げ→クリック確定の分類機構をそのまま流用し、`エリア`プロパティを直接設定する（`setTriageArea()`）。振り分け後は仕分け画面から消え、TASK画面またはWISH画面の既存INBOX列にそのまま現れる（両画面とも別途再描画するのみで、この画面自体は行き先には関与しない）。

## 今すぐやるパネルの白背景バグ修正・WISH側への展開（2026-08）
ライトモードで`.task-gtd-area.gtd-drop-active`が背景を白へ差し替える通常のドラッグハイライトが、炎の背景画像を持つ「今すぐやる」パネル（`#gtd-slot-imasugu`）にもそのまま適用され、ドラッグ中に画像が真っ白に隠れてしまっていた。`html[data-theme="light"] #task-gtd-col #gtd-slot-imasugu.gtd-drop-active`に対して背景色を透明化し背景画像を維持する専用ルールを追加。WISH画面の`#wish-slot-imasugu`にも同様のルールを適用し、また炎の背景画像自体（`#gtd-slot-imasugu`にのみ効いていた`background-image`指定）も`#wish-slot-imasugu`に対して有効になるよう修正した（元々WISH側には未適用でパネルが白いままだった）。

## タスクページ右パネルの常時固定表示（2026-08）
`.task-gtd-col`が`position:sticky`のとき、左INBOX列が短い日に「`.task-page-grid`の下端に追いついて一緒にスクロールしてしまう」不具合があったため、常に`position:fixed`で画面上の同じ位置に固定する`applyGtdColFixed()`を追加（左INBOX列の現在位置を毎回測定し、その右隣にfixedで重ねる）。展開時（`openOverlay()`）の上部余白も、通常時と同じ`12px`に統一した。

## 表示件数の自動繰り上げ（バックフィル）廃止（2026-08）
INBOX列・IMPORTANT URGENTパネル・important URGENTパネル・4象限展開パネルの4箇所で採用していた「件数ベースの上位N件選択」を、「今表示している具体的なタスクIDの集合（pinned ids）」ベースの選択に置き換えた。表示中の1枚を完了・移動させて母数が減っても、次点のカードが自動で繰り上がって表示件数が埋まる動きをなくし、「もっと見る」を明示的に押したときだけ表示件数が増えるようにした。折りたたみ（▲）を押すとpinned idsをクリアし、次回描画時に先頭N件から再スタートする。

## その他のUI調整（2026-08）
- **PROJECTパネルの簡略化**：個別プロジェクトの一覧表示をやめ、パネル中央に「PROJECT」ラベルのみを表示する形に変更（`.gtd-area-project-simple`/`.gtd-slot-header-centered`）。同じスタイルをWISH画面の「TASK」パネルにも流用
- **タスクカードの2本指クリックメニュー**：TASK画面のカードのみを対象に、2本指クリック（`contextmenu`イベント）で「完了にする」「削除する」の2ボタンを持つ簡易メニュー（`.task-ctx-menu`、`openTaskCtxMenu()`）を表示する。「削除する」はNotionからの削除ではなく、GTD種別を「非重要×非緊急（ゴミ箱）」へ分類する従来の完了扱いと同じ処理
