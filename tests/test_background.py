"""Tests for the static fullscreen backdrop."""

from __future__ import annotations

from haikala.background import generate_background, stamp_grid, stamp_text_line
from haikala.mandala import Cell


def test_backdrop_size_matches_console_dimensions():
    bg = generate_background(80, 24, seed=1234)
    assert len(bg) == 24
    assert all(len(row) == 80 for row in bg)


def test_backdrop_is_deterministic():
    a = generate_background(60, 18, seed=42)
    b = generate_background(60, 18, seed=42)
    assert [
        [(c.glyph, c.color, c.style) for c in row] for row in a
    ] == [
        [(c.glyph, c.color, c.style) for c in row] for row in b
    ]


def test_backdrop_seed_changes_pattern():
    """Different seeds must produce visibly different fields. Compare
    the full (glyph, color, style) tuples since dim color variants
    sometimes coincide in glyph alone for adjacent seeds."""
    a = generate_background(60, 18, seed=1)
    b = generate_background(60, 18, seed=99999)
    a_tuples = [(c.glyph, c.color, c.style) for row in a for c in row]
    b_tuples = [(c.glyph, c.color, c.style) for row in b for c in row]
    assert a_tuples != b_tuples


def test_backdrop_marks_cells_static():
    """Every non-empty backdrop cell must have static=True so hue cycling
    leaves the backdrop alone."""
    bg = generate_background(60, 18, seed=7)
    for row in bg:
        for c in row:
            if c.glyph != " ":
                assert c.static is True, f"backdrop cell {c!r} is not static"


def test_backdrop_handles_tiny_console():
    """Very small terminals must not crash the backdrop generator."""
    bg = generate_background(5, 3, seed=0)
    assert len(bg) == 3 and len(bg[0]) == 5


def test_stamp_grid_skips_empty_cells_only():
    """EMPTY src cells should not overwrite canvas; non-EMPTY should."""
    canvas = [[Cell(".", "white", "") for _ in range(5)] for _ in range(3)]
    src = [
        [Cell("X", "red", "")],
    ]
    stamp_grid(canvas, src, 1, 2)
    assert canvas[1][2].glyph == "X"
    # Untouched cells unchanged:
    assert canvas[0][0].glyph == "."
    assert canvas[1][0].glyph == "."


def test_stamp_text_line_centers_text():
    canvas = [[Cell(" ", None, "") for _ in range(11)] for _ in range(3)]
    stamp_text_line(canvas, "abc", row=1)
    rendered = "".join(c.glyph for c in canvas[1])
    assert rendered.strip() == "abc"
    # Centered in width 11: leading spaces == trailing (within 1).
    leading = len(rendered) - len(rendered.lstrip())
    trailing = len(rendered) - len(rendered.rstrip())
    assert abs(leading - trailing) <= 1
