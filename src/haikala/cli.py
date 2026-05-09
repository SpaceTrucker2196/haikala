"""Click CLI entrypoint."""

from __future__ import annotations

import random
import sys

import click
from rich.console import Console
from rich.table import Table

from . import haiku as haiku_lib
from .animate import animate, render_static
from .mandala import DEFAULT_FRACTAL_PALETTE, FRACTAL_PALETTES
from .palette import fold_for_haiku, palette_from_haiku
from .translate import DEFAULT_SIZE, haiku_to_spec


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--list", "list_haiku",
    is_flag=True,
    help="List the curated haiku and exit.",
)
@click.option(
    "--haiku", "haiku_id",
    default=None,
    metavar="ID",
    help="Render a specific haiku by id (see --list).",
)
@click.option(
    "--random", "random_pick",
    is_flag=True,
    help="Pick a random haiku (default behavior when --haiku is omitted).",
)
@click.option(
    "--fold",
    type=click.Choice(["auto", "4", "6", "8", "10", "12", "14", "16"]),
    default="auto",
    show_default=True,
    help="Rotational symmetry order. 'auto' picks an even fold from the "
         "haiku's word and token counts (capped at 16).",
)
@click.option(
    "--bpm",
    type=click.IntRange(1, 30),
    default=6,
    show_default=True,
    help="Breath rate when --animate is set (breaths per minute).",
)
@click.option(
    "--animate",
    "animate_flag",
    is_flag=True,
    help="Run the breathing animation. Default is to render one static "
         "mandala and exit; the animation is being parked for now while we "
         "iterate on the static design.",
)
@click.option(
    "--size",
    type=click.Choice(["small", "medium", "large", "huge"]),
    default=DEFAULT_SIZE,
    show_default=True,
    help="Mandala grid size. huge ≈ 40-tall circular mandala (default).",
)
@click.option(
    "--seed",
    type=int,
    default=None,
    help="Seed for random haiku selection (deterministic).",
)
@click.option(
    "--cycle/--no-cycle",
    default=False,
    show_default=True,
    help="Slowly rotate ring colors through the hue wheel during animation.",
)
@click.option(
    "--cycle-period",
    type=click.FloatRange(5.0, 600.0),
    default=90.0,
    show_default=True,
    help="Seconds for one full hue rotation when --cycle is on.",
)
@click.option(
    "--fractal/--no-fractal",
    default=False,
    show_default=True,
    help="Use a slowly-drifting Julia set as the background instead of dot fill.",
)
@click.option(
    "--palette",
    type=click.Choice(["auto", *sorted(FRACTAL_PALETTES.keys())]),
    default="auto",
    show_default=True,
    help="Color palette for the fractal background. 'auto' derives one "
         "from words found in the haiku; named palettes force a specific "
         "ramp.",
)
@click.option(
    "--ripple/--no-ripple",
    default=False,
    show_default=True,
    help="Sweep transient rings outward from center (during --animate).",
)
@click.option(
    "--ripple-period",
    type=click.FloatRange(0.5, 60.0),
    default=4.0,
    show_default=True,
    help="Seconds for one ripple to travel from center to rim.",
)
@click.option(
    "--spin/--no-spin",
    default=False,
    show_default=True,
    help="Kaleidoscope mode: rings rotate at varying rates (alternating "
         "directions) and the fractal symmetry axes turn with them.",
)
@click.option(
    "--spin-period",
    type=click.FloatRange(2.0, 600.0),
    default=30.0,
    show_default=True,
    help="Seconds for the innermost ring to make one full revolution.",
)
@click.option(
    "--no-emoji/--emoji",
    "no_emoji",
    default=False,
    show_default=True,
    help="Replace emoji with colorable Unicode glyphs (block / dingbat / "
         "geometric) and add cell background tints — built from ANSI/256/"
         "truecolor that emoji can't honor.",
)
@click.option(
    "--emanate/--no-emanate",
    default=False,
    show_default=True,
    help="Hue waves radiate outward from the center; each successive "
         "wave has a different angular symmetry. Cells outside the wave "
         "keep their original colors.",
)
@click.option(
    "--emanate-period",
    type=click.FloatRange(0.5, 60.0),
    default=5.0,
    show_default=True,
    help="Seconds for one emanating wave to travel from center to rim.",
)
def main(
    list_haiku: bool,
    haiku_id: str | None,
    random_pick: bool,
    fold: str,
    bpm: int,
    animate_flag: bool,
    size: str,
    seed: int | None,
    cycle: bool,
    cycle_period: float,
    fractal: bool,
    palette: str,
    ripple: bool,
    ripple_period: float,
    spin: bool,
    spin_period: float,
    no_emoji: bool,
    emanate: bool,
    emanate_period: float,
) -> None:
    """haikala — a haiku mandala generator."""
    console = Console()

    if list_haiku:
        _print_list(console)
        return

    haiku = _select_haiku(haiku_id, random_pick, seed, console)
    if haiku is None:
        sys.exit(1)

    fold_int = fold_for_haiku(haiku) if fold == "auto" else int(fold)
    spec = haiku_to_spec(haiku, fold=fold_int, size=size, no_emoji=no_emoji)

    if palette == "auto":
        fractal_colors = palette_from_haiku(haiku) or FRACTAL_PALETTES[DEFAULT_FRACTAL_PALETTE]
    else:
        fractal_colors = FRACTAL_PALETTES[palette]

    if animate_flag:
        animate(
            spec, haiku,
            bpm=bpm, console=console,
            cycle=cycle, cycle_period=cycle_period,
            fractal=fractal, fractal_colors=fractal_colors,
            ripple=ripple, ripple_period=ripple_period,
            spin=spin, spin_period=spin_period,
            emanate=emanate, emanate_period=emanate_period,
        )
        return

    render_static(spec, haiku, console, fractal=fractal, fractal_colors=fractal_colors)


def _select_haiku(
    haiku_id: str | None,
    random_pick: bool,
    seed: int | None,
    console: Console,
):
    if haiku_id is not None:
        if haiku_id not in haiku_lib.HAIKU_BY_ID:
            console.print(f"[red]unknown haiku id:[/] {haiku_id!r}")
            console.print("[dim]try `haikala --list`[/]")
            return None
        return haiku_lib.HAIKU_BY_ID[haiku_id]

    rng = random.Random(seed)
    return rng.choice(haiku_lib.HAIKU)


def _print_list(console: Console) -> None:
    table = Table(
        title="haikala — curated haiku",
        title_style="dim italic",
        header_style="bold",
        show_lines=False,
        pad_edge=False,
    )
    table.add_column("id", style="cyan")
    table.add_column("season", style="magenta")
    table.add_column("author")
    table.add_column("first line", style="dim italic")
    for h in haiku_lib.HAIKU:
        table.add_row(h.id, h.season, h.author, h.lines[0])
    console.print(table)


if __name__ == "__main__":
    main()
