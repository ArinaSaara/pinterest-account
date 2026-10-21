#!/usr/bin/env python3
"""Cut the Hot Girl Era sticker sheets (transparent webp, regular grids) into one PNG per sticker.

Inputs (not in git):  images/hot_girl/src/sheet{1..4}.webp
Outputs:              images/hot_girl/cut/<name>.png

A sticker is a connected blob of opaque pixels. Tiny blobs that sit close together (the four photo corners) are merged into one sticker.
Reading order = rows of `cols` stickers, each row sorted left to right.
"""
import os

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "images", "hot_girl", "src")
OUT = os.path.join(ROOT, "images", "hot_girl", "cut")
os.makedirs(OUT, exist_ok=True)

SHEETS = {
    "sheet1": (4, ["m_fan", "m_icewater", "m_window", "m_thermostat",
                   "m_fog", "m_lifting", "m_sleepmask", "m_nightsweat",
                   "m_rage", "m_tears", "m_shrug", "m_crown",
                   "m_doctor", "m_nocoffee", "m_nowine", "m_protein",
                   "m_pills", "m_walk", "m_bath", "m_reading",
                   "m_scroll3am", "m_dance", "m_hug", "m_coffee_ok"]),
    "sheet2": (5, ["l_hotflash", "l_nightsweat", "l_sleep", "l_mood", "l_brainfog",
                   "l_headache", "l_joints", "l_bloating", "l_palpitations", "l_energy",
                   "l_libido", "l_period", "l_spotting", "l_skipped", "l_heavy",
                   "l_cramps", "l_anxiety", "l_irritable", "l_tears", "l_dry",
                   "l_doctor", "l_labs", "l_meds", "l_hrt", "l_supplements",
                   "l_water", "l_protein", "l_workout", "l_steps", "l_win"]),
    "sheet3": (4, ["base_margo", "a_sleepmask", "a_dumbbell", "a_shaker",
                   "a_bottle", "a_potion", "a_folder", "a_fan",
                   "a_crown", "f1", "f2", "f3",
                   "f4", "f5", "moon_new", "moon_wax",
                   "moon_full", "moon_wane", "drop1", "drop2",
                   "drop3", "x_ice", "x_thermostat", "x_window"]),
    "sheet4": (4, ["q_nottoday", "q_estrogen", "q_maincharacter", "q_openwindow",
                   "q_hotgirlera", "q_unbothered", "q_imfine", "q_fogmode",
                   "q_plottwist", "q_stillhot", "q_rest", "q_askdoctor",
                   "washi_tang", "washi_pink", "washi_check", "d_frame",
                   "d_banner", "d_arrow", "d_heart", "d_lipstick",
                   "d_sunglasses", "d_icedcoffee", "d_cat", "d_flame"]),
}
BIG, SMALL = 5000, 300


def cut(sheet, cols, names):
    im = Image.open(os.path.join(SRC, sheet + ".webp")).convert("RGBA")
    a = np.asarray(im)
    mask = a[..., 3] > 20
    lab, n = ndi.label(mask)
    sizes = ndi.sum(mask, lab, range(1, n + 1))
    objs = ndi.find_objects(lab)
    groups = [[i + 1] for i, s in enumerate(sizes) if s > BIG]                  # one blob = one sticker
    small = [i + 1 for i, s in enumerate(sizes) if SMALL < s <= BIG]            # crumbs: cluster the ones that sit together
    if small:
        sm = np.isin(lab, small)
        cl, k = ndi.label(ndi.binary_dilation(sm, iterations=14))
        for j in range(1, k + 1):
            groups.append([i for i in small if (cl[lab == i] == j).any()])
    assert len(groups) == len(names), f"{sheet}: found {len(groups)} stickers, expected {len(names)}"

    def box(g):
        return (min(objs[i - 1][0].start for i in g), max(objs[i - 1][0].stop for i in g),
                min(objs[i - 1][1].start for i in g), max(objs[i - 1][1].stop for i in g))
    boxed = sorted(((g, box(g)) for g in groups), key=lambda b: b[1][0] + b[1][1])       # vertical centre
    rows = [sorted(boxed[r * cols:(r + 1) * cols], key=lambda b: b[1][2]) for r in range(len(names) // cols)]
    ordered = [b for r in rows for b in r]
    for name, (g, (y0, y1, x0, x1)) in zip(names, ordered):
        pad = 4
        y0, y1, x0, x1 = max(y0 - pad, 0), min(y1 + pad, a.shape[0]), max(x0 - pad, 0), min(x1 + pad, a.shape[1])
        arr = a[y0:y1, x0:x1].copy()
        own = ndi.binary_dilation(np.isin(lab[y0:y1, x0:x1], g), iterations=8)     # drop bits of neighbours
        arr[~own, 3] = 0
        Image.fromarray(arr).save(os.path.join(OUT, name + ".png"), optimize=True)


for sheet, (cols, names) in SHEETS.items():
    if os.path.exists(os.path.join(SRC, sheet + ".webp")):
        cut(sheet, cols, names); print(sheet, len(names))
    else:
        print(sheet, "missing, skipped")
