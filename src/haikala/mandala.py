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
    static: bool = False      # backdrop cells: don't hue-cycle, don't redraw
    bg_color: str | None = None  # ANSI/truecolor cell background tint


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
    bg_color: str | None = None,
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
    grid[y][x] = Cell(glyph, color, style, bg_color=bg_color)
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


_FRACTAL_GLYPHS = (" ", " ", "·", "˙", "░", "░", "▒", "▓")
_FRACTAL_MAX_ITER = len(_FRACTAL_GLYPHS) - 1


# Vivid 8-stop color ramps inspired by natural light and tone. Each stop maps
# 1:1 to the iteration count: index 0 is "escaped immediately" (deepest dark),
# index 7 is "inside the Julia set" (brightest interior).
FRACTAL_PALETTES: dict[str, tuple[str, ...]] = {
    # Northern lights: deep night sky → teal → jade → magenta arc.
    "aurora":   ("#000a1a", "#022040", "#0a4060", "#19828c",
                 "#2cd9a0", "#7af56a", "#c270ff", "#ffaff0"),
    # Coals and lava: char → ember → flame → pale gold.
    "ember":    ("#0a0000", "#2b0500", "#660f00", "#a82800",
                 "#e65800", "#ff9d20", "#ffd76a", "#fff8d0"),
    # Deep sea to surf: abyss → sapphire → cyan → foam.
    "ocean":    ("#000814", "#001d3d", "#003566", "#0077b6",
                 "#00b4d8", "#48cae4", "#caf0f8", "#ffffff"),
    # Moss / leaf-canopy / sun-warmed bark.
    "forest":   ("#0a1f0a", "#15391a", "#2c5a2c", "#4c7a2c",
                 "#7ea848", "#b8c870", "#e8c878", "#fff0c0"),
    # Cherry blossom at dawn: plum → rose → blush → white.
    "sakura":   ("#1a0e1a", "#3a1f30", "#6e3a55", "#a55a7a",
                 "#dc88a8", "#f5b6cc", "#fcdde6", "#ffffff"),
    # Dusk sky: ink → indigo → violet → orchid.
    "twilight": ("#080216", "#1a0a3a", "#36195e", "#5a2887",
                 "#8e3ec0", "#c266e0", "#ec96f0", "#fcd9ff"),
    # Volcanic/black-sand beach: obsidian → rust → sulfur → cream.
    "lava":     ("#050505", "#1a0a05", "#3d1a0a", "#7a2a14",
                 "#c75028", "#ee8b3a", "#f5cf6a", "#fff5d0"),
    # Coral reef: deep teal water → coral → peach → bone-white.
    "coral":    ("#001a1a", "#024040", "#157070", "#3aa8a0",
                 "#ffb88a", "#ff8466", "#ffd6b0", "#ffffff"),
}

DEFAULT_FRACTAL_PALETTE = "aurora"


def _apply_fractal_field(
    grid: list[list[Cell]],
    grid_radius: int,
    fold: int,
    t: float,
    colors: tuple[str, ...],
    spin_angle: float = 0.0,
) -> None:
    """Apply a slowly-drifting Julia set to the grid.

    A single pass over every cell:
      - empty disc cells are filled with a glyph + color from the palette
        (density gradient: " · ˙ ░ ▒ ▓"), and
      - already-placed ring/center cells keep their glyph + style but
        adopt the *same* fractal palette color at their position, so the
        whole field — backdrop and emoji alike — reads as one varying
        color landscape driven by the Julia escape time.

    `c` rotates around |c|=0.7885 with a long period for a flowing,
    organic feel. The cell's angle is folded into one half-sector of
    the mandala's N-fold symmetry, so the pattern has full dihedral
    D_fold symmetry — matching the rings.
    """
    if not colors or len(colors) <= _FRACTAL_MAX_ITER:
        colors = FRACTAL_PALETTES[DEFAULT_FRACTAL_PALETTE]
    height = len(grid)
    width = len(grid[0])
    cx = width // 2
    cy = height // 2
    edge = grid_radius + 0.5
    scale = 1.5 / max(1.0, grid_radius)
    drift = 0.05 * t
    c = complex(0.7885 * math.cos(drift), 0.7885 * math.sin(drift))
    sector = 2.0 * math.pi / max(1, fold)
    half = sector / 2.0
    for gy in range(height):
        for gx in range(width):
            cell = grid[gy][gx]
            if cell.glyph == COVERED:
                continue
            rx = (gx - cx) / 2.0
            ry = gy - cy
            r = math.hypot(rx, ry)
            if r > edge:
                continue
            # Rotate by the kaleidoscope's prism angle (no-op when spin_angle
            # is 0), then fold into [0, sector/2] for dihedral symmetry.
            theta = (math.atan2(ry, rx) - spin_angle) % sector
            if theta > half:
                theta = sector - theta
            z = complex(r * math.cos(theta) * scale, r * math.sin(theta) * scale)
            i = 0
            while i < _FRACTAL_MAX_ITER and (z.real * z.real + z.imag * z.imag) < 4.0:
                z = z * z + c
                i += 1
            color = colors[i]
            if cell.glyph == EMPTY:
                ch = _FRACTAL_GLYPHS[i]
                if ch == " ":
                    continue
                grid[gy][gx] = Cell(ch, color, "")
            else:
                grid[gy][gx] = Cell(
                    cell.glyph, color, cell.style,
                    static=cell.static, bg_color=cell.bg_color,
                )


_RIPPLE_GLYPH = "◌"
_RIPPLE_COLOR_DEFAULT = "#9ad8ff"
_RIPPLE_COUNT = 2  # number of expanding rings in flight at once

# Kaleidoscope tuning. Inner-most ring spins fastest in one direction; each
# successive ring is slower and reversed, so the layers tumble like loose
# beads in a turning prism. The fractal symmetry axes rotate at the same
# fraction of the base rate, dragging the backdrop along with the rings.
_SPIN_RING_FALLOFF = 0.32   # each ring slower than the previous by this much
_SPIN_FIELD_FRACTION = 0.35  # fractal symmetry rotation rate (× base rate)


def _spin_speed_for_ring(ring_idx: int) -> float:
    """Per-ring kaleidoscope rotation rate. Alternates sign so adjacent rings
    counter-rotate; magnitude shrinks geometrically by `_SPIN_RING_FALLOFF`.
    """
    sign = -1.0 if (ring_idx % 2 == 1) else 1.0
    return sign * (1.0 - _SPIN_RING_FALLOFF) ** ring_idx


def _styles_for_breath(breath: float) -> tuple[str, str]:
    """Return (ring_style, center_style) for a breath value in [-1, 1]."""
    if breath < -0.4:
        ring_style = "dim"
    elif breath > 0.4:
        ring_style = "bold"
    else:
        ring_style = ""
    if breath > 0.5:
        center_style = "bold"
    elif breath < -0.5:
        center_style = "dim"
    else:
        center_style = ""
    return ring_style, center_style


def _ring_breath(
    breath_global: float,
    ring_idx: int,
    n_rings: int,
    t: float,
    breath_period: float,
    vary: bool,
) -> float:
    """Per-ring breath value. With `vary=False`, all rings share the global
    `breath`. With `vary=True`, each ring runs its own slightly-shifted
    sinusoid driven by `t` and `breath_period`: inner rings (lower index)
    breathe a touch faster and the phase cascades outward, so the whole
    field swells in a soft wave instead of a single synchronized pulse.
    """
    if not vary or breath_period <= 0:
        return breath_global
    span = max(1, n_rings - 1)
    # ring_idx is 0 for innermost ring, n_rings-1 for outermost. Inner →
    # faster speed; outer → slower. ±10% spread.
    speed = 1.0 + 0.10 * (1.0 - 2.0 * ring_idx / span)
    phase = 0.45 * ring_idx  # radians; cascades outward
    return math.sin(2.0 * math.pi * t * speed / breath_period + phase)


def render_spec(
    spec: MandalaSpec,
    breath: float = 0.0,
    t: float = 0.0,
    breath_period: float = 10.0,
    vary_breath: bool = False,
    ripple: bool = False,
    ripple_period: float = 4.0,
    fractal: bool = False,
    fractal_colors: tuple[str, ...] | None = None,
    spin: bool = False,
    spin_period: float = 30.0,
) -> list[list[Cell]]:
    """Build the grid for a single frame.

    `breath` is in [-1, 1]. 0 is neutral; +1 is full inhale (rings expand
    slightly, denser); -1 is full exhale (rings contract, sparser/dimmer).
    `t` is wall-clock seconds since animation start.
    With `vary_breath=True`, each ring computes its own breath from `t`
    and `breath_period` (slight per-ring speed and phase variation).
    With `ripple=True`, transient rings sweep outward from the center on
    `ripple_period` seconds, painted only into empty space so they do not
    overdraw any haiku glyph.
    With `spin=True`, the whole figure becomes a kaleidoscope: each ring
    rotates at its own rate (alternating direction, geometric falloff),
    and the fractal's symmetry axes rotate at a fraction of the base
    rate — like a turning prism tube where loose elements counter-rotate
    inside the housing.
    """
    width, height = grid_dims(spec.grid_radius)
    grid = _new_grid(width, height)
    cx = width // 2
    cy = height // 2

    n_rings = len(spec.rings)
    # Center uses the *global* breath so it pulses with the overall feel,
    # regardless of per-ring variation.
    _, center_style = _styles_for_breath(breath)
    _place(grid, cx, cy, spec.center_glyph, spec.center_color, center_style)

    base_spin = (2.0 * math.pi * t / spin_period) if (spin and spin_period > 0) else 0.0

    for ring_idx, ring in enumerate(spec.rings):
        rb = _ring_breath(breath, ring_idx, n_rings, t, breath_period, vary_breath)
        radius_mod = 1.0 + 0.13 * rb
        density_mod = 1.0 + 0.18 * rb
        ring_style, _ = _styles_for_breath(rb)
        r_eff = ring.radius * radius_mod
        if r_eff < 0.5:
            continue
        n = _positions_per_sector(r_eff, spec.fold)
        density_eff = max(0.05, min(1.0, ring.density * density_mod))
        sel = _selected_indices(n, density_eff)
        ring_spin = base_spin * _spin_speed_for_ring(ring_idx)

        for sector in range(spec.fold):
            for k in sel:
                theta = (
                    2.0 * math.pi * (sector * n + k) / (spec.fold * n)
                    + ring.phase
                    + ring_spin
                )
                # Apply the shape function in the ring's own (un-rotated)
                # frame, then place at the rotated angle.
                r_at = _shape_radius(ring.shape, r_eff, spec.fold, theta - ring.phase - ring_spin)
                x = round(cx + r_at * math.cos(theta) * 2.0)
                y = round(cy + r_at * math.sin(theta))
                glyph = ring.glyphs[k % len(ring.glyphs)]
                _place(grid, x, y, glyph, ring.color, ring_style, bg_color=ring.bg_color)

    if ripple and ripple_period > 0:
        _paint_ripple(
            grid, spec.grid_radius, spec.fold, t, ripple_period,
        )

    if fractal:
        colors = fractal_colors or FRACTAL_PALETTES[DEFAULT_FRACTAL_PALETTE]
        field_spin = base_spin * _SPIN_FIELD_FRACTION
        _apply_fractal_field(
            grid, spec.grid_radius, spec.fold, t, colors=colors,
            spin_angle=field_spin,
        )
    else:
        _paint_background(grid, spec.grid_radius)
    return grid


def _paint_ripple(
    grid: list[list[Cell]],
    grid_radius: int,
    fold: int,
    t: float,
    ripple_period: float,
) -> None:
    """Lay transient ripple rings into empty cells.

    `_RIPPLE_COUNT` rings are kept in flight at once, evenly staggered in
    phase so there is always one mid-sweep — like ongoing ripples on a
    pond. Each ring's radius is `phase_k * grid_radius`, with phase_k =
    ((t / period) + k / count) mod 1. Glyphs are placed only into EMPTY
    cells, so no haiku content is overdrawn; if `--fractal` is on, the
    fractal pass will recolor these cells along with everything else.
    """
    height = len(grid)
    width = len(grid[0])
    cx = width // 2
    cy = height // 2
    base_phase = (t / ripple_period) % 1.0
    for k in range(_RIPPLE_COUNT):
        phase = (base_phase + k / _RIPPLE_COUNT) % 1.0
        r_eff = phase * (grid_radius - 0.5)
        if r_eff < 0.5:
            continue
        # Soft fade as the ripple approaches the rim.
        fade = "" if phase < 0.85 else "dim"
        n = _positions_per_sector(r_eff, fold)
        for sector in range(fold):
            for j in range(n):
                theta = 2.0 * math.pi * (sector * n + j) / (fold * n)
                x = round(cx + r_eff * math.cos(theta) * 2.0)
                y = round(cy + r_eff * math.sin(theta))
                _place(grid, x, y, _RIPPLE_GLYPH, _RIPPLE_COLOR_DEFAULT, fade)


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
