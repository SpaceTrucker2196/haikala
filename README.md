# haikala

A breathing haiku mandala for the terminal.

100 traditional Japanese haiku — Bashō, Buson, Issa, Chiyo-ni, Shiki, Ryōkan,
Onitsura, Kikaku, Moritake, Sōkan — each translated into a radially symmetric
mandala of emoji and Unicode glyphs. The mandala is drawn live in the terminal
and slowly breathes — rings expand on the inhale and contract on the exhale,
color and density modulating with the phase. Six breaths per minute by default.
Press `q` or `Ctrl+C` to leave.

Just run `haikala` with no arguments for a random poem rendered in the default
**huge** size — a roughly 40-tall, circular mandala that wants ~80+ columns of
terminal width.

## Install

```sh
pip install -e .
```

Requires Python 3.11+. Dependencies are `rich` and `click`. Nothing else.

### macOS

The system Python on macOS is 3.9, which is too old. Install a modern
Python with Homebrew, then create a virtualenv:

```sh
brew install python@3.12
python3.12 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/haikala
```

To put `haikala` (and `python3.12`/`pip`) on your `PATH` instead of
calling them through `.venv/bin/`, either activate the venv each
session (`source .venv/bin/activate`) or add Homebrew's unversioned
shims to your shell:

```sh
echo 'export PATH="/opt/homebrew/opt/python@3.12/libexec/bin:$PATH"' >> ~/.zshrc
```

Apple Silicon Macs use `/opt/homebrew`; Intel Macs use `/usr/local`.
Adjust the path accordingly. The default Terminal and iTerm2 both
render the mandala correctly — make sure the window is at least 80
columns wide for the default `huge` size.

## Use

```sh
haikala                                   # random poem, huge size (default)
haikala --list                            # show all 100 curated haiku
haikala --haiku old_pond                  # specific haiku
haikala --random --fold 12 --bpm 4        # explicit, denser symmetry, slower breath
haikala --haiku old_pond --no-animate     # one static frame
haikala --size medium                     # smaller grid that fits 80×24
```

`--fold` accepts 4, 6, 8, or 12. `--size` is one of:

| size     | grid (rows × cols) | notes                              |
|----------|--------------------|------------------------------------|
| `small`  | 15 × 29            | tight terminals                    |
| `medium` | 23 × 45            | fits 80×24                         |
| `large`  | 31 × 61            | roomier                            |
| `huge`   | 41 × 81            | **default** — a ~40-tall circle    |

`--bpm` ranges from 1 to 30; below ~10 it feels meditative, above ~20 it
feels like wind.

## Curated haiku

100 traditional poems, all from public-domain sources. Run `haikala --list`
for the full table. Counts by author:

| poet                | count |
|---------------------|-------|
| Matsuo Bashō        | 30    |
| Yosa Buson          | 25    |
| Kobayashi Issa      | 25    |
| Fukuda Chiyo-ni     | 8     |
| Masaoka Shiki       | 5     |
| Ryōkan Taigu        | 3     |
| Uejima Onitsura     | 1     |
| Takarai Kikaku      | 1     |
| Arakida Moritake    | 1     |
| Yamazaki Sōkan      | 1     |

## Recording

A short recording of the breath cycle for `old_pond` lives at
`docs/old_pond.cast` (asciinema) — placeholder; record locally with:

```sh
asciinema rec docs/old_pond.cast -c 'haikala --haiku old_pond'
```

## Layout

```
haikala/
  haiku.py       — Haiku dataclass + curated library (the words)
  symbols.py     — token → glyph vocabulary (the bridge)
  translate.py   — Haiku + fold + size → MandalaSpec (deterministic)
  mandala.py     — geometric grid composition with N-fold symmetry
  animate.py     — breathing loop using rich.live.Live
  glyphs.py      — narrow helpers for terminal cell widths
  cli.py         — click entrypoint
```

Read in that order. The library, the symbol map, and the translator were
designed together — they are the artistic heart of the tool. The geometry
and the breath are mechanical in comparison.

## Tests

```sh
pip install -e ".[test]"
pytest
```

Tests cover the deterministic parts: token coverage, spec construction,
ring placement, grid invariants. The animation loop is not tested — its
correctness is judged by eye.

## Philosophy

A haiku names three things and lets you feel a fourth. A mandala draws a
cosmos around a center. This tool tries to do both at once, in the
narrow medium of a terminal: choose a poem, sit with it, and watch its
images arrange themselves around an axis and breathe.

When in doubt, the renderer chooses stillness over busyness. The breath
is slow on purpose. The center is always the most essential image of the
poem; rings move outward through subjects, sensations, and atmosphere.

It is not a graphics tool. It is a small contemplative object.
# haikala
