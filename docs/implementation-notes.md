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

## Eモード「今日やること」スクロール追従の仕組み
- `today-board`（board）: CSS そのまま（ダーク背景）、`overflow:visible` のみ追加
- `today-board-inner`（inner）: sticky **外す**、`height:100%`、`overflow:visible`
- `.section-header`（ヘッダー）: sticky なし → カレンダーヘッダーと同タイミングで流れる
- `#today-tasks`（tc）: `position:sticky; top:headerH(≈38px)` → ヘッダーが消えるにつれ 0→38px のスペースが生まれ固定
- board が page と一緒にスクロールするため「panel の底が自然に流れる」ように見える

## 重要な実装メモ
- `taskState`はlocalStorageに保存（done/pinned/important/jikantai/timeIdx/links）
- 振り返りは3時リセット、frPageIdで重複保存防止
- `day-schedule-content` IDは存在しない→renderAllでnullチェック済み
