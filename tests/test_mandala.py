"""Tests for grid construction and mandala geometry."""

from __future__ import annotations

from collections import Counter

import pytest

from haikala import haiku as haiku_lib
from haikala.glyphs import COVERED, EMPTY
from haikala.mandala import grid_dims, grid_to_plain, render_spec
from haikala.translate import SIZE_RADIUS, haiku_to_spec


@pytest.mark.parametrize("size", ["small", "medium", "large", "huge"])
def test_grid_dims_match_size(size):
    r = SIZE_RADIUS[size]
    width, height = grid_dims(r)
    assert height == 2 * r + 1
    assert width == 4 * r + 1


def test_grid_has_expected_shape():
    spec = haiku_to_spec(haiku_lib.get("old_pond"), size="medium")
    grid = render_spec(spec)
    width, height = grid_dims(spec.grid_radius)
    assert len(grid) == height
    assert all(len(row) == width for row in grid)


def test_center_cell_holds_center_glyph():
    spec = haiku_to_spec(haiku_lib.get("old_pond"), size="medium")
    grid = render_spec(spec)
    width, height = grid_dims(spec.grid_radius)
    cy, cx = height // 2, width // 2
    assert grid[cy][cx].glyph == spec.center_glyph


def test_each_ring_glyph_appears_at_least_once():
    spec = haiku_to_spec(haiku_lib.get("old_pond"), size="medium")
    grid = render_spec(spec)
    placed = Counter(cell.glyph for row in grid for cell in row)
    for ring in spec.rings:
        first = ring.glyphs[0]
        assert placed[first] >= 1, f"ring glyph {first!r} never placed"


def test_grid_is_mostly_empty_at_corners():
    """The mandala is circular — corners should be empty space."""
    spec = haiku_to_spec(haiku_lib.get("old_pond"), size="medium")
    grid = render_spec(spec)
    h = len(grid)
    w = len(grid[0])
    assert grid[0][0].glyph == EMPTY
    assert grid[0][w - 1].glyph == EMPTY
    assert grid[h - 1][0].glyph == EMPTY
    assert grid[h - 1][w - 1].glyph == EMPTY


def test_covered_cells_follow_wide_glyphs():
    """Every COVERED sentinel should be immediately right of a wide glyph."""
    from haikala.symbols import is_wide
    spec = haiku_to_spec(haiku_lib.get("old_pond"), size="medium")
    grid = render_spec(spec)
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell.glyph == COVERED:
                assert x > 0, f"covered cell at left edge ({y},{x})"
                left = grid[y][x - 1]
                assert is_wide(left.glyph), (
                    f"covered cell at ({y},{x}) but left ({left.glyph!r}) isn't wide"
                )


def test_grid_to_plain_line_count():
    spec = haiku_to_spec(haiku_lib.get("old_pond"), size="medium")
    grid = render_spec(spec)
    text = grid_to_plain(grid)
    assert text.count("\n") == len(grid) - 1


@pytest.mark.parametrize("fold", [4, 6, 8, 12])
def test_ring_glyph_count_grows_with_fold(fold):
    """Each ring's primary glyph should be placed roughly fold-many times."""
    spec = haiku_to_spec(haiku_lib.get("old_pond"), fold=fold, size="medium")
    grid = render_spec(spec)
    placed = Counter(cell.glyph for row in grid for cell in row)
    for ring in spec.rings:
        # primary glyph at index 0 of ring should appear at least `fold` times
        # for sufficiently large rings; allow some collisions on tight inner rings
        cnt = placed[ring.glyphs[0]]
        assert cnt >= max(1, fold // 2), (
            f"ring {ring.glyphs[0]!r} (band={ring.band}) only placed {cnt} times for fold={fold}"
        )


def test_breath_modulates_glyph_count():
    """Inhale should place at least as many glyphs as exhale."""
    spec = haiku_to_spec(haiku_lib.get("old_pond"), size="medium")
    inhale = render_spec(spec, breath=1.0)
    exhale = render_spec(spec, breath=-1.0)
    inhale_count = sum(1 for row in inhale for c in row if c.glyph not in (EMPTY, COVERED))
    exhale_count = sum(1 for row in exhale for c in row if c.glyph not in (EMPTY, COVERED))
    assert inhale_count >= exhale_count


def test_render_works_for_every_haiku():
    """Smoke test: every curated haiku renders without raising."""
    for h in haiku_lib.HAIKU:
        spec = haiku_to_spec(h)
        grid = render_spec(spec)
        assert grid[len(grid) // 2][len(grid[0]) // 2].glyph != EMPTY


def test_vary_breath_renders_without_error():
    """Per-ring breath path must accept ring index as int (regression)."""
    spec = haiku_to_spec(haiku_lib.get("old_pond"), size="medium")
    for t in (0.0, 0.7, 1.5, 3.3):
        grid = render_spec(spec, t=t, breath_period=10.0, vary_breath=True)
        # Some glyphs land in the disc.
        assert any(
            c.glyph not in (EMPTY, COVERED) for row in grid for c in row
        )


def test_ripple_paints_rings_at_increasing_radii_over_time():
    """At t≈0 ripple sits near center; at t=period/2 it has moved outward."""
    spec = haiku_to_spec(haiku_lib.get("old_pond"), size="medium")
    grid_radius = spec.grid_radius

    def ripple_max_radius(t: float) -> float:
        from haikala.mandala import _RIPPLE_GLYPH
        grid = render_spec(spec, t=t, ripple=True, ripple_period=4.0)
        cx = len(grid[0]) // 2
        cy = len(grid) // 2
        max_r = 0.0
        import math as _math
        for y, row in enumerate(grid):
            for x, c in enumerate(row):
                if c.glyph == _RIPPLE_GLYPH:
                    r = _math.hypot((x - cx) / 2.0, y - cy)
                    if r > max_r:
                        max_r = r
        return max_r

    early = ripple_max_radius(0.2)
    late = ripple_max_radius(1.6)
    # Both should be inside the disc.
    assert early <= grid_radius
    assert late <= grid_radius
    # Later ripple has reached further out (with 2 staggered ripples in
    # flight, the leading one is past the trailing one).
    assert late >= early


def test_ripple_does_not_overdraw_center():
    """Ripple must paint into empty cells only — never replace center glyph."""
    spec = haiku_to_spec(haiku_lib.get("old_pond"), size="medium")
    grid = render_spec(spec, t=0.0, ripple=True, ripple_period=4.0)
    cy = len(grid) // 2
    cx = len(grid[0]) // 2
    assert grid[cy][cx].glyph == spec.center_glyph
