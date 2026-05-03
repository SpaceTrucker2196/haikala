"""Curated haiku library — 100 traditional haiku.

Poets: Matsuo Bashō, Yosa Buson, Kobayashi Issa, Fukuda Chiyo-ni, Masaoka
Shiki, Ryōkan Taigu, Uejima Onitsura, Takarai Kikaku, Arakida Moritake,
Yamazaki Sōkan. All authors are 17th–early-20th century — long out of
copyright. The English forms here are minimal, common-knowledge
translations of the source images; the artistic decisions are the
hand-picked `tokens`, which the renderer maps to glyphs.

Token order matters: token[0] is the most "essential" image — it becomes
the mandala's center. Subsequent tokens fan outward through
subjects → sensations → atmosphere.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Season = Literal["spring", "summer", "autumn", "winter", "new_year"]


@dataclass(frozen=True)
class Haiku:
    id: str
    lines: tuple[str, str, str]
    author: str
    season: Season
    tokens: tuple[str, ...]


HAIKU: tuple[Haiku, ...] = (
    # ===================== Bashō (30) ===================================
    Haiku(
        id="old_pond",
        lines=("old pond—", "a frog leaps in", "the sound of water"),
        author="Matsuo Bashō", season="spring",
        tokens=("pond", "frog", "splash", "water", "stillness"),
    ),
    Haiku(
        id="withered_branch",
        lines=("on a withered branch", "a crow has settled—", "autumn nightfall"),
        author="Matsuo Bashō", season="autumn",
        tokens=("crow", "branch", "evening", "stillness"),
    ),
    Haiku(
        id="summer_grass",
        lines=("summer grasses—", "all that remains", "of warriors' dreams"),
        author="Matsuo Bashō", season="summer",
        tokens=("grass", "warriors", "dream", "memory"),
    ),
    Haiku(
        id="first_snow_bridge",
        lines=("first snow", "falling on the half-finished", "bridge"),
        author="Matsuo Bashō", season="winter",
        tokens=("snow", "bridge", "stillness", "first"),
    ),
    Haiku(
        id="basho_journey_dreams",
        lines=("sick on a journey", "my dreams wander", "the withered fields"),
        author="Matsuo Bashō", season="winter",
        tokens=("dream", "journey", "field", "withered", "sickness"),
    ),
    Haiku(
        id="basho_cicada_rock",
        lines=("such stillness—", "the cicada's voice", "soaks into the rocks"),
        author="Matsuo Bashō", season="summer",
        tokens=("cicada", "voice", "stone", "silence", "summer"),
    ),
    Haiku(
        id="basho_lonely_road",
        lines=("this road—", "no one travels it", "autumn evening"),
        author="Matsuo Bashō", season="autumn",
        tokens=("road", "traveler", "evening", "loneliness", "autumn"),
    ),
    Haiku(
        id="basho_sea_duck_voice",
        lines=("the sea darkens—", "a wild duck's call", "faintly white"),
        author="Matsuo Bashō", season="winter",
        tokens=("sea", "duck", "voice", "dusk", "white"),
    ),
    Haiku(
        id="basho_temple_bell_blossom",
        lines=("the bell fades", "the scent of blossoms ringing—", "evening"),
        author="Matsuo Bashō", season="spring",
        tokens=("bell", "blossom", "fragrance", "lingering", "evening"),
    ),
    Haiku(
        id="basho_octopus_pot",
        lines=("octopus traps—", "fleeting dreams", "under the summer moon"),
        author="Matsuo Bashō", season="summer",
        tokens=("octopus", "pot", "dream", "moon", "summer"),
    ),
    Haiku(
        id="basho_wild_sea_stars",
        lines=("a wild sea—", "and stretched across to Sado", "the river of stars"),
        author="Matsuo Bashō", season="autumn",
        tokens=("sea", "milky_way", "star", "island", "wind"),
    ),
    Haiku(
        id="basho_cuckoo_clouds",
        lines=("a cuckoo cries—", "and through the clouds", "vanishes"),
        author="Matsuo Bashō", season="summer",
        tokens=("cuckoo", "cloud", "voice", "vanishing", "summer"),
    ),
    Haiku(
        id="basho_moon_treetops",
        lines=("the moon swift overhead—", "treetops still", "wet with rain"),
        author="Matsuo Bashō", season="autumn",
        tokens=("moon", "tree", "rain", "stillness", "night"),
    ),
    Haiku(
        id="basho_monkey_mask",
        lines=("year after year", "on the monkey's face", "a monkey's mask"),
        author="Matsuo Bashō", season="new_year",
        tokens=("monkey", "mask", "year", "repetition", "new_year"),
    ),
    Haiku(
        id="basho_winter_solitude",
        lines=("winter solitude—", "in a world of one color", "the sound of wind"),
        author="Matsuo Bashō", season="winter",
        tokens=("winter", "color", "wind", "loneliness", "sound"),
    ),
    Haiku(
        id="basho_skylark_moor",
        lines=("a skylark singing—", "all day long", "and never enough"),
        author="Matsuo Bashō", season="spring",
        tokens=("skylark", "song", "field", "freedom", "spring"),
    ),
    Haiku(
        id="basho_spring_departs",
        lines=("spring departing—", "birds cry, and in the eyes", "of fishes are tears"),
        author="Matsuo Bashō", season="spring",
        tokens=("spring", "sparrow", "fish", "tears", "parting"),
    ),
    Haiku(
        id="basho_snowy_morning",
        lines=("a snowy morning—", "by myself", "chewing on dried salmon"),
        author="Matsuo Bashō", season="winter",
        tokens=("snow", "morning", "fish", "loneliness", "winter"),
    ),
    Haiku(
        id="basho_cherry_petals",
        lines=("from all four sides", "cherry petals blowing in—", "Lake Biwa"),
        author="Matsuo Bashō", season="spring",
        tokens=("cherry", "blossom", "drift", "wind", "spring"),
    ),
    Haiku(
        id="basho_lightning",
        lines=("lightning flash—", "into the darkness", "a night-heron's cry"),
        author="Matsuo Bashō", season="summer",
        tokens=("lightning", "heron", "voice", "dark", "summer"),
    ),
    Haiku(
        id="basho_plum_dawn",
        lines=("the scent of plum—", "and the sun rises", "over the mountain path"),
        author="Matsuo Bashō", season="spring",
        tokens=("plum", "sun", "mountain", "path", "fragrance"),
    ),
    Haiku(
        id="basho_harvest_moon_gate",
        lines=("the harvest moon—", "the tide rises", "to my gate"),
        author="Matsuo Bashō", season="autumn",
        tokens=("moon", "tide", "gate", "autumn", "water"),
    ),
    Haiku(
        id="basho_windy_pine",
        lines=("a wind in the pines—", "and somewhere, far off", "an axe falling"),
        author="Matsuo Bashō", season="autumn",
        tokens=("pine", "wind", "sound", "autumn", "echo"),
    ),
    Haiku(
        id="basho_wisteria_evening",
        lines=("wisteria flowers—", "in the evening light", "the crane's white"),
        author="Matsuo Bashō", season="spring",
        tokens=("wisteria", "evening", "white", "fragrance", "breeze"),
    ),
    Haiku(
        id="basho_spider_dew",
        lines=("a spider in the doorway—", "morning dew", "trembles"),
        author="Matsuo Bashō", season="autumn",
        tokens=("spider", "dew", "morning", "garden", "stillness"),
    ),
    Haiku(
        id="basho_autumn_window",
        lines=("autumn wind—", "through an open window", "the lamp wavers"),
        author="Matsuo Bashō", season="autumn",
        tokens=("wind", "autumn", "window", "lantern", "longing"),
    ),
    Haiku(
        id="basho_snow_crow",
        lines=("morning snow—", "a single crow", "without a sound"),
        author="Matsuo Bashō", season="winter",
        tokens=("crow", "snow", "morning", "silence", "winter"),
    ),
    Haiku(
        id="basho_snowy_field_traveler",
        lines=("snowy field—", "a single traveler's prints", "and then nothing"),
        author="Matsuo Bashō", season="winter",
        tokens=("snow", "field", "traveler", "path", "winter"),
    ),
    Haiku(
        id="basho_butterfly_dream",
        lines=("am I a butterfly", "dreaming I am Bashō—", "spring afternoon"),
        author="Matsuo Bashō", season="spring",
        tokens=("butterfly", "dream", "drift", "awakening", "spring"),
    ),
    Haiku(
        id="basho_temple_bell_flowers",
        lines=("the temple bell stops—", "but the sound keeps coming", "out of the flowers"),
        author="Matsuo Bashō", season="spring",
        tokens=("bell", "blossom", "lingering", "sound", "temple"),
    ),

    # ===================== Buson (25) ===================================
    Haiku(
        id="candle_flame",
        lines=("the light of a candle", "is transferred to another—", "spring twilight"),
        author="Yosa Buson", season="spring",
        tokens=("candle", "flame", "transfer", "twilight"),
    ),
    Haiku(
        id="autumn_moon",
        lines=("autumn moon—", "a worm digs silently", "into a chestnut"),
        author="Yosa Buson", season="autumn",
        tokens=("moon", "worm", "chestnut", "silence"),
    ),
    Haiku(
        id="buson_peony_cart",
        lines=("a heavy cart rumbles by—", "and the peonies", "tremble"),
        author="Yosa Buson", season="summer",
        tokens=("peony", "cart", "summer", "sound", "opening"),
    ),
    Haiku(
        id="buson_spring_rain_cat",
        lines=("spring rain—", "a girl is teaching", "the cat to dance"),
        author="Yosa Buson", season="spring",
        tokens=("rain", "cat", "dance", "woman", "spring"),
    ),
    Haiku(
        id="buson_summer_river_horse",
        lines=("a summer river—", "horses crossing one by one,", "each with a moon"),
        author="Yosa Buson", season="summer",
        tokens=("river", "horse", "moon", "summer", "crossing"),
    ),
    Haiku(
        id="buson_heron_breeze",
        lines=("evening breeze—", "water laps", "against the heron's legs"),
        author="Yosa Buson", season="summer",
        tokens=("heron", "breeze", "water", "evening", "summer"),
    ),
    Haiku(
        id="buson_willow_pool",
        lines=("the willow tree", "has thinned out", "the muddy pool"),
        author="Yosa Buson", season="spring",
        tokens=("willow", "pool", "mud", "stillness", "spring"),
    ),
    Haiku(
        id="buson_spring_road_basket",
        lines=("along the muddy road", "in a passing basket—", "young cockles"),
        author="Yosa Buson", season="spring",
        tokens=("basket", "road", "rain", "spring", "mud"),
    ),
    Haiku(
        id="buson_wife_comb",
        lines=("a sudden chill—", "in our room, my dead wife's comb", "under my heel"),
        author="Yosa Buson", season="autumn",
        tokens=("comb", "woman", "regret", "longing", "autumn"),
    ),
    Haiku(
        id="buson_pawnshop_trees",
        lines=("two villages", "one pawnshop—", "leafless trees"),
        author="Yosa Buson", season="winter",
        tokens=("tree", "village", "withered", "winter", "loneliness"),
    ),
    Haiku(
        id="buson_morning_haze",
        lines=("morning haze—", "the village still asleep,", "and a bridge"),
        author="Yosa Buson", season="spring",
        tokens=("mist", "village", "bridge", "morning", "stillness"),
    ),
    Haiku(
        id="buson_short_night_peony",
        lines=("the short night—", "by the riverbank a peony", "blooms wide"),
        author="Yosa Buson", season="summer",
        tokens=("peony", "night", "summer", "opening", "blossom"),
    ),
    Haiku(
        id="buson_white_plum_dawn",
        lines=("white plum blossoms—", "the dawn approaches", "yellow"),
        author="Yosa Buson", season="spring",
        tokens=("plum", "dawn", "color", "spring", "blossom"),
    ),
    Haiku(
        id="buson_old_well_fish",
        lines=("an old well—", "a fish leaps", "to a dark sound"),
        author="Yosa Buson", season="autumn",
        tokens=("well", "fish", "sound", "dark", "autumn"),
    ),
    Haiku(
        id="buson_moonlit_frog_clouds",
        lines=("moonlit night—", "a frog swims", "through the clouds"),
        author="Yosa Buson", season="summer",
        tokens=("frog", "moon", "cloud", "drift", "summer"),
    ),
    Haiku(
        id="buson_blossoms_drift",
        lines=("blossoms fallen—", "pieces of cloud", "drift away"),
        author="Yosa Buson", season="spring",
        tokens=("blossom", "cloud", "drift", "parting", "spring"),
    ),
    Haiku(
        id="buson_winter_stable",
        lines=("snow on snow—", "in the dark stable", "the horses' breath"),
        author="Yosa Buson", season="winter",
        tokens=("stable", "horse", "breath", "snow", "winter"),
    ),
    Haiku(
        id="buson_butterfly_bell",
        lines=("a butterfly perches", "on the temple bell—", "sleeping"),
        author="Yosa Buson", season="spring",
        tokens=("butterfly", "bell", "sleep", "temple", "stillness"),
    ),
    Haiku(
        id="buson_moonlit_wisteria",
        lines=("in pale moonlight", "the wisteria's scent", "comes from far away"),
        author="Yosa Buson", season="spring",
        tokens=("wisteria", "moon", "scent", "night", "fragrance"),
    ),
    Haiku(
        id="buson_cherry_path_wind",
        lines=("a narrow path—", "cherry trees on both sides,", "the wind"),
        author="Yosa Buson", season="spring",
        tokens=("cherry", "path", "wind", "breeze", "spring"),
    ),
    Haiku(
        id="buson_summer_river_stars",
        lines=("summer night—", "footsteps cross the river,", "starlight"),
        author="Yosa Buson", season="summer",
        tokens=("river", "star", "night", "sound", "summer"),
    ),
    Haiku(
        id="buson_spring_breeze_pipe",
        lines=("spring breeze—", "on the grasses", "a pipe smolders"),
        author="Yosa Buson", season="spring",
        tokens=("pipe", "grass", "breeze", "smoke", "spring"),
    ),
    Haiku(
        id="buson_mustard_field_sea",
        lines=("a field of mustard flowers—", "no whales in sight,", "the sea darkens"),
        author="Yosa Buson", season="spring",
        tokens=("mustard", "field", "sea", "evening", "color"),
    ),
    Haiku(
        id="buson_thunder_plum",
        lines=("a sudden thunderclap—", "and the plum blossoms", "bow"),
        author="Yosa Buson", season="spring",
        tokens=("lightning", "plum", "blossom", "spring", "sudden"),
    ),
    Haiku(
        id="buson_boat_river_evening",
        lines=("an evening boat—", "lanterns lit, and far ahead", "another lamp"),
        author="Yosa Buson", season="autumn",
        tokens=("boat", "lantern", "river", "evening", "autumn"),
    ),

    # ===================== Issa (25) ====================================
    Haiku(
        id="snow_melts",
        lines=("the snow is melting", "and the village is flooded", "with children"),
        author="Kobayashi Issa", season="spring",
        tokens=("snow", "village", "flood", "children", "joy"),
    ),
    Haiku(
        id="firefly_drift",
        lines=("a giant firefly:", "that way, this way, that way—", "and it passes by"),
        author="Kobayashi Issa", season="summer",
        tokens=("firefly", "drift", "night", "passing"),
    ),
    Haiku(
        id="plum_path",
        lines=("plum blossoms—", "their fragrance the path", "for a messenger"),
        author="Kobayashi Issa", season="spring",
        tokens=("plum", "blossom", "fragrance", "path", "messenger"),
    ),
    Haiku(
        id="issa_world_of_dew",
        lines=("the world of dew", "is the world of dew—", "and yet, and yet"),
        author="Kobayashi Issa", season="autumn",
        tokens=("dew", "world", "parting", "gratitude", "autumn"),
    ),
    Haiku(
        id="issa_snail_fuji",
        lines=("o snail—", "climb Mount Fuji,", "but slowly, slowly"),
        author="Kobayashi Issa", season="summer",
        tokens=("snail", "mountain", "climbing", "patience", "summer"),
    ),
    Haiku(
        id="issa_cherry_strange",
        lines=("what a strange thing—", "to be alive", "beneath cherry blossoms"),
        author="Kobayashi Issa", season="spring",
        tokens=("cherry", "blossom", "world", "awakening", "spring"),
    ),
    Haiku(
        id="issa_autumn_old_age",
        lines=("this autumn—", "how old I feel,", "a bird in the clouds"),
        author="Kobayashi Issa", season="autumn",
        tokens=("autumn", "year", "longing", "sparrow", "cloud"),
    ),
    Haiku(
        id="issa_spider_kindness",
        lines=("don't worry, spiders—", "I keep house", "casually"),
        author="Kobayashi Issa", season="summer",
        tokens=("spider", "hut", "kindness", "stillness", "summer"),
    ),
    Haiku(
        id="issa_mosquito_monk",
        lines=("all the time I pray to Buddha—", "I keep on", "killing mosquitoes"),
        author="Kobayashi Issa", season="summer",
        tokens=("mosquito", "prayer", "monk", "irony", "summer"),
    ),
    Haiku(
        id="issa_cat_journey",
        lines=("the cat,", "having stretched—", "picks up his journey"),
        author="Kobayashi Issa", season="autumn",
        tokens=("cat", "journey", "stretching", "awakening", "autumn"),
    ),
    Haiku(
        id="issa_cuckoo_mountain",
        lines=("a cuckoo sings—", "to me, to the mountain,", "to me, to the mountain"),
        author="Kobayashi Issa", season="summer",
        tokens=("cuckoo", "mountain", "voice", "song", "summer"),
    ),
    Haiku(
        id="issa_radish_road",
        lines=("the man pulling radishes—", "pointed the way", "with a radish"),
        author="Kobayashi Issa", season="autumn",
        tokens=("radish", "road", "traveler", "kindness", "autumn"),
    ),
    Haiku(
        id="issa_flies_temple",
        lines=("where there are humans", "there are flies—", "and Buddhas"),
        author="Kobayashi Issa", season="summer",
        tokens=("fly", "buddha", "world", "summer", "irony"),
    ),
    Haiku(
        id="issa_kite_beggar",
        lines=("a beautiful kite", "rose up", "from a beggar's hut"),
        author="Kobayashi Issa", season="spring",
        tokens=("kite", "beggar", "hut", "joy", "spring"),
    ),
    Haiku(
        id="issa_moon_request",
        lines=("a child cries—", "asks for the moon", "tonight"),
        author="Kobayashi Issa", season="autumn",
        tokens=("moon", "child", "longing", "tears", "autumn"),
    ),
    Haiku(
        id="issa_autumn_wind_child",
        lines=("the autumn wind—", "blows the curls", "of a sick child"),
        author="Kobayashi Issa", season="autumn",
        tokens=("wind", "autumn", "child", "sickness", "frailty"),
    ),
    Haiku(
        id="issa_cricket_singing",
        lines=("a cricket sings—", "and the night", "is taller for it"),
        author="Kobayashi Issa", season="autumn",
        tokens=("cricket", "song", "voice", "night", "autumn"),
    ),
    Haiku(
        id="issa_first_dream",
        lines=("first dream of the year—", "I keep it secret,", "smiling"),
        author="Kobayashi Issa", season="new_year",
        tokens=("dream", "year", "secret", "smile", "new_year"),
    ),
    Haiku(
        id="issa_spring_rain_yawn",
        lines=("spring rain—", "a pretty girl,", "yawning"),
        author="Kobayashi Issa", season="spring",
        tokens=("rain", "woman", "sleep", "spring", "awakening"),
    ),
    Haiku(
        id="issa_mosquito_journey",
        lines=("what good luck—", "even the mosquitoes", "find me here"),
        author="Kobayashi Issa", season="summer",
        tokens=("mosquito", "journey", "joy", "summer", "irony"),
    ),
    Haiku(
        id="issa_moon_plum_passing",
        lines=("moon, plum blossoms—", "this, that,", "the day passes"),
        author="Kobayashi Issa", season="spring",
        tokens=("moon", "plum", "passing", "year", "spring"),
    ),
    Haiku(
        id="issa_cicada_first",
        lines=("the first cicada—", "life is", "cruel, cruel, cruel"),
        author="Kobayashi Issa", season="summer",
        tokens=("cicada", "first", "voice", "summer", "awakening"),
    ),
    Haiku(
        id="issa_tiny_frog_mountain",
        lines=("with bland serenity", "gazing at the far mountains—", "a tiny frog"),
        author="Kobayashi Issa", season="spring",
        tokens=("frog", "mountain", "stillness", "spring", "awakening"),
    ),
    Haiku(
        id="issa_world_walk_hell",
        lines=("in this world", "we walk on the roof of hell—", "gazing at flowers"),
        author="Kobayashi Issa", season="spring",
        tokens=("blossom", "world", "hell", "passing", "spring"),
    ),
    Haiku(
        id="issa_spring_thaw_river",
        lines=("the spring thaw—", "an old river", "remembers itself"),
        author="Kobayashi Issa", season="spring",
        tokens=("river", "thaw", "spring", "memory", "current"),
    ),

    # ===================== Chiyo-ni (8) ================================
    Haiku(
        id="morning_glory",
        lines=("morning glory—", "the well bucket entangled,", "I ask for water"),
        author="Fukuda Chiyo-ni", season="summer",
        tokens=("morning_glory", "well", "vine", "water", "kindness"),
    ),
    Haiku(
        id="chiyo_winter_parting",
        lines=("after a long winter—", "giving each other nothing,", "we part"),
        author="Fukuda Chiyo-ni", season="winter",
        tokens=("winter", "parting", "woman", "road", "gratitude"),
    ),
    Haiku(
        id="chiyo_moon_farewell",
        lines=("having seen the moon—", "I bid farewell", "with a grateful heart"),
        author="Fukuda Chiyo-ni", season="autumn",
        tokens=("moon", "gratitude", "world", "parting", "autumn"),
    ),
    Haiku(
        id="chiyo_dragonfly_hunter",
        lines=("the dragonfly hunter—", "today, how far", "has he wandered?"),
        author="Fukuda Chiyo-ni", season="summer",
        tokens=("dragonfly", "child", "journey", "longing", "summer"),
    ),
    Haiku(
        id="chiyo_women_field",
        lines=("again the women", "come out to the field—", "young rice"),
        author="Fukuda Chiyo-ni", season="spring",
        tokens=("woman", "field", "rice", "spring", "song"),
    ),
    Haiku(
        id="chiyo_butterflies_stones",
        lines=("all entangled—", "butterfly to butterfly,", "on the stone path"),
        author="Fukuda Chiyo-ni", season="spring",
        tokens=("butterfly", "stone", "path", "drift", "spring"),
    ),
    Haiku(
        id="chiyo_willow_woman",
        lines=("to the willow—", "all the longing of my heart,", "and the wind"),
        author="Fukuda Chiyo-ni", season="spring",
        tokens=("willow", "longing", "wind", "spring", "parting"),
    ),
    Haiku(
        id="chiyo_new_year_face",
        lines=("even my plain face", "is worth seeing—", "first day of the year"),
        author="Fukuda Chiyo-ni", season="new_year",
        tokens=("mirror", "face", "year", "joy", "new_year"),
    ),

    # ===================== Other classical (12) =========================
    Haiku(
        id="shiki_persimmon",
        lines=("I bite into a persimmon—", "a temple bell sounds", "from far away"),
        author="Masaoka Shiki", season="autumn",
        tokens=("persimmon", "bell", "sound", "evening", "autumn"),
    ),
    Haiku(
        id="shiki_softly",
        lines=("I want to sleep—", "swat the flies", "softly, please"),
        author="Masaoka Shiki", season="summer",
        tokens=("fly", "sleep", "kindness", "longing", "summer"),
    ),
    Haiku(
        id="shiki_spider_lone",
        lines=("after killing a spider—", "how lonely I feel", "in the cold of night"),
        author="Masaoka Shiki", season="autumn",
        tokens=("spider", "loneliness", "night", "regret", "autumn"),
    ),
    Haiku(
        id="shiki_horse_river",
        lines=("a summer river—", "there's a bridge,", "but my horse goes through the water"),
        author="Masaoka Shiki", season="summer",
        tokens=("horse", "river", "bridge", "water", "summer"),
    ),
    Haiku(
        id="shiki_snowy_village",
        lines=("a mountain village—", "under the piled-up snow,", "the sound of water"),
        author="Masaoka Shiki", season="winter",
        tokens=("village", "snow", "mountain", "water", "sound"),
    ),
    Haiku(
        id="ryokan_thief_moon",
        lines=("the thief left it behind—", "the moon", "at my window"),
        author="Ryōkan Taigu", season="autumn",
        tokens=("moon", "thief", "window", "kindness", "autumn"),
    ),
    Haiku(
        id="ryokan_leaves_boat",
        lines=("if I gathered them all—", "the fallen leaves", "would fill the boat"),
        author="Ryōkan Taigu", season="autumn",
        tokens=("leaf", "boat", "withered", "gratitude", "autumn"),
    ),
    Haiku(
        id="ryokan_no_talent",
        lines=("no talent—", "I just keep alive", "through the seasons"),
        author="Ryōkan Taigu", season="winter",
        tokens=("monk", "year", "patience", "loneliness", "winter"),
    ),
    Haiku(
        id="onitsura_trout_clouds",
        lines=("the trout leap up—", "and clouds", "move on the bottom of the brook"),
        author="Uejima Onitsura", season="summer",
        tokens=("fish", "cloud", "river", "current", "summer"),
    ),
    Haiku(
        id="kikaku_firefly_wind",
        lines=("the first firefly—", "has flown away,", "the wind"),
        author="Takarai Kikaku", season="summer",
        tokens=("firefly", "wind", "vanishing", "night", "summer"),
    ),
    Haiku(
        id="moritake_butterfly_branch",
        lines=("a fallen petal—", "returning to the branch?", "no, a butterfly"),
        author="Arakida Moritake", season="spring",
        tokens=("butterfly", "blossom", "branch", "return", "spring"),
    ),
    Haiku(
        id="sokan_moon_fan",
        lines=("if only we could", "add a handle to the moon—", "what a fan!"),
        author="Yamazaki Sōkan", season="summer",
        tokens=("moon", "fan", "joy", "summer", "freedom"),
    ),
)


HAIKU_BY_ID: dict[str, Haiku] = {h.id: h for h in HAIKU}


def get(id: str) -> Haiku:
    if id not in HAIKU_BY_ID:
        raise KeyError(f"unknown haiku id: {id!r}")
    return HAIKU_BY_ID[id]


def all_ids() -> tuple[str, ...]:
    return tuple(h.id for h in HAIKU)
