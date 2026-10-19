#!/usr/bin/env python3
"""Build the "Code & Cozy" sticker pack from the cut stickers (see cut_it_girl_stickers.py, it_stickers.py).

Outputs (images/it_girl/sticker_pack/):
  PNG/<NN>_<category>_<name>.png    transparent stickers with the white die-cut border
  sheets/<category>_sheet.png       2x4 sheet per category on cream (Pinterest / Etsy)
  overview.jpg                      2000x2000 collage of the whole pack (Etsy main photo)
  Code_and_Cozy_Sticker_Book.pdf    one page per category, copy-paste into GoodNotes
  Code_and_Cozy_Stickers_Part<N>.zip   the PNGs split to stay under Etsy's 20 MB file limit

Run:  .venv-planner/bin/python build_it_stickerpack.py
"""
import os
import shutil
import zipfile

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from it_stickers import CATEGORIES
from pdf_utils import lighten

ROOT = os.path.dirname(os.path.abspath(__file__))
CUT = os.path.join(ROOT, "images", "it_girl", "cut")
OUT = os.path.join(ROOT, "images", "it_girl", "sticker_pack")
CREAM = (250, 246, 234)
FONTS = os.path.join(ROOT, "fonts")

cats = [(code, label, names) for code, label, names in CATEGORIES if all(os.path.exists(os.path.join(CUT, f"{code}_{i}.png")) for i in range(1, len(names) + 1))]
shutil.rmtree(OUT, ignore_errors=True)
for sub in ("PNG", "sheets"):
    os.makedirs(os.path.join(OUT, sub))

# 1. named PNGs
files = []
for ci, (code, label, names) in enumerate(cats, 1):
    for i, name in enumerate(names, 1):
        dst = os.path.join(OUT, "PNG", f"{ci:02d}_{code}_{i}_{name}.png")
        shutil.copy(os.path.join(CUT, f"{code}_{i}.png"), dst); files.append((code, label, name, dst))


def fit(im, w, h):
    s = min(w / im.width, h / im.height); return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)


# 2. category sheets 2x4 on cream
for code, label, names in cats:
    sh = Image.new("RGB", (1024, 1536), CREAM)
    for i in range(len(names)):
        im = Image.open(os.path.join(CUT, f"{code}_{i + 1}.png")); im = fit(im, 470, 340)
        cx, cy = 256 + (i % 2) * 512, 192 + (i // 2) * 384
        sh.paste(im, (cx - im.width // 2, cy - im.height // 2), im)
    sh.save(os.path.join(OUT, "sheets", f"{code}_sheet.png"))

# 3. overview collage
n = len(files); cols = 10; rows = (n + cols - 1) // cols
ov = Image.new("RGB", (2000, 2000), CREAM); d = ImageDraw.Draw(ov)
title_f = ImageFont.truetype(os.path.join(FONTS, "PlayfairDisplay-Regular.ttf"), 120); sub_f = ImageFont.truetype(os.path.join(FONTS, "DMSans-SemiBold.ttf"), 34)
d.text((1000, 96), "Code & Cozy", font=title_f, fill=(56, 54, 46), anchor="mm")
d.text((1000, 190), f"{n} DIGITAL STICKERS  ·  GOODNOTES  ·  TRANSPARENT PNG", font=sub_f, fill=(107, 127, 88), anchor="mm")
cw, ch = 2000 // cols, (2000 - 260) // rows
for i, (code, label, name, path) in enumerate(files):
    im = fit(Image.open(path), cw - 18, ch - 18); cx, cy = (i % cols) * cw + cw // 2, 260 + (i // cols) * ch + ch // 2
    ov.paste(im, (cx - im.width // 2, cy - im.height // 2), im)
ov.save(os.path.join(OUT, "overview.jpg"), quality=92)

# 4. sticker book PDF
for nm, fn in (("Disp", "PlayfairDisplay-Regular"), ("Sans", "DMSans-Regular"), ("SansB", "DMSans-SemiBold")):
    pdfmetrics.registerFont(TTFont(nm, os.path.join(FONTS, fn + ".ttf")))
W, H = 834, 1112
pdf = os.path.join(OUT, "Code_and_Cozy_Sticker_Book.pdf"); c = canvas.Canvas(pdf, pagesize=(W, H)); c.setTitle("Code & Cozy Sticker Book")
for code, label, names in cats:
    c.setFillColor(HexColor("#FAF6EA")); c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(HexColor("#38362E")); c.setFont("Disp", 40); c.drawString(40, H - 84, label)
    c.setFillColor(HexColor("#6B7F58")); c.setFont("SansB", 8.6); o = c.beginText(42, H - 106); o.setCharSpace(1.7); o.textOut("STICKER BOOK  ·  LASSO, COPY, PASTE INTO ANY PAGE"); c.drawText(o)
    for i, name in enumerate(names):
        im = Image.open(os.path.join(CUT, f"{code}_{i + 1}.png")); s = min(340 / im.width, 190 / im.height)
        w_, h_ = im.width * s, im.height * s; cx, cy = 40 + 187 + (i % 2) * 380, H - 130 - 100 - (i // 2) * 242
        c.drawImage(os.path.join(CUT, f"{code}_{i + 1}.png"), cx - w_ / 2, cy - h_ / 2, w_, h_, mask="auto")
        c.setFillColor(HexColor("#8C8672")); c.setFont("Sans", 8.6); c.drawCentredString(cx, cy - 104, name.replace("_", " "))
    c.showPage()
c.save(); lighten(pdf, 88)

# 5. zips (Etsy allows 20 MB per file): fill each part up to ~17 MB, whole categories together
parts, cur, size = [], [], 0
for code, label, names in cats:
    grp = [f for f in files if f[0] == code]; gsz = sum(os.path.getsize(f[3]) for f in grp)
    if cur and size + gsz > 17e6:
        parts.append(cur); cur, size = [], 0
    cur += grp; size += gsz
parts.append(cur)
for k, grp in enumerate(parts, 1):
    with zipfile.ZipFile(os.path.join(OUT, f"Code_and_Cozy_Stickers_Part{k}.zip"), "w", zipfile.ZIP_STORED) as z:
        for _, _, _, path in grp:
            z.write(path, os.path.join("PNG", os.path.basename(path)))
print(len(files), "stickers,", len(cats), "categories,", len(parts), "zip parts ->", OUT)
