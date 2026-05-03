"""Small helpers for working with terminal glyph cells."""

from __future__ import annotations

from .symbols import is_wide

EMPTY = " "
COVERED = ""  # sentinel meaning "the previous (wide) cell extends here"


def visual_width(glyph: str) -> int:
    if glyph == COVERED:
        return 0
    return 2 if is_wide(glyph) else 1
