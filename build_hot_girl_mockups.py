#!/usr/bin/env python3
"""iPad mockups for the Hot Girl Era listing: 2000x2000 Etsy photos and 1000x1500 Pinterest pins.

Inputs:  images/hot_girl/Hot_Girl_Era_Perimenopause_Planner.pdf, images/hot_girl/cut/*.png
Outputs: images/hot_girl/mockups/*.png (+ preview_mockups.jpg)

Run:  .venv-planner/bin/python build_hot_girl_mockups.py
"""
import glob
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from build_mockups import ipad, pencil, place

ROOT = os.path.dirname(os.path.abspath(__file__))
WD = os.path.join(ROOT, "images", "hot_girl")
PDF = os.path.join(WD, "Hot_Girl_Era_Perimenopause_Planner.pdf")
CUT = os.path.join(WD, "cut"); PNGS = os.path.join(WD, "pages_png"); OUT = os.path.join(WD, "mockups"); FONTS = os.path.join(ROOT, "fonts")
os.makedirs(PNGS, exist_ok=True); os.makedirs(OUT, exist_ok=True)

INK = (62, 44, 38); MOCHA = (107, 74, 58); TANG = (232, 112, 58); PINK = (229, 69, 122); MUTED = (140, 122, 110)
# page numbers in the PDF (see build_hot_girl_planner.main order)
PAGE = dict(cover=1, home=2, profile=3, howto=4, cy_over=5, cy_hotmap=6, cy_symptoms=7, m01=8, h01=9, m03=12, b_strength=32, b_triggers=34, c_meds=35, c_supps=36,
            c_summary=37, c_questions=38, c_labs=39, c_annual=40, mi_journal1=41, mi_rage=43, mi_wins=44, mi_energy=46, s1=54, s3=56, s6=59, s7=60, s8=61)


def F(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name + ".ttf"), size)


def page(key, scale=133):
    f = os.path.join(PNGS, f"{PAGE[key]:03d}.png")
    if not os.path.exists(f):
        subprocess.run(["pdftoppm", "-f", str(PAGE[key]), "-l", str(PAGE[key]), "-r", str(scale), "-png", "-singlefile", PDF, f[:-4]], check=True)
    return Image.open(f).convert("RGB")


def stk(name, h, rot=0):
    s = Image.open(os.path.join(CUT, name + ".png")).convert("RGBA"); s = s.resize((int(s.width * h / s.height), h), Image.LANCZOS)
    return s.rotate(rot, expand=True, resample=Image.BICUBIC) if rot else s


def backdrop(size, tint=0):
    w, h = size; bg = Image.new("RGB", (w, h), (248, 240, 226)); d = ImageDraw.Draw(bg)
    blobs = [((249, 216, 196), (0.2, 0.25)), ((247, 208, 222), (0.85, 0.7)), ((242, 226, 200), (0.5, 0.97))]
    for c, (fx, fy) in blobs:
        cx, cy = int(w * (fx + 0.05 * tint)), int(h * fy); d.ellipse((cx - w // 3, cy - h // 3, cx + w // 3, cy + h // 3), fill=c)
    return bg.filter(ImageFilter.GaussianBlur(int(w * 0.11))).convert("RGBA")


def heading(c, title, sub, badges, y, x=None, align="left", size=None):
    d = ImageDraw.Draw(c); W = c.width; x = int(W * 0.07) if x is None else x; size = size or int(W * 0.07)
    anchor = "la" if align == "left" else "ma"
    d.text((x, y), title, font=F("PlayfairDisplay-Regular", size), fill=INK, anchor=anchor)
    d.text((x + 2, y + int(size * 1.25)), sub.upper(), font=F("DMSans-SemiBold", int(W * 0.0145)), fill=TANG, anchor=anchor)
    fb = F("DMSans-SemiBold", int(W * 0.0145)); by = y + int(size * 1.25) + int(W * 0.04); pad = int(W * 0.018)
    widths = [d.textlength(b.upper(), font=fb) + 2 * pad for b in badges]; total = sum(widths) + 14 * (len(badges) - 1)
    bx = x - total // 2 if align != "left" else x
    for b, w_ in zip(badges, widths):
        d.rounded_rectangle((bx, by, bx + w_, by + int(W * 0.036)), int(W * 0.018), fill=(255, 255, 255, 235), outline=PINK, width=2)
        d.text((bx + w_ / 2, by + int(W * 0.018)), b.upper(), font=fb, fill=MOCHA, anchor="mm"); bx += w_ + 14


def callout(c, text, tx, ty, px, py, side="right", col=PINK):
    d = ImageDraw.Draw(c); f = F("DMSans-SemiBold", 30); w = d.textlength(text.upper(), font=f) + 56; h = 64
    x0 = tx if side == "right" else tx - w
    d.line((x0 if side == "right" else x0 + w, ty + h // 2, px, py), fill=col, width=4)
    d.ellipse((px - 11, py - 11, px + 11, py + 11), fill=col, outline=(255, 255, 255), width=4)
    d.rounded_rectangle((x0, ty, x0 + w, ty + h), h // 2, fill=(255, 255, 255, 245), outline=col, width=3)
    d.text((x0 + w / 2, ty + h / 2), text.upper(), font=f, fill=col, anchor="mm")


def pt(tab, bez, sw, x, y, ix, iy):
    s = sw / 834; return int(ix + bez + x * s), int(iy + bez + y * s)


def device(key, sw, img=None):
    tab = ipad(img if img is not None else page(key), sw); return tab, int(sw * 0.045)


def save(c, name):
    c.convert("RGB").save(os.path.join(OUT, name), optimize=True)


def tilted(key, w, rot):
    pg = page(key).resize((w, int(w * 4 / 3)), Image.LANCZOS).convert("RGBA"); fr = Image.new("RGBA", (pg.width + 24, pg.height + 24), (255, 255, 255, 255)); fr.alpha_composite(pg, (12, 12))
    return fr.rotate(rot, expand=True, resample=Image.BICUBIC)


def log_with_stickers():
    """Daily log with a Margo mood, a thermometer and a label pasted into the notes column."""
    img = page("m01").convert("RGBA"); s = img.width / 834
    x0 = (44 + 28 + 30 + 76 + 44 + 42 + 76 + 30 + 76 + 10) * s; rh = 28 * s; top = (134 + 30) * s
    for row, n, h in ((1, "f4", 22), (2, "l_nightsweat", 22), (4, "q_nottoday", 60), (8, "m_fan", 86), (12, "l_brainfog", 22), (15, "q_openwindow", 56), (19, "m_lifting", 86), (24, "f2", 22)):
        st = stk(n, int(h * s)); img.alpha_composite(st, (int(x0 + 6 * s), int(top + row * rh + rh / 2 - st.height / 2)))
    return img.convert("RGB")


def profile_with_rewards():
    """Profile page with three rewards already pasted on Margo."""
    img = page("profile").convert("RGBA"); s = img.width / 834
    for n, x, y, h in (("a_fan", 262, 520, 70), ("a_crown", 194, 336, 52), ("a_dumbbell", 100, 560, 56)):
        st = stk(n, int(h * s)); img.alpha_composite(st, (int(x * s - st.width / 2), int(y * s - st.height / 2)))
    return img.convert("RGB")


# ------------------------------------------------------------------ Etsy photos
def m01_hero():
    S = 2000; c = backdrop((S, S)); tab, _ = device("cover", 860); place(c, tab, S - tab.width - 150, 500)
    place(c, pencil(760, 30, -28), 110, S - 640)
    for n, h, x, y, r in (("m_icewater", 420, 90, 680, -5), ("q_nottoday", 230, 470, 900, 5), ("m_thermostat", 380, 60, 1120, 4), ("l_hotflash", 150, 500, 1330, -4), ("q_stillhot", 230, 150, 1600, -3)):
        place(c, stk(n, h, r), x, y)
    heading(c, "Hot Girl Era", "perimenopause symptom tracker for GoodNotes", ["62 pages", "hyperlinked", "102 stickers", "undated"], 150, size=160)
    save(c, "01_hero_square.png")


def m02_inside():
    S = 2000; c = backdrop((S, S), 2); heading(c, "What is inside", "62 hyperlinked pages, undated, start any day", ["cycle", "daily log", "habits", "doctor pages", "mind"], 120, size=100)
    keys = [("cover", "Cover"), ("profile", "Build your Hot Girl"), ("cy_over", "Cycle"), ("m01", "Daily log"), ("h01", "Habit grids"), ("c_summary", "For the doctor"), ("mi_rage", "Rage page"), ("s1", "Stickers")]
    sw = 360
    for i, (k, lab) in enumerate(keys):
        tab, _ = device(k, sw); x = 95 + (i % 4) * 470; y = 520 + (i // 4) * 740; place(c, tab, x, y)
        ImageDraw.Draw(c).text((x + tab.width // 2, y + tab.height + 40), lab.upper(), font=F("DMSans-SemiBold", 28), fill=MOCHA, anchor="mm")
    save(c, "02_whats_inside.png")


def m03_log():
    S = 2000; c = backdrop((S, S)); sw = 960; tab, bez = device("m01", sw); ix, iy = (S - tab.width) // 2, 540; place(c, tab, ix, iy)
    heading(c, "One row a night, thirty seconds", "the daily symptom log, 12 undated months", ["hot flashes 1–5", "sleep · mood · fog"], 120, size=96)
    P = lambda x, y: pt(tab, bez, sw, x, y, ix, iy)
    lx, rx = ix - 40, ix + tab.width + 40
    callout(c, "Period & flow", lx, 700, *P(87, 230), side="left"); callout(c, "Hot flash scale", lx, 980, *P(140, 420), side="left"); callout(c, "Night sweat", lx, 1260, *P(200, 640), side="left")
    callout(c, "Sleep hours", rx, 660, *P(265, 200)); callout(c, "Mood & energy 1–5", rx, 940, *P(400, 500)); callout(c, "Notes & stickers", rx, 1220, *P(700, 800))
    place(c, stk("m_sleepmask", 330, 3), 30, 1600); place(c, stk("f5", 170, -4), 1660, 1680)
    save(c, "03_daily_log.png")


def m04_cycle():
    S = 2000; c = backdrop((S, S), 1); heading(c, "The cycle that stopped behaving", "cycle overview, the Hot Map and a symptom checklist", ["14 cycles", "a year of hot flashes on one page"], 130, size=92)
    for i, k in enumerate(["cy_over", "cy_hotmap", "cy_symptoms"]):
        fr = tilted(k, 600, -8 + i * 8); place(c, fr, 130 + i * 590, 640 + abs(i - 1) * 80)
    place(c, stk("moon_full", 260, -4), 120, 1560); place(c, stk("drop2", 200, 3), 760, 1640); place(c, stk("l_period", 180, -3), 1300, 1620)
    save(c, "04_cycle_hotmap.png")


def m05_build():
    S = 2000; c = backdrop((S, S)); sw = 900; tab, bez = device("profile", sw, profile_with_rewards()); ix, iy = (S - tab.width) // 2, 560; place(c, tab, ix, iy)
    heading(c, "Build your Hot Girl", "8 habit streaks unlock 8 rewards you paste onto Margo", ["sleep · strength · protein · water", "a paper doll for grown women"], 120, size=100)
    P = lambda x, y: pt(tab, bez, sw, x, y, ix, iy)
    callout(c, "Margo lives here", ix - 40, 760, *P(190, 420), side="left"); callout(c, "8 rewards", ix + tab.width + 40, 760, *P(700, 420)); callout(c, "Tick when earned", ix + tab.width + 40, 1060, *P(760, 700))
    for i, n in enumerate(("a_sleepmask", "a_dumbbell", "a_shaker", "a_bottle")):
        place(c, stk(n, 150, (-1) ** i * 4), 60, 1000 + i * 190)
    for i, n in enumerate(("a_potion", "a_folder", "a_fan", "a_crown")):
        place(c, stk(n, 150, (-1) ** i * 4), 1760, 1180 + i * 170)
    save(c, "05_build_hot_girl.png")


def m06_habits():
    S = 2000; c = backdrop((S, S), 1); sw = 960; tab, bez = device("h01", sw); ix, iy = (S - tab.width) // 2, 540; place(c, tab, ix, iy)
    heading(c, "Colour a square, earn a reward", "12 monthly habit grids with what helped and what made it worse", ["8 habits", "streak boxes"], 120, size=92)
    P = lambda x, y: pt(tab, bez, sw, x, y, ix, iy)
    lx, rx = ix - 40, ix + tab.width + 40
    callout(c, "One square a day", lx, 700, *P(300, 240), side="left"); callout(c, "What helped", lx, 1060, *P(200, 620), side="left")
    callout(c, "Streak", rx, 660, *P(760, 200)); callout(c, "Rewards unlocked", rx, 1300, *P(600, 920))
    place(c, stk("m_protein", 330, -3), 30, 1580); place(c, stk("a_crown", 180, 4), 1680, 1700)
    save(c, "06_habits.png")


def m07_doctor():
    S = 2000; c = backdrop((S, S), 2); heading(c, "Show it to your doctor as it is", "symptom summary, labs, questions, meds and HRT", ["one-page summary", "FSH · estradiol · thyroid · vitamin D"], 130, size=92)
    for i, k in enumerate(["c_labs", "c_summary", "c_questions"]):
        fr = tilted(k, 600, -8 + i * 8); place(c, fr, 130 + i * 590, 640 + abs(i - 1) * 80)
    place(c, stk("m_doctor", 330, -3), 100, 1520); place(c, stk("l_labs", 170, 3), 800, 1640); place(c, stk("q_askdoctor", 230, -3), 1340, 1600)
    save(c, "07_doctor.png")


def m08_stickers():
    S = 2000; c = backdrop((S, S), 1); heading(c, "102 stickers with Margo", "transparent PNG for GoodNotes and Android", ["die-cut", "sticker book PDF", "moods · labels · scales · quotes"], 90, size=100)
    names = ["m_fan", "m_icewater", "m_window", "m_thermostat", "m_fog", "m_lifting", "m_rage", "m_shrug", "m_scroll3am", "m_dance", "m_bath", "m_crown",
             "l_hotflash", "l_nightsweat", "l_brainfog", "l_period", "l_hrt", "l_win", "f1", "f3", "f5", "moon_full", "drop3", "x_window",
             "a_sleepmask", "a_dumbbell", "a_shaker", "a_bottle", "a_potion", "a_folder", "a_fan", "a_crown", "base_margo", "x_ice", "x_thermostat", "d_cat",
             "q_nottoday", "q_estrogen", "q_maincharacter", "q_hotgirlera", "q_imfine", "q_fogmode", "q_stillhot", "q_rest"]
    cols, cw, chh = 6, 300, 250; x0 = (S - cols * cw) // 2
    for i, n in enumerate(names):
        s = stk(n, chh - 30); s.thumbnail((cw - 30, chh - 30)); x = x0 + (i % cols) * cw + (cw - s.width) // 2; y = 470 + (i // cols) * chh + (chh - s.height) // 2; place(c, s, x, y)
    save(c, "08_all_stickers.png")


def m09_in_use():
    S = 2000; c = backdrop((S, S)); sw = 900; tab, bez = device("m01", sw, log_with_stickers()); ix, iy = (S - tab.width) // 2, 560; place(c, tab, ix, iy)
    heading(c, "Peel, paste, done", "stickers sit right on your tracker pages", ["lasso & paste", "resize freely"], 120, size=100)
    P = lambda x, y: pt(tab, bez, sw, x, y, ix, iy)
    callout(c, "Margo moods", ix + tab.width + 40, 800, *P(520, 420)); callout(c, "Thermometers & labels", ix + tab.width + 40, 1100, *P(480, 220))
    place(c, stk("m_nightsweat", 260, -4), 60, 700); place(c, stk("l_sleep", 150, 3), 80, 1000); place(c, stk("f3", 130, -3), 60, 1200); place(c, stk("q_fogmode", 190, 4), 60, 1420)
    save(c, "09_stickers_in_use.png")


def m10_how():
    S = 2000; c = backdrop((S, S), 2); sw = 780; tab, _ = device("howto", sw); place(c, tab, 160, 620)
    heading(c, "Ready in 3 steps", "instant digital download", ["GoodNotes 5 & 6", "iPad & Android"], 130, size=120)
    steps = [("1", "Download the PDF", "and import it into GoodNotes"), ("2", "Add the stickers", "PNGs go to Elements, or use the sticker book"), ("3", "One row a night", "every tab and arrow is linked")]
    d = ImageDraw.Draw(c)
    for i, (n, t, s_) in enumerate(steps):
        y = 640 + i * 330; d.rounded_rectangle((1060, y, 1860, y + 270), 40, fill=(255, 255, 255, 240), outline=TANG, width=3)
        d.ellipse((1100, y + 80, 1190, y + 170), fill=TANG); d.text((1145, y + 125), n, font=F("PlayfairDisplay-Bold", 60), fill=(255, 255, 255), anchor="mm")
        d.text((1230, y + 105), t, font=F("PlayfairDisplay-Regular", 52), fill=INK, anchor="lm"); d.text((1230, y + 180), s_, font=F("DMSans-Regular", 30), fill=MUTED, anchor="lm")
    place(c, stk("m_coffee_ok", 300, 3), 1500, 1640)
    save(c, "10_how_it_works.png")


# ------------------------------------------------------------------ Pinterest pins 1000x1500
def p01_hero():
    Wp, Hp = 1000, 1500; c = backdrop((Wp, Hp)); tab, _ = device("cover", 600); place(c, tab, (Wp - tab.width) // 2, 400)
    heading(c, "Hot Girl Era", "perimenopause symptom tracker for GoodNotes", ["62 pages", "hyperlinked", "102 stickers"], 90, x=Wp // 2, align="center", size=120)
    place(c, stk("m_icewater", 330, -6), 10, 1080); place(c, stk("q_nottoday", 200, 6), 740, 1200)
    save(c, "p01_hero_pin.png")


def p02_hotmap():
    Wp, Hp = 1000, 1500; c = backdrop((Wp, Hp), 1); heading(c, "A year of hot flashes on one page", "the Hot Map: one square per day", ["hot flash tracker"], 70, x=Wp // 2, align="center", size=58)
    tab, _ = device("cy_hotmap", 640); place(c, tab, (Wp - tab.width) // 2, 330); place(c, stk("m_fan", 300, -5), 10, 1150); place(c, stk("f5", 150, 5), 800, 1300)
    save(c, "p02_hotmap_pin.png")


def p03_doctor():
    Wp, Hp = 1000, 1500; c = backdrop((Wp, Hp)); heading(c, "What to bring to your doctor", "symptom summary, labs and questions", ["menopause journal"], 70, x=Wp // 2, align="center", size=62)
    for k, w, x, y, r in (("c_labs", 380, 40, 520, 7), ("c_questions", 380, 590, 520, -7), ("c_summary", 470, 265, 460, 0)):
        fr = tilted(k, w, r); place(c, fr, x, y)
    place(c, stk("m_doctor", 300, -3), 10, 1150); place(c, stk("l_labs", 150, 3), 780, 1300)
    save(c, "p03_doctor_pin.png")


def p04_stickers():
    Wp, Hp = 1000, 1500; c = backdrop((Wp, Hp), 2); heading(c, "102 perimenopause stickers", "digital stickers for GoodNotes", ["transparent PNG"], 70, x=Wp // 2, align="center", size=66)
    names = ["m_fan", "l_hotflash", "m_window", "q_estrogen", "f5", "m_rage", "q_fogmode", "a_crown", "m_scroll3am", "l_nightsweat"]
    for i, n in enumerate(names):
        s = stk(n, 200); s.thumbnail((440, 200)); x = 40 + (i % 2) * 490 + (440 - s.width) // 2; y = 330 + (i // 2) * 215; place(c, s, x, y)
    save(c, "p04_stickers_pin.png")


if __name__ == "__main__":
    for fn in (m01_hero, m02_inside, m03_log, m04_cycle, m05_build, m06_habits, m07_doctor, m08_stickers, m09_in_use, m10_how, p01_hero, p02_hotmap, p03_doctor, p04_stickers):
        fn()
    files = sorted(glob.glob(os.path.join(OUT, "*.png"))); h = 480
    ims = [Image.open(f).convert("RGB") for f in files]; ims = [i.resize((int(i.width * h / i.height), h), Image.LANCZOS) for i in ims]
    cols = 7; rows = (len(ims) + cols - 1) // cols; mw = max(i.width for i in ims)
    sheet = Image.new("RGB", (cols * (mw + 10) + 10, rows * (h + 10) + 10), (200, 196, 190))
    for k, i in enumerate(ims):
        sheet.paste(i, (10 + (k % cols) * (mw + 10), 10 + (k // cols) * (h + 10)))
    sheet.save(os.path.join(OUT, "preview_mockups.jpg"), quality=85); print("mockups:", len(files))
