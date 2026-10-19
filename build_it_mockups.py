#!/usr/bin/env python3
"""iPad mockups for the Code & Cozy listing: 2000x2000 Etsy photos and 1000x1500 Pinterest pins.

Inputs:  images/it_girl/Code_and_Cozy_Planner_2027_Mon.pdf, images/it_girl/cut/*.png, images/it_girl/sticker_pack/
Outputs: images/it_girl/mockups/*.png (+ preview_mockups.jpg)

Run:  .venv-planner/bin/python build_it_mockups.py
"""
import glob
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from build_mockups import ipad, pencil, place

ROOT = os.path.dirname(os.path.abspath(__file__))
IT = os.path.join(ROOT, "images", "it_girl")
PDF = os.path.join(IT, "Code_and_Cozy_Planner_2027_Mon.pdf")
CUT = os.path.join(IT, "cut"); PNGS = os.path.join(IT, "pages_png"); OUT = os.path.join(IT, "mockups")
FONTS = os.path.join(ROOT, "fonts")
os.makedirs(PNGS, exist_ok=True); os.makedirs(OUT, exist_ok=True)

INK = (56, 54, 46); MUTED = (140, 134, 114); SAGE = (107, 127, 88); SAGE_D = (76, 94, 64); TERRA = (192, 105, 74); GOLD = (181, 139, 58)
CREAM = (250, 246, 234)
PAGE = dict(cover=1, home=2, start=3, year=4, goals=5, pixels=6, q1=7, jan=11, week=36, day_wed=100, day_fri=88, work=453, proj=454, sprint=455, one=456, meet=457,
            brag=458, learn=459, bug=460, career=461, health=462, habits=463, workout=475, meal=476, sleep=477, life=479, budget=482, travel=484, social=488, love=490, seasons=491)


def F(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name + ".ttf"), size)


def page(key):
    f = os.path.join(PNGS, f"{PAGE[key]:03d}.png")
    if not os.path.exists(f):
        subprocess.run(["pdftoppm", "-f", str(PAGE[key]), "-l", str(PAGE[key]), "-r", "133", "-png", "-singlefile", PDF, f[:-4]], check=True)
    return Image.open(f).convert("RGB")


def stk(name, h, rot=0):
    s = Image.open(os.path.join(CUT, name + ".png")).convert("RGBA"); s = s.resize((int(s.width * h / s.height), h), Image.LANCZOS)
    return s.rotate(rot, expand=True, resample=Image.BICUBIC) if rot else s


def backdrop(size, tint=0):
    w, h = size; bg = Image.new("RGB", (w, h), (246, 241, 229)); d = ImageDraw.Draw(bg)
    blobs = [((220, 229, 204), (0.2, 0.25)), ((245, 221, 207), (0.85, 0.7)), ((242, 228, 191), (0.5, 0.95))]
    for i, (c, (fx, fy)) in enumerate(blobs):
        cx, cy = int(w * (fx + 0.05 * tint)), int(h * fy); d.ellipse((cx - w // 3, cy - h // 3, cx + w // 3, cy + h // 3), fill=c)
    return bg.filter(ImageFilter.GaussianBlur(int(w * 0.11))).convert("RGBA")


def heading(c, title, sub, badges, y, x=None, align="left", size=None):
    d = ImageDraw.Draw(c); W = c.width; x = int(W * 0.07) if x is None else x; size = size or int(W * 0.07)
    anchor = "la" if align == "left" else "ma"
    d.text((x, y), title, font=F("PlayfairDisplay-Regular", size), fill=INK, anchor=anchor)
    d.text((x + 2, y + int(size * 1.25)), sub.upper(), font=F("DMSans-SemiBold", int(W * 0.0145)), fill=SAGE_D, anchor=anchor)
    fb = F("DMSans-SemiBold", int(W * 0.0145)); by = y + int(size * 1.25) + int(W * 0.04); pad = int(W * 0.018)
    widths = [d.textlength(b.upper(), font=fb) + 2 * pad for b in badges]; total = sum(widths) + 14 * (len(badges) - 1)
    bx = x - total // 2 if align != "left" else x
    for b, w_ in zip(badges, widths):
        d.rounded_rectangle((bx, by, bx + w_, by + int(W * 0.036)), int(W * 0.018), fill=(255, 255, 255, 235), outline=SAGE, width=2)
        d.text((bx + w_ / 2, by + int(W * 0.018)), b.upper(), font=fb, fill=SAGE_D, anchor="mm"); bx += w_ + 14


def callout(c, text, tx, ty, px, py, side="right", col=TERRA):
    """Pill with a leader line to point (px, py)."""
    d = ImageDraw.Draw(c); f = F("DMSans-SemiBold", 30); w = d.textlength(text.upper(), font=f) + 56; h = 64
    x0 = tx if side == "right" else tx - w
    d.line((x0 if side == "right" else x0 + w, ty + h // 2, px, py), fill=col, width=4)
    d.ellipse((px - 11, py - 11, px + 11, py + 11), fill=col, outline=(255, 255, 255), width=4)
    d.rounded_rectangle((x0, ty, x0 + w, ty + h), h // 2, fill=(255, 255, 255, 245), outline=col, width=3)
    d.text((x0 + w / 2, ty + h / 2), text.upper(), font=f, fill=col, anchor="mm")


def pt(tab, bez, sw, x, y, ix, iy):
    """page point (pt, top-based, 834x1112) -> canvas px."""
    s = sw / 834; return int(ix + bez + x * s), int(iy + bez + y * s)


def save(c, name):
    c.convert("RGB").save(os.path.join(OUT, name), optimize=True)


def device(key, sw):
    tab = ipad(page(key), sw); return tab, int(sw * 0.045)


# ------------------------------------------------------------------ Etsy photos
def m01_hero():
    S = 2000; c = backdrop((S, S)); tab, bez = device("cover", 860); ix, iy = S - tab.width - 150, 500; place(c, tab, ix, iy)
    place(c, pencil(760, 30, -28), 110, S - 640)
    for n, h, x, y, r in (("work_3", 330, 120, 700, -6), ("fit_2", 420, 360, 900, 5), ("cozy_4", 300, 90, 1130, -4), ("travel_6", 320, 520, 1330, 6)):
        place(c, stk(n, h, r), x, y)
    heading(c, "Code & Cozy", "2027 daily planner for GoodNotes", ["508 pages", "hyperlinked", "80 stickers", "work · health · life"], 150, size=160)
    save(c, "01_hero_square.png")


def m02_daily():
    S = 2000; c = backdrop((S, S), 1); sw = 960; tab, bez = device("day_wed", sw); ix, iy = (S - tab.width) // 2, 540; place(c, tab, ix, iy)
    heading(c, "Plan the day, not just the tasks", "one daily page, work and life together", ["365 daily pages"], 120, size=96)
    P = lambda x, y: pt(tab, bez, sw, x, y, ix, iy)
    lx, rx = ix - 40, ix + tab.width + 40
    callout(c, "Top 3 + to-do", lx, 660, *P(300, 245), side="left"); callout(c, "Focus blocks", lx, 1080, *P(170, 828), side="left"); callout(c, "Mood · energy · sleep", lx, 1240, *P(150, 925), side="left")
    callout(c, "Hourly schedule", rx, 720, *P(650, 330)); callout(c, "Tap tabs to jump", rx, 900, *P(822, 560)); callout(c, "Water · meals · move", rx, 1290, *P(650, 925))
    place(c, stk("dev_6", 300, 3), 40, 1560); place(c, stk("dev_3", 280, -4), 1660, 1620)
    save(c, "02_daily_page.png")


def m03_links():
    S = 2000; c = backdrop((S, S)); sw = 1000; tab, bez = device("jan", sw); ix, iy = S - sw - 330, 520; place(c, tab, ix, iy)
    heading(c, "Everything is a link", "tabs, dates, weeks and months", ["tap any date", "12 month jumps", "53 weeks"], 140, size=110)
    P = lambda x, y: pt(tab, bez, sw, x, y, ix, iy)
    callout(c, "Month strip", 110, 620, *P(120, 28)); callout(c, "Review & habits", 110, 770, *P(330, 27))
    callout(c, "Week number: weekly page", 110, 920, *P(53, 320)); callout(c, "Tap a date: daily page", 110, 1070, *P(200, 450))
    callout(c, "Colour tabs", 110, 1220, *P(822, 640))
    place(c, stk("seasons_7", 360, -5), 140, 1560)
    save(c, "03_everything_linked.png")


def m04_inside():
    S = 2000; c = backdrop((S, S), 2); heading(c, "What is inside", "508 hyperlinked pages in one PDF", ["365 daily", "53 weekly", "12 monthly", "40+ templates"], 120, size=100)
    keys = [("cover", "Cover"), ("year", "Year at a glance"), ("q1", "Quarter OKRs"), ("jan", "12 months"), ("week", "53 weeks"), ("day_fri", "365 days"), ("sprint", "Work hub"), ("meal", "Health & life")]
    sw = 360
    for i, (k, lab) in enumerate(keys):
        tab, bez = device(k, sw); x = 95 + (i % 4) * 470; y = 520 + (i // 4) * 740; place(c, tab, x, y)
        ImageDraw.Draw(c).text((x + tab.width // 2, y + tab.height + 40), lab.upper(), font=F("DMSans-SemiBold", 28), fill=SAGE_D, anchor="mm")
    save(c, "04_whats_inside.png")


def m05_work():
    S = 2000; c = backdrop((S, S)); heading(c, "Built for women in tech", "sprint board, 1:1s, brag document and more", ["8 work templates", "bug log", "career roadmap"], 130, size=110)
    for k, sw, x, y, r in (("brag", 640, 130, 740, 7), ("meet", 640, 1200, 740, -7), ("sprint", 760, 620, 640, 0)):
        tab, _ = device(k, sw); tab = tab.rotate(r, expand=True, resample=Image.BICUBIC); place(c, tab, x, y)
    for n, h, x, y, r in (("dev_2", 340, 120, 1480, -4), ("dev_3", 330, 1480, 1500, 4)):
        place(c, stk(n, h, r), x, y)
    save(c, "05_work_hub.png")


def m06_life():
    S = 2000; c = backdrop((S, S), 1); heading(c, "Health, home and the fun part", "habits, meals, budget, trips, date nights", ["12 habit trackers", "budget", "travel", "hobbies"], 130, size=100)
    ks = ["habits", "meal", "budget", "travel", "love"]
    for i, k in enumerate(ks):
        pg = page(k).resize((560, 747), Image.LANCZOS).convert("RGBA"); fr = Image.new("RGBA", (pg.width + 24, pg.height + 24), (255, 255, 255, 255)); fr.alpha_composite(pg, (12, 12))
        fr = fr.rotate(-14 + i * 7, expand=True, resample=Image.BICUBIC); place(c, fr, 130 + i * 340, 640 + abs(i - 2) * 70)
    place(c, stk("travel_1", 360, -4), 110, 1500); place(c, stk("hobby_5", 300, 3), 1500, 1560)
    save(c, "06_health_life.png")


def m07_stickers():
    Image.open(os.path.join(IT, "sticker_pack", "overview.jpg")).convert("RGB").resize((2000, 2000), Image.LANCZOS).save(os.path.join(OUT, "07_all_stickers.png"), optimize=True)


def m08_categories():
    S = 2000; c = backdrop((S, S), 1); heading(c, "10 sticker sets", "80 transparent PNG stickers for GoodNotes", ["die-cut", "ready for Elements", "sticker book PDF"], 110, size=100)
    names = [("work", "Work"), ("dev", "Dev life"), ("fit", "Move & eat"), ("cozy", "Cozy"), ("travel", "Travel"), ("home", "Home"), ("hobby", "Hobbies"), ("social", "Friends"), ("seasons", "Seasons"), ("love", "Date night")]
    cw, chh = 360, 540
    for i, (code, lab) in enumerate(names):
        sh = Image.open(os.path.join(IT, "sticker_pack", "sheets", f"{code}_sheet.png")).convert("RGB").resize((cw, chh), Image.LANCZOS).convert("RGBA")
        fr = Image.new("RGBA", (cw + 16, chh + 16), (255, 255, 255, 255)); fr.alpha_composite(sh, (8, 8)); x = 78 + (i % 5) * 382; y = 480 + (i // 5) * 690
        place(c, fr, x, y); ImageDraw.Draw(c).text((x + fr.width // 2, y + fr.height + 36), lab.upper(), font=F("DMSans-SemiBold", 26), fill=SAGE_D, anchor="mm")
    save(c, "08_sticker_sets.png")


def m09_year():
    S = 2000; c = backdrop((S, S)); heading(c, "See the whole year", "year at a glance, goals and year in pixels", ["12 mini calendars", "365 dots"], 130, size=110)
    for k, sw, x, y, r in (("year", 700, 150, 640, -4), ("pixels", 760, 1060, 600, 4), ("goals", 520, 700, 1180, 0)):
        tab, _ = device(k, sw); tab = tab.rotate(r, expand=True, resample=Image.BICUBIC); place(c, tab, x, y)
    place(c, stk("seasons_8", 330, -4), 120, 1500); place(c, stk("seasons_1", 300, 4), 1500, 1560)
    save(c, "09_year_view.png")


def m10_how():
    S = 2000; c = backdrop((S, S), 2); sw = 780; tab, _ = device("start", sw); place(c, tab, 160, 620)
    heading(c, "Ready in 3 steps", "instant digital download", ["GoodNotes 5 & 6", "iPad & Apple Pencil"], 130, size=120)
    steps = [("1", "Download the PDF", "and import it into GoodNotes"), ("2", "Add the stickers", "PNGs go to Elements, or use the sticker book"), ("3", "Tap and plan", "every tab, date and month is linked")]
    d = ImageDraw.Draw(c)
    for i, (n, t, s_) in enumerate(steps):
        y = 640 + i * 330; d.rounded_rectangle((1060, y, 1860, y + 270), 40, fill=(255, 255, 255, 240), outline=SAGE, width=3)
        d.ellipse((1100, y + 80, 1190, y + 170), fill=SAGE); d.text((1145, y + 125), n, font=F("PlayfairDisplay-Bold", 60), fill=(255, 255, 255), anchor="mm")
        d.text((1230, y + 105), t, font=F("PlayfairDisplay-Regular", 52), fill=INK, anchor="lm"); d.text((1230, y + 180), s_, font=F("DMSans-Regular", 30), fill=MUTED, anchor="lm")
    place(c, stk("work_5", 300, 3), 1500, 1620)
    save(c, "10_how_it_works.png")


# ------------------------------------------------------------------ Pinterest pins 1000x1500
def p01_hero():
    Wp, Hp = 1000, 1500; c = backdrop((Wp, Hp)); tab, _ = device("cover", 600); place(c, tab, (Wp - tab.width) // 2, 400)
    heading(c, "Code & Cozy", "2027 daily planner for GoodNotes", ["508 pages", "hyperlinked", "80 stickers"], 90, x=Wp // 2, align="center", size=120)
    place(c, stk("fit_2", 300, -6), 20, 1090); place(c, stk("cozy_4", 230, 6), 740, 1180)
    save(c, "p01_hero_pin.png")


def p02_daily():
    Wp, Hp = 1000, 1500; c = backdrop((Wp, Hp), 1); heading(c, "A daily planner for women in tech", "work and life on one page", ["GoodNotes", "iPad"], 70, x=Wp // 2, align="center", size=62)
    tab, _ = device("day_wed", 640); place(c, tab, (Wp - tab.width) // 2, 330); place(c, stk("dev_3", 270, -5), 10, 1170); place(c, stk("work_6", 220, 5), 780, 1250)
    save(c, "p02_daily_pin.png")


def p03_work():
    Wp, Hp = 1000, 1500; c = backdrop((Wp, Hp)); heading(c, "Sprint board, brag doc, 1:1 notes", "the work hub for your career", ["8 templates"], 70, x=Wp // 2, align="center", size=62)
    for k, sw, x, y, r in (("brag", 380, 40, 520, 7), ("meet", 380, 590, 520, -7), ("sprint", 470, 265, 460, 0)):
        tab, _ = device(k, sw); tab = tab.rotate(r, expand=True, resample=Image.BICUBIC); place(c, tab, x, y)
    place(c, stk("dev_1", 300, -3), 20, 1150); place(c, stk("dev_2", 280, 3), 640, 1170)
    save(c, "p03_work_pin.png")


def p04_stickers():
    Wp, Hp = 1000, 1500; c = backdrop((Wp, Hp), 2); heading(c, "80 cozy IT-girl stickers", "digital stickers for GoodNotes", ["transparent PNG"], 70, x=Wp // 2, align="center", size=70)
    names = ["dev_3", "work_3", "travel_6", "cozy_4", "hobby_5", "dev_2", "fit_2", "seasons_8", "social_2", "home_5"]
    for i, n in enumerate(names):
        s = stk(n, 200); s.thumbnail((440, 200)); x = 40 + (i % 2) * 490 + (440 - s.width) // 2; y = 390 + (i // 2) * 205; place(c, s, x, y)
    save(c, "p04_stickers_pin.png")


if __name__ == "__main__":
    for fn in (m01_hero, m02_daily, m03_links, m04_inside, m05_work, m06_life, m07_stickers, m08_categories, m09_year, m10_how, p01_hero, p02_daily, p03_work, p04_stickers):
        fn()
    files = sorted(glob.glob(os.path.join(OUT, "*.png"))); h = 480
    ims = [Image.open(f).convert("RGB") for f in files]; ims = [i.resize((int(i.width * h / i.height), h), Image.LANCZOS) for i in ims]
    cols = 7; rows = (len(ims) + cols - 1) // cols; mw = max(i.width for i in ims)
    sheet = Image.new("RGB", (cols * (mw + 10) + 10, rows * (h + 10) + 10), (200, 196, 190))
    for k, i in enumerate(ims):
        sheet.paste(i, (10 + (k % cols) * (mw + 10), 10 + (k // cols) * (h + 10)))
    sheet.save(os.path.join(OUT, "preview_mockups.jpg"), quality=85); print("mockups:", len(files))
