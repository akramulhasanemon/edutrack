"""EduTrack — Academic Intelligence & Workspace Application.

Modern live bioluminescent bubble-glass UI for academic trajectory modeling,
CGPA forecasting, AI advisory, attendance tracking, and transcript reporting.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    """Launch the EduTrack desktop application."""
    try:
        from desktop_app import enable_high_dpi_awareness
        enable_high_dpi_awareness()
    except Exception:
        pass

    if "--legacy" in sys.argv:
        print("Notice: Launching legacy interface as requested by --legacy flag...")
        try:
            import tkinter as tk
            from UI.main_window import EduTrackDashboard
            root = tk.Tk()
            app = EduTrackDashboard(root)
            root.mainloop()
            sys.exit(0)
        except Exception as exc:
            print(f"Notice: Legacy interface unavailable ({exc}). Continuing with modern interface...")

    try:
        import desktop_app
        desktop_app.main()
    except Exception as exc:
        print(f"Error launching modern EduTrack interface: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
