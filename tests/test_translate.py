"""Tests for the haiku → MandalaSpec translator and the symbol vocabulary."""

from __future__ import annotations

import pytest

from haikala import haiku as haiku_lib
from haikala.symbols import SYMBOLS, glyphs_for, validate_against
from haikala.translate import (
    PALETTES,
    SIZE_RADIUS,
    MandalaSpec,
    Ring,
    haiku_to_spec,
)


def test_every_curated_token_has_symbols():
    missing = validate_against(haiku_lib.HAIKU)
    assert missing == [], f"tokens with no SYMBOLS entry: {missing}"


def test_haiku_library_size():
    assert len(haiku_lib.HAIKU) >= 100, (
        f"library has {len(haiku_lib.HAIKU)} entries; expected at least 100"
    )


def test_haiku_library_no_originals():
    """Library should be 100% public-domain traditional sources."""
    for h in haiku_lib.HAIKU:
        assert h.author != "Original", f"{h.id} is marked Original — should be traditional"


def test_required_haiku_present():
    required = {
        "old_pond",
        "withered_branch",
        "snow_melts",
        "morning_glory",
        "candle_flame",
    }
    have = {h.id for h in haiku_lib.HAIKU}
    assert required <= have, f"missing required haiku: {required - have}"


def test_unique_ids():
    ids = [h.id for h in haiku_lib.HAIKU]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("h", haiku_lib.HAIKU, ids=lambda h: h.id)
def test_haiku_has_lines_and_tokens(h):
    assert len(h.lines) == 3
    assert all(line.strip() for line in h.lines)
    assert 4 <= len(h.tokens) <= 8


def test_translation_is_deterministic():
    h = haiku_lib.get("old_pond")
    a = haiku_to_spec(h, fold=8, size="medium")
    b = haiku_to_spec(h, fold=8, size="medium")
    assert a == b


def test_center_glyph_from_first_token():
    h = haiku_lib.get("old_pond")
    spec = haiku_to_spec(h, fold=8, size="medium")
    assert spec.center_glyph == glyphs_for(h.tokens[0])[0]


def test_palette_matches_season():
    for h in haiku_lib.HAIKU:
        spec = haiku_to_spec(h)
        assert spec.palette == PALETTES[h.season]


def test_ring_count_matches_non_center_tokens():
    """Each non-center token gets a ring, plus the fixed lotus throne ring."""
    for h in haiku_lib.HAIKU:
        spec = haiku_to_spec(h)
        # 1 lotus throne + (len(tokens) - 1) content rings.
        assert len(spec.rings) == len(h.tokens)


def test_ring_radii_increase_with_band():
    h = haiku_lib.get("old_pond")
    spec = haiku_to_spec(h, fold=8, size="medium")
    band_order = {"inner": 0, "middle": 1, "outer": 2}
    last_band = -1
    last_radius = -1.0
    for ring in spec.rings:
        b = band_order[ring.band]
        if b > last_band:
            last_band = b
            last_radius = -1.0
        assert ring.radius >= last_radius
        last_radius = ring.radius


@pytest.mark.parametrize("fold", [4, 6, 8, 10, 12, 14, 16])
def test_supported_folds(fold):
    h = haiku_lib.get("old_pond")
    spec = haiku_to_spec(h, fold=fold)
    assert spec.fold == fold


@pytest.mark.parametrize("fold", [3, 5, 7, 0, -1, 18, 20])
def test_invalid_folds_raise(fold):
    h = haiku_lib.get("old_pond")
    with pytest.raises(ValueError):
        haiku_to_spec(h, fold=fold)


def test_no_emoji_strips_emoji_from_every_ring():
    """With no_emoji=True, no ring glyph should be in the SMP emoji range."""
    from haikala.symbols import is_emoji
    for h in haiku_lib.HAIKU:
        spec = haiku_to_spec(h, no_emoji=True)
        for ring in spec.rings:
            for g in ring.glyphs:
                assert not is_emoji(g), (
                    f"{h.id}: ring still has emoji glyph {g!r}"
                )
        assert not is_emoji(spec.center_glyph), (
            f"{h.id}: center glyph {spec.center_glyph!r} is still emoji"
        )


def test_no_emoji_assigns_bg_color_to_rings():
    """In no_emoji mode every ring carries a bg_color so cells render as
    color patches rather than thin glyph outlines."""
    h = haiku_lib.get("old_pond")
    spec = haiku_to_spec(h, no_emoji=True)
    for ring in spec.rings:
        assert ring.bg_color, f"ring missing bg_color: {ring}"


def test_emoji_mode_leaves_bg_color_unset():
    """Default (emoji) mode keeps bg_color None to preserve existing look."""
    h = haiku_lib.get("old_pond")
    spec = haiku_to_spec(h, no_emoji=False)
    for ring in spec.rings:
        assert ring.bg_color is None


@pytest.mark.parametrize("size", ["small", "medium", "large", "huge"])
def test_supported_sizes(size):
    h = haiku_lib.get("old_pond")
    spec = haiku_to_spec(h, size=size)
    assert spec.grid_radius == SIZE_RADIUS[size]


def test_default_size_is_huge():
    from haikala.translate import DEFAULT_SIZE
    assert DEFAULT_SIZE == "huge"
    h = haiku_lib.get("old_pond")
    spec = haiku_to_spec(h)
    assert spec.grid_radius == SIZE_RADIUS["huge"]
    assert spec.grid_radius == 20


def test_invalid_size_raises():
    h = haiku_lib.get("old_pond")
    with pytest.raises(ValueError):
        haiku_to_spec(h, size="enormous")


def test_unknown_haiku_id_raises():
    with pytest.raises(KeyError):
        haiku_lib.get("nonexistent")


def test_old_pond_has_frog_inner_ring():
    """Sanity check on the artistic mapping for the canonical poem."""
    spec = haiku_to_spec(haiku_lib.get("old_pond"))
    inner = [r for r in spec.rings if r.band == "inner"]
    assert any("🐸" in r.glyphs for r in inner), "frog should land in the inner band"
