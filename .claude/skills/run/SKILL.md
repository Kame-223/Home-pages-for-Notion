---
name: run
description: このスキルは、public/index.html（タスクページ等のUI）の見た目・動作を実際にブラウザで確認したいときに使う。「動かして確認して」「UIを見せて」「ちゃんと動いてるか確認して」のような依頼でトリガーする。ヘッドレスChromium（Playwright）でページを開き、クリック等の操作を行い、スクリーンショットとJS状態を取得する。Macの画面収録・アクセシビリティ権限は一切不要（実ブラウザ・実Notionログインとは別の使い捨てインスタンスを使うため）。
---

# UI動作確認（このプロジェクト専用）

`public/index.html` は単一ファイルのバニラJSアプリで、ビルド手順はない。
確認には Playwright(Python) を使う。Node/npm は不要（このMacには入っていない）。

## 前提（初回のみ）

```bash
python3 -m pip install --user playwright
python3 -m playwright install chromium
```

## 手順

1. `public/` を静的配信する（まだ起動していなければ）：

```bash
cd public && python3 -m http.server 8934 &
```

2. 検証スクリプトを実行する：

```bash
python3 .claude/skills/run/verify_task_page.py
```

デフォルトで `http://localhost:8934/index.html` を開き、タスクページの折りたたみ状態と、
「重要×緊急」パネルをクリックした展開状態、それぞれのスクリーンショットを
`.claude/skills/run/screenshots/` に保存し、主要なCSS計算値・JS状態を標準出力に表示する。
console の error（`console.error` / 未捕捉例外）があれば標準エラーに列挙される。

3. 保存されたスクリーンショット（`1_task_collapsed.png` / `2_task_expanded.png`）を Read で開いて目視確認する。

## できること・できないこと

- できる：実際のChromiumエンジンによる正確なレンダリング、クリックでのJS動作確認（`onclick`ハンドラが本物のクリックイベントとして発火する）、CSS計算値の検証、コンソールエラーの検知
- できない：実際のNotionログイン状態を伴うデータ表示の確認（Notionプロキシ（`api/notion.js`等）を別途起動し、実際にOAuthログインしない限り「Notion接続エラー」等が出る。これは正常）。あなたの実Chromeウィンドウそのものの見え方（拡張機能・実際のウィンドウサイズ等）でもない

## 他のページ・操作を確認したいとき

`verify_task_page.py` は「タスクページを開いて重要×緊急パネルをクリックする」という1パターンの
サンプル実装。別の画面・操作を確認したい場合は、このファイルをコピーして
`page.evaluate(...)` / `page.click(...)` の対象を書き換える。共通の骨格（起動・`showPage`呼び出し・
スクリーンショット・console監視）はそのまま流用できる。

## 終了時

```bash
pkill -f "http.server 8934"
```
