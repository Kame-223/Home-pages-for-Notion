---
name: notion-api-safety
description: このスキルは、Notion APIのプロパティ定義（特に properties.<name>.select.options / status.options）をPATCHする前、api/notion.jsを編集する前、select・statusのoptionを追加・削除・リネームする前に必ず参照する。過去にoption配列の全上書きPATCHにより既存ページのデータが消失した事故があり、その再発防止の安全手順と既知の失敗パターンを記載している。「Notionのoptionを変更したい」「GTD種別の選択肢を増やしたい」「select/statusプロパティを編集したい」のような依頼でトリガーする。
---

# Notion API 安全ガイド

このスキルは、Notionのプロパティ操作で実際に発生したデータ消失事故を受けて作られた。
select/statusのoptionsをPATCHで扱う作業に着手する前に、必ずこのファイルを読む。

## 既知の問題（失敗ログ）

**この節は、実際に起きた不具合・誤りを見つけるたびに一行足していく。**

- 2026-07-12：Notionのselectプロパティのoptionをリネームしようとして `properties.<name>.select.options` をPATCHしたところ、既存option（idを指定したもの）は名前が変わらず無視される一方、配列に含めなかった既存optionは削除され、それを参照していた全ページの値が空になった。**select optionの配列PATCHは「完全上書き」であり、含めなかった既存optionは黙って削除される。またid一致のoptionは名前変更が反映されない（rename非対応）。**

## 安全な手順（option追加・削除・リネーム時）

1. 新option追加：既存の全option＋新規分を含む配列でPATCHする（差分は純粋追加のみになる）
2. 該当ページを1件ずつ新optionへ付け替える（page単位のPATCH）
3. 全ページで旧optionの参照が0件になったことを確認する
4. 旧optionだけを除いた配列でPATCHして削除する

リネームは実質「追加→付け替え→削除」でのみ安全に行える。idを指定した直接リネームは反映されないため行わない。
