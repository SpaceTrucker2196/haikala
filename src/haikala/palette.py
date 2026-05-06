"""Derive a fractal color palette from a haiku's words.

Each haiku carries `tokens` (the curated essence — the artistic heart of
the spec) and `lines` (the English translation). Both are scanned for
recognized nature/color words; matches are mapped to representative hex
colors and resampled into an 8-stop ramp the fractal painter can use.

Falls back to None when nothing matches, so the caller can pick a named
palette instead.
"""

from __future__ import annotations

import re

from .haiku import Haiku


# Curated mapping of haiku-relevant words to a representative hex color.
# Pulled from natural light, plants, water, weather, creatures, and the
# small set of literal color words. Keys are lowercased.
HAIKU_COLOR_WORDS: dict[str, str] = {
    # celestial
    "moon": "#e6e2c0", "moons": "#e6e2c0", "moonlight": "#e6e2c0",
    "sun": "#ffd06a", "sunlight": "#ffd06a", "sunshine": "#ffd06a",
    "star": "#e8e8ff", "stars": "#e8e8ff",
    # times of day
    "morning": "#ffba70", "dawn": "#ffb88a",
    "noon": "#fff0a0",
    "evening": "#705080", "dusk": "#9060a0", "twilight": "#7050a0",
    "night": "#0a1030", "nightfall": "#0a1030", "midnight": "#000814",
    # weather / sky
    "rain": "#7090b0", "raindrop": "#90b0d0", "drop": "#90b0d0", "drops": "#90b0d0",
    "snow": "#f0f6ff", "snowflake": "#dce8f0",
    "frost": "#cde4f0", "ice": "#b0d8e8",
    "fire": "#ff4d20", "flame": "#ff8030", "ember": "#d04020", "embers": "#d04020",
    "smoke": "#a0a0a8",
    "mist": "#c0c8d0", "fog": "#b0b8c0",
    "wind": "#b0c8d8", "breeze": "#b0c8d8",
    "lightning": "#fff8a0", "storm": "#506070",
    "rainbow": "#c870e0",
    # seasons
    "spring": "#a0d050", "summer": "#80c020",
    "autumn": "#d8702a", "fall": "#d8702a",
    "winter": "#c0d8e8",
    # plants & wood
    "blossom": "#ffb0c8", "blossoms": "#ffb0c8",
    "cherry": "#ff90b0", "plum": "#a04060",
    "petal": "#ffc0d0", "petals": "#ffc0d0",
    "leaf": "#60a040", "leaves": "#60a040",
    "grass": "#7ab050", "grasses": "#7ab050",
    "moss": "#5a8040", "pine": "#306030", "bamboo": "#80a050",
    "willow": "#a0c060", "lotus": "#f0c0d8",
    "lily": "#f8f0f8", "iris": "#7050a0", "fern": "#508040",
    "branch": "#604030", "branches": "#604030",
    "tree": "#3a5a2a", "trees": "#3a5a2a", "wood": "#704030",
    "rice": "#f0e0b0", "wheat": "#e0c870", "field": "#a08840", "fields": "#a08840",
    "seed": "#a08040", "seeds": "#a08040",
    # water
    "sky": "#80b8e0",
    "cloud": "#e8e8f0", "clouds": "#e8e8f0",
    "river": "#3a7aa8", "stream": "#5090c0",
    "water": "#4080b0", "pond": "#3070a0", "lake": "#286490",
    "sea": "#106090", "ocean": "#005078",
    "wave": "#3088b0", "waves": "#3088b0",
    "splash": "#90c8e8", "puddle": "#5080a0",
    "well": "#3a6080",
    # creatures
    "crow": "#101010", "raven": "#101010",
    "frog": "#508040", "frogs": "#508040",
    "fish": "#a0b0c0",
    "bird": "#a08070", "birds": "#a08070",
    "swallow": "#3a3a48", "heron": "#e0e0e0", "crane": "#f0f0f0",
    "duck": "#506050",
    "deer": "#a07050", "horse": "#603020", "monkey": "#806040",
    "snail": "#988868", "spider": "#403030",
    "bee": "#f0c020", "butterfly": "#e8b0e0", "dragonfly": "#5090b0",
    "firefly": "#c8ee88", "fireflies": "#c8ee88",
    "cricket": "#60702a", "cicada": "#a0a020",
    # earth & landscape
    "stone": "#808080", "stones": "#808080",
    "rock": "#707070", "rocks": "#707070",
    "earth": "#604030", "soil": "#604030",
    "mountain": "#506070", "mountains": "#506070",
    "valley": "#5a7050",
    "road": "#888070", "path": "#888070",
    "bridge": "#a08868", "house": "#806030",
    "temple": "#a06848", "garden": "#7a9a48",
    # named colors
    "gold": "#ffc848", "silver": "#c8d0d8",
    "red": "#d83040", "white": "#f8f8f8", "black": "#101010",
    "green": "#40a040", "blue": "#3070b0",
    "purple": "#7040a0", "yellow": "#f0d040",
    "orange": "#ff8830", "pink": "#ff90b0",
    "rose": "#e06080", "scarlet": "#d83040", "crimson": "#aa1830",
    # abstract / atmosphere
    "shadow": "#404048", "shadows": "#404048",
    "warriors": "#603030",
    "dream": "#704080", "dreams": "#704080",
    "memory": "#605880",
    "stillness": "#506070", "silence": "#506070",
}


_WORD_RE = re.compile(r"[a-z]+")


def _hex_to_rgb(hex_: str) -> tuple[int, int, int]:
    h = hex_.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def _luminance(hex_: str) -> float:
    r, g, b = _hex_to_rgb(hex_)
    return 0.299 * r + 0.587 * g + 0.114 * b


def _lerp(a: int, b: int, t: float) -> int:
    return max(0, min(255, round(a + (b - a) * t)))


def _lerp_color(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return _rgb_to_hex(_lerp(r1, r2, t), _lerp(g1, g2, t), _lerp(b1, b2, t))


def _resample_anchors(anchors: list[str], n: int) -> tuple[str, ...]:
    """Linearly interpolate `anchors` into `n` evenly-spaced stops."""
    if n <= 0:
        return ()
    if len(anchors) == 1:
        return tuple([anchors[0]] * n)
    out: list[str] = []
    last = len(anchors) - 1
    for i in range(n):
        pos = i / (n - 1) * last
        lo = int(pos)
        if lo >= last:
            out.append(anchors[-1])
            continue
        out.append(_lerp_color(anchors[lo], anchors[lo + 1], pos - lo))
    return tuple(out)


def _haiku_words(haiku: Haiku) -> list[str]:
    """Tokens first (curated essence), then full-text words, all lowercased."""
    words = [t.lower() for t in haiku.tokens]
    words.extend(_WORD_RE.findall(" ".join(haiku.lines).lower()))
    return words


FOLD_MIN: int = 4
FOLD_MAX: int = 16


def fold_for_haiku(haiku: Haiku) -> int:
    """Choose a rotational symmetry order from the haiku's content.

    Tokens are the curated artistic symbols and weigh more (×1.5 each).
    Words from the English lines contribute the lighter "/3" term — they
    fill in detail without dominating short, evocative haiku.

    The result is rounded to the nearest even integer and clamped to
    [FOLD_MIN, FOLD_MAX]. Even folds keep the mandala symmetric across
    both axes; the cap is set at 16 so the geometry stays distinct on a
    terminal grid (above 16 the rotational sectors start to merge into
    visual mush).
    """
    n_tokens = len(haiku.tokens)
    n_words = sum(len(_WORD_RE.findall(line.lower())) for line in haiku.lines)
    score = round(1.5 * n_tokens + n_words / 3)
    fold = max(FOLD_MIN, min(FOLD_MAX, score))
    if fold % 2 != 0:
        fold += 1
    return min(FOLD_MAX, fold)


def palette_from_haiku(
    haiku: Haiku,
    n_stops: int = 8,
) -> tuple[str, ...] | None:
    """Build an n_stops fractal palette from color words found in the haiku.

    Returns None when no recognized words are present, leaving the caller
    free to fall back to a named palette. The ramp interpolates from a
    deep-night anchor through the matched colors (sorted by luminance) to
    a brightened tip — so the brightest haiku image lights up the
    interior of the Julia set.
    """
    seen: list[str] = []
    seen_set: set[str] = set()
    for w in _haiku_words(haiku):
        color = HAIKU_COLOR_WORDS.get(w)
        if color and color not in seen_set:
            seen.append(color)
            seen_set.add(color)
    if not seen:
        return None
    seen.sort(key=_luminance)
    tip = _lerp_color(seen[-1], "#ffffff", 0.30)
    anchors = ["#020208", *seen, tip]
    return _resample_anchors(anchors, n_stops)
