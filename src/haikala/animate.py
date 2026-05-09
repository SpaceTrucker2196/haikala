"""Breathing animation loop.

A slow sinusoidal phase drives the rendering. Frame rate ~15 FPS by default.
On exit (q, Ctrl+C, ESC), terminal state is restored cleanly.
"""

from __future__ import annotations

import colorsys
import math
import sys
import time
from typing import Callable

from rich.align import Align
from rich.color import Color
from rich.console import Console, Group
from rich.live import Live
from rich.text import Text

from .background import generate_background, stamp_grid, stamp_text_line
from .glyphs import COVERED
from .haiku import Haiku
from .mandala import Cell, render_spec
from .translate import MandalaSpec

try:
    import select
    import termios
    import tty
    HAVE_TTY = True
except ImportError:
    HAVE_TTY = False


def _shift_hue(color: str, deg: float) -> str:
    """Rotate a color's hue by `deg` degrees in HLS space.

    Returns a `#rrggbb` string. Falls back to the input on parse error.
    """
    try:
        rgb = Color.parse(color).get_truecolor()
    except Exception:
        return color
    h, l, s = colorsys.rgb_to_hls(rgb.red / 255.0, rgb.green / 255.0, rgb.blue / 255.0)
    h = (h + deg / 360.0) % 1.0
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def grid_to_text(
    grid: list[list[Cell]],
    hue_shift: float = 0.0,
    hue_field: Callable[[int, int], float] | None = None,
) -> Text:
    """Render a Cell grid to a Rich Text.

    Hue rotation = `hue_shift` (uniform across the grid) plus, optionally,
    a position-dependent term from `hue_field(x, y)`. The combined shift
    is applied only to non-static cells; backdrop cells (`static=True`)
    keep their original color so the backdrop never drifts. Cells with
    `bg_color` set emit `on {bg}` so colorable Unicode glyphs (block,
    dingbat) render as filled patches — used by --no-emoji mode.
    """
    text = Text(no_wrap=True)
    # Cache per (color, quantized_shift). Quantization keeps the cache
    # small when hue_field varies per cell (5° buckets → ≤72 buckets per
    # source color).
    cache: dict[tuple[str, int], str] = {}

    def shifted(color: str, deg: float) -> str:
        bucket = int(round(deg / 5.0)) % 72
        key = (color, bucket)
        out = cache.get(key)
        if out is None:
            out = _shift_hue(color, bucket * 5.0)
            cache[key] = out
        return out

    for i, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell.glyph == COVERED:
                continue
            parts: list[str] = []
            if cell.style:
                parts.append(cell.style)

            shift = 0.0
            if not cell.static:
                shift = hue_shift
                if hue_field is not None:
                    shift += hue_field(x, i)

            if cell.color:
                if shift and not cell.static:
                    parts.append(shifted(cell.color, shift))
                else:
                    parts.append(cell.color)
            if cell.bg_color:
                bg = cell.bg_color
                if shift and not cell.static:
                    bg = shifted(bg, shift)
                parts.append(f"on {bg}")
            style = " ".join(parts) if parts else None
            text.append(cell.glyph, style=style)
        if i < len(grid) - 1:
            text.append("\n")
    return text


# Default fold sequence the emanating wave cycles through. Picked to give
# distinct angular flavors (low/medium/high symmetry) so each pass looks
# different from the previous.
EMANATE_FOLDS: tuple[int, ...] = (2, 4, 6, 8, 12)


def make_emanate_field(
    cx: int,
    cy: int,
    t: float,
    period: float,
    max_r: float,
    folds: tuple[int, ...] = EMANATE_FOLDS,
    band: float = 4.0,
    intensity: float = 140.0,
) -> Callable[[int, int], float]:
    """Build a per-cell hue offset that radiates outward from (cx, cy).

    A thin annular "wave" expands from the center at speed max_r/period.
    Cells inside the band get a hue shift modulated by `cos(F·θ)`, where
    `F` cycles through `folds` once per pulse. Cells outside the band
    return zero — they keep their original colors, satisfying the "while
    keeping the other colors the same" intent.

    The x-axis is stretched 2× to match terminal cell aspect (so the
    wavefront stays circular on screen).
    """
    period = max(0.25, period)
    if max_r <= 0:
        return lambda x, y: 0.0
    cycle = t / period
    wave_idx = int(cycle) % len(folds)
    fold = folds[wave_idx]
    phase = cycle - int(cycle)
    wave_r = phase * max_r

    def hue_at(x: int, y: int) -> float:
        rx = (x - cx) / 2.0
        ry = y - cy
        r = math.hypot(rx, ry)
        d = abs(r - wave_r)
        if d > band:
            return 0.0
        falloff = 1.0 - (d / band)
        if r < 0.5:
            return falloff * intensity
        theta = math.atan2(ry, rx)
        modulation = (1.0 + math.cos(fold * theta)) / 2.0
        return falloff * modulation * intensity

    return hue_at


def _haiku_header(haiku: Haiku) -> Group:
    parts = [Align.center(Text(line)) for line in haiku.lines]
    parts.append(Text(""))
    parts.append(Align.center(Text(f"— {haiku.author}", style="dim italic")))
    return Group(*parts)


def render_frame(
    spec: MandalaSpec,
    haiku: Haiku,
    breath: float,
    t: float = 0.0,
    breath_period: float = 10.0,
    vary_breath: bool = False,
    ripple: bool = False,
    ripple_period: float = 4.0,
    hue_shift: float = 0.0,
    fractal: bool = False,
    fractal_colors: tuple[str, ...] | None = None,
    spin: bool = False,
    spin_period: float = 30.0,
) -> Group:
    header = _haiku_header(haiku)
    grid = render_spec(
        spec, breath,
        t=t,
        breath_period=breath_period,
        vary_breath=vary_breath,
        ripple=ripple,
        ripple_period=ripple_period,
        fractal=fractal,
        fractal_colors=fractal_colors,
        spin=spin,
        spin_period=spin_period,
    )
    body = Align.center(grid_to_text(grid, hue_shift=hue_shift))
    spacer = Text("")
    return Group(header, spacer, body)


def render_static(
    spec: MandalaSpec,
    haiku: Haiku,
    console: Console,
    fractal: bool = False,
    fractal_colors: tuple[str, ...] | None = None,
) -> None:
    console.print(render_frame(
        spec, haiku, breath=0.0,
        fractal=fractal, fractal_colors=fractal_colors,
    ))


def _compose_fullscreen(
    backdrop: list[list[Cell]],
    spec: MandalaSpec,
    haiku: Haiku,
    breath: float,
    t: float,
    breath_period: float,
    vary_breath: bool,
    ripple: bool,
    ripple_period: float,
    fractal: bool,
    fractal_colors: tuple[str, ...] | None,
    spin: bool,
    spin_period: float,
    hue_shift: float,
    emanate: bool = False,
    emanate_period: float = 5.0,
) -> Text:
    """Build a single Text that fills the console: copy of the static
    backdrop, with the haiku header and the animated mandala body
    stamped on top of it."""
    canvas = [row[:] for row in backdrop]
    H = len(canvas)
    W = len(canvas[0]) if H else 0

    # Stamp haiku header at the top.
    header_top = 1
    for i, line in enumerate(haiku.lines):
        stamp_text_line(canvas, line, header_top + i, style="")
    stamp_text_line(canvas, f"— {haiku.author}", header_top + len(haiku.lines) + 1,
                    style="dim italic")

    # Render the mandala body and overlay it centered, below the header.
    mandala_grid = render_spec(
        spec, breath,
        t=t,
        breath_period=breath_period,
        vary_breath=vary_breath,
        ripple=ripple,
        ripple_period=ripple_period,
        fractal=fractal,
        fractal_colors=fractal_colors,
        spin=spin,
        spin_period=spin_period,
    )
    mh = len(mandala_grid)
    mw = len(mandala_grid[0]) if mh else 0
    header_block = header_top + len(haiku.lines) + 3
    top = max(header_block, (H - mh) // 2 + (header_block // 4))
    if top + mh > H:
        top = max(0, H - mh)
    left = max(0, (W - mw) // 2)
    stamp_grid(canvas, mandala_grid, top, left)

    hue_field = None
    if emanate:
        # Mandala center in canvas coordinates.
        cx = left + mw // 2
        cy = top + mh // 2
        max_r = float(spec.grid_radius + 1)
        hue_field = make_emanate_field(cx, cy, t, emanate_period, max_r)

    return grid_to_text(canvas, hue_shift=hue_shift, hue_field=hue_field)


def _setup_input():
    if not HAVE_TTY or not sys.stdin.isatty():
        return None
    try:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        return (fd, old)
    except (termios.error, OSError, AttributeError):
        return None


def _restore_input(state) -> None:
    if state is None:
        return
    fd, old = state
    try:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except (termios.error, OSError):
        pass


def _quit_pressed() -> bool:
    if not HAVE_TTY or not sys.stdin.isatty():
        return False
    try:
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if rlist:
            ch = sys.stdin.read(1)
            return ch in ("q", "Q", "\x03", "\x1b")
    except (OSError, ValueError):
        pass
    return False


def animate(
    spec: MandalaSpec,
    haiku: Haiku,
    bpm: int = 6,
    fps: int = 24,
    console: Console | None = None,
    cycle: bool = False,
    cycle_period: float = 90.0,
    fractal: bool = False,
    fractal_colors: tuple[str, ...] | None = None,
    ripple: bool = False,
    ripple_period: float = 4.0,
    vary_breath: bool = True,
    spin: bool = False,
    spin_period: float = 30.0,
    emanate: bool = False,
    emanate_period: float = 5.0,
) -> None:
    if console is None:
        console = Console()
    period = 60.0 / max(1, bpm)
    frame_interval = 1.0 / max(1, fps)
    cycle_period = max(1.0, cycle_period)
    start = time.monotonic()
    input_state = _setup_input()

    # Build the static backdrop once, sized to the current console.
    size = console.size
    backdrop = generate_background(size.width, size.height, hash(haiku.id))

    try:
        with Live(
            _compose_fullscreen(
                backdrop, spec, haiku,
                breath=0.0, t=0.0,
                breath_period=period, vary_breath=False,
                ripple=ripple, ripple_period=ripple_period,
                fractal=fractal, fractal_colors=fractal_colors,
                spin=spin, spin_period=spin_period,
                hue_shift=0.0,
                emanate=emanate, emanate_period=emanate_period,
            ),
            console=console,
            screen=True,
            auto_refresh=False,
            transient=False,
        ) as live:
            while True:
                if _quit_pressed():
                    break
                t = time.monotonic() - start
                breath = math.sin(2.0 * math.pi * t / period)
                hue_shift = (t / cycle_period) * 360.0 if cycle else 0.0
                live.update(
                    _compose_fullscreen(
                        backdrop, spec, haiku,
                        breath=breath, t=t,
                        breath_period=period, vary_breath=vary_breath,
                        ripple=ripple, ripple_period=ripple_period,
                        fractal=fractal, fractal_colors=fractal_colors,
                        spin=spin, spin_period=spin_period,
                        hue_shift=hue_shift,
                        emanate=emanate, emanate_period=emanate_period,
                    ),
                    refresh=True,
                )
                time.sleep(frame_interval)
    except KeyboardInterrupt:
        pass
    finally:
        _restore_input(input_state)
        try:
            console.show_cursor(True)
        except Exception:
            pass
        console.print()
        console.print("[dim italic]breath out.[/]")
