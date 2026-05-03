"""Mandala geometry and grid composition.

The grid is a 2D character grid. Terminal cells are roughly 2:1
(taller than wide), so x is multiplied by 2 when placing positions on a
circle — otherwise circles render as flat ovals.

Each ring is placed by sweeping `fold * n` positions around the circle.
Glyphs cycle through `ring.glyphs` by within-sector index, so every fold
sector receives the same rotated pattern (true N-fold symmetry).
Inner rings are placed first; later placements that would collide are
skipped so the inner ring wins.

After ring placement, a deterministic background pass fills remaining
empty cells with low-emphasis shading and dot characters. The fill is
denser near the center and thins out toward the edge, giving the
mandala a textured backdrop without competing with the colorful
foreground emoji.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .glyphs import COVERED, EMPTY
from .symbols import is_wide
from .translate import MandalaSpec


@dataclass(frozen=True)
class Cell:
    glyph: str
    color: str | None = None
    style: str = ""           # "" | "dim" | "bold"


def grid_dims(grid_radius: int) -> tuple[int, int]:
    """Return (width, height) for the given y-cell radius. x is doubled."""
    height = 2 * grid_radius + 1
    width = 4 * grid_radius + 1
    return width, height


def _new_grid(width: int, height: int) -> list[list[Cell]]:
    return [[Cell(EMPTY, None) for _ in range(width)] for _ in range(height)]


def _positions_per_sector(radius: float, fold: int) -> int:
    """How many distinct positions per fold sector for a ring of this radius."""
    # circumference (in x-cells, after the *2 stretch) ≈ 2π r * 2.
    # The 2.6 multiplier packs ~30% more positions than the geometric
    # baseline of 2.0; rounding leaves inner rings unchanged (avoids
    # wide-emoji crowding) but middle/outer rings get noticeably denser.
    raw = 2.6 * radius / fold + 0.5
    return max(1, round(raw))


_STAR_INNER_RATIO = 0.55  # how deep the star valleys cut between fold points
_PETAL_AMP = 0.22         # 0=circle, 0.4 ≈ pronounced lobes; normalized below


def _shape_radius(shape: str, R: float, fold: int, theta_local: float) -> float:
    """Effective radius at angle `theta_local` for the given shape.

    `theta_local` is the angle measured in the shape's own (un-rotated)
    frame — i.e. caller has already subtracted the ring's `phase`. R is the
    ring's nominal radius (vertex circumradius for polygon/star, mean
    radius for petal).
    """
    if shape == "circle":
        return R
    if shape == "polygon":
        # Regular fold-gon inscribed in a circle of radius R. Distance from
        # center to a point on the polygon along the ray at theta_local:
        #   r = R * cos(π/fold) / cos(α)
        # where α is the angular distance to the nearest edge midpoint
        # (range [0, π/fold]).
        sector = 2.0 * math.pi / fold
        midpoint = math.pi / fold
        a = theta_local % sector            # [0, sector)
        edge_dist = abs(a - midpoint)       # [0, midpoint]
        denom = math.cos(edge_dist)
        if denom < 1e-9:
            return R
        return R * math.cos(midpoint) / denom
    if shape == "star":
        # 2*fold-pointed star: outer vertex at angle 0, inner vertex at
        # angle π/fold, repeating with period 2π/fold. Linear interpolation
        # along each half-sector for a clean V-shape.
        sector = 2.0 * math.pi / fold
        midpoint = math.pi / fold
        a = theta_local % sector
        # |a - midpoint| / midpoint ∈ [0, 1]; 0 at inner vertex, 1 at outer
        t = abs(a - midpoint) / midpoint
        return R * (_STAR_INNER_RATIO + (1.0 - _STAR_INNER_RATIO) * t)
    if shape == "petal":
        # Rose curve, normalized so max(r) == R (so the petal stays inside
        # the band and doesn't crash into the next ring out).
        amp = _PETAL_AMP
        return R * (1.0 + amp * math.cos(fold * theta_local)) / (1.0 + amp)
    return R


def _selected_indices(n: int, density: float) -> tuple[int, ...]:
    """Pick m of n positions as evenly as possible."""
    m = max(1, round(n * density))
    if m >= n:
        return tuple(range(n))
    return tuple(round(i * n / m) for i in range(m))


def _place(
    grid: list[list[Cell]],
    x: int,
    y: int,
    glyph: str,
    color: str | None,
    style: str = "",
) -> bool:
    height = len(grid)
    if not (0 <= y < height):
        return False
    width = len(grid[0])
    if not (0 <= x < width):
        return False
    if grid[y][x].glyph != EMPTY:
        return False
    wide = is_wide(glyph)
    if wide:
        if x + 1 >= width:
            return False
        if grid[y][x + 1].glyph != EMPTY:
            return False
    grid[y][x] = Cell(glyph, color, style)
    if wide:
        grid[y][x + 1] = Cell(COVERED, None, "")
    return True


_BG_INNER = ("░", "·", "▒", "·")
_BG_MIDDLE = ("░", "·", "˙", "·")
_BG_OUTER = ("·", "˙", "·", " ")


def _bg_zone(rx: float, ry: float, grid_radius: int) -> tuple[tuple[str, ...], float]:
    """Pick a background palette + fill probability based on distance.

    rx and ry are signed offsets from the center, in y-cell units (rx is
    already de-stretched: divide x-cell offset by 2 before passing in).

    Returns (palette, probability). Cells past the disc edge get prob 0.
    """
    r = math.hypot(rx, ry)
    edge = grid_radius + 0.5
    if r > edge:
        return ((), 0.0)
    norm = r / max(1.0, edge)            # 0 at center, 1 at the disc edge
    if norm < 0.35:
        return (_BG_INNER, 0.78)
    if norm < 0.70:
        return (_BG_MIDDLE, 0.55)
    return (_BG_OUTER, 0.32)


def _bg_pick(palette: tuple[str, ...], gx: int, gy: int) -> str:
    """Deterministic per-cell choice from `palette` (no randomness)."""
    # Cheap hash that varies along both axes; same (gx,gy) always picks same.
    h = (gx * 73856093) ^ (gy * 19349663)
    return palette[(h & 0xFFFF) % len(palette)]


def _paint_background(grid: list[list[Cell]], grid_radius: int) -> None:
    """Fill empty cells with low-emphasis shading and dots.

    Runs after rings have placed their bright glyphs. Only writes into
    EMPTY cells; ring glyphs and their wide-COVERED extensions are
    untouched. Background cells are styled `dim` so they recede.
    """
    height = len(grid)
    width = len(grid[0])
    cx = width // 2
    cy = height // 2
    for gy in range(height):
        for gx in range(width):
            if grid[gy][gx].glyph != EMPTY:
                continue
            rx = (gx - cx) / 2.0
            ry = gy - cy
            palette, prob = _bg_zone(rx, ry, grid_radius)
            if prob <= 0.0 or not palette:
                continue
            # Same hash drives both "fill or skip" and "which glyph",
            # so the pattern is stable per (gx,gy).
            h = (gx * 2654435761) ^ (gy * 40503)
            if (h & 0xFFFF) / 65535.0 > prob:
                continue
            ch = _bg_pick(palette, gx, gy)
            if ch == EMPTY:
                continue
            grid[gy][gx] = Cell(ch, None, "dim")


def render_spec(spec: MandalaSpec, breath: float = 0.0) -> list[list[Cell]]:
    """Build the grid for a single frame.

    `breath` is in [-1, 1]. 0 is neutral; +1 is full inhale (rings expand
    slightly, denser); -1 is full exhale (rings contract, sparser/dimmer).
    """
    width, height = grid_dims(spec.grid_radius)
    grid = _new_grid(width, height)
    cx = width // 2
    cy = height // 2

    radius_mod = 1.0 + 0.13 * breath
    density_mod = 1.0 + 0.18 * breath
    if breath < -0.4:
        ring_style = "dim"
    elif breath > 0.4:
        ring_style = "bold"
    else:
        ring_style = ""

    # center pulses subtly: bold near full inhale, dim near full exhale
    if breath > 0.5:
        center_style = "bold"
    elif breath < -0.5:
        center_style = "dim"
    else:
        center_style = ""
    _place(grid, cx, cy, spec.center_glyph, spec.center_color, center_style)

    for ring in spec.rings:
        r_eff = ring.radius * radius_mod
        if r_eff < 0.5:
            continue
        n = _positions_per_sector(r_eff, spec.fold)
        density_eff = max(0.05, min(1.0, ring.density * density_mod))
        sel = _selected_indices(n, density_eff)

        for sector in range(spec.fold):
            for k in sel:
                theta = 2.0 * math.pi * (sector * n + k) / (spec.fold * n) + ring.phase
                # Apply the shape function in the ring's own (un-rotated)
                # frame, then place at the rotated angle.
                r_at = _shape_radius(ring.shape, r_eff, spec.fold, theta - ring.phase)
                x = round(cx + r_at * math.cos(theta) * 2.0)
                y = round(cy + r_at * math.sin(theta))
                glyph = ring.glyphs[k % len(ring.glyphs)]
                _place(grid, x, y, glyph, ring.color, ring_style)

    _paint_background(grid, spec.grid_radius)
    return grid


def grid_to_plain(grid: list[list[Cell]]) -> str:
    """Concatenate the grid into a plain-text string (no color)."""
    rows: list[str] = []
    for row in grid:
        chunks: list[str] = []
        for cell in row:
            if cell.glyph == COVERED:
                continue
            chunks.append(cell.glyph)
        rows.append("".join(chunks).rstrip())
    return "\n".join(rows)
