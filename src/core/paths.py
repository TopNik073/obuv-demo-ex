from __future__ import annotations

import sys

from pathlib import Path


def _frozen() -> bool:
    return bool(getattr(sys, 'frozen', False))


def bundle_root() -> Path:
    if _frozen():
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass is not None:
            return Path(meipass)
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent.parent


def config_root() -> Path:
    if _frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent.parent
