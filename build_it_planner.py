#!/usr/bin/env python3
"""Build "Code & Cozy", a 2027 daily planner for a girl in IT (GoodNotes / iPad, portrait 3:4).

Vector PDF (real text, crisp at any zoom, searchable) with hyperlinked tabs, month strips, calendar
cells, prev/next arrows and an outline for GoodNotes.

Inputs (not in git):  images/it_girl/cut/*.png   (run cut_it_girl_stickers.py first)
Outputs:              images/it_girl/Code_and_Cozy_Planner_2027_<Mon|Sun>.pdf

Run:  .venv-planner/bin/python build_it_planner.py            # Monday start
      .venv-planner/bin/python build_it_planner.py sun        # Sunday start
"""
import calendar
import datetime as dt
import math
import os
import sys

from PIL import Image, ImageFilter
from reportlab.lib.colors import Color, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from pdf_utils import lighten

ROOT = os.path.dirname(os.path.abspath(__file__))
FULL = os.path.join(ROOT, "images", "it_girl", "cut")
CUT = os.path.join(ROOT, "images", "it_girl", "cut_small")      # planner-sized copies keep the PDF light
MAXPX = 640
SHADOW = os.path.join(ROOT, "images", "it_girl", "shadow")
OUT = os.path.join(ROOT, "images", "it_girl")
os.makedirs(SHADOW, exist_ok=True); os.makedirs(CUT, exist_ok=True)
for _f in os.listdir(FULL):
    if _f.endswith(".png") and not os.path.exists(os.path.join(CUT, _f)):
        _im = Image.open(os.path.join(FULL, _f)); _im.thumbnail((MAXPX, MAXPX), Image.LANCZOS); _im.save(os.path.join(CUT, _f), optimize=True)

YEAR = 2027
SUNDAY = len(sys.argv) > 1 and sys.argv[1].lower().startswith("sun")
WSTART = 6 if SUNDAY else 0
NAME = "Code & Cozy"

# ---------------------------------------------------------------- page, fonts, colours
W, H = 834, 1112                     # 3:4, iPad
ML, CR = 40, 790                     # content left / right edge (tabs live in the right margin)
CW = CR - ML

# Open-licence fonts (SIL OFL) from fonts/, made static by build_it_fonts.py
FONTS = os.path.join(ROOT, "fonts")
for _name, _file in (("Disp", "PlayfairDisplay-Regular"), ("DispI", "PlayfairDisplay-Italic"), ("DispB", "PlayfairDisplay-Bold"), ("GeoI", "PlayfairDisplay-Italic"),
                     ("Sans", "DMSans-Regular"), ("SansM", "DMSans-Medium"), ("SansB", "DMSans-SemiBold"), ("SansI", "DMSans-Italic"),
                     ("Num", "Jost-ExtraLight"), ("Script", "PinyonScript-Regular")):
    pdfmetrics.registerFont(TTFont(_name, os.path.join(FONTS, _file + ".ttf")))

PAPER = HexColor("#FAF6EA"); CARD = HexColor("#FFFDF7"); INK = HexColor("#38362E"); MUTED = HexColor("#8C8672")
RULE = HexColor("#DCD3BC"); RULE2 = HexColor("#EBE4D1")
SAGE = HexColor("#6B7F58"); SAGE_D = HexColor("#4C5E40"); SAGE_L = HexColor("#DDE5CC"); SAGE_XL = HexColor("#EFF3E3")
TERRA = HexColor("#C0694A"); TERRA_L = HexColor("#F5DDCF"); TERRA_XL = HexColor("#FBEFE6")
GOLD = HexColor("#B58B3A"); GOLD_L = HexColor("#F2E4BF"); GOLD_XL = HexColor("#FAF2DC")
BROWN = HexColor("#7A5638"); TAUPE = HexColor("#9C8B73"); TAUPE_L = HexColor("#EAE2D1")
WHITE = HexColor("#FFFFFF")
MOODS = [HexColor(h) for h in ("#C98468", "#E3AE80", "#E8D08A", "#B9C792", "#84A06B")]

# section -> (strong, light)
SEC = {"plan": (BROWN, TAUPE_L), "work": (SAGE, SAGE_L), "health": (TERRA, TERRA_L), "life": (GOLD, GOLD_L), "notes": (TAUPE, TAUPE_L)}

MONTHS = [calendar.month_name[i] for i in range(1, 13)]
DAYS = ([calendar.day_name[i] for i in range(7)] if not SUNDAY else [calendar.day_name[6]] + [calendar.day_name[i] for i in range(6)])
D1 = dt.date(YEAR, 1, 1)
W1 = D1 - dt.timedelta(days=(D1.weekday() - WSTART) % 7)           # first day of week 1 (may be in Dec of the previous year)
DEC31 = dt.date(YEAR, 12, 31)
NWEEKS = ((DEC31 - W1).days // 7) + 1


def week_of(d):
    return (d - W1).days // 7 + 1


def week_start(n):
    return W1 + dt.timedelta(days=7 * (n - 1))


def in_year(d):
    return d.year == YEAR


def dkey(d):
    return f"d{d.month:02d}{d.day:02d}"


def Y(t):
    return H - t


# ---------------------------------------------------------------- stickers
_SIZE = {}


def sticker_path(name, shadow=False):
    return os.path.join(SHADOW if shadow else CUT, name + ".png")


def make_shadow(name):
    out = sticker_path(name, True)
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(sticker_path(name)):
        return
    im = Image.open(sticker_path(name)).convert("RGBA"); pad = 40
    base = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    a = Image.new("L", base.size, 0); a.paste(im.getchannel("A"), (pad, pad + 10))
    a = a.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.30))
    sh = Image.new("RGBA", base.size, (92, 64, 40, 0)); sh.putalpha(a)
    base = Image.alpha_composite(base, sh); base.alpha_composite(im, (pad, pad)); base.save(out)


def stk(c, name, cx, ct, h, rot=0, shadow=False, maxw=None):
    """Draw sticker `name` centred on (cx, ct[top-based]) with height h."""
    if name not in _SIZE:
        _SIZE[name] = Image.open(sticker_path(name)).size
    iw, ih = _SIZE[name]
    if maxw and iw * h / ih > maxw:
        h = maxw * ih / iw
    sc = h / ih; w = iw * sc
    c.saveState(); c.translate(cx, Y(ct)); c.rotate(rot)
    if shadow:
        make_shadow(name); pad = 40 * sc
        c.drawImage(sticker_path(name, True), -w / 2 - pad, -h / 2 - pad, w + 2 * pad, h + 2 * pad, mask="auto")
    else:
        c.drawImage(sticker_path(name), -w / 2, -h / 2, w, h, mask="auto")
    c.restoreState()
    return w, h


WORK = [f"work_{i}" for i in range(1, 9)]
WEEKDAY_STK = [["dev_8", "work_7", "work_1"], ["dev_2", "work_2", "work_3"], ["dev_6", "dev_4", "work_5"], ["dev_1", "work_4", "dev_5"], ["dev_3", "work_6", "dev_7"]]
SAT = ["fit_1", "travel_6", "social_5", "fit_3", "home_2", "travel_5", "fit_6", "social_8", "home_5", "travel_4", "fit_4", "social_1", "fit_2", "travel_7", "love_5", "home_8"]
SUN = ["cozy_1", "hobby_1", "cozy_3", "hobby_2", "cozy_7", "hobby_6", "hobby_8", "cozy_5", "hobby_5", "cozy_4", "love_7", "cozy_8", "hobby_3", "cozy_2", "social_2", "fit_8"]
SEASON_STK = {1: ["seasons_7"], 2: ["seasons_7"], 3: ["seasons_2"], 4: ["seasons_3", "seasons_2"], 5: ["seasons_3"], 6: ["seasons_4", "seasons_1"], 7: ["seasons_1", "seasons_4"], 8: ["seasons_1"],
              9: ["seasons_5"], 10: ["seasons_6", "seasons_5"], 11: ["seasons_5"], 12: ["seasons_8", "seasons_7"]}
SPECIAL = {(1, 1): "dev_3", (2, 14): "love_3", (10, 31): "seasons_6", (12, 25): "seasons_8", (12, 31): "love_4"}
WEEK_STK = ["dev_2", "work_2", "dev_4", "travel_8", "work_5", "home_1", "dev_6", "hobby_1", "work_3", "social_2", "dev_5", "home_7", "work_4", "dev_8", "travel_2", "hobby_2"]
MONTH_STK = ["seasons_7", "love_3", "seasons_2", "seasons_3", "hobby_8", "seasons_4", "seasons_1", "travel_7", "home_1", "seasons_6", "seasons_5", "seasons_8"]
QUARTER_STK = ["seasons_7", "seasons_3", "seasons_1", "seasons_5"]


def day_sticker(d):
    wi = week_of(d)
    if (d.month, d.day) in SPECIAL:
        return SPECIAL[(d.month, d.day)]
    if d.weekday() < 5:
        pool = WEEKDAY_STK[d.weekday()]; return pool[wi % len(pool)]
    if wi % 4 == 0:                       # every fourth weekend belongs to the season
        pool = SEASON_STK[d.month]; return pool[(wi // 4) % len(pool)]
    return SAT[wi % len(SAT)] if d.weekday() == 5 else SUN[wi % len(SUN)]


# ---------------------------------------------------------------- primitives
def txt(c, s, x, t, font="Sans", size=10, col=INK, al="l", tr=0):
    c.setFillColor(col); c.setFont(font, size)
    w = stringWidth(s, font, size) + tr * max(len(s) - 1, 0)
    if al == "c":
        x -= w / 2
    elif al == "r":
        x -= w
    if tr:
        o = c.beginText(x, Y(t)); o.setFont(font, size); o.setCharSpace(tr); o.setFillColor(col); o.textOut(s); o.setCharSpace(0); c.drawText(o)
    else:
        c.drawString(x, Y(t), s)
    return w


def wrap(s, font, size, width):
    out, line = [], ""
    for w_ in s.split():
        cand = (line + " " + w_).strip()
        if stringWidth(cand, font, size) <= width:
            line = cand
        else:
            out.append(line); line = w_
    return out + [line] if line else out


def rr(c, x, t, w, h, r=8, fill=None, stroke=None, lw=0.8, dash=None):
    c.saveState()
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(lw)
        if dash:
            c.setDash(*dash)
    c.roundRect(x, Y(t) - h, w, h, r, stroke=1 if stroke is not None else 0, fill=1 if fill is not None else 0)
    c.restoreState()


def hline(c, x1, x2, t, col=RULE, lw=0.6, dash=None):
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(lw)
    if dash:
        c.setDash(*dash)
    c.line(x1, Y(t), x2, Y(t)); c.restoreState()


def vline(c, x, t1, t2, col=RULE, lw=0.6, dash=None):
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(lw)
    if dash:
        c.setDash(*dash)
    c.line(x, Y(t1), x, Y(t2)); c.restoreState()


def circ(c, cx, ct, r, stroke=None, fill=None, lw=0.8):
    c.saveState()
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(lw)
    c.circle(cx, Y(ct), r, stroke=1 if stroke is not None else 0, fill=1 if fill is not None else 0); c.restoreState()


def link(c, dest, x, t, w, h):
    c.linkRect("", dest, (x, Y(t) - h, x + w, Y(t)), relative=0, thickness=0)


def sparkle(c, cx, ct, r, col=GOLD):
    c.saveState(); c.setFillColor(col); p = c.beginPath(); y = Y(ct); k = r * 0.22
    p.moveTo(cx, y + r); p.curveTo(cx + k, y + k, cx + k, y + k, cx + r, y); p.curveTo(cx + k, y - k, cx + k, y - k, cx, y - r)
    p.curveTo(cx - k, y - k, cx - k, y - k, cx - r, y); p.curveTo(cx - k, y + k, cx - k, y + k, cx, y + r)
    c.drawPath(p, stroke=0, fill=1); c.restoreState()


def drop(c, cx, ct, s, col=SAGE, fill=None):
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(0.9)
    if fill is not None:
        c.setFillColor(fill)
    y = Y(ct); p = c.beginPath(); p.moveTo(cx, y + s)
    p.curveTo(cx + .2 * s, y + .55 * s, cx + .7 * s, y + .15 * s, cx + .7 * s, y - .3 * s)
    p.curveTo(cx + .7 * s, y - .72 * s, cx + .3 * s, y - s, cx, y - s)
    p.curveTo(cx - .3 * s, y - s, cx - .7 * s, y - .72 * s, cx - .7 * s, y - .3 * s)
    p.curveTo(cx - .7 * s, y + .15 * s, cx - .2 * s, y + .55 * s, cx, y + s)
    c.drawPath(p, stroke=1, fill=1 if fill is not None else 0); c.restoreState()


def face(c, cx, ct, level, r=9.5, col=MUTED, fill=None):
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(0.9)
    if fill is not None:
        c.setFillColor(fill)
    y = Y(ct); c.circle(cx, y, r, stroke=1, fill=1 if fill is not None else 0)
    c.setFillColor(col); c.circle(cx - r * .36, y + r * .2, 0.9, stroke=0, fill=1); c.circle(cx + r * .36, y + r * .2, 0.9, stroke=0, fill=1)
    k = [r * .42, r * .2, 0, -r * .26, -r * .46][level]
    p = c.beginPath(); my = y - r * .38; p.moveTo(cx - r * .38, my); p.curveTo(cx - r * .2, my - k * 1.3, cx + r * .2, my - k * 1.3, cx + r * .38, my)
    c.drawPath(p, stroke=1, fill=0); c.restoreState()


def battery(c, x, ct, w, h, col=SAGE, n=5):
    rr(c, x, ct, w, h, 3, stroke=col, lw=0.9); rr(c, x + w, ct + h * .3, 3, h * .4, 1, fill=col)
    sw = (w - 6 - (n - 1) * 2) / n
    for i in range(n):
        rr(c, x + 3 + i * (sw + 2), ct + 3, sw, h - 6, 1, stroke=col, lw=0.5)


def tomato(c, cx, ct, r=8.5, col=TERRA):
    circ(c, cx, ct, r, stroke=col, lw=0.9)
    c.saveState(); c.setStrokeColor(SAGE); c.setLineWidth(0.9); y = Y(ct) + r
    for dx in (-1, 1):
        p = c.beginPath(); p.moveTo(cx, y - 1); p.curveTo(cx + dx * 3, y + 4, cx + dx * 6, y + 3, cx + dx * 6.5, y + 1); c.drawPath(p, stroke=1, fill=0)
    c.restoreState()


def chevron(c, cx, ct, d=1, s=4.5, col=MUTED):
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(1.3); c.setLineCap(1); y = Y(ct)
    p = c.beginPath(); p.moveTo(cx - d * s * .5, y + s); p.lineTo(cx + d * s * .5, y); p.lineTo(cx - d * s * .5, y - s); c.drawPath(p, stroke=1, fill=0); c.restoreState()


def progress(c, x, ct, w, h=6, n=10, col=SAGE):
    gw = (w - (n - 1) * 2) / n
    for i in range(n):
        rr(c, x + i * (gw + 2), ct, gw, h, 1.5, stroke=col, lw=0.5)


def dotted(c, x1, x2, t, col=RULE):
    hline(c, x1, x2, t, col=col, lw=0.7, dash=(1.2, 3))


def lines(c, x, t, w, n, gap, col=RULE, solid=False):
    for i in range(n):
        if solid:
            hline(c, x, x + w, t + gap * (i + 1), col=col, lw=0.5)
        else:
            dotted(c, x, x + w, t + gap * (i + 1), col)


def checks(c, x, t, w, n, gap, col=SAGE, r=5.2):
    for i in range(n):
        yy = t + gap * (i + 1)
        circ(c, x + r + 1, yy - 4.2, r, stroke=col, lw=0.9); dotted(c, x + 2 * r + 8, x + w, yy)


def card(c, x, t, w, h, title=None, col=SAGE, fill=CARD, r=10, num=None):
    rr(c, x, t, w, h, r, fill=fill, stroke=RULE, lw=0.7)
    if title:
        circ(c, x + 13, t + 15.5, 2.6, fill=col)
        txt(c, title.upper(), x + 21, t + 19, "SansB", 7.6, col, tr=1.15)


def numbered(c, x, t, w, n, gap, col=SAGE):
    for i in range(n):
        yy = t + gap * (i + 1)
        circ(c, x + 8, yy - 5, 8, stroke=col, lw=0.9); txt(c, str(i + 1), x + 8, yy - 2.6, "SansB", 8.4, col, "c")
        dotted(c, x + 24, x + w, yy)


def chip(c, s, x, t, w, h, col, fill, dest=None, size=7.8, font="SansB", tr=0.8):
    rr(c, x, t, w, h, h / 2, fill=fill)
    txt(c, s, x + w / 2, t + h / 2 + size * .34, font, size, col, "c", tr)
    if dest:
        link(c, dest, x, t, w, h)


def table(c, x, t, w, cols, nrows, row_h, col, head_h=24, light=None, first_label=True):
    """cols = [(label, weight)]; draws header + nrows dotted-row table, returns the x position of each column."""
    tot = sum(wt for _, wt in cols); xs = [x]
    rr(c, x, t, w, head_h + nrows * row_h, 10, fill=CARD, stroke=RULE, lw=0.7)
    c.saveState(); p = c.beginPath(); p.roundRect(x, Y(t) - head_h, w, head_h, 10); c.clipPath(p, stroke=0, fill=0)
    c.setFillColor(light or SAGE_L); c.rect(x, Y(t) - head_h, w, head_h, stroke=0, fill=1); c.restoreState()
    rr(c, x, t, w, head_h, 0, fill=None)  # keep stroke crisp
    rr(c, x, t, w, head_h + nrows * row_h, 10, stroke=RULE, lw=0.7)
    cx = x
    for i, (lab, wt) in enumerate(cols):
        cw_ = w * wt / tot
        txt(c, lab.upper(), cx + 9, t + head_h / 2 + 2.6, "SansB", 7.2, col, tr=0.9)
        cx += cw_; xs.append(cx)
        if i < len(cols) - 1:
            vline(c, cx, t + 5, t + head_h + nrows * row_h - 4, RULE2, 0.6)
    for r_ in range(nrows):
        hline(c, x + 8, x + w - 8, t + head_h + (r_ + 1) * row_h, RULE2, 0.6)
    return xs


# ---------------------------------------------------------------- shared chrome
TABS = [("HOME", "home", "#5B5546"), ("YEAR", "year", "#7A5638"), ("MONTH", None, "#B58B3A"), ("WEEK", None, "#7C9166"),
        ("WORK", "work", "#5F7350"), ("HEALTH", "health", "#C0694A"), ("LIFE", "life", "#C98B4E"), ("NOTES", "notes", "#8E7E66")]


def tabs(c, ctx, active):
    n = len(TABS); h = 112; gap = 8; top = (H - (n * h + (n - 1) * gap)) / 2
    for i, (lab, dest, hexcol) in enumerate(TABS):
        col = HexColor(hexcol); t = top + i * (h + gap)
        if lab == "MONTH":
            dest = f"m{ctx.get('month', 1):02d}"
        if lab == "WEEK":
            dest = f"w{ctx.get('week', 1):02d}"
        on = (lab == active)
        w = 31 if on else 21
        rr(c, W - w, t, w + 8, h, 8, fill=col)
        c.saveState(); c.translate(W - w / 2 - 1 + (2 if on else 0), Y(t) - h / 2); c.rotate(-90)
        c.setFillColor(WHITE); c.setFont("SansB", 8.4); o = c.beginText(-stringWidth(lab, "SansB", 8.4) / 2 - 0.4 * (len(lab) - 1), -3); o.setFont("SansB", 8.4); o.setCharSpace(1.0); o.setFillColor(WHITE); o.textOut(lab); o.setCharSpace(0); c.drawText(o)
        c.restoreState()
        link(c, dest, W - 32, t, 40, h)


def month_strip(c, x, t, active=None):
    for i in range(12):
        cx = x + i * 21 + 9
        on = (i + 1 == active)
        if on:
            circ(c, cx, t + 8, 9, fill=SAGE)
        txt(c, MONTHS[i][0], cx, t + 11.3, "SansB", 8.5, WHITE if on else MUTED, "c")
        link(c, f"m{i + 1:02d}", cx - 10, t - 2, 20, 20)


def arrows(c, x_right, t, prev=None, nxt=None):
    cx_p, cx_n = x_right - 39, x_right - 11
    for cx, dest, d in ((cx_p, prev, -1), (cx_n, nxt, 1)):
        circ(c, cx, t + 11, 11, stroke=RULE, fill=CARD, lw=0.8)
        chevron(c, cx + (-.5 if d < 0 else .5), t + 11, d, 3.6, MUTED if dest else RULE)
        if dest:
            link(c, dest, cx - 12, t - 1, 24, 24)


def paper(c, dots=False):
    c.setFillColor(PAPER); c.rect(0, 0, W, H, stroke=0, fill=1)
    if dots:
        c.setFillColor(HexColor("#CDC2A4"))
        for yy in range(60, H - 40, 24):
            for xx in range(48, int(W - 50), 24):
                c.circle(xx, yy, 0.95, stroke=0, fill=1)


class Doc:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=(W, H), pageCompression=1)
        self.c.setTitle(f"{NAME} Daily Planner {YEAR}"); self.c.setAuthor(NAME); self.c.setSubject("Hyperlinked daily planner for GoodNotes")
        self.n = 0

    def page(self, name, outline=None, level=0, active=None, ctx=None, dots=False, chrome=True):
        c = self.c; self.n += 1
        c.bookmarkPage(name)
        if outline:
            c.addOutlineEntry(outline, name, level, closed=True)
        paper(c, dots)
        if chrome:
            tabs(c, ctx or {}, active)
        return c

    def end(self):
        self.c.showPage()


def title_block(c, title, sub=None, col=SAGE, t=86, size=46, sticker=None, st_h=118):
    txt(c, title, ML, t, "Disp", size, INK)
    if sub:
        txt(c, sub.upper(), ML + 2, t + 24, "SansB", 8.6, col, tr=1.7)
    if sticker:
        stk(c, sticker, CR - 78, 82, st_h, maxw=190, shadow=False)


# ---------------------------------------------------------------- cover + home
def cover(d):
    c = d.page("cover", None, chrome=False)
    # arch window
    ax, aw, at, ah = 112, W - 224, 226, 676
    c.saveState(); c.setFillColor(SAGE_L); c.setStrokeColor(SAGE); c.setLineWidth(1)
    p = c.beginPath(); r = aw / 2
    p.moveTo(ax, Y(at + ah)); p.lineTo(ax, Y(at + r)); p.arcTo(ax, Y(at + 2 * r), ax + aw, Y(at), 180, -180); p.lineTo(ax + aw, Y(at + ah)); p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setLineWidth(0.9); c.setStrokeColor(SAGE); c.setDash(2, 4)
    p = c.beginPath(); o = 14; r2 = r - o
    p.moveTo(ax + o, Y(at + ah - o)); p.lineTo(ax + o, Y(at + r)); p.arcTo(ax + o, Y(at + o + 2 * r2), ax + aw - o, Y(at + o), 180, -180); p.lineTo(ax + aw - o, Y(at + ah - o)); p.close()
    c.drawPath(p, stroke=1, fill=0); c.restoreState()
    for x, t, r_, col in ((90, 150, 9, GOLD), (736, 188, 12, GOLD), (60, 520, 7, TERRA), (770, 560, 8, GOLD), (120, 960, 10, GOLD), (718, 940, 7, TERRA)):
        sparkle(c, x, t, r_, col)
    txt(c, "Code", W / 2, 128, "Disp", 92, INK, "c")
    txt(c, "& Cozy", W / 2 + 2, 184, "DispI", 64, TERRA, "c")
    txt(c, "DAILY PLANNER  ·  " + str(YEAR), W / 2, 214, "SansB", 11, SAGE_D, "c", 4.2)
    stk(c, "work_3", W / 2, 470, 236, shadow=True, maxw=390)
    stk(c, "work_7", 214, 352, 182, rot=-6, shadow=True)
    stk(c, "cozy_2", 636, 352, 176, rot=6, shadow=True)
    stk(c, "fit_2", 230, 626, 214, rot=-4, shadow=True)
    stk(c, "cozy_4", 602, 612, 178, rot=4, shadow=True, maxw=270)
    stk(c, "fit_6", 262, 804, 176, rot=-3, shadow=True)
    stk(c, "cozy_6", 566, 820, 142, rot=3, shadow=True, maxw=270)
    txt(c, "for the girl who ships code", W / 2, 962, "GeoI", 23, INK, "c")
    txt(c, "and takes very serious naps", W / 2, 992, "GeoI", 23, INK, "c")
    labels = ("365 DAILY PAGES", "HYPERLINKED", "WORK · HEALTH · LIFE")
    ws = [stringWidth(s, "SansB", 7.8) + 26 for s in labels]; x = W / 2 - (sum(ws) + 12 * 2) / 2
    for s, w_ in zip(labels, ws):
        chip(c, s, x, 1030, w_, 22, SAGE_D, SAGE_L, "home", 7.8); x += w_ + 12
    txt(c, "GoodNotes · iPad · tap anywhere to start", W / 2, 1078, "SansI", 9.5, MUTED, "c")
    link(c, "home", 0, 0, W, H)
    d.end()


def home(d):
    c = d.page("home", "Home", 0, active="HOME", ctx={})
    title_block(c, "Hello, 2027", "tap anything — everything is linked", BROWN, sticker="cozy_1", st_h=120)
    # months
    t0 = 196
    txt(c, "JUMP TO A MONTH", ML, t0, "SansB", 8, TAUPE, tr=1.4)
    cw = (CW - 5 * 8) / 6
    for i in range(12):
        x = ML + (i % 6) * (cw + 8); t = t0 + 10 + (i // 6) * 38
        chip(c, MONTHS[i][:3].upper(), x, t, cw, 30, SAGE_D, SAGE_L if i % 2 == 0 else SAGE_XL, f"m{i + 1:02d}", 10, "SansB", 1.4)
    # quarters
    t1 = t0 + 100
    txt(c, "QUARTERS", ML, t1, "SansB", 8, TAUPE, tr=1.4)
    for i in range(4):
        x = ML + i * (cw * 1.5 + 8); chip(c, f"Q{i + 1}  ·  {MONTHS[i * 3][:3]}–{MONTHS[i * 3 + 2][:3]}".upper(), x, t1 + 10, cw * 1.5, 30, BROWN, TAUPE_L, f"q{i + 1}", 8.4, "SansB", 0.8)
    # section cards
    t2 = t1 + 64
    cards = [("Year", "plan", "cozy_3", [("Overview", "year"), ("Goals", "goals"), ("In pixels", "pixels")], "Big picture, goals and the 365 dots of your year."),
             ("Weeks", "plan", "work_6", [("W1", "w01"), ("W14", f"w{week_of(dt.date(YEAR, 4, 1)):02d}"), ("W27", f"w{week_of(dt.date(YEAR, 7, 1)):02d}"), ("W40", f"w{week_of(dt.date(YEAR, 10, 1)):02d}")], "Sprint-style weekly spreads, 53 of them."),
             ("Work hub", "work", "work_2", [("Projects", "w_proj"), ("Sprint", "w_sprint"), ("1:1", "w_one"), ("Brag doc", "w_brag")], "Projects, sprints, meetings, brag doc, learning."),
             ("Health", "health", "fit_1", [("Habits", "h01"), ("Workout", "h_work"), ("Meals", "h_meal"), ("Sleep", "h_sleep")], "Habits, workouts, meals, sleep and water."),
             ("Life", "life", "cozy_8", [("Reading", "l_read"), ("Budget", "l_budget"), ("Travel", "l_travel"), ("Self-care", "l_care")], "Books, games, money, trips and cosy rituals."),
             ("Notes", "notes", "cozy_2", [("Lined", "n_lined1"), ("Dotted", "n_dot1"), ("Grid", "n_grid1"), ("Cornell", "n_corn1")], "Blank pages for brain dumps and ideas.")]
    cw2 = (CW - 14) / 2; chh = 214
    for i, (nm, sec, st, chips_, desc) in enumerate(cards):
        x = ML + (i % 2) * (cw2 + 14); t = t2 + (i // 2) * (chh + 14); col, lt = SEC[sec]
        rr(c, x, t, cw2, chh, 14, fill=CARD, stroke=RULE)
        rr(c, x, t, 7, chh, 3, fill=col)
        txt(c, nm, x + 24, t + 44, "Disp", 30, INK)
        for k, ln in enumerate(wrap(desc, "Sans", 9.5, cw2 - 190)):
            txt(c, ln, x + 24, t + 68 + k * 13, "Sans", 9.5, MUTED)
        stk(c, st, x + cw2 - 78, t + 70, 100, maxw=130)
        for k, (lab, dest) in enumerate(chips_):
            cx_ = x + 24 + (k % 2) * ((cw2 - 60) / 2 + 2); cy_ = t + 124 + (k // 2) * 38
            chip(c, lab.upper(), cx_, cy_, (cw2 - 60) / 2 - 6, 30, col, lt, dest, 8.4, "SansB", 0.9)
    d.end()


def start_here(d):
    c = d.page("start", "Start here", 0, active="HOME", ctx={})
    title_block(c, "Start here", "how this planner works", BROWN, sticker="work_1", st_h=116)
    tips = [("Tabs are links", "The coloured tabs on the right edge jump anywhere. MONTH and WEEK always jump to the month or week you are in."),
            ("Dates are links", "Tap a day in any month or week to open its daily page. The 12 letters at the top jump between months."),
            ("Write with Apple Pencil", "Every page is a real PDF with room to write. Use the lasso tool to move things; duplicate pages for extra copies."),
            ("Stickers", "Drop the PNG stickers from the sticker pack onto any page. Layer them on the daily page header, the weekend or a big win."),
            ("Daily page, top to bottom", "Top 3 -> to-do -> schedule -> notes -> focus blocks -> life check-in. Close the day with the shutdown ritual."),
            ("Work hub", "Projects, sprint board, 1:1s, meeting notes, brag document, learning tracker, bug log and career roadmap."),
            ("Duplicate templates", "Hub pages are templates. In GoodNotes: page thumbnail -> Duplicate Page to keep adding."),
            ("Make it yours", "Colour the pixels, highlight deadlines in terracotta, keep one sticker as your word of the year.")]
    for i, (h_, b_) in enumerate(tips):
        x = ML + (i % 2) * (CW / 2 + 7); t = 196 + (i // 2) * 216; w_ = CW / 2 - 7
        rr(c, x, t, w_, 202, 14, fill=CARD, stroke=RULE)
        circ(c, x + 30, t + 34, 17, fill=SAGE_L if i % 2 == 0 else TERRA_L)
        txt(c, str(i + 1), x + 30, t + 40.5, "DispB", 17, SAGE_D if i % 2 == 0 else TERRA, "c")
        txt(c, h_, x + 58, t + 40, "Disp", 20, INK)
        for k, ln in enumerate(wrap(b_, "Sans", 10, w_ - 44)):
            txt(c, ln, x + 22, t + 78 + k * 15, "Sans", 10, MUTED)
    d.end()


# ---------------------------------------------------------------- year level
def year_overview(d):
    c = d.page("year", "Year overview", 0, active="YEAR", ctx={})
    title_block(c, f"{YEAR}", "year at a glance", BROWN, sticker="fit_6", st_h=104)
    cal = calendar.Calendar(WSTART); cw3 = (CW - 28) / 3; ch = 209; t0 = 188
    hdr = [calendar.day_name[(WSTART + i) % 7][0] for i in range(7)]
    for m in range(1, 13):
        x = ML + ((m - 1) % 3) * (cw3 + 14); t = t0 + ((m - 1) // 3) * (ch + 10)
        rr(c, x, t, cw3, ch, 12, fill=CARD, stroke=RULE)
        txt(c, MONTHS[m - 1], x + 14, t + 25, "Disp", 17, INK); link(c, f"m{m:02d}", x, t, cw3, 34)
        cw_ = (cw3 - 20) / 7
        for i, hd in enumerate(hdr):
            txt(c, hd, x + 10 + i * cw_ + cw_ / 2, t + 48, "SansB", 6.8, SAGE, "c")
        for r, wk in enumerate(cal.monthdatescalendar(YEAR, m)):
            for i, dd in enumerate(wk):
                if dd.month != m:
                    continue
                cx = x + 10 + i * cw_ + cw_ / 2; ty = t + 70 + r * 22
                wend = dd.weekday() >= 5
                txt(c, str(dd.day), cx, ty, "Sans", 8.2, TERRA if wend else INK, "c")
                link(c, dkey(dd), cx - cw_ / 2, ty - 12, cw_, 20)
    d.end()


def goals(d):
    c = d.page("goals", "Year goals", 1, active="YEAR", ctx={})
    title_block(c, "Goals for 2027", "five circles, three goals each", BROWN, sticker="work_4", st_h=108)
    areas = [("Career", SAGE, SAGE_XL, "ship, grow, get paid what I am worth"), ("Health", TERRA, TERRA_XL, "strong body, quiet mind"),
             ("Money", GOLD, GOLD_XL, "save, invest, stay calm"), ("Learning", SAGE, SAGE_XL, "one skill I can show for it"),
             ("Life", TERRA, TERRA_XL, "people, places, play")]
    cw2 = (CW - 14) / 2; chh = 262; t0 = 186
    for i, (nm, col, lt, sub) in enumerate(areas):
        x = ML + (i % 2) * (cw2 + 14); t = t0 + (i // 2) * (chh + 12)
        rr(c, x, t, cw2, chh, 14, fill=CARD, stroke=RULE); rr(c, x, t, cw2, 40, 14, fill=lt); rr(c, x, t + 24, cw2, 16, 0, fill=lt)
        txt(c, nm, x + 16, t + 28, "Disp", 21, INK); txt(c, sub, x + cw2 - 14, t + 27, "SansI", 8.6, MUTED, "r")
        checks(c, x + 14, t + 40, cw2 - 28, 3, 34, col)
        txt(c, "WHY IT MATTERS", x + 16, t + 160, "SansB", 7.4, col, tr=1.1); lines(c, x + 14, t + 160, cw2 - 28, 2, 24)
        txt(c, "PROGRESS", x + 16, t + 238, "SansB", 7.4, col, tr=1.1); progress(c, x + 80, t + 232, cw2 - 100, 8, 10, col)
    x = ML + (cw2 + 14); t = t0 + 2 * (chh + 12)
    rr(c, x, t, cw2, chh, 14, fill=SAGE_L); circ(c, x + cw2 / 2, t + 120, 82, stroke=SAGE, fill=CARD, lw=1)
    circ(c, x + cw2 / 2, t + 120, 74, stroke=SAGE, lw=0.5)
    txt(c, "WORD OF THE YEAR", x + cw2 / 2, t + 36, "SansB", 8, SAGE_D, "c", 1.8)
    dotted(c, x + cw2 / 2 - 50, x + cw2 / 2 + 50, t + 126, SAGE)
    txt(c, "my vibe for 2027", x + cw2 / 2, t + 240, "Script", 22, SAGE_D, "c")
    d.end()


def pixels(d):
    c = d.page("pixels", "Year in pixels", 1, active="YEAR", ctx={})
    title_block(c, "Year in pixels", "colour one dot a day  ·  tap a dot to open the day", BROWN, sticker="cozy_6", st_h=96)
    lab = ["awful", "meh", "okay", "good", "great"]; x = ML
    for i in range(5):
        circ(c, x + 7, 172, 7, fill=MOODS[i]); txt(c, lab[i], x + 18, 175.5, "Sans", 8.5, MUTED); x += 76
    t0 = 218; colw = (CW - 28) / 12; rh = (1086 - t0) / 32
    for m in range(12):
        cx = ML + 28 + m * colw + colw / 2
        txt(c, MONTHS[m][:3].upper(), cx, t0 - 8, "SansB", 7.6, SAGE_D, "c", 0.8); link(c, f"m{m + 1:02d}", cx - colw / 2, t0 - 20, colw, 16)
    for day in range(1, 32):
        ty = t0 + (day - 0.5) * rh + rh / 2 - 6
        txt(c, str(day), ML + 20, ty + 3, "Sans", 7.4, MUTED, "r")
        for m in range(12):
            if day <= calendar.monthrange(YEAR, m + 1)[1]:
                cx = ML + 28 + m * colw + colw / 2; dd = dt.date(YEAR, m + 1, day)
                circ(c, cx, ty, 8.2, stroke=RULE, fill=TERRA_XL if dd.weekday() >= 5 else CARD, lw=0.8); link(c, dkey(dd), cx - 9, ty - 9, 18, 18)
    d.end()


def quarter(d, q):
    m0 = (q - 1) * 3 + 1
    c = d.page(f"q{q}", f"Q{q} · {MONTHS[m0 - 1][:3]}–{MONTHS[m0 + 1][:3]}", 1, active="YEAR", ctx={"month": m0, "week": week_of(dt.date(YEAR, m0, 1))})
    txt(c, "Q", ML, 96, "Disp", 62, INK); txt(c, str(q), ML + stringWidth("Q", "Disp", 62) + 4, 96, "Num", 66, SAGE_D); txt(c, f"{MONTHS[m0 - 1]} – {MONTHS[m0 + 1]} {YEAR}".upper(), ML + 100, 80, "SansB", 9, BROWN, tr=1.6)
    for k in range(3):
        chip(c, MONTHS[m0 - 1 + k][:3].upper(), ML + 100 + k * 76, 92, 68, 24, SAGE_D, SAGE_L, f"m{m0 + k:02d}", 8.6)
    stk(c, QUARTER_STK[q - 1], CR - 74, 80, 112, maxw=190)
    arrows(c, CR, 16, f"q{q - 1}" if q > 1 else None, f"q{q + 1}" if q < 4 else None)
    t = 176
    for o in range(3):
        rr(c, ML, t, CW, 150, 12, fill=CARD, stroke=RULE); rr(c, ML, t, 6, 150, 3, fill=SAGE)
        txt(c, f"OBJECTIVE {o + 1}", ML + 20, t + 22, "SansB", 7.8, SAGE, tr=1.4); dotted(c, ML + 114, CR - 16, t + 22, SAGE_L)
        for k in range(3):
            yy = t + 52 + k * 31; circ(c, ML + 28, yy - 4.4, 5.2, stroke=SAGE, lw=0.9)
            txt(c, f"KR{k + 1}", ML + 40, yy - 1.5, "SansB", 7.2, MUTED, tr=0.6); dotted(c, ML + 68, ML + 520, yy)
            progress(c, ML + 540, yy - 9, CW - 540 - 14, 8, 10, SAGE)
        t += 158
    t = 656
    txt(c, "ROADMAP  ·  13 WEEKS", ML, t, "SansB", 8, BROWN, tr=1.4)
    first = week_of(dt.date(YEAR, m0, 1)); bw = (CW - 12 * 5) / 13
    for k in range(13):
        wn = first + k
        if wn > NWEEKS:
            break
        x = ML + k * (bw + 5); rr(c, x, t + 10, bw, 62, 9, fill=CARD, stroke=RULE)
        txt(c, f"W{wn}", x + bw / 2, t + 28, "SansB", 8, SAGE, "c"); txt(c, week_start(wn).strftime("%b %d").replace(" 0", " "), x + bw / 2, t + 40, "Sans", 6.6, MUTED, "c")
        link(c, f"w{wn:02d}", x, t + 10, bw, 62)
    t = 752; cw3 = (CW - 20) / 3
    for i, (ti, col) in enumerate((("Skills I am levelling up", SAGE), ("Wins & brag-doc entries", GOLD), ("Quarter review", TERRA))):
        x = ML + i * (cw3 + 10); card(c, x, t, cw3, 332, ti, col); lines(c, x + 14, t + 30, cw3 - 28, 10, 29)
    d.end()


# ---------------------------------------------------------------- months
def month_pages(d, m):
    first = dt.date(YEAR, m, 1); wk = week_of(first)
    ctx = {"month": m, "week": wk}
    c = d.page(f"m{m:02d}", MONTHS[m - 1], 1, active="MONTH", ctx=ctx)
    txt(c, MONTHS[m - 1], ML, 100, "Disp", 62, INK); txt(c, str(YEAR), ML + 4, 124, "SansB", 9, BROWN, tr=3)
    stk(c, MONTH_STK[m - 1], CR - 84, 90, 124, maxw=200)
    arrows(c, CR, 16, f"m{m - 1:02d}" if m > 1 else None, f"m{m + 1:02d}" if m < 12 else None)
    month_strip(c, ML, 18, m)
    chip(c, "REVIEW →", ML + 258, 18, 74, 20, TERRA, TERRA_L, f"m{m:02d}r", 7.4)
    chip(c, "HABITS →", ML + 338, 18, 74, 20, SAGE_D, SAGE_L, f"h{m:02d}", 7.4)
    chip(c, f"Q{(m - 1) // 3 + 1} →", ML + 418, 18, 50, 20, BROWN, TAUPE_L, f"q{(m - 1) // 3 + 1}", 7.4)
    cal = calendar.Calendar(WSTART); weeks = cal.monthdatescalendar(YEAR, m)
    gx = ML + 26; gw = CW - 26; cwd = gw / 7; t0 = 178
    for i in range(7):
        txt(c, DAYS[i][:3].upper(), gx + i * cwd + cwd / 2, t0 + 12, "SansB", 7.8, TERRA if (i >= 5 if not SUNDAY else i in (0, 6)) else SAGE, "c", 1.2)
    nr = len(weeks); rh = (808 - (t0 + 20)) / nr; gt = t0 + 20
    rr(c, gx, gt, gw, rh * nr, 10, fill=CARD, stroke=RULE, lw=0.7)
    for r, wkd in enumerate(weeks):
        wn = week_of(wkd[0]); ty = gt + r * rh
        if 1 <= wn <= NWEEKS:
            txt(c, f"W{wn}", ML + 13, ty + rh / 2 + 3, "SansB", 7.4, SAGE, "c"); link(c, f"w{wn:02d}", ML, ty, 26, rh)
        for i, dd in enumerate(wkd):
            x = gx + i * cwd
            if (dd.weekday() >= 5) and dd.month == m:
                c.saveState(); c.setFillColor(TERRA_XL); c.rect(x + 0.5, Y(ty) - rh + 0.5, cwd - 1, rh - 1, stroke=0, fill=1); c.restoreState()
            if dd.month == m:
                txt(c, str(dd.day), x + 8, ty + 17, "Sans", 11, INK); link(c, dkey(dd), x, ty, cwd, rh)
            else:
                txt(c, str(dd.day), x + 8, ty + 17, "Sans", 9, RULE)
    for r in range(1, nr):
        hline(c, gx, gx + gw, gt + r * rh, RULE2, 0.6)
    for i in range(1, 7):
        vline(c, gx + i * cwd, gt, gt + rh * nr, RULE2, 0.6)
    # bottom
    t = 824; cw3 = (CW - 20) / 3
    card(c, ML, t, cw3, 168, "Month focus", SAGE); numbered(c, ML + 14, t + 24, cw3 - 28, 3, 30, SAGE); txt(c, "WORD", ML + 16, t + 146, "SansB", 7.2, MUTED, tr=1); dotted(c, ML + 50, ML + cw3 - 14, t + 146)
    card(c, ML + cw3 + 10, t, cw3, 168, "Deadlines & events", TERRA); lines(c, ML + cw3 + 24, t + 22, cw3 - 28, 5, 28)
    card(c, ML + 2 * (cw3 + 10), t, cw3, 168, "Habits to build", GOLD); checks(c, ML + 2 * (cw3 + 10) + 14, t + 24, cw3 - 28, 5, 28, GOLD)
    rr(c, ML, 1004, CW, 80, 12, fill=SAGE_XL, stroke=SAGE_L)
    txt(c, "this month's mantra", ML + 18, 1030, "Script", 21, SAGE_D); dotted(c, ML + 18, CR - 18, 1056, SAGE); dotted(c, ML + 18, CR - 18, 1074, SAGE)
    d.end()
    # review page
    c = d.page(f"m{m:02d}r", None, 1, active="MONTH", ctx=ctx)
    txt(c, MONTHS[m - 1], ML, 96, "Disp", 46, INK); txt(c, "REVIEW & RESET", ML + 4, 120, "SansB", 9, TERRA, tr=2.4)
    chip(c, "← CALENDAR", ML + 2, 134, 88, 20, SAGE_D, SAGE_L, f"m{m:02d}", 7.4); stk(c, MONTH_STK[(m + 4) % 12], CR - 78, 82, 108, maxw=180)
    cw2 = (CW - 14) / 2; t = 176
    items = [("Wins", SAGE, 190), ("Lessons learned", TERRA, 190), ("Brag-doc entries (work)", SAGE, 190), ("Gratitude", GOLD, 190)]
    for i, (ti, col, hh) in enumerate(items):
        x = ML + (i % 2) * (cw2 + 14); tt = t + (i // 2) * (hh + 12); card(c, x, tt, cw2, hh, ti, col); lines(c, x + 14, tt + 26, cw2 - 28, 5, 28)
    t = 176 + 2 * 202
    card(c, ML, t, cw2, 170, "Scores", GOLD)
    for k, lab in enumerate(("Energy", "Sleep", "Movement", "Focus", "Joy")):
        yy = t + 40 + k * 25; txt(c, lab, ML + 16, yy, "Sans", 9.5, INK); progress(c, ML + 100, yy - 8, cw2 - 120, 9, 10, GOLD)
    card(c, ML + cw2 + 14, t, cw2, 170, "Money snapshot", GOLD)
    for k, lab in enumerate(("Income", "Spent", "Saved", "Subscriptions")):
        yy = t + 44 + k * 30; txt(c, lab, ML + cw2 + 30, yy, "Sans", 9.5, INK); dotted(c, ML + cw2 + 118, ML + 2 * cw2 + 0, yy + 3)
    t += 182
    rr(c, ML, t, CW, 1086 - t, 14, fill=SAGE_XL, stroke=SAGE_L)
    txt(c, "NEXT MONTH", ML + 18, t + 28, "SansB", 8, SAGE_D, tr=1.6)
    numbered(c, ML + 18, t + 34, CW - 36, 3, 32, SAGE)
    if m < 12:
        chip(c, f"{MONTHS[m].upper()} →", CR - 112, t + 12, 96, 22, SAGE_D, WHITE, f"m{m + 1:02d}", 7.8)
    d.end()


# ---------------------------------------------------------------- weeks
def week_page(d, wn):
    s = week_start(wn); e = s + dt.timedelta(days=6)
    anchor = max(s, D1) if s.year == YEAR else D1
    ctx = {"month": min(max(s + dt.timedelta(days=3), D1), DEC31).month, "week": wn}
    c = d.page(f"w{wn:02d}", f"W{wn} · {s.strftime('%b %d').replace(' 0', ' ')} – {e.strftime('%b %d').replace(' 0', ' ')}", 1, active="WEEK", ctx=ctx)
    txt(c, "Week", ML, 98, "Disp", 50, INK); txt(c, str(wn), ML + stringWidth("Week", "Disp", 50) + 12, 98, "Num", 54, SAGE_D)
    span = s.strftime("%b %d").replace(" 0", " ") + " – " + e.strftime("%b %d").replace(" 0", " ")
    txt(c, span.upper(), ML + 3, 122, "SansB", 9, SAGE_D, tr=1.8)
    month_strip(c, ML, 18, ctx["month"]); arrows(c, CR, 16, f"w{wn - 1:02d}" if wn > 1 else None, f"w{wn + 1:02d}" if wn < NWEEKS else None)
    stk(c, WEEK_STK[(wn * 5) % len(WEEK_STK)], CR - 138, 92, 108, maxw=200)
    t = 160
    card(c, ML, t, 366, 112, "Week focus", SAGE); lines(c, ML + 14, t + 24, 338, 3, 27)
    card(c, ML + 376, t, CW - 376, 112, "Top 3 this week", TERRA); numbered(c, ML + 390, t + 20, CW - 404, 3, 27, TERRA)
    t = 284; rh = 88
    for i in range(7):
        dd = s + dt.timedelta(days=i); ty = t + i * (rh + 5); wkend = dd.weekday() >= 5
        rr(c, ML, ty, CW, rh, 11, fill=TERRA_XL if wkend else CARD, stroke=RULE)
        vline(c, ML + 92, ty + 10, ty + rh - 10, RULE2)
        txt(c, dd.strftime("%a").upper(), ML + 46, ty + 27, "SansB", 8.4, TERRA if wkend else SAGE, "c", 1.5)
        txt(c, str(dd.day), ML + 46, ty + 65, "Num", 36, INK if in_year(dd) else RULE, "c")
        if in_year(dd):
            link(c, dkey(dd), ML, ty, 92, rh)
        lines(c, ML + 106, ty + 2, CW - 106 - 128, 2, 29)
        vline(c, CR - 118, ty + 10, ty + rh - 10, RULE2)
        for k, lab in enumerate(("GYM", "H2O", "MOOD")):
            cx = CR - 95 + k * 36; circ(c, cx, ty + 52, 8.5, stroke=SAGE if k < 2 else TERRA, lw=0.9); txt(c, lab, cx, ty + 30, "SansB", 6, MUTED, "c", 0.6)
    t = 284 + 7 * (rh + 5) + 2; hh = 1086 - t
    cw3 = (CW - 20) / 3
    card(c, ML, t, cw3 + 6, hh, "Meals & workouts", TERRA); lines(c, ML + 14, t + 22, cw3 - 22, 4, 24)
    card(c, ML + cw3 + 16, t, cw3 - 6, hh, "Wins", GOLD); lines(c, ML + cw3 + 30, t + 22, cw3 - 34, 4, 24)
    card(c, ML + 2 * cw3 + 20, t, cw3 + 0, hh, "Carry over", SAGE); checks(c, ML + 2 * cw3 + 34, t + 22, cw3 - 28, 4, 24, SAGE, 4.6)
    d.end()


# ---------------------------------------------------------------- daily
def daily(d, dd):
    wn = week_of(dd); i = (dd - D1).days + 1
    prev = dkey(dd - dt.timedelta(days=1)) if i > 1 else None
    nxt = dkey(dd + dt.timedelta(days=1)) if i < 365 else None
    ctx = {"month": dd.month, "week": wn}
    c = d.page(dkey(dd), None, 1, active=None, ctx=ctx)
    wkend = dd.weekday() >= 5
    month_strip(c, ML, 18, dd.month)
    chip(c, f"WEEK {wn} →", ML + 262, 18, 74, 20, SAGE_D, SAGE_L, f"w{wn:02d}", 7.4)
    arrows(c, CR, 16, prev, nxt)
    # date block
    num = str(dd.day); w_ = stringWidth(num, "Num", 96)
    txt(c, num, ML - 3, 132, "Num", 96, INK)
    x2 = ML + w_ + 14
    txt(c, dd.strftime("%A"), x2, 92, "DispI", 34, TERRA if wkend else SAGE_D)
    txt(c, f"{MONTHS[dd.month - 1]} {dd.year}".upper(), x2 + 2, 114, "SansB", 9.5, INK, tr=2.2)
    txt(c, f"DAY {i:03d} / 365  ·  WEEK {wn}  ·  Q{(dd.month - 1) // 3 + 1}", x2 + 2, 132, "SansM", 7.6, MUTED, tr=1.3)
    stk(c, day_sticker(dd), CR - 96, 112, 120, maxw=250, shadow=False)
    hline(c, ML, CR, 170, RULE, 0.8)
    LW, RX, RW = 428, 486, CR - 486
    # top 3
    card(c, ML, 184, LW, 118, "Top 3 today", SAGE); numbered(c, ML + 14, 202, LW - 28, 3, 30, SAGE)
    # to-do
    card(c, ML, 310, LW, 260, "To-do", SAGE); checks(c, ML + 14, 328, LW - 28, 8, 28, SAGE)
    # notes
    card(c, ML, 578, LW, 206, "Standup · meetings · notes", SAGE); lines(c, ML + 14, 598, LW - 28, 6, 28)
    # focus + shutdown
    card(c, ML, 792, 252, 70, "Focus blocks", TERRA)
    for k in range(8):
        tomato(c, ML + 22 + k * 27, 833, 8.5, TERRA)
    card(c, ML + 260, 792, LW - 260, 70, "Shutdown", TERRA)
    for k, lab in enumerate(("laptop closed", "tomorrow planned")):
        circ(c, ML + 276, 822 + k * 19, 4.6, stroke=TERRA, lw=0.9); txt(c, lab, ML + 286, 825 + k * 19, "Sans", 8.6, MUTED)
    # schedule
    card(c, RX, 184, RW, 678, "Schedule", SAGE)
    gt = 218; rh = (862 - 10 - gt) / 15
    for k in range(15):
        hh_ = 7 + k; ty = gt + k * rh
        hline(c, RX + 40, RX + RW - 12, ty, RULE, 0.6)
        hline(c, RX + 40, RX + RW - 12, ty + rh / 2, RULE2, 0.5, (1, 3))
        txt(c, f"{hh_:02d}", RX + 30, ty + 12, "SansB", 8.6, INK if 9 <= hh_ <= 18 else MUTED, "r")
    vline(c, RX + 38, gt, gt + 15 * rh, RULE, 0.6)
    # life band
    t = 878; gap = 10
    ws = [190, 130, 150, 250]; xs = [ML]
    for w_ in ws[:-1]:
        xs.append(xs[-1] + w_ + gap)
    card(c, xs[0], t, ws[0], 88, "Mood", TERRA)
    for k in range(5):
        face(c, xs[0] + 24 + k * 35, t + 56, k, 10.5, MUTED)
    card(c, xs[1], t, ws[1], 88, "Energy", GOLD); battery(c, xs[1] + 18, t + 42, 90, 26, GOLD)
    card(c, xs[2], t, ws[2], 88, "Sleep", SAGE_D)
    txt(c, "hours", xs[2] + 16, t + 45, "Sans", 8.4, MUTED); dotted(c, xs[2] + 52, xs[2] + ws[2] - 16, t + 47)
    txt(c, "rested", xs[2] + 16, t + 72, "Sans", 8.4, MUTED)
    for k in range(5):
        circ(c, xs[2] + 62 + k * 17, t + 69, 5.6, stroke=SAGE_D, lw=0.8)
    card(c, xs[3], t, ws[3], 88, "Water", SAGE)
    for k in range(8):
        drop(c, xs[3] + 20 + k * 27.5, t + 56, 9.5, SAGE)
    t2 = 974
    card(c, ML, t2, 306, 110, "Meals", TERRA)
    for k, lab in enumerate(("B", "L", "D", "S")):
        yy = t2 + 38 + k * 22; txt(c, lab, ML + 18, yy, "SansB", 8.6, TERRA); dotted(c, ML + 34, ML + 292, yy + 3)
    card(c, ML + 316, t2, 190, 110, "Move", GOLD)
    for k, lab in enumerate(("what", "min", "steps")):
        yy = t2 + 44 + k * 26; txt(c, lab, ML + 330, yy, "Sans", 8.4, MUTED); dotted(c, ML + 366, ML + 496, yy + 3)
    card(c, ML + 516, t2, CW - 516, 110, "Gratitude · win", SAGE)
    lines(c, ML + 530, t2 + 20, CW - 544, 3, 26)
    d.end()


# ---------------------------------------------------------------- hub pages
def hub_index(d, name, outline, active, sec, title, sub, items, st):
    col, lt = SEC[sec]
    c = d.page(name, outline, 0, active=active, ctx={})
    title_block(c, title, sub, col, sticker=st, st_h=122)
    cw2 = (CW - 14) / 2; t0 = 196; rows = (len(items) + 1) // 2
    chh = min(236, (1086 - t0 - (rows - 1) * 14) / rows); k_ = chh / 104
    for i, (lab, desc, dest, stn) in enumerate(items):
        x = ML + (i % 2) * (cw2 + 14); t = t0 + (i // 2) * (chh + 14)
        rr(c, x, t, cw2, chh, 14, fill=CARD, stroke=RULE); rr(c, x, t, 7, chh, 3, fill=col)
        txt(c, lab, x + 24, t + chh * .38, "Disp", 23, INK)
        for k, ln in enumerate(wrap(desc, "Sans", 9.8, cw2 - 170)):
            txt(c, ln, x + 24, t + chh * .38 + 22 + k * 14, "Sans", 9.8, MUTED)
        chip(c, "OPEN →", x + 24, t + chh - 40, 74, 24, col, SEC_LIGHT[col], None, 7.6)
        stk(c, stn, x + cw2 - 76, t + chh / 2, 84 * k_ ** .7, maxw=112); link(c, dest, x, t, cw2, chh)
    d.end()


def page_head(c, title, sub, col, sticker=None, back=None, backname="HUB"):
    txt(c, title, ML, 84, "Disp", 38, INK); txt(c, sub.upper(), ML + 2, 106, "SansB", 8.4, col, tr=1.7)
    if back:
        chip(c, f"← {backname}", ML + 2, 118, 78, 20, col, SEC_LIGHT[col], back, 7.4)
    if sticker:
        stk(c, sticker, CR - 66, 74, 96, maxw=150)


SEC_LIGHT = {SAGE: SAGE_L, TERRA: TERRA_L, GOLD: GOLD_L, TAUPE: TAUPE_L, BROWN: TAUPE_L}


def work_pages(d):
    items = [("Project tracker", "Status, priority, deadline and next step.", "w_proj", "dev_2"), ("Sprint planner", "Two-week board, capacity and retro.", "w_sprint", "dev_4"),
             ("1:1 notes", "Wins, topics, feedback and career talk.", "w_one", "work_5"), ("Meeting notes", "Agenda, decisions, action items.", "w_meet", "dev_6"),
             ("Brag document", "Impact, numbers and skills. For reviews.", "w_brag", "dev_3"), ("Learning tracker", "Courses, books, certs and skill levels.", "w_learn", "dev_5"),
             ("Bug & incident log", "Severity, root cause, fix and follow-up.", "w_bug", "dev_1"), ("Career roadmap", "Target role, skills, salary, interview prep.", "w_career", "dev_8")]
    hub_index(d, "work", "Work hub", "WORK", "work", "Work hub", "for the girl who ships", items, "dev_7")
    col = SAGE
    # project tracker
    c = d.page("w_proj", "Project tracker", 1, active="WORK", ctx={}); page_head(c, "Project tracker", "what is on my plate", col, "dev_2", "work")
    xs = table(c, ML, 160, CW, [("Project", 22), ("Status", 11), ("Prio", 7), ("Deadline", 11), ("Stakeholder", 15), ("Next step", 34)], 15, 58, col)
    for r in range(15):
        for k in range(3):
            circ(c, xs[1] + 18 + k * 17, 160 + 24 + r * 58 + 29, 5.6, stroke=[TERRA, GOLD, SAGE][k], lw=0.9)
    txt(c, "STATUS DOTS:  todo  ·  doing  ·  done", ML, 1082, "SansB", 7, MUTED, tr=0.8)
    d.end()
    # sprint planner
    c = d.page("w_sprint", "Sprint planner", 1, active="WORK", ctx={}); page_head(c, "Sprint planner", "two weeks, one goal", col, "dev_4", "work")
    card(c, ML, 150, 440, 66, "Sprint goal", SAGE); dotted(c, ML + 14, ML + 426, 192); card(c, ML + 450, 150, CW - 450, 66, "Sprint # · dates", SAGE); dotted(c, ML + 464, CR - 14, 192)
    colw = (CW - 3 * 8) / 4; tops = ["BACKLOG", "IN PROGRESS", "REVIEW", "DONE"]; cs = [TAUPE, TERRA, GOLD, SAGE]
    for k in range(4):
        x = ML + k * (colw + 8); rr(c, x, 228, colw, 540, 12, fill=CARD, stroke=RULE); rr(c, x, 228, colw, 28, 12, fill=SEC_LIGHT[cs[k]]); rr(c, x, 244, colw, 12, 0, fill=SEC_LIGHT[cs[k]])
        txt(c, tops[k], x + colw / 2, 246, "SansB", 7.8, cs[k], "c", 1.3)
        for j in range(6):
            rr(c, x + 8, 266 + j * 83, colw - 16, 74, 8, fill=HexColor("#FFF8E6") if k != 3 else SAGE_XL, stroke=RULE2, lw=0.6)
            dotted(c, x + 16, x + colw - 16, 266 + j * 83 + 28); dotted(c, x + 16, x + colw - 16, 266 + j * 83 + 50)
    card(c, ML, 782, 250, 302, "Capacity", GOLD); lines(c, ML + 14, 800, 222, 8, 33)
    cw3 = (CW - 260) / 3
    for k, (ti, cc) in enumerate((("Start", SAGE), ("Stop", TERRA), ("Continue", GOLD))):
        card(c, ML + 260 + k * (cw3 + 5), 782, cw3 - 0, 302, f"Retro · {ti}", cc); lines(c, ML + 274 + k * (cw3 + 5), 800, cw3 - 28, 8, 33)
    d.end()
    # 1:1
    c = d.page("w_one", "1:1 notes", 1, active="WORK", ctx={}); page_head(c, "1:1 notes", "talk less in circles", col, "work_5", "work")
    card(c, ML, 150, 366, 54, "With", SAGE); dotted(c, ML + 60, ML + 352, 186); card(c, ML + 376, 150, CW - 376, 54, "Date", SAGE); dotted(c, ML + 424, CR - 14, 186)
    cw2 = (CW - 12) / 2
    for i, (ti, cc, hh) in enumerate((("Wins since last time", SAGE, 188), ("Topics to discuss", SAGE, 188), ("Feedback I got", GOLD, 188), ("Feedback I gave", GOLD, 188), ("Career & growth", TERRA, 296), ("Action items", TERRA, 296))):
        x = ML + (i % 2) * (cw2 + 12); t = 216 + (i // 2) * 200 if i < 4 else 216 + 400 + ((i - 4) // 2) * 0
        card(c, x, t, cw2, hh, ti, cc); (checks if i == 5 else lines)(c, x + 14, t + 26, cw2 - 28, 5 if i < 4 else 8, 28 if i < 4 else 33, *( (cc,) if i == 5 else ()))
    d.end()
    # meeting notes
    c = d.page("w_meet", "Meeting notes", 1, active="WORK", ctx={}); page_head(c, "Meeting notes", "so nobody asks what we decided", col, "dev_6", "work")
    card(c, ML, 150, 330, 54, "Meeting", SAGE); dotted(c, ML + 80, ML + 316, 186); card(c, ML + 340, 150, 200, 54, "Date", SAGE); dotted(c, ML + 392, ML + 526, 186); card(c, ML + 550, 150, CW - 550, 54, "Time", SAGE); dotted(c, ML + 592, CR - 14, 186)
    card(c, ML, 214, CW, 70, "Attendees", SAGE); lines(c, ML + 14, 230, CW - 28, 2, 24)
    card(c, ML, 294, 280, 400, "Agenda", SAGE); checks(c, ML + 14, 312, 252, 11, 33, SAGE)
    card(c, ML + 290, 294, CW - 290, 400, "Notes", SAGE); lines(c, ML + 304, 312, CW - 318, 11, 33)
    card(c, ML, 704, 280, 380, "Decisions", GOLD); lines(c, ML + 14, 722, 252, 10, 33)
    xs = table(c, ML + 290, 704, CW - 290, [("Action", 50), ("Owner", 25), ("Due", 15)], 10, 33, TERRA, 24, TERRA_L)
    d.end()
    # brag document
    c = d.page("w_brag", "Brag document", 1, active="WORK", ctx={}); page_head(c, "Brag document", "write it down before you forget you are amazing", col, "dev_3", "work")
    table(c, ML, 160, CW, [("Date", 9), ("What I did", 32), ("Impact (numbers!)", 24), ("Skills", 15), ("Link", 14)], 14, 52, col)
    rr(c, ML, 930, CW, 156, 12, fill=SAGE_XL, stroke=SAGE_L)
    txt(c, "REVIEW CHEAT SHEET", ML + 16, 954, "SansB", 7.8, SAGE_D, tr=1.4)
    for k, ln in enumerate(("Quantify:  made X faster by Y%, saved Z hours, unblocked N people.", "Ownership:  what did I lead, not just do?", "Growth:  what could I not do in January that I can do now?")):
        txt(c, ln, ML + 16, 982 + k * 20, "Sans", 10, INK)
    dotted(c, ML + 16, CR - 16, 1066, SAGE)
    d.end()
    # learning tracker
    c = d.page("w_learn", "Learning tracker", 1, active="WORK", ctx={}); page_head(c, "Learning tracker", "one skill you can show for it", col, "dev_5", "work")
    xs = table(c, ML, 160, CW, [("Course · book · cert", 30), ("Platform", 14), ("Started", 9), ("Progress", 26), ("Notes", 21)], 9, 44, col)
    for r in range(9):
        progress(c, xs[3] + 12, 160 + 24 + r * 44 + 18, xs[4] - xs[3] - 24, 8, 10, SAGE)
    txt(c, "SKILLS HEATMAP", ML, 624, "SansB", 8, SAGE, tr=1.4)
    for r in range(8):
        yy = 640 + r * 55; rr(c, ML, yy, CW, 47, 10, fill=CARD, stroke=RULE); dotted(c, ML + 14, ML + 300, yy + 30)
        for k in range(5):
            circ(c, ML + 360 + k * 56, yy + 24, 11, stroke=SAGE, lw=0.9)
    txt(c, "beginner  ←→  can teach it", ML + 360, 1100, "SansI", 8, MUTED)
    d.end()
    # bug log
    c = d.page("w_bug", "Bug & incident log", 1, active="WORK", ctx={}); page_head(c, "Bug & incident log", "write the post-mortem while it still hurts", col, "dev_1", "work")
    table(c, ML, 160, CW, [("ID", 7), ("Date", 9), ("Sev", 6), ("What happened", 28), ("Root cause", 20), ("Fix", 20), ("Done", 5)], 16, 54, col)
    for r in range(16):
        circ(c, CR - 24, 160 + 24 + r * 54 + 27, 6, stroke=SAGE, lw=0.9)
    d.end()
    # career
    c = d.page("w_career", "Career roadmap", 1, active="WORK", ctx={}); page_head(c, "Career roadmap", "where I am going and how I get paid for it", col, "dev_8", "work")
    cw2 = (CW - 12) / 2
    card(c, ML, 150, cw2, 150, "Target role · 12 months", SAGE); lines(c, ML + 14, 170, cw2 - 28, 4, 27)
    card(c, ML + cw2 + 12, 150, cw2, 150, "Skills to level up", SAGE); checks(c, ML + cw2 + 26, 170, cw2 - 28, 4, 27)
    table(c, ML, 312, cw2, [("Quarter", 20), ("Salary", 40), ("Note", 40)], 4, 34, GOLD, 24, GOLD_L)
    card(c, ML + cw2 + 12, 312, cw2, 160, "Network & events", TERRA); lines(c, ML + cw2 + 26, 332, cw2 - 28, 4, 30)
    txt(c, "INTERVIEW PREP · STAR STORIES", ML, 506, "SansB", 8, SAGE, tr=1.4)
    for i, ti in enumerate(("Situation", "Task", "Action", "Result")):
        x = ML + (i % 2) * (cw2 + 12); t = 518 + (i // 2) * 168; card(c, x, t, cw2, 158, ti, SAGE); lines(c, x + 14, t + 24, cw2 - 28, 4, 28)
    card(c, ML, 862, CW, 222, "Questions I should ask · people to thank · offers", GOLD); lines(c, ML + 14, 882, CW - 28, 6, 30)
    d.end()


def health_pages(d):
    items = [("Habit tracker", "A grid for every month. Open from the month page.", "h01", "fit_1"), ("Workout log", "Date, type, minutes, sets and feelings.", "h_work", "fit_2"),
             ("Meal planner", "Seven days of meals and a shopping list.", "h_meal", "fit_4"), ("Sleep · water · mood", "A month of tiny data on one page.", "h_sleep", "cozy_6"),
             ("Body check-in", "Monthly measurements and how I feel.", "h_body", "fit_7"), ("Self-care menu", "What actually helps, written down.", "l_care", "cozy_1")]
    hub_index(d, "health", "Health hub", "HEALTH", "health", "Health", "strong body, quiet mind", items, "fit_3")
    col = TERRA
    for m in range(1, 13):
        c = d.page(f"h{m:02d}", f"Habits · {MONTHS[m - 1]}" if m == 1 else None, 1, active="HEALTH", ctx={"month": m, "week": week_of(dt.date(YEAR, m, 1))})
        page_head(c, f"Habits  ·  {MONTHS[m - 1]}", "show up, tick the circle", col, MONTH_STK[m - 1], f"m{m:02d}", MONTHS[m - 1][:3].upper())
        nd = calendar.monthrange(YEAR, m)[1]; x0 = ML + 134; cwd = (CW - 134 - 6) / 31; t0 = 168
        rr(c, ML, t0, CW, 30 + 14 * 38, 12, fill=CARD, stroke=RULE)
        for k in range(1, nd + 1):
            cx = x0 + (k - .5) * cwd; txt(c, str(k), cx, t0 + 19, "SansB", 6.8, MUTED if dt.date(YEAR, m, k).weekday() < 5 else TERRA, "c"); link(c, dkey(dt.date(YEAR, m, k)), cx - cwd / 2, t0 + 4, cwd, 20)
        txt(c, "HABIT", ML + 14, t0 + 19, "SansB", 7.2, col, tr=1.2)
        for r in range(14):
            ty = t0 + 30 + r * 38; hline(c, ML + 8, CR - 8, ty, RULE2, 0.6); dotted(c, ML + 14, ML + 124, ty + 28)
            for k in range(1, nd + 1):
                circ(c, x0 + (k - .5) * cwd, ty + 19, 4.3, stroke=RULE, lw=0.7)
        card(c, ML, 750, 366, 334, "What helped", SAGE); lines(c, ML + 14, 770, 338, 9, 33)
        card(c, ML + 376, 750, CW - 376, 334, "What I will change", TERRA); lines(c, ML + 390, 770, CW - 404, 9, 33)
        d.end()
    # workout log
    c = d.page("h_work", "Workout log", 1, active="HEALTH", ctx={}); page_head(c, "Workout log", "future you says thanks", col, "fit_2", "health")
    table(c, ML, 160, CW, [("Date", 9), ("Type", 16), ("Min", 7), ("Exercises · sets × reps", 40), ("Felt", 14)], 16, 46, col, 24, TERRA_L)
    for r in range(16):
        for k in range(5):
            circ(c, ML + CW * 0.86 + 6 + k * 14.5, 160 + 24 + r * 46 + 23, 5, stroke=MOODS[k], lw=1)
    d.end()
    # meal planner
    c = d.page("h_meal", "Meal planner", 1, active="HEALTH", ctx={}); page_head(c, "Meal planner", "decide once, eat well all week", col, "fit_4", "health")
    xs = table(c, ML, 160, 530, [("", 12), ("Breakfast", 22), ("Lunch", 22), ("Dinner", 22), ("Snack", 22)], 7, 76, col, 24, TERRA_L)
    for r in range(7):
        txt(c, ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"][(r + WSTART) % 7 if SUNDAY else r], xs[0] + 32, 160 + 24 + r * 76 + 42, "SansB", 8.4, TERRA, "c", 1.2)
    card(c, ML + 542, 160, CW - 542, 556, "Shopping list", SAGE); checks(c, ML + 556, 178, CW - 570, 15, 34, SAGE, 4.8)
    card(c, ML, 732, CW, 352, "Prep notes · recipes to try", GOLD); lines(c, ML + 14, 752, CW - 28, 10, 32)
    d.end()
    # sleep water mood
    c = d.page("h_sleep", "Sleep · water · mood", 1, active="HEALTH", ctx={}); page_head(c, "Sleep · water · mood", "a month of tiny data", col, "cozy_6", "health")
    xs = table(c, ML, 160, CW, [("Day", 6), ("Bed", 10), ("Wake", 10), ("Hours", 9), ("Sleep quality", 18), ("Water", 24), ("Mood", 23)], 31, 25.4, col, 24, TERRA_L)
    for r in range(31):
        yy = 160 + 24 + r * 25.4 + 13; txt(c, str(r + 1), xs[0] + 14, yy + 3, "SansB", 7.6, MUTED, "c")
        for k in range(5):
            circ(c, xs[4] + 14 + k * 17, yy, 4.6, stroke=RULE, lw=0.8)
        for k in range(8):
            circ(c, xs[5] + 12 + k * 14.2, yy, 4.2, stroke=SAGE, lw=0.7)
        for k in range(5):
            circ(c, xs[6] + 14 + k * 17, yy, 4.6, stroke=MOODS[k], lw=0.9)
    d.end()
    # body
    c = d.page("h_body", "Body check-in", 1, active="HEALTH", ctx={}); page_head(c, "Body check-in", "numbers are data, not a verdict", col, "fit_7", "health")
    table(c, ML, 160, CW, [("Month", 12), ("Weight", 12), ("Waist", 10), ("Hips", 10), ("Energy", 14), ("How I feel", 42)], 12, 44, col, 24, TERRA_L)
    for r in range(12):
        txt(c, MONTHS[r][:3].upper(), ML + 16, 160 + 24 + r * 44 + 26, "SansB", 8.4, TERRA, tr=1.2)
    card(c, ML, 740, CW, 344, "Notes for my doctor · supplements · cycle", GOLD); lines(c, ML + 14, 760, CW - 28, 9, 33)
    d.end()


def life_pages(d):
    items = [("Reading list", "Twelve shelves of books and progress.", "l_read", "travel_8"), ("Watch & play", "Series, movies, games and co-op nights.", "l_play", "hobby_6"),
             ("Budget", "Income, spend, savings and subscriptions.", "l_budget", "home_2"), ("Savings goals", "Jars that fill up, slowly.", "l_save", "home_1"),
             ("Travel planner", "Where, when, how much, what to pack.", "l_travel", "travel_1"), ("Gifts & birthdays", "Never forget again.", "l_gifts", "social_6"),
             ("Self-care menu", "Morning, evening, and the emergency list.", "l_care", "hobby_3"), ("Home reset", "A weekly cleaning loop that is not scary.", "l_home", "home_3"),
             ("Friends & plans", "Who to see, what to do, what to look forward to.", "l_social", "social_2"), ("Hobbies", "Make things. Track the joy, not the output.", "l_hobby", "hobby_1"),
             ("Date night", "Dates, anniversaries, little surprises.", "l_love", "love_4"), ("Seasonal bucket list", "Four seasons, four lists of small adventures.", "l_seasons", "seasons_3")]
    hub_index(d, "life", "Life hub", "LIFE", "life", "Life", "the part that is not work", items, "travel_2")
    col = GOLD
    c = d.page("l_read", "Reading list", 1, active="LIFE", ctx={}); page_head(c, "Reading list", "12 books, no guilt", col, "travel_8", "life")
    cw2 = (CW - 14) / 2
    for i in range(12):
        x = ML + (i % 2) * (cw2 + 14); t = 160 + (i // 2) * 154; rr(c, x, t, cw2, 144, 12, fill=CARD, stroke=RULE); rr(c, x + 12, t + 14, 60, 86, 4, fill=[SAGE_L, TERRA_L, GOLD_L][i % 3], stroke=RULE)
        txt(c, MONTHS[i][:3].upper(), x + 42, t + 62, "SansB", 8, MUTED, "c", 1.2)
        txt(c, "TITLE", x + 86, t + 26, "SansB", 6.8, col, tr=1); dotted(c, x + 86, x + cw2 - 14, t + 38); dotted(c, x + 86, x + cw2 - 14, t + 62)
        txt(c, "AUTHOR", x + 86, t + 76, "SansB", 6.8, col, tr=1); dotted(c, x + 86, x + cw2 - 14, t + 90)
        for k in range(5):
            sparkle(c, x + 90 + k * 15, t + 112, 5, GOLD_L if k > 0 else GOLD)
        progress(c, x + 12, t + 124, cw2 - 24, 6, 20, col)
    d.end()
    c = d.page("l_play", "Watch & play", 1, active="LIFE", ctx={}); page_head(c, "Watch & play", "cosy queue", col, "hobby_6", "life")
    cw3 = (CW - 24) / 3
    for i, (ti, cc) in enumerate((("Series & movies", TERRA), ("Games", SAGE), ("Podcasts & music", GOLD))):
        x = ML + i * (cw3 + 12); card(c, x, 160, cw3, 924, ti, cc); checks(c, x + 14, 180, cw3 - 28, 26, 34, cc, 4.8)
    d.end()
    c = d.page("l_budget", "Budget", 1, active="LIFE", ctx={}); page_head(c, "Monthly budget", "calm money, soft numbers", col, "home_2", "life")
    cw2 = (CW - 12) / 2
    table(c, ML, 160, cw2, [("Income", 60), ("Amount", 40)], 6, 32, GOLD, 24, GOLD_L)
    table(c, ML + cw2 + 12, 160, cw2, [("Savings & goals", 60), ("Amount", 40)], 6, 32, GOLD, 24, GOLD_L)
    table(c, ML, 390, CW, [("Expense", 34), ("Planned", 16), ("Actual", 16), ("Diff", 12), ("Paid", 10)], 16, 33, GOLD, 24, GOLD_L)
    for r in range(16):
        circ(c, ML + CW * 0.945, 390 + 24 + r * 33 + 17, 5.4, stroke=SAGE, lw=0.9)
    rr(c, ML, 962, CW, 122, 12, fill=GOLD_XL, stroke=GOLD_L); txt(c, "MONEY NOTES", ML + 16, 986, "SansB", 7.8, GOLD, tr=1.4); lines(c, ML + 14, 990, CW - 28, 3, 28)
    d.end()
    c = d.page("l_save", "Savings goals", 1, active="LIFE", ctx={}); page_head(c, "Savings goals", "jars that fill up slowly", col, "home_1", "life")
    cw3 = (CW - 24) / 3
    for i in range(6):
        x = ML + (i % 3) * (cw3 + 12); t = 160 + (i // 3) * 330
        rr(c, x, t, cw3, 318, 14, fill=CARD, stroke=RULE)
        jw, jh = 92, 130; jx = x + cw3 / 2 - jw / 2
        rr(c, jx + 8, t + 28, jw - 16, 12, 3, fill=GOLD_L, stroke=GOLD, lw=.9); rr(c, jx, t + 44, jw, jh, 20, fill=GOLD_XL, stroke=GOLD, lw=1.1)
        for k in range(1, 5):
            hline(c, jx + 10, jx + 24, t + 44 + jh * k / 5, GOLD, 0.7)
        txt(c, "GOAL", x + 16, t + 214, "SansB", 7, GOLD, tr=1); dotted(c, x + 50, x + cw3 - 14, t + 217)
        txt(c, "TARGET", x + 16, t + 242, "SansB", 7, GOLD, tr=1); dotted(c, x + 56, x + cw3 - 14, t + 245)
        txt(c, "SAVED", x + 16, t + 270, "SansB", 7, GOLD, tr=1); dotted(c, x + 50, x + cw3 - 14, t + 273); progress(c, x + 16, t + 288, cw3 - 32, 7, 10, GOLD)
    d.end()
    c = d.page("l_travel", "Travel planner", 1, active="LIFE", ctx={}); page_head(c, "Travel planner", "pack light, plan loosely", col, "travel_1", "life")
    for i, ti in enumerate(("Where", "When", "Budget")):
        x = ML + i * (CW / 3 + 2); card(c, x, 160, CW / 3 - 8, 66, ti, GOLD); dotted(c, x + 14, x + CW / 3 - 22, 206)
    card(c, ML, 238, 366, 340, "Itinerary", TERRA); lines(c, ML + 14, 258, 338, 9, 33)
    card(c, ML + 376, 238, CW - 376, 340, "Bookings", GOLD); checks(c, ML + 390, 258, CW - 404, 9, 33, GOLD)
    card(c, ML, 590, 366, 494, "Packing list", SAGE); checks(c, ML + 14, 610, 338, 13, 34, SAGE, 4.8)
    card(c, ML + 376, 590, CW - 376, 494, "Must see · eat · try", TERRA); lines(c, ML + 390, 610, CW - 404, 13, 34)
    d.end()
    c = d.page("l_gifts", "Gifts & birthdays", 1, active="LIFE", ctx={}); page_head(c, "Gifts & birthdays", "be the friend who remembers", col, "social_6", "life")
    cw3 = (CW - 24) / 3
    for m in range(12):
        x = ML + (m % 3) * (cw3 + 12); t = 160 + (m // 3) * 232; card(c, x, t, cw3, 222, MONTHS[m], [SAGE, TERRA, GOLD][m % 3]); lines(c, x + 14, t + 24, cw3 - 28, 6, 31)
    d.end()
    c = d.page("l_care", "Self-care menu", 1, active="LIFE", ctx={}); page_head(c, "Self-care menu", "what actually helps", col, "hobby_3", "life")
    cw2 = (CW - 12) / 2
    for i, (ti, cc) in enumerate((("Morning ritual", GOLD), ("Evening ritual", SAGE), ("When I am overwhelmed", TERRA), ("Tiny joys (under 10 min)", GOLD))):
        x = ML + (i % 2) * (cw2 + 12); t = 160 + (i // 2) * 266; card(c, x, t, cw2, 254, ti, cc); checks(c, x + 14, t + 24, cw2 - 28, 7, 31, cc)
    card(c, ML, 700, CW, 384, "Digital detox · boundaries · what to say no to", TERRA); lines(c, ML + 14, 720, CW - 28, 10, 33)
    d.end()
    c = d.page("l_home", "Home reset", 1, active="LIFE", ctx={}); page_head(c, "Home reset", "a loop that is not scary", col, "home_3", "life")
    for i in range(8):
        x = ML + (i % 2) * (cw2 + 12); t = 160 + (i // 2) * 232; card(c, x, t, cw2, 220, ["Mon · kitchen", "Tue · bathroom", "Wed · floors", "Thu · laundry", "Fri · desk & inbox", "Sat · plants & fridge", "Sun · reset & plan", "Extra · what I keep forgetting"][i], [SAGE, TERRA][i % 2]); checks(c, x + 14, t + 24, cw2 - 28, 6, 31, [SAGE, TERRA][i % 2])
    d.end()


def social_hobby_pages(d):
    col = GOLD; cw2 = (CW - 12) / 2
    c = d.page("l_social", "Friends & plans", 1, active="LIFE", ctx={}); page_head(c, "Friends & plans", "protect the fun parts", col, "social_2", "life")
    xs = table(c, ML, 160, CW, [("Who", 22), ("Last seen", 14), ("Plan", 40), ("Booked", 12), ("Gift idea", 12)], 10, 40, col, 24, GOLD_L)
    for r in range(10):
        circ(c, xs[4] - 22, 160 + 24 + r * 40 + 20, 5.4, stroke=SAGE, lw=0.9)
    card(c, ML, 600, cw2, 244, "Things to look forward to", TERRA); lines(c, ML + 14, 620, cw2 - 28, 7, 31)
    card(c, ML + cw2 + 12, 600, cw2, 244, "Hangout ideas", SAGE); checks(c, ML + cw2 + 26, 620, cw2 - 28, 7, 31, SAGE)
    card(c, ML, 856, cw2, 228, "Dates · concerts · cinema", GOLD); lines(c, ML + 14, 876, cw2 - 28, 6, 31)
    card(c, ML + cw2 + 12, 856, cw2, 228, "Conversations to remember", TERRA); lines(c, ML + cw2 + 26, 876, cw2 - 28, 6, 31)
    d.end()
    c = d.page("l_hobby", "Hobbies", 1, active="LIFE", ctx={}); page_head(c, "Hobbies", "make things, track the joy not the output", col, "hobby_1", "life")
    for i, (ti, cc) in enumerate((("Painting & drawing", TERRA), ("Baking & cooking", GOLD), ("Plants & flowers", SAGE), ("Music & dance", TERRA))):
        x = ML + (i % 2) * (cw2 + 12); t = 160 + (i // 2) * 250; card(c, x, t, cw2, 238, ti, cc); checks(c, x + 14, t + 24, cw2 - 28, 6, 33, cc)
    table(c, ML, 668, CW, [("Project / recipe / idea", 40), ("Started", 12), ("Done", 10), ("Joy", 38)], 8, 38, col, 24, GOLD_L)
    for r in range(8):
        for k in range(5):
            sparkle(c, ML + CW * 0.66 + 20 + k * 24, 668 + 24 + r * 38 + 19, 6, GOLD_L)
    d.end()


def love_season_pages(d):
    col = TERRA; cw2 = (CW - 12) / 2
    c = d.page("l_love", "Date night", 1, active="LIFE", ctx={}); page_head(c, "Date night", "small rituals, big difference", col, "love_6", "life")
    xs = table(c, ML, 160, CW, [("Date", 12), ("Where / what", 34), ("Who planned", 16), ("Notes", 38)], 8, 40, col, 24, TERRA_L)
    card(c, ML, 528, cw2, 270, "Date ideas", TERRA); checks(c, ML + 14, 548, cw2 - 28, 7, 34, TERRA)
    card(c, ML + cw2 + 12, 528, cw2, 270, "Anniversaries & important dates", GOLD); lines(c, ML + cw2 + 26, 548, cw2 - 28, 7, 34)
    card(c, ML, 810, cw2, 274, "Little things they love", SAGE); lines(c, ML + 14, 830, cw2 - 28, 7, 34)
    card(c, ML + cw2 + 12, 810, cw2, 274, "Love notes to self", TERRA); lines(c, ML + cw2 + 26, 830, cw2 - 28, 7, 34)
    d.end()
    c = d.page("l_seasons", "Seasonal bucket list", 1, active="LIFE", ctx={}); page_head(c, "Seasonal bucket list", "four seasons, four lists", GOLD, "seasons_3", "life")
    for i, (ti, cc, stn) in enumerate((("Winter", SAGE, "seasons_7"), ("Spring", TERRA, "seasons_2"), ("Summer", GOLD, "seasons_1"), ("Autumn", TERRA, "seasons_5"))):
        x = ML + (i % 2) * (cw2 + 12); t = 160 + (i // 2) * 466
        card(c, x, t, cw2, 454, ti, cc); stk(c, stn, x + cw2 - 78, t + 50, 74, maxw=120); checks(c, x + 14, t + 52, cw2 - 28, 11, 34, cc)
    d.end()


def notes_pages(d):
    items = [("Lined", "For thoughts in sentences.", "n_lined1", "cozy_8"), ("Dotted", "For sketches and lists.", "n_dot1", "work_4"), ("Grid", "For diagrams and tables.", "n_grid1", "work_2"), ("Cornell", "For lectures, calls and courses.", "n_corn1", "work_5")]
    hub_index(d, "notes", "Notes", "NOTES", "notes", "Notes", "brain dumps welcome", items, "cozy_2")
    for kind, label in (("lined", "Lined"), ("dot", "Dotted"), ("grid", "Grid"), ("corn", "Cornell")):
        for n in range(1, 5):
            c = d.page(f"n_{kind}{n}", f"{label} {n}" if n == 1 else None, 1, active="NOTES", ctx={}, dots=(kind == "dot"))
            txt(c, label, ML, 70, "Disp", 30, INK); txt(c, f"NOTES  ·  {n}", ML + 2, 90, "SansB", 7.8, TAUPE, tr=1.7)
            txt(c, "DATE", CR - 220, 70, "SansB", 7.2, TAUPE, tr=1.2); dotted(c, CR - 190, CR, 72)
            nxt = f"n_{kind}{n + 1}" if n < 4 else None
            chip(c, "← NOTES", ML + 120, 56, 70, 20, TAUPE, TAUPE_L, "notes", 7.2)
            if kind == "lined":
                for y in range(120, 1088, 30):
                    hline(c, ML, CR, y, RULE, 0.6)
            elif kind == "grid":
                c.saveState(); c.setStrokeColor(RULE2); c.setLineWidth(0.5)
                for y in range(120, 1090, 26):
                    c.line(ML, Y(y), CR, Y(y))
                for x in range(ML, CR + 1, 25):
                    c.line(x, Y(120), x, Y(1088 - (1088 - 120) % 26))
                c.restoreState()
            elif kind == "corn":
                rr(c, ML, 110, CW, 976, 12, stroke=RULE, lw=0.8)
                vline(c, ML + 200, 110, 936, RULE); hline(c, ML, CR, 936, RULE)
                txt(c, "CUES · QUESTIONS", ML + 16, 132, "SansB", 7.4, SAGE, tr=1.2); txt(c, "NOTES", ML + 216, 132, "SansB", 7.4, SAGE, tr=1.2); txt(c, "SUMMARY", ML + 16, 958, "SansB", 7.4, TERRA, tr=1.2)
                for y in range(160, 930, 30):
                    hline(c, ML + 212, CR - 12, y, RULE2, 0.5)
                for y in range(984, 1080, 30):
                    hline(c, ML + 16, CR - 12, y, RULE2, 0.5)
            d.end()


# ---------------------------------------------------------------- main
def main():
    path = os.path.join(OUT, f"Code_and_Cozy_Planner_{YEAR}_{'Sun' if SUNDAY else 'Mon'}.pdf")
    d = Doc(path)
    cover(d); home(d); start_here(d)
    year_overview(d); goals(d); pixels(d)
    for q in range(1, 5):
        quarter(d, q)
    for m in range(1, 13):
        month_pages(d, m)
    for wn in range(1, NWEEKS + 1):
        week_page(d, wn)
    day = D1
    while day <= DEC31:
        daily(d, day)
        day += dt.timedelta(days=1)
    work_pages(d); health_pages(d); life_pages(d); social_hobby_pages(d); love_season_pages(d); notes_pages(d)
    d.c.save(); lighten(path)
    print(path, d.n, "pages", round(os.path.getsize(path) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
