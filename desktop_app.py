"""EduTrack Next-Generation Desktop Application.

Runs the pixel-perfect glassmorphism UI powered by Microsoft Edge WebView2
and connects it directly to the local SQLite database and AI services.
Optimized for multi-DPI screens (100%, 125%, 150%, 175%, 200%) and all laptop/desktop resolutions.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import webview

from desktop_bridge import DesktopBridgeAPI


def enable_high_dpi_awareness() -> None:
    """Ensure Windows desktop scaling (100%, 125%, 150%, 200%) renders razor sharp without blur."""
    if sys.platform != "win32":
        return

    import ctypes

    # 1. Windows 10 Creators Update (1703) and later: Per-Monitor V2
    try:
        # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
        res = ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        if res:
            return
    except Exception:
        pass

    # 2. Windows 8.1 and Windows 10 (pre-1703): Per-Monitor
    try:
        # PROCESS_PER_MONITOR_DPI_AWARE = 2
        res = ctypes.windll.shcore.SetProcessDpiAwareness(2)
        if res == 0:
            return
    except Exception:
        pass

    # 3. Windows Vista / 7 fallback: System DPI Aware
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def get_optimal_window_size(default_w: int = 1320, default_h: int = 840) -> tuple[int, int]:
    """Calculate the best initial window width & height based on usable screen work area.

    Guarantees the window fits comfortably on 1366x768 screens and 1080p screens with
    125%, 150%, or 175% Windows display scaling without overflowing the taskbar or edges.
    """
    work_w = None
    work_h = None

    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            rect = wintypes.RECT()
            # SPI_GETWORKAREA = 0x0030 (returns usable screen area excluding taskbar)
            if ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):
                work_w = rect.right - rect.left
                work_h = rect.bottom - rect.top
        except Exception:
            pass

    if not work_w or not work_h:
        try:
            if hasattr(webview, "screens") and webview.screens:
                screen = webview.screens[0]
                work_w = getattr(screen, "width", None)
                work_h = getattr(screen, "height", None)
        except Exception:
            pass

    if work_w and work_h:
        # Leave a clean margin of at least 40px width and 50px height from the work area
        target_w = min(default_w, max(920, int(work_w * 0.92)))
        target_h = min(default_h, max(580, int(work_h * 0.90)))

        # Never exceed usable work area bounds
        if target_w > (work_w - 20):
            target_w = max(900, work_w - 30)
        if target_h > (work_h - 40):
            target_h = max(560, work_h - 50)

        return target_w, target_h

    return default_w, default_h


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
    # Set Windows High-DPI awareness before creating any window
    enable_high_dpi_awareness()

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

    # Calculate optimal window dimensions to fit any laptop / screen scale
    initial_w, initial_h = get_optimal_window_size(1320, 840)

    window = webview.create_window(
        title="EduTrack | Academic Intelligence & Workspace",
        html=app_html,
        js_api=api,
        width=initial_w,
        height=initial_h,
        min_size=(900, 560),
        background_color="#060d1a",
        text_select=True,
    )
    api.set_window(window)

    # Start PyWebView desktop GUI
    webview.start(debug=False)


if __name__ == "__main__":
    main()
