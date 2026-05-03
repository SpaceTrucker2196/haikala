"""Click CLI entrypoint."""

from __future__ import annotations

import random
import sys

import click
from rich.console import Console
from rich.table import Table

from . import haiku as haiku_lib
from .animate import animate, render_static
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
    type=click.Choice(["4", "6", "8", "12"]),
    default="8",
    show_default=True,
    help="Rotational symmetry order.",
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
def main(
    list_haiku: bool,
    haiku_id: str | None,
    random_pick: bool,
    fold: str,
    bpm: int,
    animate_flag: bool,
    size: str,
    seed: int | None,
) -> None:
    """haikala — a haiku mandala generator."""
    console = Console()

    if list_haiku:
        _print_list(console)
        return

    haiku = _select_haiku(haiku_id, random_pick, seed, console)
    if haiku is None:
        sys.exit(1)

    spec = haiku_to_spec(haiku, fold=int(fold), size=size)

    if animate_flag:
        animate(spec, haiku, bpm=bpm, console=console)
        return

    render_static(spec, haiku, console)


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
