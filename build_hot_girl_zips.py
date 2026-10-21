#!/usr/bin/env python3
"""Package the Hot Girl Era stickers for Etsy: PNG zips under 17 MB each (Etsy allows 20 MB per file) plus the sticker book PDF.

Inputs:  images/hot_girl/cut_2x/*.png, images/hot_girl/Hot_Girl_Era_Sticker_Pack.pdf
Outputs: images/hot_girl/sticker_pack/
"""
import os
import shutil
import zipfile

from android_series import SERIES

ROOT = os.path.dirname(os.path.abspath(__file__)); WD = os.path.join(ROOT, "images", "hot_girl")
SRC = os.path.join(WD, "cut_2x"); OUT = os.path.join(WD, "sticker_pack"); os.makedirs(OUT, exist_ok=True)
LIMIT = 17 * 1024 * 1024
folder = SERIES["hot_girl"]["category"]

groups = {}
for f in sorted(os.listdir(SRC)):
    if f.endswith(".png"):
        groups.setdefault(folder(f), []).append(f)
parts, cur, size = [], [], 0
for g in sorted(groups):
    gs = sum(os.path.getsize(os.path.join(SRC, f)) for f in groups[g])
    if cur and size + gs > LIMIT:
        parts.append(cur); cur, size = [], 0
    cur.append(g); size += gs
parts.append(cur)
for k, gs in enumerate(parts, 1):
    path = os.path.join(OUT, f"Hot_Girl_Era_Stickers_Part{k}.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as z:
        for g in gs:
            for f in groups[g]:
                z.write(os.path.join(SRC, f), f"{g}/{f}")
    print(os.path.basename(path), round(os.path.getsize(path) / 1e6, 1), "MB", gs)
shutil.copy(os.path.join(WD, "Hot_Girl_Era_Sticker_Pack.pdf"), os.path.join(OUT, "Hot_Girl_Era_Sticker_Book.pdf"))
print(sum(len(v) for v in groups.values()), "stickers")
