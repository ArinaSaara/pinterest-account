#!/usr/bin/env python3
"""Vertical 1000x1500 Pinterest pins for the Year of Dragons listing.

Output: images/pins/*.jpg (under 1 MB each) and a preview sheet.
Run:  python3 build_pins.py
"""
import glob
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "images"); YD = os.path.join(IMG, "year_of_dragons"); OUT = os.path.join(IMG, "pins")
os.makedirs(OUT, exist_ok=True)
AV = "/System/Library/Fonts/Avenir Next.ttc"; SUP = "/System/Library/Fonts/Supplemental/"
W, H = 1000, 1500
DARK = (60, 56, 54); GREY = (130, 122, 116)
ELEMENTS = [("fire", "Fire", "Autumn", (226, 112, 52), (252, 226, 206)), ("ice", "Ice", "Winter", (86, 140, 196), (222, 236, 248)),
            ("water", "Water", "Spring", (36, 148, 166), (210, 240, 242)), ("lightning", "Lightning", "Summer", (122, 92, 190), (232, 224, 248))]


def font(n, s, i=0):
    return ImageFont.truetype(n, s, index=i)


def sticker(key, stage, h):
    f = sorted(glob.glob(os.path.join(IMG, key, "transparent", f"{stage}*.png")))[0]
    s = Image.open(f).convert("RGBA"); s = s.crop(s.getchannel("A").getbbox())
    return s.resize((int(s.width * h / s.height), h), Image.LANCZOS)


def backdrop(soft, accent=None):
    bg = Image.new("RGB", (W, H), (250, 246, 238)); d = ImageDraw.Draw(bg)
    d.ellipse((-200, 200, 700, 1100), fill=soft); d.ellipse((400, 700, 1300, 1700), fill=(255, 255, 255))
    return bg.filter(ImageFilter.GaussianBlur(140)).convert("RGBA")


def header(im, title, sub, accent, y=90):
    d = ImageDraw.Draw(im); F1 = font(AV, 66, 2); F2 = font(SUP + "Bradley Hand Bold.ttf", 36)
    d.text((W // 2, y), title, font=F1, fill=DARK, anchor="mm"); d.text((W // 2, y + 70), sub, font=F2, fill=accent, anchor="mm")


def footer(im, text, accent):
    d = ImageDraw.Draw(im); F = font(AV, 28, 2)
    w = d.textlength(text, font=F) + 60; x = (W - w) / 2
    d.rounded_rectangle((x, H - 110, x + w, H - 50), 30, fill=(255, 255, 255), outline=accent, width=3)
    d.text((W // 2, H - 80), text, font=F, fill=accent, anchor="mm")


def save(im, name):
    p = os.path.join(OUT, name); q = 90
    while True:
        im.convert("RGB").save(p, "JPEG", quality=q, optimize=True, progressive=True)
        if os.path.getsize(p) <= 1_000_000 or q <= 70:
            break
        q -= 5
    print(name, os.path.getsize(p) // 1000, "KB")


# 1-4: one sheet pin per element (2 columns x 4 rows of stages)
for key, name, season, accent, soft in ELEMENTS:
    im = backdrop(soft); header(im, f"{name} Dragon Stickers", f"8 life stages · {season.lower()} dragon for GoodNotes", accent)
    cw, rh, top = 440, 300, 230
    for i in range(8):
        r, c = divmod(i, 2); s = sticker(key, f"0{i + 1}", 270)
        cx = 60 + c * cw + cw / 2 + 10; cy = top + r * rh + rh / 2
        im.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))
    footer(im, "digital stickers · transparent PNG · instant download", accent)
    save(im, f"pin_{key}_stickers.jpg")

# 5: all four adults, "collect them all"
im = backdrop((232, 224, 248)); header(im, "Year of Dragons", "four seasons · four dragons · one planner", (122, 92, 190))
for i, (key, name, season, accent, soft) in enumerate(ELEMENTS):
    r, c = divmod(i, 2); s = sticker(key, "08", 520); cx = 60 + c * 440 + 230; cy = 240 + r * 580 + 270
    im.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))
    d = ImageDraw.Draw(im); d.text((cx, cy + 290), f"{season.upper()} · {name.upper()}", font=font(AV, 24, 2), fill=accent, anchor="mm")
footer(im, "hyperlinked GoodNotes planner · 33 pages", (122, 92, 190))
save(im, "pin_year_of_dragons.jpg")

# 6: how it works (September page with 4 stages pasted, from the photo mockup pipeline)
demo = os.path.join(YD, "pages", "_demo_sep.png")
if os.path.exists(demo):
    pg = Image.open(demo).convert("RGB"); im = backdrop((252, 226, 206)); header(im, "Watch it grow", "paste the next dragon stage at every streak milestone", (226, 112, 52))
    crop = pg.crop((60, 60, 1476, 1300)).resize((880, 770), Image.LANCZOS)
    fr = Image.new("RGBA", (904, 794), (44, 44, 50, 255)); fr.paste(crop, (12, 12)); im.alpha_composite(fr, (48, 230))
    s = sticker("fire", "05", 360); im.alpha_composite(s, (600, 1040))
    d = ImageDraw.Draw(im); F = font(SUP + "Bradley Hand Bold.ttf", 34)
    for i, t in enumerate(["1. track 5 habits a day", "2. hit a streak milestone", "3. lasso the next sticker", "4. paste it over the faded stage"]):
        d.text((80, 1060 + i * 50), t, font=F, fill=DARK)
    footer(im, "habit tracker for GoodNotes · instant download", (226, 112, 52))
    save(im, "pin_how_it_works.jpg")

# 7-8: copy existing photo pins
for src, dst in (("mockups_photo/05_pin_cover.jpg", "pin_photo_cover.jpg"), ("mockups_photo/06_pin_ice_sheet.jpg", "pin_photo_ice_sheet.jpg")):
    save(Image.open(os.path.join(YD, src)).convert("RGB"), dst)

# 9: trackers pin (fan of four tracker pages)
im = backdrop((210, 240, 242)); header(im, "8 themed trackers", "reading, sleep, water, mood, focus, study, habits, savings", (36, 148, 166))
pages = ["ice_90_reading.png", "water_90_mood.png", "lightning_90_savings.png", "fire_90_focus.png"]
for i, n in enumerate(pages):
    pg = Image.open(os.path.join(YD, "pages", n)).convert("RGBA").resize((420, 560), Image.LANCZOS)
    fr = Image.new("RGBA", (436, 576), (255, 255, 255, 255)); fr.alpha_composite(pg, (8, 8)); fr = fr.rotate(-10 + i * 7, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(fr, (60 + i * 130, 300 + abs(i - 1) * 60))
s = sticker("water", "04", 330); im.alpha_composite(s, (620, 1050))
footer(im, "each with its own dragon growth bar", (36, 148, 166))
save(im, "pin_trackers.jpg")

files = sorted(glob.glob(os.path.join(OUT, "pin_*.jpg"))); th = [Image.open(f).resize((300, 450)) for f in files]
sheet = Image.new("RGB", (len(th) * 310 + 10, 460), (200, 196, 190))
for i, t in enumerate(th):
    sheet.paste(t, (10 + i * 310, 5))
sheet.save(os.path.join(OUT, "preview_pins.jpg"), quality=85); print("pins:", len(files))
