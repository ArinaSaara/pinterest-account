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
BIG, SMALL, NEAR = 5000, 300, 40


def cut(sheet, cols, names):
    im = Image.open(os.path.join(SRC, sheet + ".webp")).convert("RGBA")
    a = np.asarray(im)
    mask = a[..., 3] > 20
    lab, n = ndi.label(mask)
    sizes = ndi.sum(mask, lab, range(1, n + 1))
    objs = ndi.find_objects(lab)
    groups = [[i + 1] for i, s in enumerate(sizes) if s > BIG]                  # one blob = one sticker
    small = [i + 1 for i, s in enumerate(sizes) if SMALL < s <= BIG]            # crumbs: sparkles, steam, motion lines
    if small:                                                                    # a crumb within NEAR px of a sticker belongs to it
        bigmask = np.isin(lab, [g[0] for g in groups])
        dist, (iy, ix) = ndi.distance_transform_edt(~bigmask, return_indices=True)
        keep = []
        for i in small:
            ys, xs = np.where(lab == i); j = int(np.argmin(dist[ys, xs]))
            if dist[ys[j], xs[j]] < NEAR:
                owner = lab[iy[ys[j], xs[j]], ix[ys[j], xs[j]]]
                next(g for g in groups if g[0] == owner).append(i)
            else:
                keep.append(i)
        small = keep
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


def cut_grid(sheet, cols, names):
    """Fallback for sheets where stickers touch: split the mask along the emptiest line between grid cells,
    use the eroded body of each cell as a marker, and hand every opaque pixel to the nearest marker."""
    im = Image.open(os.path.join(SRC, sheet + ".webp")).convert("RGBA")
    a = np.asarray(im); mask = a[..., 3] > 20; hgt, wid = mask.shape; rows = len(names) // cols

    def seps(profile, n, span):
        out = []
        for i in range(1, n):
            lo, hi = int(span * i / n - span / n * 0.3), int(span * i / n + span / n * 0.3)
            out.append(lo + int(np.argmin(profile[lo:hi])))
        return out
    xs = [0] + seps(mask.sum(0), cols, wid) + [wid]; ys = [0] + seps(mask.sum(1), rows, hgt) + [hgt]
    core = ndi.binary_erosion(mask, iterations=10)
    for x in xs[1:-1]:
        core[:, x - 3:x + 3] = False
    for y in ys[1:-1]:
        core[y - 3:y + 3, :] = False
    lab, n = ndi.label(core); sizes = ndi.sum(core, lab, range(1, n + 1)); cent = ndi.center_of_mass(core, lab, range(1, n + 1))
    marker = np.zeros(mask.shape, dtype=np.int32)
    for i in range(n):
        if sizes[i] < 1500:
            continue
        cy, cx = cent[i]; r = np.searchsorted(ys, cy) - 1; c = np.searchsorted(xs, cx) - 1
        marker[lab == i + 1] = r * cols + c + 1
    found = len(np.unique(marker)) - 1
    assert found == len(names), f"{sheet}: grid split found {found} stickers, expected {len(names)}"
    _, (iy, ix) = ndi.distance_transform_edt(marker == 0, return_indices=True)
    owner = marker[iy, ix] * mask
    for k, name in enumerate(names):
        own = owner == k + 1
        yy, xx = np.where(own); y0, y1, x0, x1 = yy.min(), yy.max() + 1, xx.min(), xx.max() + 1
        arr = a[y0:y1, x0:x1].copy(); arr[~own[y0:y1, x0:x1], 3] = 0
        Image.fromarray(arr).save(os.path.join(OUT, name + ".png"), optimize=True)


if __name__ == "__main__":
    for sheet, (cols, names) in SHEETS.items():
        if not os.path.exists(os.path.join(SRC, sheet + ".webp")):
            print(sheet, "missing, skipped"); continue
        try:
            cut(sheet, cols, names); print(sheet, len(names), "by blobs")
        except AssertionError as e:
            cut_grid(sheet, cols, names); print(sheet, len(names), "by grid  (", e, ")")
