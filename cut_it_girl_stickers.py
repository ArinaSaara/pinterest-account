#!/usr/bin/env python3
"""Cut the 3 sticker sheets (8 stickers each, white paper) into transparent PNGs.

Inputs (not in git):  images/it_girl/src/*.webp  (fit, cozy, work, travel, home, hobby, social)
Outputs:              images/it_girl/cut/<sheet>_<n>.png  (n = 1..8, reading order)
"""
import os

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "images", "it_girl", "src")
CUT = os.path.join(ROOT, "images", "it_girl", "cut")


# stickers where a cone of the neighbour below hangs off the bottom edge; cut everything under the last wide row
CROP_BOTTOM = {"seasons_6"}


def trim_stubs(mask):
    """Cut a fragment of a neighbouring sticker that hangs off the top edge by a thin neck (rows are scanned top-down)."""
    w = mask.sum(axis=1)
    if not w.any():
        return mask
    main = int(np.argmax(w >= 0.25 * w.max()))
    # a neck = a dip below an earlier, narrower dome: a dome >= 20 rows tall hanging off the main body (natural tops ramp up smoothly)
    necks = [r for r in range(20, main) if w[:r].max() >= 25 and w[:r].max() <= 0.6 * w.max() and w[r] <= 0.94 * w[:r].max()]
    if necks:
        mask = mask.copy(); mask[: necks[-1] + 1] = False
    return mask


def cut(sheet):
    im = Image.open(os.path.join(SRC, sheet + ".webp")).convert("RGB")
    a = np.asarray(im).astype(int)
    # Background = near-white pixels connected to the page edge (the sticker's own white border stops at its thin grey outline).
    near_white = (a.min(axis=2) >= 243)
    lab, _ = ndi.label(near_white)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    # Paper trapped between touching die-cuts is not connected to the page edge. A sticker's own white border ring always
    # touches painted pixels (saturated or dark; the thin grey outline is neither), trapped paper never does.
    painted = ndi.binary_dilation(((a.max(axis=2) - a.min(axis=2)) > 40) | (a.min(axis=2) < 185), iterations=3)
    touching = set(np.unique(lab[painted & (lab > 0)])) - {0}
    bg = np.isin(lab, list(edge)) | ((lab > 0) & ~np.isin(lab, list(touching)))
    fg = ndi.binary_fill_holes(~bg)
    fg = ndi.binary_opening(fg, iterations=2)
    # Stickers sit close together and can touch: erode until the 8 bodies separate, then grow each seed back inside the mask.
    for it in range(4, 60, 2):
        seeds, n = ndi.label(ndi.binary_erosion(fg, iterations=it))
        sizes = ndi.sum(fg, seeds, range(1, n + 1))
        keep = [i + 1 for i, z in enumerate(sizes) if z > 1500]
        if len(keep) == 8:
            break
    else:
        # Sheets whose stickers overlap: the layout is always 2 columns x 4 rows, so seed each cell from its own eroded core.
        h_, w_ = fg.shape; yy, xx = np.mgrid[:h_, :w_]
        cell = (yy * 4 // h_) * 2 + (xx * 2 // w_)
        for it in range(40, 4, -4):
            core = ndi.binary_erosion(fg, iterations=it)
            if all(core[cell == k].any() for k in range(8)):
                break
        else:
            raise SystemExit(f"{sheet}: could not split into 8 stickers")
        seeds = np.where(core, cell + 1, 0); keep = list(range(1, 9))
    seed_map = np.where(np.isin(seeds, keep), seeds, 0)
    _, idx = ndi.distance_transform_edt(seed_map == 0, return_indices=True)
    lab = np.where(fg, seed_map[idx[0], idx[1]], 0)
    slices = ndi.find_objects(lab)
    boxes = [(i, slices[i - 1]) for i in keep]
    # reading order: rows of two columns
    boxes.sort(key=lambda b: (round((b[1][0].start + b[1][0].stop) / 2 / 380), b[1][1].start))
    if len(boxes) != 8:
        raise SystemExit(f"{sheet}: expected 8 stickers, found {len(boxes)}")
    for n_, (i, sl) in enumerate(boxes, 1):
        own = lab == i
        body, k = ndi.label(ndi.binary_opening(own, iterations=10))  # drop stray fragments of neighbours
        body = body == (1 + int(np.argmax(ndi.sum(body > 0, body, range(1, k + 1)))))
        body = trim_stubs(trim_stubs(body.T).T)
        body = trim_stubs(body[::-1])[::-1]
        body = trim_stubs(body[:, ::-1].T).T[:, ::-1]
        if f"{sheet}_{n_}" in CROP_BOTTOM:
            wide = np.where(body.sum(axis=1) >= 0.5 * body.sum(axis=1).max())[0]; body = body.copy(); body[wide[-1] + 4:] = False
        body = ndi.label(body)[0]; body = body == (1 + int(np.argmax(ndi.sum(body > 0, body, range(1, body.max() + 1)))))
        m = Image.fromarray((body * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1))
        out = im.convert("RGBA"); out.putalpha(m)
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        out.crop((max(0, x0 - 4), max(0, y0 - 4), min(im.width, x1 + 4), min(im.height, y1 + 4))).save(os.path.join(CUT, f"{sheet}_{n_}.png"))


for s in sorted(f[:-5] for f in os.listdir(SRC) if f.endswith(".webp")):
    cut(s)
print("ok", sorted(os.listdir(CUT)))
