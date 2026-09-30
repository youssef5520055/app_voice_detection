from __future__ import annotations

import sys
from pathlib import Path


def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return base / relative


def default_dialog_dir() -> str:
    desktop = Path.home() / "Desktop"
    if desktop.exists():
        return str(desktop)
    return str(Path.home())
