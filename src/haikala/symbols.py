"""Token → glyph vocabulary.

Three glyph layers, deliberately mixed:
  - emoji (🐸 🦋 🐌): bright, semantic, the "subjects" of the poem.
  - unicode symbols (☾ ✦ ⬢ ❀): alchemical / astronomical / floral "essences."
  - box-drawing & dot characters (─ ┄ · ˙): the negative-space connective tissue.

Every token used by every haiku in haiku.HAIKU has an entry here.
"""

from __future__ import annotations

SYMBOLS: dict[str, tuple[str, ...]] = {
    # --- water ----------------------------------------------------------
    "pond":      ("💧", "◯", "○", "～"),
    "water":     ("💧", "～", "≈", "∽"),
    "splash":    ("💦", "✦", "✧", "·"),
    "well":      ("💧", "◉", "◎", "○"),
    "flood":     ("🌊", "～", "≈", "∿"),
    "sea":       ("🌊", "≈", "～", "∿"),
    "ocean":     ("🌊", "≈", "～", "∿"),
    "river":     ("🌊", "～", "∽", "∿"),
    "tide":      ("🌊", "～", "∿", "≈"),
    "ice":       ("🧊", "◇", "·", "˙"),
    "dew":       ("💧", "·", "˙", "◦"),
    "frost":     ("🧊", "·", "˙", "❅"),
    "rain":      ("🌧", "·", "│", "ı"),
    "mist":      ("🌫", "·", "˙", "˜"),
    "cloud":     ("☁️", "◌", "○", "·"),
    "pool":      ("💧", "◯", "○", "·"),
    "shore":     ("🌊", "─", "·", "˙"),
    "thaw":      ("💧", "·", "～", "˙"),
    "ford":      ("🌊", "～", "·", "˙"),

    # --- creatures ------------------------------------------------------
    "frog":      ("🐸", "🪷", "✿", "·"),
    "crow":      ("🦅", "🐦", "✦", "⬢"),
    "worm":      ("🐛", "～", "˜", "·"),
    "firefly":   ("🌟", "✺", "✦", "˚"),
    "cicada":    ("🦗", "⊛", "·", "˙"),
    "cuckoo":    ("🐦", "∽", "·", "˙"),
    "dragonfly": ("🐝", "✺", "✦", "·"),
    "butterfly": ("🦋", "🌸", "✤", "·"),
    "cricket":   ("🦗", "⊛", "·", "˙"),
    "sparrow":   ("🐦", "✦", "·", "˙"),
    "goose":     ("🪿", "∨", "·", "˙"),
    "duck":      ("🦆", "⌒", "·", "˙"),
    "heron":     ("🪶", "│", "·", "˙"),
    "snail":     ("🐌", "◉", "○", "·"),
    "fish":      ("🐟", "🐠", "≈", "˜"),
    "octopus":   ("🐙", "✱", "·", "˙"),
    "mosquito":  ("🦟", "·", "˙", "·"),
    "spider":    ("🕷", "🕸", "·", "˙"),
    "deer":      ("🦌", "⌬", "·", "˙"),
    "horse":     ("🐎", "⊏", "·", "˙"),
    "cat":       ("🐈", "🐾", "◑", "·"),
    "skylark":   ("🐦", "✦", "·", "˙"),
    "monkey":    ("🐒", "◔", "·", "˙"),
    "fly":       ("🪰", "·", "˙", "·"),

    # --- plants ---------------------------------------------------------
    "branch":    ("🌿", "┄", "─", "╴"),
    "grass":     ("🌾", "│", "┊", "·"),
    "morning_glory": ("🌺", "✿", "❀", "❁"),
    "plum":      ("🌸", "✿", "❁", "❀"),
    "blossom":   ("🌸", "🌼", "✿", "❀"),
    "petal":     ("🌸", "✿", "·", "˙"),
    "vine":      ("🌿", "∿", "～", "·"),
    "chestnut":  ("🌰", "●", "◉", "•"),
    "cherry":    ("🌸", "🍒", "✿", "❀"),
    "willow":    ("🌿", "┊", "│", "·"),
    "peony":     ("🌺", "❀", "✿", "·"),
    "wisteria":  ("🌸", "❁", "·", "˙"),
    "leaf":      ("🍃", "🍂", "⌒", "·"),
    "persimmon": ("🍑", "●", "◉", "·"),
    "lotus":     ("🪷", "❀", "○", "·"),
    "bamboo":    ("🎋", "│", "┊", "·"),
    "pine":      ("🌲", "⋆", "·", "˙"),
    "iris":      ("🌷", "❁", "·", "˙"),
    "chrysanthemum": ("🌼", "✿", "❀", "·"),
    "mustard":   ("🌼", "·", "˙", "✿"),
    "radish":    ("🌱", "│", "·", "˙"),
    "tree":      ("🌳", "│", "┊", "·"),
    "rose":      ("🌹", "❀", "·", "˙"),

    # --- weather / sky --------------------------------------------------
    "snow":      ("🌨", "❄️", "❅", "·"),
    "moon":      ("🌙", "🌕", "☾", "○"),
    "star":      ("⭐️", "🌟", "✦", "✧"),
    "milky_way": ("🌌", "✨", "·", "˙"),
    "sun":       ("☀️", "🌞", "○", "·"),
    "dawn":      ("🌅", "○", "◌", "·"),
    "dusk":      ("🌆", "·", "˙", "◦"),
    "evening":   ("🌆", "·", "˙", "◦"),
    "twilight":  ("🌆", "·", "˙", "◦"),
    "night":     ("🌙", "·", "˙", "✦"),
    "morning":   ("🌅", "○", "◌", "·"),
    "horizon":   ("🌅", "─", "━", "┄"),
    "mountain":  ("🏔", "⛰️", "▲", "△"),
    "wind":      ("🌬", "∽", "～", "·"),
    "breeze":    ("🌬", "∽", "·", "˙"),
    "lightning": ("⚡️", "🌩", "⌇", "✦"),
    "color":     ("🌈", "·", "˙", "◦"),
    "white":     (" ", "·", "˙"),
    "dark":      ("·", "˙", "•"),
    "smoke":     ("∽", "·", "˙"),
    "breath":    ("🌬", "∽", "·", "˙"),
    "warmth":    ("🌞", "☼", "·", "˙"),
    "valley":    ("🏞", "∨", "·", "˙"),
    "hill":      ("⛰", "△", "·", "˙"),

    # --- fire / light ---------------------------------------------------
    "candle":    ("🕯", "✦", "·", "˙"),
    "flame":     ("🔥", "✦", "✧", "·"),
    "lantern":   ("🏮", "◯", "·", "˙"),

    # --- people ---------------------------------------------------------
    "village":   ("🏘", "⌂", "·", "◦"),
    "children":  ("🧒", "·", "˙", "✦"),
    "child":     ("🧒", "·", "˙", "✦"),
    "warriors":  ("⚔️", "┼", "╋", "╳"),
    "messenger": ("🏃", "→", "·", "˙"),
    "monk":      ("🧘", "○", "·", "˙"),
    "traveler":  ("🚶", "→", "·", "˙"),
    "beggar":    ("·", "˙", "○"),
    "woman":     ("👩", "○", "·", "˙"),
    "man":       ("👨", "○", "·", "˙"),
    "pilgrim":   ("🚶", "→", "·", "˙"),
    "thief":     ("·", "˙", "˚"),
    "bell":      ("🔔", "☉", "◉", "○"),
    "stone":     ("🪨", "◉", "●", "○"),

    # --- places / objects -----------------------------------------------
    "temple":    ("⛩️", "🛕", "⌂", "△"),
    "gate":      ("⛩️", "∏", "·", "˙"),
    "road":      ("🛣", "┄", "─", "·"),
    "roof":      ("🏠", "∧", "·", "˙"),
    "hut":       ("🛖", "⌂", "·", "˙"),
    "boat":      ("⛵️", "⌒", "·", "˙"),
    "sail":      ("⛵️", "△", "·", "˙"),
    "mask":      ("🎭", "○", "·", "˙"),
    "fan":       ("🪭", "⌒", "·", "˙"),
    "garden":    ("🌷", "🌼", "✿", "·"),
    "field":     ("🌾", "│", "·", "˙"),
    "window":    ("🪟", "□", "·", "˙"),
    "basket":    ("🧺", "⌣", "·", "˙"),
    "pipe":      ("∼", "·", "˙"),
    "comb":      ("│", "·", "˙"),
    "mirror":    ("🪞", "◯", "○", "·"),
    "cart":      ("🛒", "◉", "·", "˙"),
    "pot":       ("🪴", "⌒", "·", "˙"),
    "island":    ("🏝", "◬", "·", "˙"),
    "stable":    ("🏠", "⌂", "·", "˙"),
    "rock":      ("🪨", "◉", "●", "○"),
    "kite":      ("🪁", "◇", "·", "˙"),
    "flag":      ("🚩", "△", "·", "˙"),
    "bay":       ("🌊", "⌒", "·", "˙"),
    "sword":     ("🗡", "│", "·", "˙"),

    # --- actions / abstractions -----------------------------------------
    "stillness": (" ", "·", "˙"),
    "silence":   (" ", "·", "˙"),
    "joy":       ("✦", "✧", "·"),
    "kindness":  ("✿", "·", "˙"),
    "dream":     ("∽", "·", "˙"),
    "memory":    ("˙", "·", "∙"),
    "transfer":  ("→", "·", "˙"),
    "fragrance": ("∽", "～", "·"),
    "drift":     ("∿", "～", "·"),
    "passing":   ("·", "˙", "◦"),
    "echo":      ("∙", "·", "˙"),
    "first":     ("◉", "○", "·"),
    "beginning": ("◌", "○", "·"),
    "loneliness":("·", "˙", " "),
    "journey":   ("→", "·", "˙"),
    "year":      ("○", "◌", "·"),
    "sickness":  ("·", "˙", " "),
    "prayer":    ("·", "˙", "○"),
    "parting":   ("·", "˙", "→"),
    "song":      ("∽", "·", "˙"),
    "voice":     ("∽", "·", "˙"),
    "scent":     ("∽", "·", "˙"),
    "sound":     ("∽", "·", "˙"),
    "longing":   ("·", "˙", "◦"),
    "gratitude": ("✿", "·", "˙"),
    "sleep":     ("·", "˙", " "),
    "dance":     ("✦", "·", "˙"),
    "climbing":  ("↑", "·", "˙"),
    "vanishing": ("·", "˙", " "),
    "withered":  ("╴", "·", "˙"),
    "world":     ("○", "◌", "·"),
    "tears":     ("·", "˙", "·"),
    "coolness":  ("❅", "·", "˙"),
    "opening":   ("○", "◌", "·"),
    "awakening": ("✦", "·", "˙"),
    "lingering": ("∽", "·", "˙"),
    "current":   ("～", "∽", "·"),
    "freedom":   ("✦", "·", "˙"),
    "regret":    ("·", "˙", " "),
    "secret":    ("·", "˙", " "),
    "buddha":    ("○", "◯", "·"),
    "hell":      ("·", "˙", "•"),
    "irony":     ("·", "˙", " "),
    "frailty":   ("·", "˙", " "),
    "patience":  ("·", "˙", " "),
    "slow":      ("·", "˙", " "),
    "work":      ("│", "·", "˙"),
    "planting":  ("│", "·", "˙"),
    "return":    ("←", "·", "˙"),
    "stretching":("→", "·", "˙"),
    "sudden":    ("✦", "·", "˙"),
    "breaking":  ("·", "˙", "·"),
    "rice":      ("│", "·", "˙"),
    "mud":       ("·", "•", "˙"),
    "hair":      ("│", "·", "˙"),
    "face":      ("○", "·", "˙"),
    "dust":      ("·", "˙", "·"),
    "crossing":  ("┼", "·", "˙"),
    "repetition":("·", "˙", "·"),
    "smile":     ("⌣", "·", "˙"),
    "ash":       ("·", "˙", "·"),

    # --- paths / structure ----------------------------------------------
    "path":      ("┄", "─", "·"),
    "bridge":    ("═", "─", "┄"),

    # --- seasonal -------------------------------------------------------
    "spring":    ("🌸", "🌷", "✿", "❀"),
    "summer":    ("🌞", "🌻", "☼", "✦"),
    "autumn":    ("🍁", "🍂", "⌬", "·"),
    "winter":    ("🌨", "❄", "❅", "·"),
    "new_year":  ("🎍", "🎋", "◉", "✦"),
}


def glyphs_for(token: str) -> tuple[str, ...]:
    if token not in SYMBOLS:
        raise KeyError(f"no glyph mapping for token {token!r}")
    return SYMBOLS[token]


_VS16 = "️"  # variation selector-16: "render preceding char with emoji presentation"


def is_emoji(glyph: str) -> bool:
    """Return True if the glyph is rendered with emoji (color bitmap)
    presentation, which most terminals draw with their own embedded
    palette — ignoring our `cell.color` and `cell.bg_color`. Emoji are
    detected via VS-16 or by codepoint in the SMP emoji/pictograph planes.
    BMP geometric/dingbat symbols (✦ ❀ ◯ …) are *not* emoji and remain
    selectable in `--no-emoji` mode because they honor ANSI styling.
    """
    if _VS16 in glyph:
        return True
    for ch in glyph:
        if ord(ch) >= 0x1F300:
            return True
    return False


def text_glyphs_for(token: str) -> tuple[str, ...]:
    """Like `glyphs_for`, but with emoji entries removed. Falls back to a
    generic outline circle if a token's vocabulary is entirely emoji."""
    filtered = tuple(g for g in glyphs_for(token) if not is_emoji(g))
    return filtered or ("◯",)


def is_wide(glyph: str) -> bool:
    """Return True if the glyph occupies two terminal columns.

    Detection layers:
      1. VS-16 (U+FE0F) requests emoji presentation. A char tagged with VS-16
         is rendered wide on every modern terminal that supports emoji,
         regardless of the underlying codepoint's default width. Use VS-16 in
         the symbol table when you want a BMP char like `⭐️` `❄️` `⛩️` `☀️`
         to occupy two cells (the symbol entry must include `\\uFE0F`).
      2. Codepoints in the emoji / pictograph planes (>= U+1F300) are wide.
      3. CJK Unified Ideographs and related ranges are wide.
      4. Hangul syllables and fullwidth forms are wide.
    """
    if _VS16 in glyph:
        return True
    for ch in glyph:
        cp = ord(ch)
        if cp >= 0x1F300:
            return True
        if 0x2E80 <= cp <= 0x9FFF:
            return True
        if 0xAC00 <= cp <= 0xD7A3:
            return True
        if 0xFF00 <= cp <= 0xFF60:
            return True
    return False


def validate_against(haikus) -> list[str]:
    """Return a list of tokens used in haikus that have no SYMBOLS entry."""
    missing = []
    for h in haikus:
        for tok in h.tokens:
            if tok not in SYMBOLS:
                missing.append(f"{h.id}:{tok}")
    return missing
