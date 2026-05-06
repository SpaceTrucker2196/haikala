"""Breathing animation loop.

A slow sinusoidal phase drives the rendering. Frame rate ~15 FPS by default.
On exit (q, Ctrl+C, ESC), terminal state is restored cleanly.
"""

from __future__ import annotations

import colorsys
import math
import sys
import time

from rich.align import Align
from rich.color import Color
from rich.console import Console, Group
from rich.live import Live
from rich.text import Text

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


def grid_to_text(grid: list[list[Cell]], hue_shift: float = 0.0) -> Text:
    text = Text(no_wrap=True)
    # Memoize the per-frame hue rotation by source color — typically only
    # ~5–10 distinct colors per spec, vs thousands of cells.
    cache: dict[str, str] = {}
    for i, row in enumerate(grid):
        for cell in row:
            if cell.glyph == COVERED:
                continue
            parts: list[str] = []
            if cell.style:
                parts.append(cell.style)
            if cell.color:
                if hue_shift:
                    shifted = cache.get(cell.color)
                    if shifted is None:
                        shifted = _shift_hue(cell.color, hue_shift)
                        cache[cell.color] = shifted
                    parts.append(shifted)
                else:
                    parts.append(cell.color)
            style = " ".join(parts) if parts else None
            text.append(cell.glyph, style=style)
        if i < len(grid) - 1:
            text.append("\n")
    return text


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
) -> None:
    if console is None:
        console = Console()
    period = 60.0 / max(1, bpm)
    frame_interval = 1.0 / max(1, fps)
    cycle_period = max(1.0, cycle_period)
    start = time.monotonic()
    input_state = _setup_input()

    try:
        with Live(
            render_frame(
                spec, haiku, 0.0,
                fractal=fractal, fractal_colors=fractal_colors,
                ripple=ripple, ripple_period=ripple_period,
            ),
            console=console,
            screen=False,
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
                    render_frame(
                        spec, haiku, breath,
                        t=t,
                        breath_period=period,
                        vary_breath=vary_breath,
                        ripple=ripple,
                        ripple_period=ripple_period,
                        hue_shift=hue_shift,
                        fractal=fractal,
                        fractal_colors=fractal_colors,
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
