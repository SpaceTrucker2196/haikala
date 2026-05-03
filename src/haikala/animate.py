"""Breathing animation loop.

A slow sinusoidal phase drives the rendering. Frame rate ~15 FPS by default.
On exit (q, Ctrl+C, ESC), terminal state is restored cleanly.
"""

from __future__ import annotations

import math
import sys
import time

from rich.align import Align
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


def grid_to_text(grid: list[list[Cell]]) -> Text:
    text = Text(no_wrap=True)
    for i, row in enumerate(grid):
        for cell in row:
            if cell.glyph == COVERED:
                continue
            parts: list[str] = []
            if cell.style:
                parts.append(cell.style)
            if cell.color:
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


def render_frame(spec: MandalaSpec, haiku: Haiku, breath: float) -> Group:
    header = _haiku_header(haiku)
    grid = render_spec(spec, breath)
    body = Align.center(grid_to_text(grid))
    spacer = Text("")
    return Group(header, spacer, body)


def render_static(spec: MandalaSpec, haiku: Haiku, console: Console) -> None:
    console.print(render_frame(spec, haiku, breath=0.0))


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
    fps: int = 15,
    console: Console | None = None,
) -> None:
    if console is None:
        console = Console()
    period = 60.0 / max(1, bpm)
    frame_interval = 1.0 / max(1, fps)
    start = time.monotonic()
    input_state = _setup_input()

    try:
        with Live(
            render_frame(spec, haiku, 0.0),
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
                live.update(render_frame(spec, haiku, breath), refresh=True)
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
