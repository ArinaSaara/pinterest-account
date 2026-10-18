#!/usr/bin/env python3
"""Build the "Year of Dragons" GoodNotes planner from four elemental sticker sets.

Inputs (not in git):
  images/<element>/0*.png              8 stickers on cream paper, 1000x1500
  images/<element>/transparent/0*.png  same 8 with alpha channel
  for element in fire, ice, water, lightning

Outputs:
  images/year_of_dragons/pages/*.png                     every page, 1536x2048
  images/year_of_dragons/Year_of_Dragons_Planner.pdf     full planner, linked contents + bookmarks
  images/year_of_dragons/<Element>_Season_Planner.pdf    one PDF per element (cheaper SKU)
  images/year_of_dragons/<element>_sheet.png             2x4 sticker sheet per element (Pinterest)
  images/year_of_dragons/preview_*.jpg                   contact sheets for a quick look

Run:  python3 build_year_of_dragons.py
"""
import calendar
import glob
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "images")
OUT = os.path.join(IMG, "year_of_dragons")
PAGES = os.path.join(OUT, "pages")
os.makedirs(PAGES, exist_ok=True)

SUP = "/System/Library/Fonts/Supplemental/"
AV = "/System/Library/Fonts/Avenir Next.ttc"


def font(name, size, index=0):
    return ImageFont.truetype(name, size, index=index)


W, H, M = 1536, 2048, 110
F_TITLE = font(AV, 116, 2); F_TITLE2 = font(AV, 52); F_HEAD = font(AV, 64, 2); F_SUB = font(AV, 30); F_SEC = font(AV, 30, 2)
F_LABEL = font(AV, 24); F_SMALL = font(AV, 20); F_TINY = font(AV, 17); F_TOC = font(AV, 40); F_TOCB = font(AV, 40, 2); F_BIG = font(AV, 44, 2)
F_HAND = font(SUP + "Bradley Hand Bold.ttf", 34); F_HAND_S = font(SUP + "Bradley Hand Bold.ttf", 28); F_HAND_L = font(SUP + "Bradley Hand Bold.ttf", 40); F_HAND_XS = font(SUP + "Bradley Hand Bold.ttf", 24)

DARK = (60, 56, 54); GREY = (150, 145, 140); LINE = (222, 216, 208); DOT = (218, 212, 204); CREAM = (252, 249, 243); PAPER = (250, 246, 238)
YEAR = 2027  # calendar used for day counts; change to the year you sell for
KEYS = ["01", "02", "03", "04", "05", "06", "07", "08"]
STAGE_NAMES = ["Egg", "Hatchling", "Baby", "Child", "Juvenile", "Adolescent", "Young adult", "Adult"]

ELEMENTS = [
    dict(key="fire", name="Fire", season="Autumn", months=[9, 10, 11], accent=(226, 112, 52), soft=(252, 226, 206), glow=(253, 214, 170),
         sphere="energy, movement and daily habits", short="energy & habits", motto="feed the flame every day", trackers=["habit", "focus"],
         dragon="Ember", lore=["Wakes before you do.", "Grows on daily wins.", "Sulks on skipped days."]),
    dict(key="ice", name="Ice", season="Winter", months=[12, 1, 2], accent=(86, 140, 196), soft=(222, 236, 248), glow=(214, 232, 250),
         sphere="rest, calm and slow evenings", short="rest & calm", motto="let the frost settle", trackers=["reading", "sleep"],
         dragon="Lumi", lore=["Collects quiet evenings.", "Grows on early nights.", "Melts near screens."]),
    dict(key="water", name="Water", season="Spring", months=[3, 4, 5], accent=(36, 148, 166), soft=(210, 240, 242), glow=(208, 240, 236),
         sphere="health, hydration and self-care", short="health & self-care", motto="go with the flow", trackers=["water", "mood"],
         dragon="Marin", lore=["Lives in your bottle.", "Grows on water and walks.", "Loves honest mood notes."]),
    dict(key="lightning", name="Lightning", season="Summer", months=[6, 7, 8], accent=(122, 92, 190), soft=(232, 224, 248), glow=(236, 226, 250),
         sphere="study, projects and money", short="study & money", motto="strike while it sparks", trackers=["study", "savings"],
         dragon="Volt", lore=["Keeps a very tidy hoard.", "Grows on focus sessions.", "Counts every saved coin."]),
]
GOLD = (214, 170, 60)


def load_set(key):
    cream = {os.path.basename(f)[:2]: Image.open(f).convert("RGB") for f in sorted(glob.glob(os.path.join(IMG, key, "0*.png")))}
    trans = {}
    for f in sorted(glob.glob(os.path.join(IMG, key, "transparent", "0*.png"))):
        im = Image.open(f).convert("RGBA"); b = im.getchannel("A").getbbox(); p = 16
        trans[os.path.basename(f)[:2]] = im.crop((max(0, b[0] - p), max(0, b[1] - p), min(im.width, b[2] + p), min(im.height, b[3] + p)))
    if len(cream) != 8 or len(trans) != 8:
        raise SystemExit(f"{key}: expected 8 cream + 8 transparent stickers, got {len(cream)} + {len(trans)}")
    return cream, trans


SETS = {e["key"]: load_set(e["key"]) for e in ELEMENTS}


def sticker(key, stage):
    return SETS[key][1][stage]


def put(img, key, stage, h, x, y, rot=0, opacity=1.0, center=False):
    s = sticker(key, stage); s = s.resize((int(s.width * h / s.height), h), Image.LANCZOS)
    if rot:
        s = s.rotate(rot, expand=True, resample=Image.BICUBIC)
    if opacity < 1:
        s.putalpha(s.getchannel("A").point(lambda v: int(v * opacity)))
    if center:
        x, y = x - s.width // 2, y - s.height // 2
    img.alpha_composite(s, (int(x), int(y)))


class Page:
    def __init__(self, title, subtitle, accent, dots=True):
        self.accent = accent
        self.img = Image.new("RGBA", (W, H), CREAM + (255,)); self.d = ImageDraw.Draw(self.img)
        if dots:
            for y in range(80, H - 60, 48):
                for x in range(80, W - 60, 48):
                    self.d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=DOT)
        self.d.text((M, 90), title, font=F_HEAD, fill=DARK)
        self.d.text((M + 2, 170), subtitle, font=F_SUB, fill=GREY)
        self.d.line((M, 225, M + 620, 225), fill=accent, width=5)

    def put(self, *a, **k):
        put(self.img, *a, **k); self.d = ImageDraw.Draw(self.img)

    def stages(self, key, y, labels, caption):
        d = self.d; a = self.accent
        d.text((M, y), "DRAGON GROWTH", font=F_SEC, fill=DARK); d.text((M + 300, y + 2), caption, font=F_HAND_S, fill=a)
        slot = (W - 2 * M) / 8; ry = y + 60
        for i, k in enumerate(KEYS):
            cx = M + slot * i + slot / 2
            self.d.rounded_rectangle((cx - slot / 2 + 8, ry, cx + slot / 2 - 8, ry + 200), 16, fill=(255, 255, 255), outline=LINE, width=3)
            self.put(key, k, 170, cx, ry + 100, opacity=0.22, center=True)
            self.d.text((cx, ry + 228), labels[i], font=F_LABEL, fill=DARK, anchor="mm")
        d = self.d; d.line((M + slot / 2, ry + 263, W - M - slot / 2, ry + 263), fill=LINE, width=4)
        for i in range(8):
            cx = M + slot * i + slot / 2; d.ellipse((cx - 13, ry + 250, cx + 13, ry + 276), fill=(255, 255, 255), outline=a, width=3)
        d.text((M, ry + 300), "Paste the next dragon sticker over the faded one each time you hit a milestone.", font=F_SMALL, fill=GREY)
        return ry + 340

    def note(self, y, lines):
        n = Image.new("RGBA", (760, 40 + 44 * len(lines)), (0, 0, 0, 0))
        ImageDraw.Draw(n).rounded_rectangle((0, 0, 759, n.height - 1), 14, fill=(255, 241, 196, 255))
        self.img.alpha_composite(n.rotate(-1.2, expand=True, resample=Image.BICUBIC), (M, y)); self.d = ImageDraw.Draw(self.img)
        for i, l in enumerate(lines):
            self.d.text((M + 30, y + 22 + 44 * i), l, font=F_HAND_S, fill=DARK)

    def save(self, name):
        path = os.path.join(PAGES, name + ".png"); self.img.convert("RGB").save(path, optimize=True); return path


# ------------------------------------------------------------------ shared pages
def cover_page():
    bg = (243, 236, 228)
    glow = Image.new("RGB", (W, H), bg); gd = ImageDraw.Draw(glow)
    gd.ellipse((60, 520, 760, 1320), fill=ELEMENTS[0]["glow"]); gd.ellipse((776, 520, 1476, 1320), fill=ELEMENTS[1]["glow"])
    gd.ellipse((60, 1180, 760, 1980), fill=ELEMENTS[2]["glow"]); gd.ellipse((776, 1180, 1476, 1980), fill=ELEMENTS[3]["glow"])
    img = glow.filter(ImageFilter.GaussianBlur(170)).convert("RGBA"); d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, 70, W - 70, H - 70), 40, outline=DARK, width=3); d.rounded_rectangle((90, 90, W - 90, H - 90), 32, outline=(200, 190, 180), width=2)
    d.text((W // 2, 220), "DRAGON HATCHERY", font=F_TITLE2, fill=GREY, anchor="mm")
    d.text((W // 2, 330), "YEAR OF", font=F_TITLE, fill=DARK, anchor="mm"); d.text((W // 2, 440), "DRAGONS", font=F_TITLE, fill=DARK, anchor="mm")
    d.line((W // 2 - 260, 510, W // 2 + 260, 510), fill=DARK, width=4)
    d.text((W // 2, 575), "four seasons, four elements, one dragon hatched each quarter", font=F_HAND, fill=(110, 100, 95), anchor="mm")
    pos = [(400, 880), (1136, 880), (400, 1500), (1136, 1500)]
    for e, (cx, cy) in zip(ELEMENTS, pos):
        put(img, e["key"], "08", 470, cx, cy, center=True)
        d = ImageDraw.Draw(img); d.text((cx, cy + 285), f"{e['season'].upper()}  ·  {e['name'].upper()}", font=F_SEC, fill=e["accent"], anchor="mm")
    d.text((W // 2, 1930), "12 monthly trackers  ·  8 element trackers  ·  32 growth stages  ·  for GoodNotes", font=F_SUB, fill=(120, 110, 100), anchor="mm")
    path = os.path.join(PAGES, "00_cover.png"); img.convert("RGB").save(path, optimize=True); return path


def contents_page(targets):
    """targets: dict name -> page index (0-based). Returns (path, links)."""
    p = Page("CONTENTS", "Tap a card to jump to a season", DARK); d = p.d; links = []
    y = 300; cw = (W - 2 * M - 40) / 2
    for i, e in enumerate(ELEMENTS):
        r, c = divmod(i, 2); x0 = M + c * (cw + 40); y0 = y + r * 330
        d.rounded_rectangle((x0, y0, x0 + cw, y0 + 300), 22, fill=e["soft"], outline=e["accent"], width=3)
        d.text((x0 + 30, y0 + 28), e["season"].upper(), font=F_SEC, fill=e["accent"])
        d.text((x0 + 30, y0 + 68), e["name"] + " dragon", font=F_BIG, fill=DARK)
        d.text((x0 + 30, y0 + 130), e["short"], font=F_SUB, fill=GREY)
        d.text((x0 + 30, y0 + 175), "  ·  ".join(calendar.month_abbr[m] for m in e["months"]), font=F_SEC, fill=DARK)
        d.text((x0 + 30, y0 + 240), f"p.{targets[e['key']] + 1}", font=F_LABEL, fill=e["accent"])
        p.put(e["key"], "04", 220, x0 + cw - 230, y0 + 60, rot=(6 if i % 2 else -6)); d = p.d
        links.append({"rect": [x0, y0, x0 + cw, y0 + 300], "page": targets[e["key"]]})
    # 12 month chips, each linked to its month page
    ym = y + 2 * 330 + 10; d.text((M, ym), "YEAR AT A GLANCE", font=F_SEC, fill=DARK); ym += 50
    chip_w = (W - 2 * M - 3 * 20) / 4
    order_months = [(e, m) for e in ELEMENTS for m in e["months"]]
    for i, (e, m) in enumerate(order_months):
        r, c = divmod(i, 4); x0 = M + c * (chip_w + 20); y0 = ym + r * 80
        d.rounded_rectangle((x0, y0, x0 + chip_w, y0 + 64), 14, fill=e["soft"], outline=e["accent"], width=2)
        d.text((x0 + 20, y0 + 18), calendar.month_name[m], font=F_SEC, fill=DARK)
        page = targets[e["key"]] + 2 + e["months"].index(m)
        d.text((x0 + chip_w - 20, y0 + 32), f"p.{page + 1}", font=F_LABEL, fill=e["accent"], anchor="rm")
        links.append({"rect": [x0, y0, x0 + chip_w, y0 + 64], "page": page})
    y2 = ym + 3 * 80 + 30
    bw = (W - 2 * M - 2 * 20) / 3
    for i, (label, key) in enumerate([("Hall of Dragons", "hall"), ("How it works", "how"), ("Notes", "notes")]):
        x0 = M + i * (bw + 20)
        d.rounded_rectangle((x0, y2, x0 + bw, y2 + 84), 18, fill=(255, 255, 255), outline=LINE, width=3)
        d.text((x0 + 26, y2 + 22), label, font=F_SEC, fill=DARK); d.text((x0 + bw - 26, y2 + 42), f"p.{targets[key] + 1}", font=F_LABEL, fill=GREY, anchor="rm")
        links.append({"rect": [x0, y2, x0 + bw, y2 + 84], "page": targets[key]})
    # meet your dragons: four lore cards
    y3 = y2 + 130; d.text((M, y3), "MEET YOUR DRAGONS", font=F_SEC, fill=DARK)
    d.text((M + 360, y3 + 2), "every inner page: tap the title to come back here", font=F_HAND_S, fill=GREY)
    y3 += 50; cw4 = (W - 2 * M - 3 * 20) / 4; ch4 = H - 100 - y3
    for i, e in enumerate(ELEMENTS):
        x0 = M + i * (cw4 + 20)
        d.rounded_rectangle((x0, y3, x0 + cw4, y3 + ch4), 22, fill=(255, 255, 255), outline=e["accent"], width=3)
        d.rounded_rectangle((x0 + 14, y3 + 14, x0 + cw4 - 14, y3 + 210), 16, fill=e["soft"])
        p.put(e["key"], "03", 180, x0 + cw4 / 2, y3 + 112, center=True); d = p.d
        d.text((x0 + cw4 / 2, y3 + 248), e["dragon"].upper(), font=F_BIG, fill=e["accent"], anchor="mm")
        d.text((x0 + cw4 / 2, y3 + 290), f"the {e['name'].lower()} dragon", font=F_LABEL, fill=GREY, anchor="mm")
        for j, line in enumerate(e["lore"]):
            d.text((x0 + cw4 / 2, y3 + 335 + j * 34), line, font=F_HAND_XS, fill=DARK, anchor="mm")
        d.text((x0 + cw4 / 2, y3 + ch4 - 30), f"hatches in {e['season'].lower()}", font=F_LABEL, fill=e["accent"], anchor="mm")
    return p.save("01_contents"), links


def how_page():
    p = Page("HOW IT WORKS", "One mechanic for the whole year", DARK)
    y = p.stages("fire", 260, ["day 3", "day 7", "day 10", "day 14", "day 18", "day 22", "day 26", "month"], "example: the autumn fire dragon")
    d = p.d; steps = [
        ("1", "Each season has its own dragon and its own life area.", "Autumn is fire and habits, winter is ice and rest, spring is water and self-care, summer is lightning and projects."),
        ("2", "Every month page has a growth bar with 8 faded stages.", "Milestones are streak days: 3, 7, 10, 14, 18, 22, 26 and the full month."),
        ("3", "Hit a milestone, open the season's sticker sheet, lasso the next dragon.", "Copy it and paste it over the faded stage. The dragon grows on your page."),
        ("4", "Finish the season and the adult moves into the Hall of Dragons.", "Four seasons, four adults. The hall is the year's trophy shelf."),
    ]
    for i, (n, a, b) in enumerate(steps):
        yy = y + 30 + i * 190
        d.ellipse((M, yy, M + 64, yy + 64), fill=DARK); d.text((M + 32, yy + 32), n, font=F_TOCB, fill=(255, 255, 255), anchor="mm")
        d.text((M + 90, yy + 4), a, font=F_SEC, fill=DARK); d.text((M + 90, yy + 50), b, font=F_HAND_S, fill=GREY)
        if i == 2:
            d.text((M + 90, yy + 92), "Tip: add the transparent PNGs to GoodNotes Elements and drag them in with one tap.", font=F_SMALL, fill=GREY)
    for e, (cx, cy) in zip(ELEMENTS, [(M + 150, H - 330), (M + 480, H - 330), (M + 810, H - 330), (M + 1140, H - 330)]):
        p.put(e["key"], "03", 250, cx, cy, center=True)
    return p.save("02_how_it_works")


def hall_page():
    p = Page("HALL OF DRAGONS", "One adult per season. Paste it here when the season is done.", DARK); d = p.d
    cw = (W - 2 * M - 40) / 2
    for i, e in enumerate(ELEMENTS):
        r, c = divmod(i, 2); x0 = M + c * (cw + 40); y0 = 290 + r * 820
        d.rounded_rectangle((x0, y0, x0 + cw, y0 + 780), 26, fill=(255, 255, 255), outline=e["accent"], width=4)
        d.rounded_rectangle((x0 + 20, y0 + 20, x0 + cw - 20, y0 + 600), 20, fill=e["soft"])
        p.put(e["key"], "08", 540, x0 + cw / 2, y0 + 310, opacity=0.18, center=True); d = p.d
        d.text((x0 + cw / 2, y0 + 650), f"{e['season'].upper()}  ·  {e['name'].upper()}", font=F_SEC, fill=e["accent"], anchor="mm")
        d.text((x0 + cw / 2, y0 + 700), "unlocked on  ____ / ____", font=F_HAND_S, fill=GREY, anchor="mm")
        d.text((x0 + cw / 2, y0 + 745), "best streak  ______ days", font=F_HAND_S, fill=GREY, anchor="mm")
    return p.save("03_hall_of_dragons")


def notes_page(name="99_notes"):
    p = Page("NOTES", "", DARK)
    for e, x in zip(ELEMENTS, [W - M - 560, W - M - 420, W - M - 280, W - M - 140]):
        p.put(e["key"], "01", 130, x, 60, rot=(5 if x % 2 else -5))
    return p.save(name)


# ------------------------------------------------------------------ element pages
def season_cover(e):
    bg = Image.new("RGB", (W, H), (246, 242, 236)); gd = ImageDraw.Draw(bg); gd.ellipse((200, 560, 1336, 1760), fill=e["glow"])
    img = bg.filter(ImageFilter.GaussianBlur(160)).convert("RGBA"); d = ImageDraw.Draw(img); a = e["accent"]
    d.rounded_rectangle((70, 70, W - 70, H - 70), 40, outline=a, width=4)
    d.text((W // 2, 230), e["season"].upper(), font=F_TITLE2, fill=a, anchor="mm")
    d.text((W // 2, 340), e["name"].upper(), font=F_TITLE, fill=DARK, anchor="mm"); d.text((W // 2, 450), "DRAGON", font=F_TITLE, fill=DARK, anchor="mm")
    d.line((W // 2 - 260, 520, W // 2 + 260, 520), fill=a, width=5)
    d.text((W // 2, 585), e["sphere"], font=F_HAND_L, fill=(110, 100, 95), anchor="mm")
    put(img, e["key"], "08", 1000, W // 2, 1180, center=True); put(img, e["key"], "01", 240, 200, 1540, rot=-8); put(img, e["key"], "02", 240, 1130, 1540, rot=8)
    d = ImageDraw.Draw(img)
    d.text((W // 2, 1870), "  ·  ".join(calendar.month_name[m] for m in e["months"]), font=F_SEC, fill=DARK, anchor="mm")
    d.text((W // 2, 1920), e["motto"], font=F_HAND_S, fill=a, anchor="mm")
    path = os.path.join(PAGES, f"{e['key']}_00_cover.png"); img.convert("RGB").save(path, optimize=True); return path


def sheet_page(e):
    p = Page("STICKER SHEET", f"{e['name']} dragon, 8 stages. Lasso one, copy, paste it anywhere.", e["accent"], dots=False)
    cols = 4; cw = (W - 2 * M) / cols; top = 300; rh = 820
    for i, k in enumerate(KEYS):
        r, c = divmod(i, cols); cx = M + cw * c + cw / 2; cy = top + rh * r
        s = sticker(e["key"], k); h = 540; w = int(s.width * h / s.height)
        if w > cw - 30:
            w = int(cw - 30); h = int(s.height * w / s.width)
        p.img.alpha_composite(s.resize((w, h), Image.LANCZOS), (int(cx - w / 2), int(cy + 330 - h / 2)))
        p.d = ImageDraw.Draw(p.img); p.d.text((cx, cy + 660), f"{i + 1} {STAGE_NAMES[i]}", font=F_LABEL, fill=GREY, anchor="mm")
    return p.save(f"{e['key']}_01_sheet")


def month_page(e, month):
    days = calendar.monthrange(YEAR, month)[1]; a = e["accent"]
    p = Page(calendar.month_name[month].upper(), f"{e['season']} · {e['name']} dragon · 5 daily habits, {days} days", a)
    p.put(e["key"], KEYS[e["months"].index(month) * 2 + 1], 230, W - M - 250, 60, rot=6)
    y = p.stages(e["key"], 260, ["day 3", "day 7", "day 10", "day 14", "day 18", "day 22", "day 26", f"day {days}"], "milestones = your longest streak this month")
    d = p.d; gy = y + 20; d.text((M, gy), "HABITS", font=F_SEC, fill=DARK); d.text((M + 170, gy + 4), "colour one circle per habit per day", font=F_HAND_S, fill=GREY)
    gx = M + 300; cell = (W - M - gx) / days; gy += 50
    for day in range(days):
        wd = calendar.weekday(YEAR, month, day + 1)
        d.text((gx + day * cell + cell / 2, gy), str(day + 1), font=F_TINY, fill=(a if wd >= 5 else GREY), anchor="mm")
    for r in range(5):
        yy = gy + 30 + r * 78
        d.rounded_rectangle((M, yy, M + 270, yy + 56), 10, fill=(255, 255, 255), outline=LINE, width=3)
        for day in range(days):
            x = gx + day * cell + cell / 2; wd = calendar.weekday(YEAR, month, day + 1)
            d.ellipse((x - 11, yy + 17, x + 11, yy + 39), outline=(a if wd < 5 else e["soft"]), width=2)
    ty = gy + 30 + 5 * 78 + 30
    d.text((M, ty), "LONGEST STREAK  ______ days", font=F_SEC, fill=DARK); d.text((M + 640, ty + 2), "= your dragon stage", font=F_HAND_S, fill=a)
    d.text((M, ty + 60), "MONTH TOTAL  ______ / " + str(5 * days), font=F_SEC, fill=DARK)
    p.note(ty + 130, ["Streak = days in a row with at least 3 of 5 habits done.", "Missed a day? The streak restarts, the dragon stays. No shame."])
    p.put(e["key"], "07", 400, W - M - 300, H - 480, rot=-5)
    return p.save(f"{e['key']}_{month:02d}_{calendar.month_abbr[month].lower()}")


def tracker_page(e, kind):
    a = e["accent"]; k = e["key"]
    if kind == "habit":
        p = Page("HABIT TRACKER", "Quarter view: 5 habits x 13 weeks", a); p.put(k, "03", 230, W - M - 250, 60, rot=6)
        y = p.stages(k, 260, ["5 done", "20", "40", "60", "80", "100", "130", "160"], "every tick feeds the dragon"); d = p.d; gy = y + 20
        d.text((M, gy), "HABITS", font=F_SEC, fill=DARK); gx = M + 300; cell = (W - M - gx) / 13; gy += 50
        for wk in range(13):
            d.text((gx + wk * cell + cell / 2, gy), f"W{wk + 1}", font=F_TINY, fill=GREY, anchor="mm")
        for r in range(5):
            yy = gy + 30 + r * 78; d.rounded_rectangle((M, yy, M + 270, yy + 56), 10, fill=(255, 255, 255), outline=LINE, width=3)
            for wk in range(13):
                x = gx + wk * cell; d.rounded_rectangle((x + 8, yy + 8, x + cell - 8, yy + 48), 8, outline=a, width=2)
        ty = gy + 30 + 5 * 78 + 30; d.text((M, ty), "Write the week's count in each box (0 to 7).", font=F_HAND_S, fill=GREY)
        p.note(ty + 60, ["Quarter total  ______ / 455", "Unlock a stage every 20 ticks, the adult at 160."]); p.put(k, "06", 420, W - M - 330, H - 520, rot=5)
    elif kind == "focus" or kind == "study":
        title = "FOCUS SESSIONS" if kind == "focus" else "STUDY SESSIONS"
        p = Page(title, "80 sessions of 25 minutes", a); p.put(k, "05", 260, W - M - 260, 40, rot=8)
        y = p.stages(k, 260, ["5", "10", "20", "30", "40", "50", "65", "80"], "every session is a breath of fire" if kind == "focus" else "every session is a spark"); d = p.d; gy = y + 20
        d.text((M, gy), "PROJECT", font=F_SEC, fill=DARK); d.rounded_rectangle((M + 150, gy - 8, M + 700, gy + 42), 10, outline=LINE, width=3)
        d.text((M + 780, gy), "WEEKS", font=F_SEC, fill=DARK); d.rounded_rectangle((M + 900, gy - 8, M + 1100, gy + 42), 10, outline=LINE, width=3)
        gy += 90; cols = 16; cw = 76; ch = 58
        for n in range(80):
            r, c = divmod(n, cols); x = M + c * cw; yy = gy + r * (ch + 14)
            d.rounded_rectangle((x, yy, x + cw - 10, yy + ch), 10, fill=(255, 255, 255), outline=a if n % 5 == 4 else LINE, width=3 if n % 5 == 4 else 2)
            d.text((x + (cw - 10) / 2, yy + ch / 2), str(n + 1), font=F_SMALL, fill=GREY, anchor="mm")
        ty = gy + 5 * (ch + 14) + 30; d.text((M, ty), "WEEKLY REVIEW", font=F_SEC, fill=DARK)
        for i in range(4):
            ry = ty + 50 + i * 60; d.text((M, ry + 10), f"Week {i + 1}", font=F_LABEL, fill=GREY); d.line((M + 120, ry + 44, M + 900, ry + 44), fill=LINE, width=2)
        p.note(ty + 320, ["Coloured boxes mark every 5th session: take a longer break", "and check if a new dragon stage has unlocked."]); p.put(k, "01", 300, W - M - 280, H - 420, rot=-6)
    elif kind == "reading":
        p = Page("READING TRACKER", "Pages read this season feed a very hungry dragon", a); p.put(k, "04", 230, W - M - 250, 60, rot=-6)
        y = p.stages(k, 260, ["100 pg", "300", "600", "1000", "1500", "2000", "3000", "5000"], "the more you read, the bigger it gets"); d = p.d; by = y + 20
        for x, t in ((M, "BOOKS"), (M + 560, "PAGES"), (M + 760, "RATING"), (M + 1040, "FINISHED")):
            d.text((x, by), t, font=F_SEC, fill=DARK)
        for i in range(10):
            ry = by + 50 + i * 64; d.line((M, ry + 50, W - M, ry + 50), fill=LINE, width=2); d.text((M, ry + 8), f"{i + 1}.", font=F_LABEL, fill=GREY)
            d.rounded_rectangle((M + 560, ry + 6, M + 700, ry + 46), 8, outline=LINE, width=2)
            for s in range(5):
                d.ellipse((M + 760 + s * 44, ry + 12, M + 788 + s * 44, ry + 40), outline=a, width=2)
            d.rounded_rectangle((M + 1040, ry + 6, M + 1200, ry + 46), 8, outline=LINE, width=2)
        ty = by + 50 + 10 * 64 + 30; d.text((M, ty), "TOTAL PAGES  ______", font=F_SEC, fill=DARK)
        p.note(ty + 70, ["Rate with snowflakes: 5 = would reread tonight.", "Finished a 5-flake book? Paste a baby dragon next to it."]); p.put(k, "06", 420, W - M - 330, H - 520, rot=5)
    elif kind == "sleep":
        p = Page("SLEEP TRACKER", "31 nights: bedtime, wake-up, hours and how you felt", a); p.put(k, "03", 230, W - M - 250, 60, rot=6)
        y = p.stages(k, 260, ["3 nights", "7", "10", "14", "18", "22", "26", "31"], "nights with 7+ hours grow the dragon"); d = p.d; gy = y + 20
        for x, t in ((M, "NIGHT"), (M + 160, "BED"), (M + 400, "WAKE"), (M + 640, "HOURS"), (M + 860, "QUALITY")):
            d.text((x, gy), t, font=F_SEC, fill=DARK)
        rowh = 42; gy += 50
        for n in range(31):
            ry = gy + n * rowh; d.line((M, ry + rowh - 4, W - M, ry + rowh - 4), fill=LINE, width=1)
            d.text((M + 20, ry + 8), str(n + 1), font=F_LABEL, fill=GREY)
            for x in (M + 160, M + 400, M + 640):
                d.line((x, ry + 30, x + 160, ry + 30), fill=LINE, width=2)
            for s in range(5):
                d.ellipse((M + 860 + s * 40, ry + 8, M + 884 + s * 40, ry + 32), outline=a, width=2)
        p.put(k, "08", 340, W - M - 250, gy + 60, rot=-4)
    elif kind == "water":
        p = Page("WATER TRACKER", "8 glasses a day, 31 days", a); p.put(k, "03", 230, W - M - 250, 60, rot=6)
        y = p.stages(k, 260, ["3 days", "7", "10", "14", "18", "22", "26", "31"], "full days of 8 glasses grow the dragon"); d = p.d; gy = y + 30
        cell = (W - 2 * M) / 8; size = 30
        for n in range(31):
            r, c = divmod(n, 8); x0 = M + c * cell; y0 = gy + r * 150
            d.text((x0 + 4, y0), f"Day {n + 1}", font=F_LABEL, fill=DARK)
            for g in range(8):
                gr, gc = divmod(g, 4); gx = x0 + 4 + gc * (size + 8); gyy = y0 + 36 + gr * (size + 8)
                d.rounded_rectangle((gx, gyy, gx + size, gyy + size), 6, outline=a, width=2)
        p.note(gy + 4 * 150 + 40, ["Colour a glass for every 250 ml.", "A full day = all eight glasses. Those days count for the growth bar."])
    elif kind == "mood":
        p = Page("MOOD TRACKER", "One circle a day, one colour per mood", a); p.put(k, "04", 230, W - M - 250, 60, rot=-6)
        y = p.stages(k, 260, ["3 days", "7", "10", "14", "18", "22", "26", "31"], "calm days grow the dragon"); d = p.d; gy = y + 20
        legend = ["calm", "happy", "tired", "stressed", "sad"]; colors = [e["soft"], (255, 236, 180), (230, 230, 230), (252, 210, 200), (214, 222, 240)]
        d.text((M, gy), "LEGEND", font=F_SEC, fill=DARK)
        for i, (l, c) in enumerate(zip(legend, colors)):
            x = M + 160 + i * 220; d.ellipse((x, gy - 2, x + 36, gy + 34), fill=c, outline=LINE, width=2); d.text((x + 50, gy + 2), l, font=F_LABEL, fill=DARK)
        gy += 90; size = 118
        for n in range(31):
            r, c = divmod(n, 7); cx = M + c * (size + 60) + size / 2; cy = gy + r * (size + 40) + size / 2
            d.ellipse((cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2), outline=a, width=3, fill=(255, 255, 255))
            d.text((cx, cy), str(n + 1), font=F_LABEL, fill=GREY, anchor="mm")
        p.note(gy + 5 * (size + 40) + 10, ["Fill the circle with today's colour. Write one word inside if you like.", "Count calm and happy days at the end of the month."])
    elif kind == "savings":
        p = Page("DRAGON HOARD", "Savings tracker: dragons guard their gold, so will you", a); p.put(k, "08", 260, W - M - 230, 40, rot=-4)
        y = p.stages(k, 260, ["5%", "15%", "30%", "45%", "60%", "75%", "90%", "100%"], "the hoard grows, the dragon grows"); d = p.d; gy = y + 20
        d.text((M, gy), "GOAL", font=F_SEC, fill=DARK); d.rounded_rectangle((M + 110, gy - 8, M + 480, gy + 42), 10, outline=LINE, width=3)
        d.text((M + 560, gy), "DEADLINE", font=F_SEC, fill=DARK); d.rounded_rectangle((M + 720, gy - 8, M + 1000, gy + 42), 10, outline=LINE, width=3)
        d.text((M, gy + 70), "50 COINS  = one coin is 2% of the goal", font=F_SEC, fill=DARK); cy0 = gy + 130; size = 92
        for n in range(50):
            r, c = divmod(n, 10); cx = M + c * (size + 36) + size / 2; cy = cy0 + r * (size + 30) + size / 2
            d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), outline=GOLD, width=4, fill=(255, 250, 236)); d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), outline=(232, 196, 110), width=2)
            d.text((cx, cy), str(n + 1), font=F_LABEL, fill=(170, 120, 40), anchor="mm")
        ty = cy0 + 5 * (size + 30) + 20; d.text((M, ty), "SAVED SO FAR  ______", font=F_SEC, fill=DARK)
        p.note(ty + 70, ["No impulse buys this week? Colour a bonus coin.", "A dragon never spends its hoard on a Tuesday."]); p.put(k, "02", 300, W - M - 300, H - 420, rot=6)
    else:
        raise ValueError(kind)
    return p.save(f"{e['key']}_90_{kind}")


# ------------------------------------------------------------------ sheets for Pinterest
def pinterest_sheet(e):
    cream = SETS[e["key"]][0]; Wp, Hp = 1000, 1500; cols, rows, margin, gap = 4, 2, 80, 40
    sheet = Image.new("RGB", (margin * 2 + cols * Wp + (cols - 1) * gap, margin * 2 + rows * Hp + gap), PAPER)
    for i, k in enumerate(KEYS):
        r, c = divmod(i, cols); sheet.paste(cream[k], (margin + c * (Wp + gap), margin + r * (Hp + gap)))
    sheet.save(os.path.join(OUT, f"{e['key']}_sheet.png"), optimize=True)
    sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(os.path.join(OUT, f"{e['key']}_sheet_small.jpg"), quality=90)


# ------------------------------------------------------------------ assembly
def make_pdf(paths, out, links=None, home_from=2, outline=None):
    ims = [Image.open(p).convert("RGB") for p in paths]
    tmp = out + ".tmp.pdf"; ims[0].save(tmp, save_all=True, append_images=ims[1:], resolution=192.0, quality=90)
    r = PdfReader(tmp); w = PdfWriter(); w.append(r)
    pw = float(w.pages[0].mediabox.width); ph = float(w.pages[0].mediabox.height); sx = pw / W; sy = ph / H
    for l in (links or []):
        x0, y0, x1, y1 = l["rect"]; w.add_annotation(page_number=l.get("on", 1), annotation=Link(rect=(x0 * sx, ph - y1 * sy, x1 * sx, ph - y0 * sy), target_page_index=l["page"]))
    for i in range(home_from, len(ims)):
        w.add_annotation(page_number=i, annotation=Link(rect=(0, ph - 230 * sy, 700 * sx, ph), target_page_index=1 if len(ims) > 2 else 0))
    for title, idx in (outline or []):
        w.add_outline_item(title, idx)
    with open(out, "wb") as f:
        w.write(f)
    os.remove(tmp); print(os.path.basename(out), round(os.path.getsize(out) / 1e6, 1), "MB", len(ims), "pages")


def build():
    for e in ELEMENTS:
        pinterest_sheet(e)
    # per-element page lists
    element_pages = {}
    for e in ELEMENTS:
        pages = [season_cover(e), sheet_page(e)] + [month_page(e, m) for m in e["months"]] + [tracker_page(e, t) for t in e["trackers"]]
        element_pages[e["key"]] = pages
    cover = cover_page(); how = how_page(); hall = hall_page(); notes = notes_page()
    # full planner order: cover, contents, how, hall, 4 x element block, notes
    order = [cover, None, how, hall]
    targets = {"how": 2, "hall": 3}
    for e in ELEMENTS:
        targets[e["key"]] = len(order); order += element_pages[e["key"]]
    targets["notes"] = len(order); order.append(notes)
    contents, links = contents_page(targets); order[1] = contents
    outline = [("Cover", 0), ("Contents", 1), ("How it works", 2), ("Hall of Dragons", 3)] + [(f"{e['season']}: {e['name']} dragon", targets[e["key"]]) for e in ELEMENTS] + [("Notes", targets["notes"])]
    make_pdf(order, os.path.join(OUT, "Year_of_Dragons_Planner.pdf"), links, home_from=2, outline=outline)
    # one PDF per element (season cover, sheet, months, trackers, notes)
    for e in ELEMENTS:
        pages = element_pages[e["key"]] + [notes]
        make_pdf(pages, os.path.join(OUT, f"{e['name']}_Season_Planner.pdf"), home_from=1, outline=[(e["season"] + " cover", 0), ("Sticker sheet", 1)] + [(calendar.month_name[m], 2 + i) for i, m in enumerate(e["months"])])
    # previews
    thumbs = [Image.open(p).convert("RGB").resize((384, 512), Image.LANCZOS) for p in order]
    cols = 6; rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 394 + 10, rows * 522 + 10), (225, 220, 212))
    for i, t in enumerate(thumbs):
        sheet.paste(t, (10 + (i % cols) * 394, 10 + (i // cols) * 522))
    sheet.save(os.path.join(OUT, "preview_all_pages.jpg"), quality=85)
    print("pages:", len(order))


if __name__ == "__main__":
    build()
