#!/usr/bin/env python3
"""Rebuild every derived fire-dragon asset from the 8 base stickers.

Inputs (not in git, see README):
  images/fire_dragon/0*.png              8 stickers on cream paper, 1000x1500
  images/fire_dragon/transparent/0*.png  same 8 with alpha channel

Outputs:
  images/fire_dragon/fire_dragon_sheet.png (+ _small.jpg)      2x4 sheet for Pinterest
  images/fire_dragon/transparent/fire_dragon_sheet_transparent.png
  images/fire_dragon/goodnotes_usage_page.png (+ _preview.jpg) planner mockup pin
  images/fire_dragon/trackers/0*.png                            4 tracker pages 1536x2048
  images/fire_dragon/planner/*.png + Fire_Dragon_Planner_GoodNotes.pdf

Run:  python3 build_fire_dragon_assets.py
"""
import glob
import json
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link

ROOT = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(ROOT, "images", "fire_dragon")
TR = os.path.join(FD, "transparent")
TRK = os.path.join(FD, "trackers")
PL = os.path.join(FD, "planner")
for d in (TRK, PL):
    os.makedirs(d, exist_ok=True)

SUP = "/System/Library/Fonts/Supplemental/"
AV = "/System/Library/Fonts/Avenir Next.ttc"


def font(name, size, index=0):
    return ImageFont.truetype(name, size, index=index)


ORANGE = (226, 112, 52)
DARK = (60, 56, 54)
GREY = (150, 145, 140)
LINE = (222, 216, 208)
DOT = (218, 212, 204)
PEACH = (252, 226, 206)
CREAM = (252, 249, 243)
PAPER = (250, 246, 238)

KEYS = ["01", "02", "03", "04", "05", "06", "07", "08"]
LABELS = ["1 Egg", "2 Hatchling", "3 Baby", "4 Child", "5 Juvenile", "6 Adolescent", "7 Young adult", "8 Adult"]


def load_stickers():
    cream = {os.path.basename(f)[:2]: Image.open(f).convert("RGB") for f in sorted(glob.glob(os.path.join(FD, "0*.png")))}
    trans = {}
    for f in sorted(glob.glob(os.path.join(TR, "0*.png"))):
        im = Image.open(f).convert("RGBA")
        bbox = im.getchannel("A").getbbox()
        pad = 16
        im = im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad)))
        trans[os.path.basename(f)[:2]] = im
    assert len(cream) == 8 and len(trans) == 8, (len(cream), len(trans))
    return cream, trans


CREAM_SET, STICK = load_stickers()


def put(img, key, h, x, y, rot=0, opacity=1.0, center=False):
    s = STICK[key]
    s = s.resize((int(s.width * h / s.height), h), Image.LANCZOS)
    if rot:
        s = s.rotate(rot, expand=True, resample=Image.BICUBIC)
    if opacity < 1:
        s.putalpha(s.getchannel("A").point(lambda v: int(v * opacity)))
    if center:
        x, y = x - s.width // 2, y - s.height // 2
    img.alpha_composite(s, (int(x), int(y)))


# ---------------------------------------------------------------- sheets
def build_sheets():
    W, H = 1000, 1500
    cols, rows, margin, gap = 4, 2, 80, 40
    sw = margin * 2 + cols * W + (cols - 1) * gap
    sh = margin * 2 + rows * H + (rows - 1) * gap
    sheet = Image.new("RGB", (sw, sh), PAPER)
    for i, k in enumerate(KEYS):
        r, c = divmod(i, cols)
        sheet.paste(CREAM_SET[k], (margin + c * (W + gap), margin + r * (H + gap)))
    sheet.save(os.path.join(FD, "fire_dragon_sheet.png"), optimize=True)
    sheet.resize((sw // 2, sh // 2), Image.LANCZOS).save(os.path.join(FD, "fire_dragon_sheet_small.jpg"), quality=90)

    cw = max(s.width for s in STICK.values())
    ch = max(s.height for s in STICK.values())
    gap, margin = 60, 60
    tsheet = Image.new("RGBA", (margin * 2 + cols * cw + (cols - 1) * gap, margin * 2 + rows * ch + (rows - 1) * gap), (0, 0, 0, 0))
    for i, k in enumerate(KEYS):
        r, c = divmod(i, cols)
        s = STICK[k]
        tsheet.alpha_composite(s, (margin + c * (cw + gap) + (cw - s.width) // 2, margin + r * (ch + gap) + (ch - s.height) // 2))
    tsheet.save(os.path.join(TR, "fire_dragon_sheet_transparent.png"), optimize=True)
    prev = Image.new("RGBA", tsheet.size, (52, 58, 70, 255))
    prev.alpha_composite(tsheet)
    prev.convert("RGB").resize((tsheet.width // 2, tsheet.height // 2), Image.LANCZOS).save(os.path.join(TR, "preview_on_dark.jpg"), quality=88)
    print("sheets ok")


# ---------------------------------------------------------------- usage page (2:3 pin)
def build_usage_page():
    W, H = 2000, 3000
    F_HEAD = font(AV, 78, 2); F_SUB = font(AV, 40); F_DAY = font(AV, 40, 2); F_LABEL = font(AV, 32)
    F_HAND = font(SUP + "Bradley Hand Bold.ttf", 46); F_HAND_S = font(SUP + "Bradley Hand Bold.ttf", 36)
    img = Image.new("RGBA", (W, H), (238, 232, 224, 255))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((90, 100, 1930, 2940), 44, fill=(0, 0, 0, 70))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(30)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((80, 80, 1920, 2920), 44, fill=(255, 255, 255, 255))
    for y in range(140, 2900, 50):
        for x in range(140, 1900, 50):
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(214, 208, 200))
    d.text((170, 170), "WEEKLY PLANNER", font=F_HEAD, fill=DARK)
    d.text((172, 270), "Fire Dragon stickers in GoodNotes", font=F_SUB, fill=GREY)
    d.line((170, 340, 1100, 340), fill=ORANGE, width=6)
    put(img, "05", 380, 1500, 90, rot=-8)
    days = [("MON", "Start the new project", "01"), ("TUE", "Gym 7:00 + read 20 pages", None), ("WED", "Dragon hatched: first draft done!", "02"),
            ("THU", "Call mom, buy tea", None), ("FRI", "Presentation day, bring fire", "03"), ("SAT", "Hike + sketchbook afternoon", "04"),
            ("SUN", "Rest. Plan next week", "06")]
    y0, rh = 500, 165
    for i, (day, task, sk) in enumerate(days):
        y = y0 + i * rh
        d = ImageDraw.Draw(img)
        d.line((170, y + rh, 1830, y + rh), fill=LINE, width=3)
        d.text((176, y + 52), day, font=F_DAY, fill=ORANGE)
        d.rounded_rectangle((330, y + 56, 376, y + 102), 8, outline=DARK, width=4)
        if i in (0, 2, 4):
            d.line((340, y + 80, 350, y + 94), fill=ORANGE, width=6); d.line((350, y + 94, 370, y + 62), fill=ORANGE, width=6)
        d.text((410, y + 50), task, font=F_HAND, fill=DARK)
        if sk:
            put(img, sk, 190, 1560, y - 10, rot=(6 if i % 2 else -6))
    d = ImageDraw.Draw(img)
    ys = 1700
    d.text((170, ys), "30-DAY STREAK", font=F_HEAD, fill=DARK)
    d.text((172, ys + 100), "your dragon grows with every finished week", font=F_HAND, fill=ORANGE)
    labels = ["Day 1", "Day 4", "Day 8", "Day 12", "Day 16", "Day 20", "Day 25", "Day 30"]
    row_y = ys + 190; slot = 1660 / 8
    for i, k in enumerate(KEYS):
        cx = 170 + slot * i + slot / 2; done = i < 5
        put(img, k, 300, cx, row_y + 170, opacity=(1.0 if done else 0.28), center=True)
        d = ImageDraw.Draw(img)
        d.text((cx, row_y + 360), labels[i], font=F_LABEL, fill=(DARK if done else GREY), anchor="mm")
    d.line((170 + slot / 2, row_y + 411, 170 + slot * 4.5, row_y + 411), fill=ORANGE, width=6)
    d.line((170 + slot * 4.5, row_y + 411, 170 + slot * 7.5, row_y + 411), fill=LINE, width=6)
    for i in range(8):
        cx = 170 + slot * i + slot / 2
        if i < 5:
            d.ellipse((cx - 16, row_y + 395, cx + 16, row_y + 427), fill=ORANGE)
        else:
            d.ellipse((cx - 16, row_y + 395, cx + 16, row_y + 427), fill=(255, 255, 255), outline=LINE, width=4)
    hy = row_y + 480
    d.text((170, hy), "HABIT TRACKER", font=F_DAY, fill=DARK)
    d.text((560, hy + 4), "draw 10 min a day", font=F_HAND_S, fill=GREY)
    for n in range(30):
        cx = 190 + (n % 15) * 86; cy = hy + 90 + (n // 15) * 86
        if n < 17:
            d.ellipse((cx - 26, cy - 26, cx + 26, cy + 26), fill=(248, 196, 160))
        else:
            d.ellipse((cx - 26, cy - 26, cx + 26, cy + 26), outline=LINE, width=4)
        d.text((cx, cy), str(n + 1), font=F_LABEL, fill=(DARK if n < 17 else GREY), anchor="mm")
    ty = hy + 250
    note = Image.new("RGBA", (1100, 230), (0, 0, 0, 0))
    ImageDraw.Draw(note).rounded_rectangle((0, 0, 1099, 229), 18, fill=(255, 241, 196, 255))
    img.alpha_composite(note.rotate(-1.5, expand=True, resample=Image.BICUBIC), (170, ty))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(["How to use: import the PNG sheet, lasso a dragon,", "Copy, then Paste on any page. Or add each PNG", "to Elements and drag it in with one tap."]):
        d.text((210, ty + 40 + 55 * i), l, font=F_HAND_S, fill=DARK)
    put(img, "08", 440, 1480, hy - 40, rot=-4)
    out = img.convert("RGB")
    out.save(os.path.join(FD, "goodnotes_usage_page.png"), optimize=True)
    out.resize((1000, 1500), Image.LANCZOS).save(os.path.join(FD, "goodnotes_usage_page_preview.jpg"), quality=90)
    print("usage page ok")


# ---------------------------------------------------------------- trackers (iPad 3:4)
W, H, M = 1536, 2048, 110
F_HEAD = font(AV, 64, 2); F_SUB = font(AV, 30); F_SEC = font(AV, 30, 2); F_LABEL = font(AV, 24); F_SMALL = font(AV, 20); F_TINY = font(AV, 17)
F_HAND = font(SUP + "Bradley Hand Bold.ttf", 34); F_HAND_S = font(SUP + "Bradley Hand Bold.ttf", 28)


class Page:
    def __init__(self, title, subtitle, dots=True):
        self.img = Image.new("RGBA", (W, H), CREAM + (255,))
        self.d = ImageDraw.Draw(self.img)
        if dots:
            for y in range(80, H - 60, 48):
                for x in range(80, W - 60, 48):
                    self.d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=DOT)
        self.d.text((M, 90), title, font=F_HEAD, fill=DARK)
        self.d.text((M + 2, 170), subtitle, font=F_SUB, fill=GREY)
        self.d.line((M, 225, M + 620, 225), fill=ORANGE, width=5)

    def put(self, *a, **k):
        put(self.img, *a, **k); self.d = ImageDraw.Draw(self.img)

    def stages(self, y, labels, caption):
        d = self.d
        d.text((M, y), "DRAGON GROWTH", font=F_SEC, fill=DARK)
        d.text((M + 300, y + 2), caption, font=F_HAND_S, fill=ORANGE)
        slot = (W - 2 * M) / 8; ry = y + 60
        for i, k in enumerate(KEYS):
            cx = M + slot * i + slot / 2
            self.d.rounded_rectangle((cx - slot / 2 + 8, ry, cx + slot / 2 - 8, ry + 200), 16, fill=(255, 255, 255), outline=LINE, width=3)
            self.put(k, 170, cx, ry + 100, opacity=0.22, center=True)
            self.d.text((cx, ry + 228), labels[i], font=F_LABEL, fill=DARK, anchor="mm")
        d = self.d
        d.line((M + slot / 2, ry + 263, W - M - slot / 2, ry + 263), fill=LINE, width=4)
        for i in range(8):
            cx = M + slot * i + slot / 2
            d.ellipse((cx - 13, ry + 250, cx + 13, ry + 276), fill=(255, 255, 255), outline=ORANGE, width=3)
        d.text((M, ry + 300), "Paste the next dragon sticker over the faded one each time you hit a milestone.", font=F_SMALL, fill=GREY)
        return ry + 340

    def note(self, y, lines):
        n = Image.new("RGBA", (760, 40 + 44 * len(lines)), (0, 0, 0, 0))
        ImageDraw.Draw(n).rounded_rectangle((0, 0, 759, n.height - 1), 14, fill=(255, 241, 196, 255))
        self.img.alpha_composite(n.rotate(-1.2, expand=True, resample=Image.BICUBIC), (M, y)); self.d = ImageDraw.Draw(self.img)
        for i, l in enumerate(lines):
            self.d.text((M + 30, y + 22 + 44 * i), l, font=F_HAND_S, fill=DARK)

    def save(self, name, folder=TRK):
        self.img.convert("RGB").save(os.path.join(folder, name + ".png"), optimize=True)


def build_trackers():
    p = Page("HABIT TRACKER", "Month: ____________   Hatch a dragon with 5 habits x 31 days")
    p.put("03", 230, W - M - 250, 60, rot=6)
    y = p.stages(260, ["5 done", "20", "40", "60", "80", "100", "125", "155 all"], "every tick feeds the dragon")
    d = p.d; gy = y + 20; d.text((M, gy), "HABITS", font=F_SEC, fill=DARK)
    gx = M + 300; cell = (W - M - gx) / 31; gy += 50
    for day in range(31):
        d.text((gx + day * cell + cell / 2, gy), str(day + 1), font=F_TINY, fill=GREY, anchor="mm")
    for r in range(5):
        yy = gy + 30 + r * 78
        d.rounded_rectangle((M, yy, M + 270, yy + 56), 10, fill=(255, 255, 255), outline=LINE, width=3)
        d.text((M + 16, yy + 14), ["Read 20 pages", "Workout", "No sugar", "Journal", "__________"][r], font=F_HAND_S, fill=DARK)
        for day in range(31):
            x = gx + day * cell + cell / 2
            d.ellipse((x - 11, yy + 17, x + 11, yy + 39), outline=ORANGE if day % 7 != 6 else PEACH, width=2)
    ty = gy + 30 + 5 * 78 + 30
    d.text((M, ty), "MONTH TOTAL  ______ / 155 ticks", font=F_SEC, fill=DARK); d.text((M + 700, ty + 2), "= your dragon stage", font=F_HAND_S, fill=ORANGE)
    p.note(ty + 70, ["Rule: colour one circle per habit per day.", "Count ticks at the end of each week and unlock the next stage."])
    p.put("07", 440, W - M - 330, H - 520, rot=-5)
    p.save("01_habit_tracker")

    p = Page("READING TRACKER", "Pages read this season feed a very hungry dragon")
    p.put("04", 230, W - M - 250, 60, rot=-6)
    y = p.stages(260, ["100 pg", "300", "600", "1000", "1500", "2000", "3000", "5000"], "the more you read, the bigger it gets")
    d = p.d; by = y + 20
    for x, t in ((M, "BOOKS"), (M + 560, "PAGES"), (M + 760, "RATING"), (M + 1040, "FINISHED")):
        d.text((x, by), t, font=F_SEC, fill=DARK)
    for i in range(10):
        ry = by + 50 + i * 64
        d.line((M, ry + 50, W - M, ry + 50), fill=LINE, width=2)
        d.text((M, ry + 8), f"{i + 1}.", font=F_LABEL, fill=GREY)
        d.rounded_rectangle((M + 560, ry + 6, M + 700, ry + 46), 8, outline=LINE, width=2)
        for s in range(5):
            d.ellipse((M + 760 + s * 44, ry + 12, M + 788 + s * 44, ry + 40), outline=ORANGE, width=2)
        d.rounded_rectangle((M + 1040, ry + 6, M + 1200, ry + 46), 8, outline=LINE, width=2)
    ty = by + 50 + 10 * 64 + 30
    d.text((M, ty), "TOTAL PAGES  ______", font=F_SEC, fill=DARK); d.text((M + 500, ty + 2), "write it here and check the growth bar", font=F_HAND_S, fill=ORANGE)
    p.note(ty + 70, ["Rate with flames: 5 flames = would reread tonight.", "Finished a 5-flame book? Paste a baby dragon next to it."])
    p.put("06", 420, W - M - 330, H - 520, rot=5)
    p.save("02_reading_tracker")

    p = Page("DRAGON HOARD", "Savings tracker: dragons guard their gold, so will you")
    p.put("08", 260, W - M - 230, 40, rot=-4)
    y = p.stages(260, ["5%", "15%", "30%", "45%", "60%", "75%", "90%", "100%"], "the hoard grows, the dragon grows")
    d = p.d; gy = y + 20
    d.text((M, gy), "GOAL", font=F_SEC, fill=DARK); d.rounded_rectangle((M + 110, gy - 8, M + 480, gy + 42), 10, outline=LINE, width=3)
    d.text((M + 560, gy), "DEADLINE", font=F_SEC, fill=DARK); d.rounded_rectangle((M + 720, gy - 8, M + 1000, gy + 42), 10, outline=LINE, width=3)
    d.text((M, gy + 70), "50 COINS  = one coin is 2% of the goal", font=F_SEC, fill=DARK)
    cy0 = gy + 130; size = 92
    for n in range(50):
        r, c = divmod(n, 10); cx = M + c * (size + 36) + size / 2; cy = cy0 + r * (size + 30) + size / 2
        d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), outline=(214, 160, 70), width=4, fill=(255, 250, 236))
        d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), outline=(232, 196, 110), width=2)
        d.text((cx, cy), str(n + 1), font=F_LABEL, fill=(170, 120, 40), anchor="mm")
    ty = cy0 + 5 * (size + 30) + 20
    d.text((M, ty), "SAVED SO FAR  ______", font=F_SEC, fill=DARK); d.text((M + 520, ty + 2), "colour a coin for every 2% saved", font=F_HAND_S, fill=ORANGE)
    p.note(ty + 70, ["No spending on impulse buys this week?", "Colour a bonus coin and let the dragon purr."])
    p.put("02", 300, W - M - 300, H - 420, rot=6)
    p.save("03_savings_tracker")

    p = Page("FOCUS SESSIONS", "Deep-work tracker: 25-minute sessions, 80 in total")
    p.put("05", 260, W - M - 260, 40, rot=8)
    y = p.stages(260, ["5", "10", "20", "30", "40", "50", "65", "80"], "every session is a breath of fire")
    d = p.d; gy = y + 20
    d.text((M, gy), "PROJECT", font=F_SEC, fill=DARK); d.rounded_rectangle((M + 150, gy - 8, M + 700, gy + 42), 10, outline=LINE, width=3)
    d.text((M + 780, gy), "WEEKS", font=F_SEC, fill=DARK); d.rounded_rectangle((M + 900, gy - 8, M + 1100, gy + 42), 10, outline=LINE, width=3)
    gy += 90; cols = 16; cw = 76; ch = 58
    for n in range(80):
        r, c = divmod(n, cols); x = M + c * cw; yy = gy + r * (ch + 14)
        d.rounded_rectangle((x, yy, x + cw - 10, yy + ch), 10, fill=(255, 255, 255), outline=ORANGE if n % 5 == 4 else LINE, width=3 if n % 5 == 4 else 2)
        d.text((x + (cw - 10) / 2, yy + ch / 2), str(n + 1), font=F_SMALL, fill=GREY, anchor="mm")
    ty = gy + 5 * (ch + 14) + 30
    d.text((M, ty), "WEEKLY REVIEW", font=F_SEC, fill=DARK)
    for i in range(4):
        ry = ty + 50 + i * 60; d.text((M, ry + 10), f"Week {i + 1}", font=F_LABEL, fill=GREY); d.line((M + 120, ry + 44, M + 900, ry + 44), fill=LINE, width=2)
    p.note(ty + 320, ["Orange boxes mark every 5th session: take a longer break", "and check if a new dragon stage has unlocked."])
    p.put("01", 300, W - M - 280, H - 420, rot=-6)
    p.save("04_focus_tracker")

    ims = [Image.open(f).convert("RGB") for f in sorted(glob.glob(os.path.join(TRK, "0*.png")))]
    w, h = ims[0].size; s = Image.new("RGB", (w * 2 + 60, h * 2 + 60), (238, 232, 224))
    for i, im in enumerate(ims):
        s.paste(im, (20 + (i % 2) * (w + 20), 20 + (i // 2) * (h + 20)))
    s.resize((s.width // 3, s.height // 3), Image.LANCZOS).save(os.path.join(TRK, "preview_all_trackers.jpg"), quality=88)
    print("trackers ok")


# ---------------------------------------------------------------- planner pages + PDF
def build_planner():
    F_TITLE = font(AV, 120, 2); F_TITLE2 = font(AV, 56); F_TOC = font(AV, 40); F_TOCB = font(AV, 40, 2); F_HANDC = font(SUP + "Bradley Hand Bold.ttf", 40)
    bg = (243, 232, 220)
    glow = Image.new("RGB", (W, H), bg); ImageDraw.Draw(glow).ellipse((200, 560, 1336, 1760), fill=(253, 214, 170))
    img = glow.filter(ImageFilter.GaussianBlur(160)).convert("RGBA"); d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, 70, W - 70, H - 70), 40, outline=ORANGE, width=4); d.rounded_rectangle((90, 90, W - 90, H - 90), 32, outline=(240, 190, 150), width=2)
    d.text((W // 2, 230), "DRAGON HATCHERY", font=F_TITLE2, fill=ORANGE, anchor="mm")
    d.text((W // 2, 330), "FIRE", font=F_TITLE, fill=DARK, anchor="mm"); d.text((W // 2, 430), "PLANNER", font=F_TITLE, fill=DARK, anchor="mm")
    d.line((W // 2 - 260, 500, W // 2 + 260, 500), fill=ORANGE, width=5)
    d.text((W // 2, 565), "grow a dragon from your habits", font=F_HANDC, fill=(120, 90, 70), anchor="mm")
    put(img, "08", 1050, W // 2, 1180, center=True); put(img, "01", 260, 200, 1500, rot=-8); put(img, "03", 260, 1130, 1520, rot=8)
    d = ImageDraw.Draw(img); d.text((W // 2, 1890), "8 growth stages  ·  4 trackers  ·  digital stickers for GoodNotes", font=F_SUB, fill=(120, 110, 100), anchor="mm")
    img.convert("RGB").save(os.path.join(PL, "00_cover.png"), optimize=True)

    toc = [("How it works", "the growth mechanic in one page", 3), ("Sticker sheet", "all 8 stages, ready to copy", 4), ("Habit tracker", "5 habits x 31 days", 5),
           ("Reading tracker", "pages that feed the dragon", 6), ("Dragon hoard", "savings tracker", 7), ("Focus sessions", "80 deep-work sessions", 8), ("Blank dotted page", "for your own trackers", 9)]
    p = Page("CONTENTS", "Tap a line to jump to the page"); p.put("05", 330, W - M - 330, 40, rot=-6); d = p.d
    links = []; y = 330
    for i, (t, s, pg) in enumerate(toc):
        d.rounded_rectangle((M, y, W - M, y + 130), 18, fill=(255, 255, 255, 255), outline=LINE, width=3)
        d.ellipse((M + 30, y + 35, M + 90, y + 95), fill=ORANGE); d.text((M + 60, y + 65), str(i + 1), font=F_TOCB, fill=(255, 255, 255), anchor="mm")
        d.text((M + 130, y + 28), t, font=F_TOCB, fill=DARK); d.text((M + 130, y + 78), s, font=F_SUB, fill=GREY)
        d.text((W - M - 40, y + 65), f"p.{pg}", font=F_TOC, fill=ORANGE, anchor="rm")
        links.append({"rect": [M, y, W - M, y + 130], "page": pg}); y += 160
    d.text((M, y + 40), "HOW TO UNLOCK A STAGE", font=F_SEC, fill=DARK)
    for i, s in enumerate(["1. Finish a milestone on any tracker.", "2. Go to the sticker sheet, lasso the next dragon, copy.", "3. Paste it over the faded stage in the growth bar.", "4. Repeat until the antlered adult appears on day 30."]):
        d.text((M, y + 95 + 48 * i), s, font=F_HAND_S, fill=DARK)
    p.put("02", 300, W - M - 300, y + 20, rot=6)
    p.save("01_contents", PL)

    img = Image.new("RGB", (W, H), (238, 232, 224)); u = Image.open(os.path.join(FD, "goodnotes_usage_page.png")).convert("RGB")
    u = u.resize((int(u.width * H / u.height), H), Image.LANCZOS); img.paste(u, ((W - u.width) // 2, 0))
    img.save(os.path.join(PL, "02_how_it_works.png"), optimize=True)

    p = Page("STICKER SHEET", "Lasso a dragon, copy, paste it anywhere in the planner", dots=False)
    cols = 4; cw = (W - 2 * M) / cols; top = 300; rh = 820
    for i, k in enumerate(KEYS):
        r, c = divmod(i, cols); cx = M + cw * c + cw / 2; cy = top + rh * r
        s = STICK[k]; h = 540; w = int(s.width * h / s.height)
        if w > cw - 30:
            w = int(cw - 30); h = int(s.height * w / s.width)
        p.img.alpha_composite(s.resize((w, h), Image.LANCZOS), (int(cx - w / 2), int(cy + 330 - h / 2)))
        p.d = ImageDraw.Draw(p.img); p.d.text((cx, cy + 660), LABELS[i], font=F_LABEL, fill=GREY, anchor="mm")
    p.save("03_sticker_sheet", PL)

    p = Page("NOTES", ""); p.put("04", 260, W - M - 260, 40, rot=6); p.save("08_blank", PL)

    order = [os.path.join(PL, n) for n in ("00_cover.png", "01_contents.png", "02_how_it_works.png", "03_sticker_sheet.png")] + \
            [os.path.join(TRK, n) for n in ("01_habit_tracker.png", "02_reading_tracker.png", "03_savings_tracker.png", "04_focus_tracker.png")] + [os.path.join(PL, "08_blank.png")]
    ims = [Image.open(f).convert("RGB") for f in order]
    tmp = os.path.join(PL, "_nolinks.pdf")
    ims[0].save(tmp, save_all=True, append_images=ims[1:], resolution=192.0, quality=92)
    r = PdfReader(tmp); wr = PdfWriter(); wr.append(r)
    pw = float(wr.pages[0].mediabox.width); ph = float(wr.pages[0].mediabox.height); sx = pw / W; sy = ph / H
    for l in links:
        x0, y0, x1, y1 = l["rect"]
        wr.add_annotation(page_number=1, annotation=Link(rect=(x0 * sx, ph - y1 * sy, x1 * sx, ph - y0 * sy), target_page_index=l["page"] - 1))
    for i in range(2, len(ims)):
        wr.add_annotation(page_number=i, annotation=Link(rect=(0, ph - 230 * sy, 700 * sx, ph), target_page_index=1))
    for i, t in enumerate(["Cover", "Contents", "How it works", "Sticker sheet", "Habit tracker", "Reading tracker", "Dragon hoard", "Focus sessions", "Notes"]):
        wr.add_outline_item(t, i)
    out = os.path.join(PL, "Fire_Dragon_Planner_GoodNotes.pdf")
    with open(out, "wb") as f:
        wr.write(f)
    os.remove(tmp)
    print("planner ok", round(os.path.getsize(out) / 1e6, 1), "MB")


if __name__ == "__main__":
    build_sheets()
    build_usage_page()
    build_trackers()
    build_planner()
