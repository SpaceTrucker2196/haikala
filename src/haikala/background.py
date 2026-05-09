"""Static, full-screen backdrop the animated mandala overlays on top of.

The backdrop is computed once per session and never re-rendered: it does
not breathe, ripple, or spin with the mandala. Visual influences are
Buddhist mandala iconography — the eight-spoked dharmachakra, lotus
petals, vajras, and the cardinal-direction toranas — translated into a
quiet, dim glyph field so the haiku content always reads as foreground.

Structural elements (deterministic per haiku id, sized to the terminal):
  * a sparse star/dot field across the whole console,
  * four faint cardinal axis lines (N/S/E/W) in single-line box-drawing,
  * eight diagonal "spoke" hints at the wheel angles,
  * brighter accent glyphs (tiny lotus / vajra) at the four cardinal
    midpoints, evoking the gates of a vajra fence.
"""

from __future__ import annotations

import math

from .glyphs import COVERED, EMPTY
from .mandala import Cell


# Quiet glyphs for the field of stars/dots. Order matters only insofar as
# the per-cell hash picks one — kept narrow so column spacing stays even.
_BG_FIELD = (
    ("·", "#1a1f2e"),
    ("·", "#1c2030"),
    ("˙", "#161b2a"),
    ("⋅", "#1c2238"),
    ("∙", "#1a1e30"),
)
_BG_ACCENT = (
    ("✦", "#28304a"),
    ("✧", "#2a3252"),
)
_BG_AXIS_COLOR = "#1a2238"
_BG_GATE_COLOR = "#3a4470"
_BG_GATE_GLYPHS = ("❀", "❀", "❀", "❀")  # N, E, S, W — lotus toranas


_FIELD_DENSITY = 0.085   # fraction of cells that get a quiet glyph
_ACCENT_RATE = 0.012     # fraction of cells that get a brighter star


def generate_background(width: int, height: int, seed: int) -> list[list[Cell]]:
    """Build the (height × width) backdrop grid for the given console size.

    Empty cells are returned as `Cell(" ", None, "")` so they fall through
    to the terminal's own background. `seed` (typically `hash(haiku_id)`)
    keeps the pattern stable per session but distinct between haiku.
    """
    width = max(1, width)
    height = max(1, height)
    canvas: list[list[Cell]] = [
        [Cell(" ", None, "") for _ in range(width)] for _ in range(height)
    ]

    # 1) Star/dot field — deterministic hash per cell.
    for y in range(height):
        for x in range(width):
            h = (x * 2654435761) ^ (y * 40503) ^ seed
            r = (h & 0xFFFFFF) / float(0xFFFFFF)
            if r < _ACCENT_RATE:
                ch, color = _BG_ACCENT[(h >> 13) % len(_BG_ACCENT)]
                canvas[y][x] = Cell(ch, color, "dim", static=True)
            elif r < _FIELD_DENSITY:
                ch, color = _BG_FIELD[(h >> 17) % len(_BG_FIELD)]
                canvas[y][x] = Cell(ch, color, "dim", static=True)

    # 2) Faint cardinal-axis lines, like the cross axes of a Buddhist
    #    mandala palace. Drawn through the geometric center.
    cx = width // 2
    cy = height // 2
    for x in range(width):
        # Horizontal axis with a small breath of empty cells so it reads
        # as a guideline, not a bar.
        if x % 3 != 0:
            continue
        if 0 <= cy < height and canvas[cy][x].glyph == " ":
            canvas[cy][x] = Cell("─", _BG_AXIS_COLOR, "dim", static=True)
    for y in range(height):
        if y % 2 != 0:
            continue
        if 0 <= cx < width and canvas[y][cx].glyph == " ":
            canvas[y][cx] = Cell("│", _BG_AXIS_COLOR, "dim", static=True)

    # 3) Diagonal "wheel-spoke" hints at 45° increments. Sparse — every
    #    fourth step — so they whisper rather than dominate.
    if width > 6 and height > 6:
        max_r = min(cx, cy)
        for step in range(0, max_r, 4):
            for ang_deg in (45, 135, 225, 315):
                a = math.radians(ang_deg)
                # Stretch x by 2 to compensate for terminal cell aspect.
                px = cx + round(step * math.cos(a) * 2)
                py = cy + round(step * math.sin(a))
                if 0 <= px < width and 0 <= py < height:
                    if canvas[py][px].glyph == " ":
                        canvas[py][px] = Cell("·", _BG_AXIS_COLOR, "dim", static=True)

    # 4) Four cardinal "gates" — lotus glyphs at the midpoints of each
    #    side, like the toranas of a Buddhist mandala palace.
    gate_north = (cx, max(1, height // 6))
    gate_south = (cx, min(height - 2, height - height // 6))
    gate_east = (max(2, width // 8), cy)
    gate_west = (min(width - 3, width - width // 8), cy)
    for (gx, gy), glyph in zip(
        (gate_north, gate_east, gate_south, gate_west), _BG_GATE_GLYPHS,
    ):
        if 0 <= gy < height and 0 <= gx < width:
            canvas[gy][gx] = Cell(glyph, _BG_GATE_COLOR, "dim", static=True)

    return canvas


def stamp_grid(
    canvas: list[list[Cell]],
    src: list[list[Cell]],
    top: int,
    left: int,
) -> None:
    """Overlay `src` onto `canvas` at (top, left), in place.

    EMPTY source cells fall through (the canvas content shows). COVERED
    cells from the source are written through as well, so wide-emoji
    placement on top of the canvas correctly reserves the second cell.
    """
    h = len(src)
    if h == 0:
        return
    w = len(src[0])
    cH = len(canvas)
    cW = len(canvas[0]) if cH else 0
    for y in range(h):
        cy = top + y
        if cy < 0 or cy >= cH:
            continue
        row = src[y]
        for x in range(w):
            cx = left + x
            if cx < 0 or cx >= cW:
                continue
            cell = row[x]
            if cell.glyph == EMPTY:
                continue
            canvas[cy][cx] = cell


def stamp_text_line(
    canvas: list[list[Cell]],
    text: str,
    row: int,
    style: str = "",
) -> None:
    """Center `text` on `row`. ASCII-only is assumed for headers."""
    if not text:
        return
    h = len(canvas)
    if not (0 <= row < h):
        return
    w = len(canvas[0])
    left = max(0, (w - len(text)) // 2)
    for i, ch in enumerate(text):
        cx = left + i
        if 0 <= cx < w:
            canvas[row][cx] = Cell(ch, None, style)


# Keep the COVERED sentinel available for callers that build src grids.
__all__ = ["generate_background", "stamp_grid", "stamp_text_line", "COVERED"]
