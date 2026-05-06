"""Tests for haiku-derived fractal palettes and symmetry."""

from __future__ import annotations

import pytest

from haikala import haiku as haiku_lib
from haikala.haiku import Haiku
from haikala.palette import (
    FOLD_MAX,
    FOLD_MIN,
    HAIKU_COLOR_WORDS,
    fold_for_haiku,
    palette_from_haiku,
)
from haikala.translate import haiku_to_spec


def test_palette_for_old_pond_picks_water_colors():
    """The old pond haiku has 'pond', 'frog', 'water', 'splash' in its tokens
    plus 'pond' / 'water' in lines — every match should be a known word."""
    h = haiku_lib.get("old_pond")
    pal = palette_from_haiku(h)
    assert pal is not None
    assert len(pal) == 8
    # Each stop is a hex string.
    for stop in pal:
        assert stop.startswith("#") and len(stop) == 7
    # Ramp must be monotonic non-decreasing in luminance (we sort matches).
    def lum(h):
        r = int(h[1:3], 16); g = int(h[3:5], 16); b = int(h[5:7], 16)
        return 0.299 * r + 0.587 * g + 0.114 * b
    lums = [lum(s) for s in pal]
    assert lums == sorted(lums), f"ramp not monotonic: {lums}"


def test_palette_returns_none_when_no_matches():
    """Synthetic haiku with no recognized color words → None (caller falls
    back to a named palette)."""
    from haikala.haiku import Haiku
    fake = Haiku(
        id="fake",
        lines=("xyzzy plugh", "qwerty asdf", "zxcv mnbv"),
        author="nobody", season="spring",
        tokens=("xyzzy", "plugh", "qwerty"),
    )
    assert palette_from_haiku(fake) is None


def test_palette_size_matches_fractal_glyph_count():
    """Default n_stops must match the fractal painter's iteration palette."""
    from haikala.mandala import _FRACTAL_GLYPHS
    h = haiku_lib.get("old_pond")
    pal = palette_from_haiku(h)
    assert pal is not None
    assert len(pal) == len(_FRACTAL_GLYPHS)


def test_every_curated_haiku_yields_a_palette_or_none():
    """Smoke test: never raise. Most curated haiku will hit a color word."""
    hits = 0
    for h in haiku_lib.HAIKU:
        pal = palette_from_haiku(h)
        if pal is not None:
            hits += 1
            assert len(pal) == 8
    # Curated tokens are nature words by design — nearly all should match.
    assert hits >= len(haiku_lib.HAIKU) * 0.9, (
        f"only {hits}/{len(haiku_lib.HAIKU)} haiku produced a palette; "
        "the color-word dictionary may be missing common terms"
    )


def test_color_words_are_valid_hex():
    """Every entry in the dictionary must be a 7-char #rrggbb hex string."""
    for word, color in HAIKU_COLOR_WORDS.items():
        assert color.startswith("#") and len(color) == 7, (
            f"word {word!r} has invalid color {color!r}"
        )
        int(color[1:], 16)  # raises if not hex


def test_fold_for_haiku_in_range_and_even():
    """Every curated haiku gets an even fold inside [FOLD_MIN, FOLD_MAX]."""
    for h in haiku_lib.HAIKU:
        f = fold_for_haiku(h)
        assert FOLD_MIN <= f <= FOLD_MAX, f"{h.id} → fold={f} out of range"
        assert f % 2 == 0, f"{h.id} → fold={f} not even"


def test_fold_grows_with_token_count():
    """A haiku with more tokens should get a fold ≥ a haiku with fewer."""
    short = Haiku(
        id="short", lines=("a", "b", "c"),
        author="x", season="spring",
        tokens=("moon", "stillness"),
    )
    long = Haiku(
        id="long",
        lines=(
            "across many fields and rivers",
            "deep mountains echo old prayers",
            "wind drifts through stones",
        ),
        author="x", season="spring",
        tokens=("moon", "river", "mountain", "wind", "stone",
                "prayer", "echo", "stillness"),
    )
    assert fold_for_haiku(long) >= fold_for_haiku(short)


def test_fold_for_haiku_caps_at_max():
    """A bombastically long haiku is still capped at FOLD_MAX."""
    huge = Haiku(
        id="huge",
        lines=(
            "many many many many many many many words here",
            "and many many many many many many more here",
            "and even more many many many many many words",
        ),
        author="x", season="spring",
        tokens=tuple(["x"] * 30),
    )
    assert fold_for_haiku(huge) == FOLD_MAX


def test_fold_for_haiku_floors_at_min():
    """A minimal haiku still gets at least FOLD_MIN."""
    tiny = Haiku(
        id="tiny",
        lines=("a", "b", "c"),
        author="x", season="spring",
        tokens=("x",),
    )
    assert fold_for_haiku(tiny) >= FOLD_MIN


@pytest.mark.parametrize("fold", [4, 6, 8, 10, 12, 14, 16])
def test_haiku_to_spec_accepts_extended_folds(fold):
    """The validator must allow every even fold in [4, 16]."""
    h = haiku_lib.get("old_pond")
    spec = haiku_to_spec(h, fold=fold)
    assert spec.fold == fold


@pytest.mark.parametrize("fold", [3, 5, 18, 0, -2])
def test_haiku_to_spec_rejects_invalid_folds(fold):
    h = haiku_lib.get("old_pond")
    with pytest.raises(ValueError):
        haiku_to_spec(h, fold=fold)
