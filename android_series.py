"""Series registry for the Android (Penly / Samsung Notes / Xodo) sticker packaging.

Used by build_android_pack.py and build_android_mockups.py.

Each series says where its transparent PNG stickers live and how a file name maps to a
category folder. Penly imports "a category from a folder", so the zip is organised as
<Category>/<sticker>.png and the buyer imports one folder = one category.
"""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "images")


def _prefix_map(mapping, default):
    def f(name):
        base = os.path.basename(name)
        for k, v in mapping.items():
            if base.startswith(k):
                return v
        return default
    return f


def _it_girl_category(name):
    # build_it_stickerpack names: NN_<code>_<i>_<name>.png
    from it_stickers import CATEGORIES
    code = os.path.basename(name).split("_")[1]
    return next((label for c, label, _ in CATEGORIES if c == code), "Stickers").replace(" & ", "_and_").replace(" ", "_")


def _wedding_category(name):
    base = os.path.basename(name)
    if base[:-4] in ("booked", "paid", "waiting", "rsvp"):
        return "Labels_and_status"
    return _prefix_map({"l_": "Labels_and_status", "t_": "Day_of_time_blocks", "d_": "Decor_and_frames", "x_": "Objects_and_honeymoon", "q_": "Quotes"}, "Florals_and_icons")(base)


def _dragon_sources():
    return [(e.capitalize() + "_dragon", os.path.join(IMG, e, "transparent")) for e in ("fire", "ice", "water", "lightning")]


SERIES = {
    "it_girl": dict(
        title="Code & Cozy", prefix="Code_and_Cozy", accent=(107, 127, 88), ink=(56, 54, 46),
        sources=[(None, os.path.join(IMG, "it_girl", "sticker_pack", "PNG"))], category=_it_girl_category,
        out=os.path.join(IMG, "it_girl", "sticker_pack", "android"), mockups=os.path.join(IMG, "it_girl", "mockups"),
        tagline="80 digital stickers for women in tech",
    ),
    "wedding": dict(
        title="Soft Rebellion", prefix="Soft_Rebellion", accent=(75, 88, 54), ink=(59, 50, 43),
        sources=[(None, os.path.join(IMG, "wedding", "cut_2x"))], category=_wedding_category,
        out=os.path.join(IMG, "wedding", "sticker_pack", "android"), mockups=os.path.join(IMG, "wedding", "mockups"),
        tagline="108 wedding planner stickers",
    ),
    "dragons": dict(
        title="Year of Dragons", prefix="Year_of_Dragons", accent=(226, 112, 52), ink=(60, 56, 54),
        sources=_dragon_sources(), category=None,   # category = source folder label
        out=os.path.join(IMG, "year_of_dragons", "sticker_pack_android"), mockups=os.path.join(IMG, "year_of_dragons", "mockups"),
        tagline="32 growing dragon stickers, 4 elements x 8 stages",
    ),
    "shadow": dict(
        title="Gothic Dragon", prefix="Gothic_Dragon", accent=(122, 46, 58), ink=(40, 34, 44),
        sources=[("Shadow_dragon", os.path.join(IMG, "shadow", "transparent"))], category=None,
        out=os.path.join(IMG, "shadow", "sticker_pack_android"), mockups=os.path.join(IMG, "shadow", "mockups"),
        tagline="8 gothic dragon stages for dark academia planners",
    ),
    "hot_girl": dict(
        title="Hot Girl Era", prefix="Hot_Girl_Era", accent=(232, 112, 58), ink=(107, 74, 58),
        sources=[(None, os.path.join(IMG, "hot_girl", "cut_2x"))],
        category=_prefix_map({"m_": "Margo_moments", "l_": "Symptom_and_care_labels", "q_": "Quotes", "a_": "Build_your_Hot_Girl", "base": "Build_your_Hot_Girl",
                              "d_": "Washi_and_decor", "washi": "Washi_and_decor", "moon": "Cycle_moons_and_drops", "drop": "Cycle_moons_and_drops",
                              "f": "Hot_flash_scale", "x_": "Objects"}, "Stickers"),
        out=os.path.join(IMG, "hot_girl", "sticker_pack_android"), mockups=os.path.join(IMG, "hot_girl", "mockups"),
        tagline="102 perimenopause planner stickers with Margo",
    ),
}


def stickers(key):
    """[(category, path)] for every PNG of the series, in a stable order."""
    s = SERIES[key]; out = []
    for label, folder in s["sources"]:
        if not os.path.isdir(folder):
            print("missing", folder); continue
        for f in sorted(os.listdir(folder)):
            if f.lower().endswith(".png") and not f.startswith(".") and not any(w in f.lower() for w in ("sheet", "preview", "overview")):
                p = os.path.join(folder, f)
                cat = label if label else s["category"](p)
                out.append((re.sub(r"[^A-Za-z0-9_]", "_", cat), p))
    return out
