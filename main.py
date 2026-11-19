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
    if "--legacy" in sys.argv:
        print("Notice: Launching legacy interface as requested by --legacy flag...")
        import legacy_main
        sys.exit(0)

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
