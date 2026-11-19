"""EduTrack Next-Generation Desktop Application.

Runs the pixel-perfect glassmorphism UI powered by Microsoft Edge WebView2
and connects it directly to the local SQLite database and AI services.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import webview

from desktop_bridge import DesktopBridgeAPI


def build_app_html(web_ui_dir: Path) -> str:
    """Bundle HTML, CSS, offline Chart.js, and app controller into a unified document."""
    index_path = web_ui_dir / "index.html"
    if not index_path.exists():
        raise FileNotFoundError(f"Missing UI entry template at {index_path}")

    html_content = index_path.read_text(encoding="utf-8")

    chart_path = web_ui_dir / "assets" / "chart.umd.min.js"
    if chart_path.exists():
        chart_js = chart_path.read_text(encoding="utf-8")
        html_content = html_content.replace(
            '<script src="assets/chart.umd.min.js"></script>',
            f"<script>{chart_js}</script>",
        )

    app_js_path = web_ui_dir / "app.js"
    if app_js_path.exists():
        app_js = app_js_path.read_text(encoding="utf-8")
        html_content = html_content.replace(
            '<script src="app.js"></script>',
            f"<script>{app_js}</script>",
        )

    return html_content


def main() -> None:
    # Ensure working directory is project root
    project_root = Path(__file__).resolve().parent
    os.chdir(project_root)

    web_ui_dir = project_root / "web_ui"
    try:
        app_html = build_app_html(web_ui_dir)
    except Exception as exc:
        print(f"Error preparing EduTrack interface: {exc}", file=sys.stderr)
        sys.exit(1)

    api = DesktopBridgeAPI()

    window = webview.create_window(
        title="EduTrack | Academic Intelligence & Workspace",
        html=app_html,
        js_api=api,
        width=1340,
        height=860,
        min_size=(1060, 680),
        background_color="#060d1a",
        text_select=True,
    )
    api.set_window(window)

    # Start PyWebView desktop GUI
    webview.start(debug=False)


if __name__ == "__main__":
    main()
