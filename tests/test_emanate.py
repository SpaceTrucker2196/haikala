"""Tests for the emanating-hue wave with cycling angular symmetry."""

from __future__ import annotations

import math

from haikala.animate import EMANATE_FOLDS, make_emanate_field


def test_outside_band_returns_zero():
    """Cells far from the wavefront keep their original color."""
    field = make_emanate_field(cx=20, cy=10, t=0.0, period=5.0, max_r=15.0)
    # At t=0, wave_r is at the center (radius 0). Far-out point should be 0.
    assert field(40, 10) == 0.0


def test_at_wavefront_band_returns_positive():
    """Cells inside the moving annulus get a positive shift; the
    wavefront sweeps outward as t advances."""
    period = 5.0
    max_r = 20.0
    # At t = period/4, wave_r ≈ 5. Pick a point on the +x axis at r=5
    # (so dx=10 in screen coords because x is stretched 2×).
    field = make_emanate_field(cx=20, cy=10, t=period / 4, period=period, max_r=max_r)
    # Probe along theta=0 (right of center).
    samples = [field(20 + 2 * round(r), 10) for r in range(0, 20)]
    # At least one sample should be strictly positive (we're inside band
    # somewhere along the radius).
    assert any(s > 0.0 for s in samples), samples


def test_fold_changes_between_cycles():
    """Each new pulse uses a different angular fold — sample the angular
    modulation at two cycle boundaries and confirm they differ."""
    period = 5.0
    max_r = 20.0
    cx, cy = 30, 15

    def angular_signature(t: float) -> tuple[float, ...]:
        # Sample at the wavefront radius at 8 angles.
        f = make_emanate_field(cx, cy, t=t, period=period, max_r=max_r)
        # Wave radius at this t:
        cycle = t / period
        wave_r = (cycle - int(cycle)) * max_r
        out = []
        for k in range(8):
            theta = 2.0 * math.pi * k / 8
            x = cx + round(wave_r * math.cos(theta) * 2)
            y = cy + round(wave_r * math.sin(theta))
            out.append(round(f(x, y), 1))
        return tuple(out)

    # Mid-pulse on cycle 0 and cycle 1 should sample different folds.
    sig0 = angular_signature(period * 0.5)            # cycle 0, fold = EMANATE_FOLDS[0]
    sig1 = angular_signature(period * 1.5)            # cycle 1, fold = EMANATE_FOLDS[1]
    assert sig0 != sig1, (
        f"angular pattern unchanged between pulses: {sig0} == {sig1}"
    )


def test_field_zero_when_max_r_is_zero():
    """Defensive: max_r=0 must not divide-by-zero or NaN."""
    f = make_emanate_field(cx=5, cy=5, t=1.0, period=5.0, max_r=0.0)
    assert f(0, 0) == 0.0
    assert f(10, 10) == 0.0


def test_emanate_folds_are_within_supported_range():
    """The cycle should stay within the spec's supported fold range so
    visual symmetry remains coherent."""
    for f in EMANATE_FOLDS:
        assert 2 <= f <= 16
