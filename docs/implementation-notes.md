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
- 今日やること / やり残し / 次やること
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

### GTD 種別の選択肢
| 表記 | 意味 | 備考 |
|---|---|---|
| 📥 INBOX | 未分類 | |
| ▶️ IU | 重要×緊急 | 旧「▶️ 次やる」。メインページの「次やること」パネルもこの値を参照 |
| 💫 Iu | 重要×非緊急 | 旧「💫今じゃない」 |
| 💨 iU | 非重要×緊急 | 新規追加（旧システムに対応する選択肢なし） |
| 🗑 iu | 非重要×非緊急（ゴミ箱） | 旧「🗑ゴミ箱」。選択すると自動的に完了扱い |
| 🔥 今すぐやる | 1分以内で片付くタスク | 旧「🔥 今やる」。選択すると自動的に完了扱い |
| 📧 待ち | 対応待ち | 今回のグリッド化の対象外、現状維持 |

ラベルは大文字＝該当（重要/緊急）・小文字＝非該当。該当する文字は太字＋上線（`.gtd-cap`）、非該当は下線（`.gtd-low`）で表示（例：`💫 <b class="gtd-cap">I</b><span class="gtd-low">u</span>`）。

### UI構造
- `.task-gtd-grid`：4象限（IU/Iu/iU/iu）を、個別の枠を持たない1つの大きな枠＋内側の仕切り線（右辺・下辺のborderのみ）で表現。背景`rgba(255,255,255,0.8)`、仕切り線は黒。既存のドラッグ&ドロップ基盤（`GTD_DROP_AREAS`、ポインターイベントベース）はそのまま流用
- `#gtd-slot-imasugu`（`.gtd-area-imasugu`）：グリッド下の横長スロット。炎の背景画像（`public/backgrounds/imasugu-flame-v2.png`）のみで、ボタン・ラベルなし。ドロップされたタスクは即座に「🔥 今すぐやる」に分類され完了扱いになる、展開・一覧機能を持たない純粋なドロップ地点
- `gtd-slot-project`：既存のPROJECTスロットは変更なし、GTD 種別とは無関係の別軸として維持

### 展開（一覧表示）の仕組み（2026-07 刷新、暗幕方式は撤去済み）
最初のバージョンはINBOX列・GTD列双方の座標を`getBoundingClientRect()`で測定して`position:fixed`に焼き付け、INBOXを1件ずつのページ送りUIに変形させる複雑な仕組みだった。次に`z-index`で暗幕より前面に浮かせる方式に変えたが、`.task-gtd-col`の`position:sticky`が独自のスタッキングコンテキストを作りz-indexが効かず、パネルごと操作不能になるバグが発生。**運用要件（展開パネルからINBOXへタスクをドラッグして戻す）にも合わないため、暗幕そのものを撤去**し、現在は以下の形になっている。

- `.task-gtd-col`内に常設・普段非表示の`#gtd-expand-panel`を1つ用意。展開時は`task-gtd-col`に`.gtd-expanded`クラスを付与し、CSSで「4象限グリッド/今すぐやる/PROJECTを隠し、`#gtd-expand-panel`を表示」に切り替えるだけ（座標測定・z-index操作なし）
- 暗幕（`#task-overlay`）は完全撤去。代わりに`document.body`へ`.gtd-expanded-mode`を付与し、**サイドバー・バナー・下部バーだけ**を`filter:brightness(0.45)`で減光（`pointer-events:none`で誤操作も防止）。task-page-grid（INBOX・展開パネル）には一切オーバーレイを被せないため、z-index競合が構造的に起きない
- INBOXは展開中も変形させず常時操作可能。表示だけ`.inbox-simplified`クラスで「INBOX」というタイトルのみに簡略化する（一覧は隠すが、ドロップ判定は`GTD_DROP_AREAS`のコンテナ矩形判定のままなので影響を受けない）。展開パネルのタスクカードを既存のドラッグ機構でINBOXへドラッグすれば、GTD 種別が📥INBOXに戻る
- 閉じる操作はEscapeキー、またはサイドバー・バナー・下部バー（減光された部分）のクリックで`closeOverlay()`が呼ばれる。明示的な閉じるボタンは無い
- `_OVERLAY_GTD_MAP`/`_overlayListCounts`：展開一覧のGTD値対応表とページネーション件数（impurg/imp/urg/trashの4区分。imasuguは展開機能自体を持たないため対象外）

## 未完了・継続中
- カレンダー課題2: Deleteキーでイベント削除（未実装）
- カレンダー課題3: タスクをドラッグしてカレンダーに追加（未実装）

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
