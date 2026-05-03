"""Haiku → MandalaSpec translation.

Deterministic. Given the same (haiku, fold, size), the spec is identical.
Randomness lives only in the breath animation, not here.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .haiku import Haiku, Season
from .symbols import glyphs_for


@dataclass(frozen=True)
class Ring:
    radius: float            # in y-cell units from center
    glyphs: tuple[str, ...]  # repeated around the ring; index by position
    density: float           # 0..1, baseline fraction of fold-sector slots filled
    color: str               # rich color name
    band: str                # "inner" | "middle" | "outer"
    shape: str = "circle"    # "circle" | "polygon" | "star" | "petal"
    phase: float = 0.0       # rotational offset in radians (breaks "spokes")


@dataclass(frozen=True)
class MandalaSpec:
    fold: int
    rings: tuple[Ring, ...]
    center_glyph: str
    center_color: str
    palette: tuple[str, ...]
    grid_radius: int         # in y-cell units
    haiku_id: str


SUBJECT_TOKENS: frozenset[str] = frozenset({
    # creatures
    "frog", "crow", "worm", "firefly", "cicada", "cuckoo", "dragonfly",
    "butterfly", "cricket", "sparrow", "goose", "duck", "heron", "snail",
    "fish", "octopus", "mosquito", "spider", "deer", "horse", "cat",
    "skylark", "monkey", "fly",
    # celestial / luminous subjects
    "moon", "sun", "star", "candle", "lantern", "bell", "stone", "rock",
    # plants treated as primary subjects
    "morning_glory", "plum", "blossom", "petal", "cherry", "peony",
    "wisteria", "lotus", "iris", "chrysanthemum", "chestnut", "persimmon",
    # human subjects
    "children", "child", "warriors", "messenger", "monk", "traveler",
    "beggar", "woman", "man", "pilgrim", "thief", "buddha",
    # objects with strong subjecthood
    "mask", "comb", "kite", "boat", "fan", "mirror", "cart", "pot",
    # named landforms
    "village", "mountain", "temple", "hut",
})

ACTION_TOKENS: frozenset[str] = frozenset({
    "splash", "stillness", "silence", "transfer", "drift", "passing",
    "echo", "flame", "joy", "kindness", "dream", "memory", "fragrance",
    "flood", "first", "beginning", "loneliness", "longing", "gratitude",
    "sleep", "dance", "climbing", "vanishing", "tears", "coolness",
    "opening", "awakening", "lingering", "freedom", "regret", "secret",
    "irony", "frailty", "patience", "slow", "work", "planting", "return",
    "stretching", "sudden", "breaking", "smile", "dust", "song", "voice",
    "scent", "sound", "prayer", "parting", "sickness", "journey",
    "thaw", "crossing", "ford", "color", "repetition", "current",
    "breath",
})
# everything else falls into "atmosphere" (outer band).


PALETTES: dict[Season, tuple[str, ...]] = {
    "spring":   ("pale_green1", "light_pink1", "medium_spring_green",
                 "pink1", "spring_green3"),
    "summer":   ("sky_blue1", "deep_sky_blue1", "gold1",
                 "light_goldenrod1", "dark_cyan"),
    "autumn":   ("dark_orange", "orange3", "rosy_brown",
                 "tan", "khaki1"),
    "winter":   ("white", "light_steel_blue", "sky_blue3",
                 "grey85", "light_slate_grey"),
    "new_year": ("red1", "gold1", "orange1",
                 "deep_pink2", "white"),
}


SIZE_RADIUS: dict[str, int] = {
    "small": 7,    # 15 × 29 — fits in tight terminals
    "medium": 11,  # 23 × 45 — fits in 80×24
    "large": 15,   # 31 × 61
    "huge": 20,    # 41 × 81 — the default; ~40 cells tall, circular
}

DEFAULT_SIZE: str = "huge"


def _band_for(token: str) -> str:
    if token in SUBJECT_TOKENS:
        return "inner"
    if token in ACTION_TOKENS:
        return "middle"
    return "outer"


def _classify(tokens: tuple[str, ...]) -> dict[str, list[str]]:
    bands: dict[str, list[str]] = {"inner": [], "middle": [], "outer": []}
    for tok in tokens[1:]:
        bands[_band_for(tok)].append(tok)
    return bands


def _radius_band(grid_radius: int, band: str) -> tuple[float, float]:
    if band == "inner":
        return (0.22 * grid_radius, 0.38 * grid_radius)
    if band == "middle":
        return (0.46 * grid_radius, 0.62 * grid_radius)
    return (0.72 * grid_radius, 0.94 * grid_radius)


def _band_density(band: str) -> float:
    return {"inner": 1.0, "middle": 0.88, "outer": 0.74}[band]


def haiku_to_spec(
    haiku: Haiku,
    fold: int = 8,
    size: str = DEFAULT_SIZE,
) -> MandalaSpec:
    if fold not in (4, 6, 8, 12):
        raise ValueError(f"fold must be one of 4, 6, 8, 12; got {fold}")
    if size not in SIZE_RADIUS:
        raise ValueError(f"size must be one of {sorted(SIZE_RADIUS)}; got {size!r}")
    if not haiku.tokens:
        raise ValueError(f"haiku {haiku.id} has no tokens")

    palette = PALETTES[haiku.season]
    grid_radius = SIZE_RADIUS[size]

    center_token = haiku.tokens[0]
    center_glyph = glyphs_for(center_token)[0]
    center_color = palette[0]

    bands = _classify(haiku.tokens)
    rings: list[Ring] = []
    color_cycle = palette[1:] + (palette[0],)
    # Shape per band: inner gets a strong polygon (tetra/hexa/octa/dodecahedral
    # cross-section depending on `fold`), middle gets soft petals, outer gets
    # alternating circle/star so the perimeter feels lacy rather than ringed.
    band_shape_cycles = {
        "inner": ("polygon", "circle", "star"),
        "middle": ("petal", "circle", "polygon"),
        "outer": ("star", "circle", "petal"),
    }
    color_idx = 0
    ring_idx = 0

    for band_name in ("inner", "middle", "outer"):
        toks = bands[band_name]
        if not toks:
            continue
        rmin, rmax = _radius_band(grid_radius, band_name)
        n = len(toks)
        cycle = band_shape_cycles[band_name]
        for i, tok in enumerate(toks):
            r = (rmin + rmax) / 2 if n == 1 else rmin + (rmax - rmin) * i / (n - 1)
            color = color_cycle[color_idx % len(color_cycle)]
            color_idx += 1
            shape = cycle[ring_idx % len(cycle)]
            # Half-sector offset per ring so adjacent rings don't share radial
            # spokes. Modulo 2π/fold keeps it within one fold-sector.
            phase = (ring_idx * math.pi / fold) % (2 * math.pi / fold)
            ring_idx += 1
            rings.append(Ring(
                radius=r,
                glyphs=glyphs_for(tok),
                density=_band_density(band_name),
                color=color,
                band=band_name,
                shape=shape,
                phase=phase,
            ))

    return MandalaSpec(
        fold=fold,
        rings=tuple(rings),
        center_glyph=center_glyph,
        center_color=center_color,
        palette=palette,
        grid_radius=grid_radius,
        haiku_id=haiku.id,
    )
