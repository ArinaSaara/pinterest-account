#!/usr/bin/env python3
"""Primary Etsy photo: iPad filling the frame with a text-free cover, bold label on top.

Composed for Etsy's 4:3 thumbnail crop (keeps the label and badges inside the
central band). Output: images/year_of_dragons/etsy_upload/photos/01_cover.jpg

Run:  python3 build_hero.py
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import build_photo_mockups as bpm
import build_year_of_dragons as yod

ROOT = os.path.dirname(os.path.abspath(__file__))
YD = os.path.join(ROOT, "images", "year_of_dragons")
PHOTOS = os.path.join(YD, "etsy_upload", "photos")
AV = "/System/Library/Fonts/Avenir Next.ttc"
W, H = yod.W, yod.H


def hero_cover_page():
    """Cover background + four adults, no title, no footer; label is added on the photo."""
    bg = (243, 236, 228)
    glow = Image.new("RGB", (W, H), bg); gd = ImageDraw.Draw(glow)
    gd.ellipse((60, 520, 760, 1320), fill=yod.ELEMENTS[0]["glow"]); gd.ellipse((776, 520, 1476, 1320), fill=yod.ELEMENTS[1]["glow"])
    gd.ellipse((60, 1180, 760, 1980), fill=yod.ELEMENTS[2]["glow"]); gd.ellipse((776, 1180, 1476, 1980), fill=yod.ELEMENTS[3]["glow"])
    img = glow.filter(ImageFilter.GaussianBlur(170)).convert("RGBA"); d = ImageDraw.Draw(img)
    for e, (cx, cy) in zip(yod.ELEMENTS, [(400, 820), (1136, 820), (400, 1440), (1136, 1440)]):
        yod.put(img, e["key"], "08", 500, cx, cy, center=True)
        d = ImageDraw.Draw(img); d.text((cx, cy + 300), f"{e['season'].upper()}  ·  {e['name'].upper()}", font=yod.F_SEC, fill=e["accent"], anchor="mm")
    p = os.path.join(YD, "pages", "_hero_cover.png"); img.convert("RGB").save(p); return p


def build():
    scene = Image.open(os.path.join(YD, "scenes", "desk_square.jpg")).convert("RGB")
    cx, cy, side = 1002, 988, 1240
    tight = os.path.join(YD, "scenes", "_desk_tight.jpg")
    scene.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2)).resize((2000, 2000), Image.LANCZOS).save(tight, quality=95)
    bpm.OUT = PHOTOS
    bpm.composite(tight, hero_cover_page(), "_hero_raw.jpg")
    im = Image.open(os.path.join(PHOTOS, "_hero_raw.jpg")).convert("RGB"); d = ImageDraw.Draw(im); S = 2000
    F1 = ImageFont.truetype(AV, 124, index=2); F2 = ImageFont.truetype(AV, 42); F3 = ImageFont.truetype(AV, 40, index=2)
    d.text((S // 2, 390), "Year of Dragons", font=F1, fill=(60, 56, 54), anchor="mm")
    d.text((S // 2, 490), "GoodNotes planner with dragon stickers", font=F2, fill=(100, 92, 88), anchor="mm")
    d.text((S // 2, 545), "that grow with your habits", font=F2, fill=(100, 92, 88), anchor="mm")
    d.line((S // 2 - 220, 600, S // 2 + 220, 600), fill=(226, 112, 52), width=5)
    badges = [("33 pages", (226, 112, 52)), ("32 stickers", (86, 140, 196)), ("hyperlinked", (36, 148, 166)), ("instant download", (122, 92, 190))]
    widths = [d.textlength(t, font=F3) + 70 for t, _ in badges]; total = sum(widths) + 24 * (len(badges) - 1)
    bx = (S - total) / 2; by = 1640
    for (t, col), w in zip(badges, widths):
        d.rounded_rectangle((bx, by, bx + w, by + 90), 45, fill=(255, 255, 255), outline=col, width=4)
        d.text((bx + w / 2, by + 45), t, font=F3, fill=col, anchor="mm"); bx += w + 24
    im.save(os.path.join(PHOTOS, "01_cover.jpg"), quality=90, optimize=True, progressive=True)
    os.remove(os.path.join(PHOTOS, "_hero_raw.jpg"))
    im.crop((0, 250, 2000, 1750)).resize((800, 600), Image.LANCZOS).save(os.path.join(YD, "etsy_upload", "_thumb_4x3_preview.jpg"), quality=85)
    print("01_cover.jpg", os.path.getsize(os.path.join(PHOTOS, "01_cover.jpg")) // 1000, "KB")


if __name__ == "__main__":
    build()
