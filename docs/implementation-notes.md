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

## カラー設定（2026-06 リニューアル済み）
### AREAタグ・カードボーダー・グループヘッダー
- 課題 → `#9070C0`（紫）
- 個人 → `#F8D8B0`（ピーチ）※旧ICUを統合
- 生活 → `#C0E0C0`（ミント）※旧カナダを統合

### SUBJECTタグ
- ELA（ER4/S&L4/RCA/ATS4/ARW含む）→ `#A0C8E8`（スカイブルー）
- それ以外のSUBJECT → グレー統一（`tag-gray`）

### カレンダーイベント色（優先順位順）
1. 当日行動（KIND or calName or title）→ `#C4C4C4`（薄いグレー）
2. ELA/ER4/S&L4/RCA/ATS4/ARW → `#A0C8E8`
3. 教育原理/憲法/社会学/PE → `#C0C0E8`
4. calNameに「生活」「寮」を含む → `#C0E0C0`
5. その他（個人カレンダー） → `#F8D8B0`

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
