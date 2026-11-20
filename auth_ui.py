"""EduTrack Authentication Entry Point.

Seamlessly launches the modern EduTrack bioluminescent bubble-glass interface.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Launch the EduTrack authentication & workspace interface."""
    try:
        import desktop_app
        desktop_app.main()
    except Exception as exc:
        print(f"Error launching modern EduTrack interface: {exc}", file=sys.stderr)
        sys.exit(1)


class EduTrackLogin:
    """Compatibility shim for any external references to EduTrackLogin."""

    def __init__(self, *args, **kwargs):
        pass

    def mainloop(self):
        main()


if __name__ == "__main__":
    main()
