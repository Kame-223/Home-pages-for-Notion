#!/usr/bin/env python3
"""
Playwright smoke-test driver for the Task page (public/index.html).

Usage:
    python3 verify_task_page.py [--url http://localhost:8934/index.html] [--out-dir DIR]

Requires: `pip install playwright && playwright install chromium` (one-time).
Serve the file first, e.g.:
    cd public && python3 -m http.server 8934 &

This does NOT need any macOS permission (no screen recording, no
accessibility access) — it drives an invisible, separate Chromium instance
via Playwright, not the user's real browser/session. It won't have real
Notion login state, so data-dependent panels will show their
loading/error states; this checks layout, CSS, and click-driven JS
behavior, not live Notion data.
"""
import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8934/index.html")
    parser.add_argument("--out-dir", default=str(Path(__file__).parent / "screenshots"))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: console_errors.append(str(exc)))

        page.goto(args.url, wait_until="load")
        page.wait_for_function("typeof showPage === 'function'")

        page.evaluate("showPage('task')")
        page.wait_for_selector("#task-content", state="visible")

        page.screenshot(path=str(out_dir / "1_task_collapsed.png"))

        info1 = page.evaluate("""
            () => ({
                theme: document.documentElement.dataset.theme,
                toggleVisible: getComputedStyle(document.getElementById('theme-toggle-btn')).display,
                inboxBg: getComputedStyle(document.getElementById('task-inbox-col-wrap')).backgroundColor,
                impurgBg: getComputedStyle(document.getElementById('gtd-slot-impurg')).backgroundColor,
                impurgText: document.getElementById('gtd-slot-impurg').querySelector('.gtd-panel-name').innerText,
            })
        """)
        print("collapsed state:", info1)

        page.click("#gtd-slot-impurg")
        page.wait_for_function("typeof overlayMode !== 'undefined' && overlayMode === 'impurg'")

        page.screenshot(path=str(out_dir / "2_task_expanded.png"))

        info2 = page.evaluate("""
            () => ({
                inboxExpandSticky: document.getElementById('task-inbox-col-wrap').classList.contains('expand-sticky'),
                inboxListDisplay: getComputedStyle(document.getElementById('task-inbox-list')).display,
                inboxTitleText: document.querySelector('.task-inbox-expand-title').innerText,
                headerText: document.getElementById('gtd-slot-impurg').querySelector('.gtd-slot-header').innerText,
                panelBg: getComputedStyle(document.getElementById('gtd-slot-impurg')).backgroundColor,
            })
        """)
        print("expanded state:", info2)

        browser.close()

    if console_errors:
        print("\nconsole errors:", file=sys.stderr)
        for e in console_errors:
            print(" -", e, file=sys.stderr)

    print(f"\nscreenshots saved to {out_dir}")


if __name__ == "__main__":
    main()
