#!/usr/bin/env python3
"""Pinterest pins (1000x1500 JPG < 1 MB) and pins_code_and_cozy.csv for the Code & Cozy listing.

Needs: build_it_mockups.py and build_it_stickerpack.py already run.
Output: images/it_girl/pins/*.jpg, pins_code_and_cozy.csv (set LISTING_URL below or via env first)
Run:  .venv-planner/bin/python build_it_pins.py
"""
import csv
import os

from PIL import Image, ImageDraw

import build_it_mockups as bm
from build_mockups import place

ROOT = os.path.dirname(os.path.abspath(__file__)); IT = os.path.join(ROOT, "images", "it_girl")
OUT = os.path.join(IT, "pins"); os.makedirs(OUT, exist_ok=True)
LISTING_URL = os.environ.get("LISTING_URL", "https://www.etsy.com/listing/PASTE_LISTING_ID/PASTE-SLUG")
BOARD = "Digital Planners"; BOARD_ST = "Digital Stickers"
W, H = 1000, 1500


def save(im, name):
    p = os.path.join(OUT, name); q = 90
    while True:
        im.convert("RGB").save(p, "JPEG", quality=q, optimize=True, progressive=True)
        if os.path.getsize(p) <= 1_000_000 or q <= 70:
            break
        q -= 5


def head(c, t1, t2):
    d = ImageDraw.Draw(c); d.text((W // 2, 100), t1, font=bm.F("PlayfairDisplay-Regular", 66), fill=bm.INK, anchor="mm")
    d.text((W // 2, 170), t2.upper(), font=bm.F("DMSans-SemiBold", 24), fill=bm.SAGE_D, anchor="mm")


def foot(c, text):
    d = ImageDraw.Draw(c); f = bm.F("DMSans-SemiBold", 28); w = d.textlength(text.upper(), font=f) + 70; x = (W - w) / 2
    d.rounded_rectangle((x, H - 110, x + w, H - 50), 30, fill=(255, 255, 255), outline=bm.SAGE, width=3); d.text((W // 2, H - 80), text.upper(), font=f, fill=bm.SAGE_D, anchor="mm")


def framed(mock, t1, t2, ft, tint=0):
    """The mockup carries its own headline, so the pin only adds a sticker strip and the footer pill."""
    c = bm.backdrop((W, H), tint)
    m = Image.open(os.path.join(bm.OUT, mock)).convert("RGBA").resize((1000, 1000), Image.LANCZOS)
    fade = Image.new("L", (1000, 1000), 255); fd = ImageDraw.Draw(fade)
    for i in range(90):
        fd.line((0, i, 1000, i), fill=int(255 * i / 90)); fd.line((0, 999 - i, 1000, 999 - i), fill=int(255 * i / 90))
    m.putalpha(fade); c.alpha_composite(m, (0, 120))
    for n, h, x, y, r in (("work_3", 230, 40, 1150, -4), ("dev_3", 220, 380, 1170, 3), ("fit_2", 250, 700, 1140, -3)):
        place(c, bm.stk(n, h, r), x, y)
    foot(c, ft); return c


def sheet_pin(code, t1, t2, ft, tint=0):
    c = bm.backdrop((W, H), tint); head(c, t1, t2)
    sh = Image.open(os.path.join(IT, "sticker_pack", "sheets", f"{code}_sheet.png")).convert("RGB").resize((733, 1100), Image.LANCZOS)
    fr = Image.new("RGBA", (749, 1116), (255, 255, 255, 255)); fr.alpha_composite(sh.convert("RGBA"), (8, 8)); place(c, fr, (W - 749) // 2, 250); foot(c, ft); return c


def copy_of(name):
    return Image.open(os.path.join(bm.OUT, name)).convert("RGB")


PINS = [
    ("pin_01_hero", lambda: copy_of("p01_hero_pin.png"), BOARD, "2027 Daily Planner for GoodNotes, Hyperlinked iPad Planner for Women in Tech",
     "A cozy 2027 daily planner for GoodNotes: 365 daily pages, weekly and monthly spreads, a work hub with sprint board, 1:1 notes and brag document, plus habit, meal and budget trackers and 80 stickers. Hyperlinked iPad planner, instant download.",
     "iPad showing the Code & Cozy 2027 planner cover with cozy girl stickers"),
    ("pin_02_daily", lambda: copy_of("p02_daily_pin.png"), BOARD, "Daily Planner Page for Women in Tech: Top 3, Schedule, Focus Blocks, Mood and Water",
     "One daily page for work and life: top 3, to-do, hourly schedule, standup notes, focus blocks, mood, energy, sleep, water and meals. GoodNotes 2027 planner for iPad with 365 hyperlinked days.",
     "Daily planner page on iPad with schedule, to-do list and life tracker"),
    ("pin_03_work", lambda: copy_of("p03_work_pin.png"), BOARD, "Sprint Planner, 1:1 Notes and Brag Document for GoodNotes: Work Hub for Developers",
     "Project tracker, sprint board with retro, 1:1 and meeting notes, brag document, learning tracker, bug log and career roadmap. A 2027 digital planner made for developers, PMs and designers in tech.",
     "iPad with sprint planner, brag document and meeting notes templates"),
    ("pin_04_stickers", lambda: copy_of("p04_stickers_pin.png"), BOARD_ST, "80 Cozy IT Girl Digital Stickers for GoodNotes, Transparent PNG",
     "Eighty die-cut watercolor stickers: coding, working from home, workouts, travel, hobbies, friends, seasons and date nights. Transparent PNG plus a sticker book PDF for GoodNotes and other iPad planner apps.",
     "Collage of cozy curly-haired girl digital stickers with a dog"),
    ("pin_05_inside", lambda: framed("04_whats_inside.png", "What is inside", "508 hyperlinked pages", "365 daily · 53 weekly · 12 monthly"), BOARD, "What Is Inside the 2027 GoodNotes Planner: 365 Daily Pages, Weekly, Monthly and Work Hub",
     "A look inside Code & Cozy: cover, year at a glance, quarter OKRs, 12 months, 53 weeks, 365 days, work hub, health and life pages. Every tab, date and week is a tap-to-jump link.",
     "Eight pages of the Code & Cozy planner on iPads"),
    ("pin_06_linked", lambda: framed("03_everything_linked.png", "Everything is a link", "tabs, dates, weeks, months", "hyperlinked GoodNotes planner", 1), BOARD, "Hyperlinked 2027 Planner for iPad: Tap Any Date, Week or Tab to Jump",
     "Colour tabs, month letters, week numbers and every calendar date are clickable. A fast hyperlinked digital planner for GoodNotes and Notability.",
     "Monthly calendar page with callouts showing clickable dates and tabs"),
    ("pin_07_health_life", lambda: framed("06_health_life.png", "Health, home, fun", "habits, meals, budget, trips", "12 habit trackers + life pages", 2), BOARD, "Habit Tracker, Meal Planner and Budget Pages for GoodNotes 2027 Planner",
     "Twelve monthly habit trackers, workout log, meal planner with shopping list, budget, savings jars, travel planner, reading list and self-care menu in one digital planner.",
     "Fan of habit tracker, meal planner, budget and travel planner pages"),
    ("pin_08_dev", lambda: sheet_pin("dev", "Dev life stickers", "debug, ship, present, repeat", "digital stickers for GoodNotes", 1), BOARD_ST, "Developer Girl Digital Stickers for GoodNotes: Coding, Debugging and Shipping",
     "Eight cozy dev-life stickers: dual monitors, whiteboard planning, debugging stress, shipping celebration and late-night overtime. Transparent PNG for GoodNotes.",
     "Eight stickers of a curly-haired girl coding, debugging and celebrating"),
    ("pin_09_work", lambda: sheet_pin("work", "Work from home", "cozy desk stickers", "digital stickers for GoodNotes"), BOARD_ST, "Work From Home Digital Stickers for iPad Planner, Cozy Desk Girl PNG",
     "Cozy work-from-home stickers with a laptop, headset, coffee and a Yorkie. Transparent die-cut PNG for GoodNotes, Notability and iPad planners.",
     "Eight work-from-home stickers of a girl with a laptop and a small dog"),
    ("pin_10_seasons", lambda: sheet_pin("seasons", "Seasonal stickers", "beach, blossoms, pumpkins, snow", "digital stickers for GoodNotes", 2), BOARD_ST, "Seasonal Digital Stickers for GoodNotes: Spring, Summer, Autumn and Winter",
     "Eight seasonal watercolor stickers: planting, cherry blossoms, beach, pool, autumn leaves, pumpkin carving, ice skating and the Christmas tree.",
     "Eight seasonal stickers from spring planting to Christmas tree"),
    ("pin_11_travel", lambda: sheet_pin("travel", "Travel stickers", "trains, trails and bookshops", "digital stickers for GoodNotes"), BOARD_ST, "Travel Digital Stickers for GoodNotes Planner: Suitcase, Hiking, Train and Picnic",
     "Eight travel stickers for your planner: suitcase, train window, rainy walk, mountain hike, picnic, bike ride, photo stop and bookshop. Transparent PNG.",
     "Eight travel stickers of a girl with a Yorkie on trips"),
    ("pin_12_cozy", lambda: sheet_pin("cozy", "Cozy evening stickers", "books, games, blankets, sleep", "digital stickers for GoodNotes", 1), BOARD_ST, "Cozy Evening Digital Stickers: Reading, Gaming and Journaling for GoodNotes",
     "Eight cozy evening stickers for reading, gaming, journaling and sleep. Warm olive and cream colours with a tiny dog. Instant download for iPad planners.",
     "Eight cozy stickers of a girl reading, gaming and sleeping"),
]

if __name__ == "__main__":
    rows = []
    for name, fn, board, title, desc, alt in PINS:
        save(fn(), name + ".jpg"); rows.append([f"images/it_girl/pins/{name}.jpg", title, desc, LISTING_URL, board, alt])
    with open(os.path.join(ROOT, "pins_code_and_cozy.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["image", "title", "description", "link", "board", "alt_text"]); w.writerows(rows)
    print(len(rows), "pins ->", OUT)
