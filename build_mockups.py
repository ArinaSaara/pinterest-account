#!/usr/bin/env python3
"""Render iPad mockups of the Year of Dragons planner for shop listings and pins.

Inputs:  images/year_of_dragons/pages/*.png (run build_year_of_dragons.py first)
         images/<element>/transparent/0*.png
Outputs: images/year_of_dragons/mockups/*.png
         2000x2000 squares for Etsy-style listings, 1000x1500 pins for Pinterest

Run:  python3 build_mockups.py
"""
import calendar
import glob
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "images")
PAGES = os.path.join(IMG, "year_of_dragons", "pages")
OUT = os.path.join(IMG, "year_of_dragons", "mockups")
os.makedirs(OUT, exist_ok=True)

AV = "/System/Library/Fonts/Avenir Next.ttc"; SUP = "/System/Library/Fonts/Supplemental/"


def font(n, s, i=0):
    return ImageFont.truetype(n, s, index=i)


DARK = (60, 56, 54); GREY = (140, 134, 128)
ACCENT = {"fire": (226, 112, 52), "ice": (86, 140, 196), "water": (36, 148, 166), "lightning": (122, 92, 190)}
SOFT = {"fire": (252, 226, 206), "ice": (222, 236, 248), "water": (210, 240, 242), "lightning": (232, 224, 248)}


def page(name):
    return Image.open(os.path.join(PAGES, name)).convert("RGB")


def sticker(key, stage):
    f = sorted(glob.glob(os.path.join(IMG, key, "transparent", f"{stage}*.png")))[0]
    im = Image.open(f).convert("RGBA"); b = im.getchannel("A").getbbox(); p = 10
    return im.crop((max(0, b[0] - p), max(0, b[1] - p), min(im.width, b[2] + p), min(im.height, b[3] + p)))


def ipad(screen_img, screen_w, portrait=True):
    """Return an RGBA iPad with the given page on screen. Screen aspect is 3:4 portrait."""
    sw = screen_w; sh = int(sw * 4 / 3)
    bez = int(sw * 0.045); r_out = int(sw * 0.075); r_in = int(sw * 0.03)
    tw, th = sw + 2 * bez, sh + 2 * bez
    body = Image.new("RGBA", (tw, th), (0, 0, 0, 0)); d = ImageDraw.Draw(body)
    d.rounded_rectangle((0, 0, tw - 1, th - 1), r_out, fill=(34, 34, 38, 255))
    d.rounded_rectangle((3, 3, tw - 4, th - 4), r_out - 3, outline=(92, 92, 98, 255), width=2)
    scr = screen_img.resize((sw, sh), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (sw, sh), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw - 1, sh - 1), r_in, fill=255)
    body.paste(scr, (bez, bez), mask)
    # camera dot and subtle glass highlight
    d = ImageDraw.Draw(body); d.ellipse((tw // 2 - 6, bez // 2 - 6, tw // 2 + 6, bez // 2 + 6), fill=(70, 70, 76))
    gl = Image.new("RGBA", (tw, th), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
    gd.polygon([(bez, bez), (bez + int(sw * 0.55), bez), (bez, bez + int(sh * 0.4))], fill=(255, 255, 255, 18))
    body.alpha_composite(gl)
    if not portrait:
        body = body.rotate(90, expand=True)
    return body


def pencil(length=900, width=34, angle=-35):
    L, Wd = length, width
    im = Image.new("RGBA", (L + 40, Wd + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20 + 60, 20, 20 + L, 20 + Wd), Wd // 2, fill=(246, 246, 248, 255), outline=(200, 200, 205, 255), width=2)
    d.polygon([(20 + 60, 20), (20 + 60, 20 + Wd), (20, 20 + Wd // 2)], fill=(238, 238, 240, 255))
    d.polygon([(20 + 22, 20 + Wd // 2 - 6), (20 + 22, 20 + Wd // 2 + 6), (20, 20 + Wd // 2)], fill=(90, 90, 95, 255))
    d.line((20 + 70, 20 + 7, 20 + L - 10, 20 + 7), fill=(255, 255, 255, 255), width=3)
    return im.rotate(angle, expand=True, resample=Image.BICUBIC)


def shadow_of(im, blur=40, offset=(0, 40), alpha=110):
    sh = Image.new("RGBA", (im.width + blur * 4, im.height + blur * 4), (0, 0, 0, 0))
    a = im.getchannel("A").point(lambda v: int(v * alpha / 255))
    sh.paste((0, 0, 0, 255), (blur * 2 + offset[0], blur * 2 + offset[1]), a)
    return sh.filter(ImageFilter.GaussianBlur(blur)), blur * 2


def place(canvas, im, x, y, shadow=True):
    if shadow:
        sh, off = shadow_of(im); canvas.alpha_composite(sh, (x - off, y - off))
    canvas.alpha_composite(im, (x, y))


def backdrop(size, key=None, warm=True):
    w, h = size
    base = (244, 238, 230) if warm else (236, 238, 242)
    bg = Image.new("RGB", (w, h), base); d = ImageDraw.Draw(bg)
    cols = [SOFT[k] for k in (("fire", "ice", "water", "lightning") if key is None else (key,))]
    for i, c in enumerate(cols):
        cx = int(w * (0.2 + 0.6 * (i % 2))); cy = int(h * (0.25 + 0.5 * (i // 2 % 2)))
        d.ellipse((cx - w // 3, cy - h // 3, cx + w // 3, cy + h // 3), fill=c)
    return bg.filter(ImageFilter.GaussianBlur(int(w * 0.12))).convert("RGBA")


def caption(canvas, title, sub, badges, y, accent=DARK, align="left", x=None):
    d = ImageDraw.Draw(canvas); W = canvas.width
    FT = font(AV, int(W * 0.046), 2); FS = font(AV, int(W * 0.02)); FB = font(AV, int(W * 0.016), 2)
    if x is None:
        x = int(W * 0.07)
    anchor = "la" if align == "left" else "ma"
    d.text((x, y), title, font=FT, fill=DARK, anchor=anchor); d.text((x, y + int(W * 0.06)), sub, font=FS, fill=GREY, anchor=anchor)
    bx = x; by = y + int(W * 0.1)
    if align != "left":
        total = sum(d.textlength(b, font=FB) + int(W * 0.03) for b in badges) + (len(badges) - 1) * 16; bx = x - total // 2
    for b in badges:
        tw = d.textlength(b, font=FB) + int(W * 0.03)
        d.rounded_rectangle((bx, by, bx + tw, by + int(W * 0.034)), int(W * 0.017), fill=(255, 255, 255, 230), outline=accent, width=2)
        d.text((bx + tw / 2, by + int(W * 0.017)), b, font=FB, fill=accent, anchor="mm"); bx += tw + 16


# ------------------------------------------------------------------ mockups
def hero_square():
    S = 2000; c = backdrop((S, S)); tab = ipad(page("00_cover.png"), 820)
    place(c, tab, S - tab.width - 170, 520)
    pen = pencil(760, 30, -28); place(c, pen, 120, S - 700, shadow=True)
    for key, stage, x, y, rot in (("fire", "03", 140, 700, -8), ("ice", "04", 420, 820, 6), ("water", "03", 120, 1020, 5), ("lightning", "04", 430, 1150, -6)):
        s = sticker(key, stage); s = s.resize((int(s.width * 300 / s.height), 300), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC); place(c, s, x, y)
    caption(c, "Year of Dragons", "digital planner for GoodNotes with growing dragon stickers", ["33 pages", "4 elements", "32 stages", "hyperlinked"], 150)
    c.convert("RGB").save(os.path.join(OUT, "01_hero_square.png"), optimize=True)


def hero_pin():
    Wp, Hp = 1000, 1500; c = backdrop((Wp, Hp)); tab = ipad(page("00_cover.png"), 560)
    place(c, tab, (Wp - tab.width) // 2, 330)
    for key, stage, x, y, rot in (("fire", "03", 40, 1120, -8), ("lightning", "04", 760, 1150, 6)):
        s = sticker(key, stage); s = s.resize((int(s.width * 220 / s.height), 220), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC); place(c, s, x, y)
    caption(c, "Year of Dragons", "GoodNotes planner: hatch a dragon every season", ["33 pages", "4 sticker sets", "hyperlinked"], 90, align="center", x=Wp // 2)
    c.convert("RGB").save(os.path.join(OUT, "02_hero_pin.png"), optimize=True)


def growth_demo():
    """September page on iPad with stages 1-4 already pasted over the faded bar: shows the mechanic."""
    S = 2000; key = "fire"; c = backdrop((S, S), key)
    pg = page("fire_09_sep.png").convert("RGBA")
    # paste coloured stages 1..4 over the faded growth bar (same geometry as build_year_of_dragons.Page.stages)
    M, W = 110, 1536; slot = (W - 2 * M) / 8; ry = 260 + 60
    for i in range(4):
        s = sticker(key, f"0{i + 1}"); s = s.resize((int(s.width * 170 / s.height), 170), Image.LANCZOS)
        cx = M + slot * i + slot / 2; pg.alpha_composite(s, (int(cx - s.width / 2), int(ry + 100 - s.height / 2)))
    d = ImageDraw.Draw(pg); a = ACCENT[key]
    for i in range(4):
        cx = M + slot * i + slot / 2; d.ellipse((cx - 13, ry + 250, cx + 13, ry + 276), fill=a)
    d.line((M + slot / 2, ry + 263, M + slot * 3.5, ry + 263), fill=a, width=5)
    # a few habit ticks
    gx = M + 300; cell = (W - M - gx) / 30; gy = ry + 340 + 20 + 50
    for r in range(5):
        yy = gy + 30 + r * 78
        for day in range(14 - r * 2):
            x = gx + day * cell + cell / 2; d.ellipse((x - 11, yy + 17, x + 11, yy + 39), fill=SOFT[key], outline=a, width=2)
    tab = ipad(pg, 860)
    place(c, tab, S - tab.width - 160, 500)
    s = sticker(key, "05"); s = s.resize((int(s.width * 460 / s.height), 460), Image.LANCZOS).rotate(-10, expand=True, resample=Image.BICUBIC)
    place(c, s, 150, 980)
    pen = pencil(700, 28, -30); place(c, pen, 110, S - 620)
    caption(c, "Watch it grow", "hit a streak milestone, paste the next stage over the faded one", ["day 3", "day 7", "day 10", "day 14", "...", "day 30"], 180, accent=a)
    c.convert("RGB").save(os.path.join(OUT, "03_growth_demo.png"), optimize=True)


def four_seasons():
    S = 2000; c = backdrop((S, S))
    covers = ["fire_00_cover.png", "ice_00_cover.png", "water_00_cover.png", "lightning_00_cover.png"]
    for i, name in enumerate(covers):
        tab = ipad(page(name), 520); x = 110 + i * 330; y = 480 + (0 if i % 2 == 0 else 120)
        place(c, tab, x, y)
    caption(c, "Four seasons, four dragons", "autumn fire, winter ice, spring water, summer lightning", ["sold separately", "or as the full year"], 170)
    d = ImageDraw.Draw(c); FS = font(SUP + "Bradley Hand Bold.ttf", 44)
    d.text((S // 2, 1800), "each season: cover, sticker sheet, 3 monthly trackers, 2 themed trackers", font=FS, fill=GREY, anchor="mm")
    c.convert("RGB").save(os.path.join(OUT, "04_four_seasons.png"), optimize=True)


def trackers_fan():
    S = 2000; c = backdrop((S, S), warm=False)
    names = ["ice_90_reading.png", "water_90_water.png", "lightning_90_savings.png", "fire_90_focus.png", "water_90_mood.png"]
    for i, n in enumerate(names):
        pg = page(n).convert("RGBA"); pg = pg.resize((560, 747), Image.LANCZOS)
        fr = Image.new("RGBA", (pg.width + 24, pg.height + 24), (255, 255, 255, 255)); fr.alpha_composite(pg, (12, 12))
        fr = fr.rotate(-14 + i * 7, expand=True, resample=Image.BICUBIC)
        place(c, fr, 160 + i * 300, 560 + abs(i - 2) * 60)
    caption(c, "8 themed trackers", "reading, sleep, water, mood, habits, focus, study and a dragon hoard", ["each with its own growth bar"], 170)
    c.convert("RGB").save(os.path.join(OUT, "05_trackers_fan.png"), optimize=True)


def stickers_square():
    S = 2000; c = backdrop((S, S))
    keys = ["fire", "ice", "water", "lightning"]; stages = ["01", "02", "03", "04", "05", "06", "07", "08"]
    top = 520; cell = (S - 2 * 120) / 8
    for r, key in enumerate(keys):
        for i, st in enumerate(stages):
            s = sticker(key, st); s = s.resize((int(s.width * 300 / s.height), 300), Image.LANCZOS)
            c.alpha_composite(s, (int(120 + i * cell + cell / 2 - s.width / 2), int(top + r * 340 + 170 - s.height / 2)))
    caption(c, "32 dragon stickers", "transparent PNG, ready for GoodNotes Elements", ["4 elements x 8 life stages", "die-cut style"], 170)
    c.convert("RGB").save(os.path.join(OUT, "06_all_stickers.png"), optimize=True)


def hall_pin():
    Wp, Hp = 1000, 1500; c = backdrop((Wp, Hp))
    tab = ipad(page("03_hall_of_dragons.png"), 600); place(c, tab, (Wp - tab.width) // 2, 300)
    for key, x, y, rot in (("ice", 30, 1130, -8), ("fire", 740, 1120, 8)):
        s = sticker(key, "08"); s = s.resize((int(s.width * 300 / s.height), 300), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC); place(c, s, x, y)
    caption(c, "Hall of Dragons", "finish a season, move the adult into the hall", ["collect all four"], 90, align="center", x=Wp // 2)
    c.convert("RGB").save(os.path.join(OUT, "07_hall_pin.png"), optimize=True)


if __name__ == "__main__":
    hero_square(); hero_pin(); growth_demo(); four_seasons(); trackers_fan(); stickers_square(); hall_pin()
    files = sorted(glob.glob(os.path.join(OUT, "*.png")))
    thumbs = [Image.open(f).convert("RGB") for f in files]
    h = 600; ims = [t.resize((int(t.width * h / t.height), h), Image.LANCZOS) for t in thumbs]
    sheet = Image.new("RGB", (sum(i.width for i in ims) + 10 * (len(ims) + 1), h + 20), (200, 196, 190)); x = 10
    for i in ims:
        sheet.paste(i, (x, 10)); x += i.width + 10
    sheet.save(os.path.join(OUT, "preview_mockups.jpg"), quality=85)
    print("mockups:", len(files))
