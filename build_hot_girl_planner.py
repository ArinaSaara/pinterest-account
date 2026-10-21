#!/usr/bin/env python3
"""Build "Hot Girl Era", an undated perimenopause tracker planner for GoodNotes / iPad (portrait 3:4).

Vector PDF (real text, hyperlinked tabs, outline). Retro 70s palette: cream, tangerine, hot pink, mocha.
Heroine: Margo (see prompts/hot_girl_era_stickers.md). Mechanic: eight habit trackers unlock eight accessories
that the user pastes onto Margo on the profile page.

Inputs (not in git):  images/hot_girl/cut/*.png   (run cut_hot_girl_stickers.py first; missing stickers are skipped)
Outputs:              images/hot_girl/Hot_Girl_Era_Perimenopause_Planner.pdf, Hot_Girl_Era_Sticker_Pack.pdf

Run:  .venv-planner/bin/python build_hot_girl_planner.py
"""
import math
import os

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from pdf_utils import lighten

ROOT = os.path.dirname(os.path.abspath(__file__))
FULL = os.path.join(ROOT, "images", "hot_girl", "cut")
CUT = os.path.join(ROOT, "images", "hot_girl", "cut_2x")
OUT = os.path.join(ROOT, "images", "hot_girl")
os.makedirs(CUT, exist_ok=True); os.makedirs(FULL, exist_ok=True)
for _f in os.listdir(FULL):                                   # 2x smooth upscale: the source sheets are small
    if _f.endswith(".png") and not os.path.exists(os.path.join(CUT, _f)):
        _im = Image.open(os.path.join(FULL, _f)); _im.resize((_im.width * 2, _im.height * 2), Image.LANCZOS).save(os.path.join(CUT, _f), optimize=True)

NAME = "Hot Girl Era"
W, H = 834, 1112
ML, CR = 44, 782
CW = CR - ML

FONTS = os.path.join(ROOT, "fonts")
for _name, _file in (("Disp", "PlayfairDisplay-Regular"), ("DispI", "PlayfairDisplay-Italic"), ("DispB", "PlayfairDisplay-Bold"),
                     ("Sans", "DMSans-Regular"), ("SansM", "DMSans-Medium"), ("SansB", "DMSans-SemiBold"), ("SansI", "DMSans-Italic"),
                     ("Num", "Jost-ExtraLight"), ("Script", "Caveat-SemiBold")):
    pdfmetrics.registerFont(TTFont(_name, os.path.join(FONTS, _file + ".ttf")))

PAPER = HexColor("#F8F0E2"); CARD = HexColor("#FFFCF5"); INK = HexColor("#3E2C26"); MUTED = HexColor("#8C7A6E")
RULE = HexColor("#E3D5C2"); RULE2 = HexColor("#EFE5D5"); WHITE = HexColor("#FFFFFF")
TANG = HexColor("#E8703A"); TANG_L = HexColor("#F9D8C4"); TANG_XL = HexColor("#FCEDE2")
PINK = HexColor("#E5457A"); PINK_L = HexColor("#F7D0DE"); PINK_XL = HexColor("#FBE9EF")
MOCHA = HexColor("#6B4A3A"); MOCHA_L = HexColor("#E5D6CB"); MOCHA_XL = HexColor("#F1E9E1")
PEACH = HexColor("#F8D9C3"); CREAM_D = HexColor("#EADCC3"); TAUPE = HexColor("#9C8878")


def Y(t):
    return H - t


# ---------------------------------------------------------------- stickers (optional)
_SIZE = {}
MISSING = set()


def stk(c, name, cx, ct, h, rot=0, maxw=None, ghost=False):
    """Draw a cut sticker centred at (cx, ct). Missing stickers are skipped (or shown as a dashed ghost slot)."""
    p = os.path.join(CUT, name + ".png")
    if not os.path.exists(p):
        MISSING.add(name)
        if ghost:
            rr(c, cx - (maxw or h) / 2, ct - h / 2, maxw or h, h, 14, stroke=RULE, lw=0.8, dash=(3, 4))
            txt(c, name, cx, ct + 3, "SansI", 7.5, MUTED, "c")
        return 0, 0
    if name not in _SIZE:
        _SIZE[name] = Image.open(p).size
    iw, ih = _SIZE[name]
    if maxw and iw * h / ih > maxw:
        h = maxw * ih / iw
    w = iw * h / ih
    c.saveState(); c.translate(cx, Y(ct)); c.rotate(rot)
    c.drawImage(p, -w / 2, -h / 2, w, h, mask="auto"); c.restoreState()
    return w, h


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


def para(c, s, x, t, width, font="Sans", size=9.6, col=INK, lead=None):
    lead = lead or size * 1.42
    for i, ln in enumerate(wrap(s, font, size, width)):
        txt(c, ln, x, t + i * lead, font, size, col)
    return t + len(wrap(s, font, size, width)) * lead


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


def dotted(c, x1, x2, t, col=RULE):
    hline(c, x1, x2, t, col=col, lw=0.7, dash=(1.2, 3))


def box(c, x, t, s=10, col=TANG, r=2.5):
    rr(c, x, t, s, s, r, stroke=col, lw=0.9)


def arcs(c, cx, base, r, cols=(TANG, PINK, PEACH), inner=None):
    """Retro half-sun: concentric half discs sitting on the baseline `base` (top-based)."""
    n = len(cols); step = r / (n + (1 if inner is not None else 0))
    for i, col in enumerate(cols):
        rr_ = r - i * step
        c.saveState(); c.setFillColor(col); p = c.beginPath(); y = Y(base)
        p.moveTo(cx - rr_, y); p.arcTo(cx - rr_, y - rr_, cx + rr_, y + rr_, 180, -180); p.close(); c.drawPath(p, stroke=0, fill=1); c.restoreState()
    if inner is not None:
        rr_ = r - n * step
        c.saveState(); c.setFillColor(inner); p = c.beginPath(); y = Y(base)
        p.moveTo(cx - rr_, y); p.arcTo(cx - rr_, y - rr_, cx + rr_, y + rr_, 180, -180); p.close(); c.drawPath(p, stroke=0, fill=1); c.restoreState()


def flame(c, cx, ct, s, col=TANG, col2=PINK):
    """Small vector flame, tip up, centred on (cx, ct)."""
    y = Y(ct)
    for k, (col_, f) in enumerate(((col, 1.0), (col2, 0.55))):
        c.saveState(); c.setFillColor(col_); p = c.beginPath(); h = s * f; w = s * .62 * f; yb = y - s * .5 * (1 if k == 0 else .85)
        p.moveTo(cx, yb + h * 1.25); p.curveTo(cx + w * .2, yb + h * .9, cx + w, yb + h * .7, cx + w * .6, yb + h * .2)
        p.curveTo(cx + w * .4, yb - h * .05, cx - w * .4, yb - h * .05, cx - w * .6, yb + h * .2)
        p.curveTo(cx - w, yb + h * .7, cx - w * .2, yb + h * .9, cx, yb + h * 1.25); c.drawPath(p, stroke=0, fill=1); c.restoreState()


def sparkle(c, cx, ct, r, col=TANG):
    c.saveState(); c.setFillColor(col); p = c.beginPath(); y = Y(ct); k = r * 0.22
    p.moveTo(cx, y + r); p.curveTo(cx + k, y + k, cx + k, y + k, cx + r, y); p.curveTo(cx + k, y - k, cx + k, y - k, cx, y - r)
    p.curveTo(cx - k, y - k, cx - k, y - k, cx - r, y); p.curveTo(cx - k, y + k, cx - k, y + k, cx, y + r)
    c.drawPath(p, stroke=0, fill=1); c.restoreState()


def chevron(c, cx, ct, d=1, s=4.5, col=MUTED):
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(1.3); c.setLineCap(1); y = Y(ct)
    p = c.beginPath(); p.moveTo(cx - d * s * .5, y + s); p.lineTo(cx + d * s * .5, y); p.lineTo(cx - d * s * .5, y - s); c.drawPath(p, stroke=1, fill=0); c.restoreState()


def chip(c, s, x, t, w, h, col, fill, dest=None, size=7.8, font="SansB", tr=0.8):
    rr(c, x, t, w, h, h / 2, fill=fill)
    txt(c, s, x + w / 2, t + h / 2 + size * .34, font, size, col, "c", tr)
    if dest:
        link(c, dest, x, t, w, h)


def card(c, x, t, w, h, title=None, col=TANG, fill=CARD, r=12):
    rr(c, x, t, w, h, r, fill=fill, stroke=RULE, lw=0.7)
    if title:
        circ(c, x + 14, t + 16, 2.6, fill=col)
        txt(c, title.upper(), x + 22, t + 19.5, "SansB", 7.6, col, tr=1.15)


def checks(c, x, t, w, items, gap, col=TANG, size=9.6, extra_lines=0):
    for i, s in enumerate(items):
        yy = t + gap * (i + 1)
        box(c, x, yy - 10, 10, col)
        if s:
            txt(c, s, x + 18, yy - 1.5, "Sans", size, INK)
        dotted(c, x + 18 + (stringWidth(s, "Sans", size) + 6 if s else 0), x + w, yy)
    for j in range(extra_lines):
        yy = t + gap * (len(items) + j + 1)
        box(c, x, yy - 10, 10, col); dotted(c, x + 18, x + w, yy)


def lines(c, x, t, w, n, gap, col=RULE):
    for i in range(n):
        dotted(c, x, x + w, t + gap * (i + 1), col)


def table(c, x, t, w, cols, nrows, row_h, col, head_h=26, light=None, prefill=None, size=9.2):
    """cols = [(label, weight)]; header + dotted rows. prefill: list of strings for the first column."""
    tot = sum(wt for _, wt in cols); xs = [x]
    rr(c, x, t, w, head_h + nrows * row_h, 12, fill=CARD)
    c.saveState(); p = c.beginPath(); p.roundRect(x, Y(t) - head_h, w, head_h, 12)
    c.clipPath(p, stroke=0, fill=0); c.setFillColor(light or TANG_L); c.rect(x, Y(t) - head_h, w, head_h, stroke=0, fill=1); c.restoreState()
    rr(c, x, t, w, head_h + nrows * row_h, 12, stroke=RULE, lw=0.7)
    cx = x
    for i, (lab, wt) in enumerate(cols):
        cw_ = w * wt / tot
        txt(c, lab.upper(), cx + 9, t + head_h / 2 + 2.6, "SansB", 7, col, tr=0.9)
        cx += cw_; xs.append(cx)
        if i < len(cols) - 1:
            vline(c, cx, t + 5, t + head_h + nrows * row_h - 4, RULE2, 0.6)
    for r_ in range(nrows):
        hline(c, x + 8, x + w - 8, t + head_h + (r_ + 1) * row_h, RULE2, 0.6)
        if prefill and r_ < len(prefill) and prefill[r_]:
            txt(c, prefill[r_], x + 9, t + head_h + (r_ + 1) * row_h - row_h / 2 + 3.2, "Sans", size, INK)
    return xs


def scale5(c, x, t, s=9, gap=4, col=TANG):
    for i in range(5):
        box(c, x + i * (s + gap), t, s, col)


# ---------------------------------------------------------------- chrome
TABS = [("HOME", "home", "#6B4A3A"), ("CYCLE", "cy_over", "#E5457A"), ("LOG", "m01", "#E8703A"), ("BODY", "b_strength", "#C9603A"),
        ("CARE", "c_meds", "#9C4B6A"), ("MIND", "mi_journal1", "#8C5A48"), ("NOTES", "n_lined1", "#9C8878"), ("STICKERS", "s1", "#E8703A")]


def tabs(c, active):
    n = len(TABS); h = 118; gap = 6; top = (H - (n * h + (n - 1) * gap)) / 2
    for i, (lab, dest, hexcol) in enumerate(TABS):
        col = HexColor(hexcol); t = top + i * (h + gap); on = (lab == active); w = 31 if on else 21
        rr(c, W - w, t, w + 8, h, 8, fill=col)
        c.saveState(); c.translate(W - w / 2 - 1 + (2 if on else 0), Y(t) - h / 2); c.rotate(-90)
        o = c.beginText(-stringWidth(lab, "SansB", 8) / 2 - 0.4 * (len(lab) - 1), -3); o.setFont("SansB", 8); o.setCharSpace(1.0); o.setFillColor(WHITE); o.textOut(lab); o.setCharSpace(0); c.drawText(o)
        c.restoreState(); link(c, dest, W - 32, t, 40, h)


def paper(c, dots=False):
    c.setFillColor(PAPER); c.rect(0, 0, W, H, stroke=0, fill=1)
    if dots:
        c.setFillColor(HexColor("#D5C5A8"))
        for yy in range(60, H - 40, 24):
            for xx in range(48, int(W - 50), 24):
                c.circle(xx, yy, 0.95, stroke=0, fill=1)


class Doc:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=(W, H), pageCompression=1)
        self.c.setTitle(f"{NAME} Perimenopause Planner"); self.c.setAuthor(NAME); self.c.setSubject("Undated, hyperlinked perimenopause tracker for GoodNotes")
        self.n = 0

    def page(self, name, outline=None, level=0, active=None, dots=False, chrome=True, seq=None):
        c = self.c; self.n += 1
        c.bookmarkPage(name)
        if outline:
            c.addOutlineEntry(outline, name, level, closed=True)
        paper(c, dots)
        if chrome:
            tabs(c, active)
            chip(c, "← HOME", ML, 1070, 70, 22, MOCHA, MOCHA_L, "home", 7.2)
            if seq:
                prv, nxt = seq
                for cx, dest, d in ((CR - 39, prv, -1), (CR - 11, nxt, 1)):
                    circ(c, cx, 1081, 11, stroke=RULE, fill=CARD, lw=0.8); chevron(c, cx + (-.5 if d < 0 else .5), 1081, d, 3.6, MUTED if dest else RULE)
                    if dest:
                        link(c, dest, cx - 12, 1069, 24, 24)
        return c

    def end(self):
        self.c.showPage()


def head(c, title, sub, col=TANG, st=None, st_h=104, rot=0, size=40):
    txt(c, title, ML, 84, "Disp", size, INK)
    txt(c, sub.upper(), ML + 2, 108, "SansB", 8.4, col, tr=1.8)
    arcs(c, ML + 18, 132, 16, (col, PEACH), PAPER)
    if st:
        stk(c, st, CR - 66, 80, st_h, rot, maxw=150)


def month_strip(c, cur, t=1078):
    """Twelve little chips 01..12 linking to each month's log page."""
    x = ML + 84
    for m in range(1, 13):
        on = (m == cur); chip(c, f"{m:02d}", x, t - 11, 26, 20, WHITE if on else MOCHA, TANG if on else MOCHA_L, f"m{m:02d}", 7.2, tr=0.3); x += 30


# ================================================================ pages
def cover(d):
    c = d.page("cover", None, chrome=False)
    for x, t, r_, col in ((86, 150, 9, PINK), (746, 170, 12, TANG), (62, 620, 7, PINK), (772, 600, 8, TANG), (110, 990, 10, PINK), (724, 980, 7, TANG)):
        sparkle(c, x, t, r_, col)
    txt(c, "THE PERIMENOPAUSE PLANNER", W / 2, 96, "SansB", 11, MOCHA, "c", 5)
    txt(c, "Hot Girl", W / 2, 218, "Disp", 104, INK, "c"); txt(c, "Era", W / 2 + 2, 300, "DispI", 84, PINK, "c")
    txt(c, "not today, hormones", W / 2, 352, "Script", 40, MOCHA, "c")
    arcs(c, W / 2, 790, 300, (TANG, PINK, PEACH), PAPER)
    stk(c, "m_fan", W / 2, 640, 340, 0, maxw=340, ghost=True)
    stk(c, "x_ice", 150, 560, 90, -8); stk(c, "d_flame", 690, 560, 90, 6)
    stk(c, "q_nottoday", 150, 760, 110, -6); stk(c, "q_maincharacter", 690, 760, 110, 6)
    rr(c, 160, 836, W - 320, 70, 35, fill=CARD, stroke=RULE, lw=0.7)
    txt(c, "track the cycle, the flashes, the sleep, the moods", W / 2, 866, "DispI", 17, INK, "c")
    txt(c, "and build your hot girl, one habit at a time", W / 2, 888, "SansI", 10.5, MUTED, "c")
    labels = ("CYCLE", "SYMPTOMS", "HABITS", "DOCTOR", "MIND")
    ws = [stringWidth(s, "SansB", 7.8) + 26 for s in labels]; x = W / 2 - (sum(ws) + 10 * 4) / 2
    for s, w_ in zip(labels, ws):
        chip(c, s, x, 936, w_, 22, MOCHA, TANG_L, "home", 7.8); x += w_ + 10
    txt(c, "GoodNotes · iPad · undated · tap anywhere to start", W / 2, 1068, "SansI", 9.5, MUTED, "c")
    link(c, "home", 0, 0, W, H); d.end()


HOME_ITEMS = [
    ("PROFILE", "Build your Hot Girl", "Margo and her 8 rewards", "profile", PINK, PINK_L, "base_margo"),
    ("CYCLE", "Cycle", "irregular is the point", "cy_over", PINK, PINK_L, "moon_full"),
    ("LOG", "Daily log", "12 months, 31 days each", "m01", TANG, TANG_L, "f3"),
    ("HABITS", "Habit grids", "the 8 that unlock rewards", "h01", TANG, TANG_L, "m_lifting"),
    ("BODY", "Body", "strength, measurements, triggers", "b_strength", MOCHA, MOCHA_L, "a_dumbbell"),
    ("CARE", "Doctor & care", "meds, labs, questions", "c_meds", PINK, PINK_L, "m_doctor"),
    ("MIND", "Mind", "journal, rage page, wins", "mi_journal1", MOCHA, MOCHA_L, "m_hug"),
    ("NOTES", "Notes", "lined, dotted, grid", "n_lined1", TAUPE, CREAM_D, "d_cat"),
    ("HOW", "How it works", "scales, legend, the rules", "howto", TANG, TANG_L, "q_hotgirlera"),
    ("STICKERS", "Sticker book", "102 stickers to lasso", "s1", PINK, PINK_L, "d_heart"),
]


def home(d):
    c = d.page("home", "Home", 0, active="HOME")
    head(c, "Hello, hot girl", "tap a card to jump in — everything is linked", MOCHA, "m_shrug", 110)
    cw = (CW - 14) / 2; ch = 150
    for i, (tab, ti, sub, dest, col, light, stn) in enumerate(HOME_ITEMS):
        x = ML + (i % 2) * (cw + 14); t = 164 + (i // 2) * (ch + 12)
        rr(c, x, t, cw, ch, 14, fill=CARD, stroke=RULE, lw=0.7)
        c.saveState(); p = c.beginPath(); p.roundRect(x, Y(t) - ch, cw, ch, 14); c.clipPath(p, stroke=0, fill=0)
        c.setFillColor(light); c.rect(x, Y(t) - 42, cw, 42, stroke=0, fill=1); c.restoreState()
        txt(c, tab, x + 16, t + 26, "SansB", 8, col, tr=1.8)
        txt(c, ti, x + 16, t + 76, "Disp", 24 if len(ti) > 14 else 27, INK); txt(c, sub, x + 17, t + 97, "SansI", 10.5, MUTED)
        stk(c, stn, x + cw - 62, t + 88, 90, maxw=100)
        chip(c, "OPEN →", x + 16, t + 112, 66, 22, col, light, dest, 7.4); link(c, dest, x, t, cw, ch)
    t = 164 + 5 * (ch + 12) + 4
    arcs(c, ML + 40, t + 30, 24, (TANG, PINK), PAPER); arcs(c, CR - 40, t + 30, 24, (PINK, TANG), PAPER)
    txt(c, "Start with “Build your Hot Girl” →", W / 2, t + 28, "DispI", 15, PINK, "c"); link(c, "profile", W / 2 - 130, t + 8, 260, 28)
    d.end()


REWARDS = [
    ("a_sleepmask", "Sleep mask", "7 nights of 7+ hours of sleep", "Sleep 7h+"),
    ("a_dumbbell", "Dumbbell", "8 strength sessions", "Strength"),
    ("a_shaker", "Shaker", "7 days hitting your protein goal", "Protein"),
    ("a_bottle", "Ice bottle", "10 days of 2 litres of water", "Water 2L"),
    ("a_potion", "Potion", "14 days of supplements or meds on time", "Supplements"),
    ("a_folder", "Folder", "one doctor visit with a prepared list", "Doctor prep"),
    ("a_fan", "Fan", "one full month of symptom logging", "Daily log"),
    ("a_crown", "Crown", "30 days of opening this planner", "Planner opened"),
]


def profile(d):
    c = d.page("profile", "Build your Hot Girl", 0, active="HOME", seq=("home", "howto"))
    head(c, "Build your Hot Girl", "eight habits, eight rewards, one Margo", PINK, "a_crown", 90)
    card(c, ML, 150, CW, 112, "This is me", MOCHA)
    for i, lab in enumerate(("Name", "Age", "Tracking since", "My doctor", "My why in one line", "")):
        if not lab:
            continue
        x = ML + 20 + (i % 3) * (CW / 3); t = 192 + (i // 3) * 40
        wdt = CW / 3 - 40 if i < 4 else CW - 40
        txt(c, lab.upper(), x, t, "SansB", 7.4, TAUPE, tr=1.2); dotted(c, x + stringWidth(lab.upper(), "SansB", 7.4) + 12 + len(lab) * 1.2, x + wdt, t + 1)
    # Margo base slot
    bx, bt, bw, bh = ML, 280, 300, 560
    rr(c, bx, bt, bw, bh, 18, fill=CARD, stroke=RULE, lw=0.7)
    rr(c, bx + 16, bt + 16, bw - 32, bh - 32, 14, stroke=PINK, lw=0.9, dash=(3, 4))
    txt(c, "MARGO LIVES HERE", bx + bw / 2, bt + 40, "SansB", 7.6, PINK, "c", 1.4)
    stk(c, "base_margo", bx + bw / 2, bt + bh / 2 + 10, bh - 100, 0, maxw=bw - 60)
    txt(c, "paste each reward onto her", bx + bw / 2, bt + bh - 28, "SansI", 9, MUTED, "c")
    # rewards list
    rx = ML + bw + 16; rw = CR - rx; rh = (bh - 7 * 8) / 8
    for i, (stn, title, cond, _) in enumerate(REWARDS):
        t = bt + i * (rh + 8)
        rr(c, rx, t, rw, rh, 12, fill=CARD, stroke=RULE, lw=0.7)
        circ(c, rx + 30, t + rh / 2, 20, stroke=TANG, lw=0.9)
        txt(c, str(i + 1), rx + 30, t + rh / 2 + 3.4, "SansB", 9.5, TANG, "c")
        stk(c, stn, rx + 30, t + rh / 2, 34, maxw=34)
        txt(c, title, rx + 62, t + rh / 2 - 3, "Disp", 15, INK)
        txt(c, cond, rx + 62, t + rh / 2 + 13, "Sans", 8.6, MUTED)
        box(c, rx + rw - 30, t + rh / 2 - 7, 14, PINK, 3.5)
    t = bt + bh + 22
    card(c, ML, t, CW, 1052 - t, "Unlocked so far", TANG)
    for i in range(8):
        cx = ML + 60 + i * ((CW - 120) / 7)
        circ(c, cx, t + 64, 16, stroke=TANG, lw=0.9, fill=TANG_XL); txt(c, str(i + 1), cx, t + 68, "SansB", 9, TANG, "c")
    txt(c, "colour a circle each time Margo gets a new accessory · 8 of 8 = you are officially unbothered", W / 2, t + 110, "SansI", 9.4, MUTED, "c")
    txt(c, "the rewards are in the sticker book →", W / 2, t + 130, "SansB", 8.4, PINK, "c", 0.6); link(c, "s7", W / 2 - 120, t + 112, 240, 26)
    d.end()


def howto(d):
    c = d.page("howto", "How it works", 0, active="HOME", seq=("profile", "cy_over"))
    head(c, "How it works", "the scales, the legend, the rules", TANG, "q_hotgirlera", 92)
    card(c, ML, 150, CW, 150, "The idea", PINK)
    t = para(c, "Perimenopause is the stretch of years before periods stop for good, when hormones swing and cycles, sleep, moods and temperature stop behaving. "
                "Tracking is how you turn “I feel weird” into a pattern you can show a doctor and act on. Margo is here to make it less clinical.", ML + 20, 186, CW - 40, "Sans", 10, INK)
    para(c, "This planner is a tracking tool, not medical advice. Bring it to a clinician you trust.", ML + 20, t + 8, CW - 40, "SansI", 9.4, MUTED)
    # scales
    card(c, ML, 318, CW / 2 - 7, 300, "Hot flash scale", TANG)
    desc = ["warm, barely noticed", "warm, took off a layer", "sweaty, needed the fan", "soaked, stopped what I was doing", "furnace, had to leave the room"]
    for i, s in enumerate(desc):
        yy = 356 + i * 46
        stk(c, f"f{i + 1}", ML + 40, yy + 6, 38, maxw=34)
        box(c, ML + 66, yy - 2, 12, TANG, 3); txt(c, str(i + 1), ML + 72, yy + 7, "SansB", 7.6, TANG, "c")
        txt(c, s, ML + 90, yy + 7, "Sans", 9.2, INK)
    txt(c, "count flashes per day, tick the worst level", ML + 20, 596, "SansI", 8.6, MUTED)
    card(c, ML + CW / 2 + 7, 318, CW / 2 - 7, 300, "Mood & energy 1–5", MOCHA)
    for i, s in enumerate(("flat, fog, zero patience", "meh", "ok, functional", "good, steady", "on fire, in the best way")):
        yy = 356 + i * 46; x = ML + CW / 2 + 27
        circ(c, x + 8, yy + 3, 8, stroke=MOCHA, lw=0.9); txt(c, str(i + 1), x + 8, yy + 6, "SansB", 7.6, MOCHA, "c")
        txt(c, s, x + 26, yy + 7, "Sans", 9.2, INK)
    txt(c, "energy uses the same five, fog is a yes / no", ML + CW / 2 + 27, 596, "SansI", 8.6, MUTED)
    card(c, ML, 636, CW / 2 - 7, 190, "Period legend", PINK)
    leg = [("moon_new", "skipped / nothing"), ("drop1", "spotting"), ("drop2", "normal"), ("drop3", "heavy, clots, flooding")]
    for i, (stn, s) in enumerate(leg):
        yy = 674 + i * 36
        stk(c, stn, ML + 40, yy + 2, 26, maxw=30, ghost=False)
        circ(c, ML + 66, yy + 2, 6, stroke=PINK, lw=0.9, fill=(PINK if i == 3 else PINK_L if i == 2 else CARD))
        txt(c, s, ML + 82, yy + 6, "Sans", 9.2, INK)
    card(c, ML + CW / 2 + 7, 636, CW / 2 - 7, 190, "The 8 habit rules", TANG)
    for i, (_, title, cond, _) in enumerate(REWARDS):
        yy = 666 + i * 19; x = ML + CW / 2 + 27
        txt(c, f"{i + 1}  {title}:", x, yy + 6, "SansB", 8, TANG); txt(c, cond, x + 78, yy + 6, "Sans", 8, INK)
    card(c, ML, 846, CW, 206, "How to use it", MOCHA)
    steps = ["Every evening: one row in the daily log. Thirty seconds, no essays.", "Every day you keep a habit: colour its square on the month grid. Streaks unlock rewards.",
             "Every month: fill the cycle table and colour the Hot Map, then paste the month’s best Margo mood.", "Before the doctor: the summary, labs and questions pages are built to be shown as they are.",
             "Any time: the rage page. Nobody is reading it."]
    yy = 880
    for i, s in enumerate(steps):
        circ(c, ML + 28, yy - 3, 8, fill=TANG); txt(c, str(i + 1), ML + 28, yy, "SansB", 8, WHITE, "c")
        yy = para(c, s, ML + 46, yy, CW - 70, "Sans", 9.4, INK) + 8
    d.end()


# ---------------------------------------------------------------- cycle
def cycle(d):
    c = d.page("cy_over", "Cycle", 0, active="CYCLE", seq=("howto", "cy_hotmap"))
    head(c, "Cycle overview", "irregular is the point — write it all down", PINK, "moon_wax", 96)
    table(c, ML, 150, CW, [("Cycle", 1), ("Started", 2), ("Ended", 2), ("Length", 1.3), ("Bleed days", 1.5), ("Flow", 1.2), ("Notes", 4)], 14, 36, PINK, 26, PINK_L, [str(i) for i in range(1, 15)])
    t = 150 + 26 + 14 * 36 + 18
    card(c, ML, t, CW / 2 - 7, 1052 - t, "What counts as a change", PINK)
    checks(c, ML + 16, t + 22, CW / 2 - 39, ["7+ days shorter or longer than usual", "A skipped cycle", "A gap of 60+ days", "Much heavier or much lighter", "Spotting between periods", "12 months with no period = menopause"], 30, PINK, size=9)
    card(c, ML + CW / 2 + 7, t, CW / 2 - 7, 1052 - t, "Flow legend", PINK)
    for i, (stn, s) in enumerate((("moon_new", "none / skipped"), ("drop1", "spotting"), ("drop2", "normal"), ("drop3", "heavy, clots"))):
        yy = t + 52 + i * 34; x = ML + CW / 2 + 27
        stk(c, stn, x + 12, yy, 24, maxw=28); circ(c, x + 34, yy, 6, stroke=PINK, lw=0.9, fill=(PINK if i == 3 else PINK_L if i == 2 else CARD)); txt(c, s, x + 50, yy + 4, "Sans", 9.2, INK)
    txt(c, "usual cycle before all this:", ML + CW / 2 + 27, t + 200, "SansB", 7.4, TAUPE, tr=1.1); dotted(c, ML + CW / 2 + 200, CR - 20, t + 201)
    d.end()

    c = d.page("cy_hotmap", None, 0, active="CYCLE", seq=("cy_over", "cy_symptoms"))
    head(c, "Hot Map", "colour a square for every day — patterns show up fast", TANG, "d_flame", 92)
    for mi, (title, col, light, legend, top) in enumerate((("Hot flashes per day", TANG, TANG_L, (("0", CARD), ("1–2", PEACH), ("3–5", TANG), ("6+", PINK)), 150),
                                                           ("Nights under 6 hours or sweaty", MOCHA, MOCHA_L, (("slept fine", CARD), ("under 6h", PEACH), ("night sweat", TANG), ("both", PINK)), 600))):
        card(c, ML, top, CW, 430, title, col)
        gx = ML + 54; cwid = (CW - 70) / 31; rh = 28
        for dday in range(31):
            txt(c, str(dday + 1), gx + dday * cwid + cwid / 2, top + 48, "SansB", 6.2, MUTED, "c")
        for m in range(12):
            yy = top + 56 + m * rh
            txt(c, f"{m + 1:02d}", ML + 30, yy + rh / 2 + 3, "Num", 12, MOCHA, "c"); link(c, f"m{m + 1:02d}", ML + 16, yy, 34, rh)
            for dday in range(31):
                rr(c, gx + dday * cwid + 1, yy + 2, cwid - 2, rh - 4, 3, fill=WHITE, stroke=RULE2, lw=0.5)
        ly = top + 56 + 12 * rh + 22; lx = ML + 20
        for lab, fill in legend:
            rr(c, lx, ly - 9, 14, 14, 3, fill=fill, stroke=RULE, lw=0.6); txt(c, lab, lx + 20, ly + 2, "Sans", 8.6, INK); lx += 26 + stringWidth(lab, "Sans", 8.6) + 24
    txt(c, "the months are undated: 01 is whenever you start", W / 2, 1050, "SansI", 9, MUTED, "c")
    d.end()

    c = d.page("cy_symptoms", None, 0, active="CYCLE", seq=("cy_hotmap", "m01"))
    head(c, "Symptom checklist", "tick what is yours, write when it started", PINK, "m_fog", 96)
    groups = [("Heat & sleep", TANG, ["Hot flashes", "Night sweats", "Trouble falling asleep", "Waking at 3 am", "Chills", "Heart palpitations"]),
              ("Mood & brain", MOCHA, ["Irritability", "Anxiety", "Low mood", "Brain fog", "Forgetting words", "Crying at adverts"]),
              ("Cycle & body", PINK, ["Irregular cycles", "Heavy or long periods", "Spotting", "Breast tenderness", "Bloating", "New cramps"]),
              ("Everything else", TANG, ["Joint & muscle aches", "Headaches, migraines", "Dry skin, eyes, hair loss", "Weight around the middle", "Low libido, vaginal dryness", "Bladder changes, UTIs"])]
    for i, (ti, col, items) in enumerate(groups):
        x = ML + (i % 2) * (CW / 2 + 7); t = 150 + (i // 2) * 330; w = CW / 2 - 7
        card(c, x, t, w, 314, ti, col)
        txt(c, "MINE", x + 16, t + 40, "SansB", 6.6, TAUPE, tr=1); txt(c, "SINCE", x + w - 90, t + 40, "SansB", 6.6, TAUPE, tr=1)
        checks(c, x + 16, t + 38, w - 32, items, 32, col, size=9.2, extra_lines=2)
    t = 150 + 2 * 330 + 4
    card(c, ML, t, CW, 1052 - t, "The three that bother me most", PINK)
    for i in range(3):
        circ(c, ML + 28, t + 56 + i * 32, 8, stroke=PINK, lw=0.9); txt(c, str(i + 1), ML + 28, t + 59 + i * 32, "SansB", 8.4, PINK, "c"); dotted(c, ML + 46, CR - 20, t + 60 + i * 32)
    d.end()


# ---------------------------------------------------------------- monthly log + habits
HABITS = ["Sleep 7h+", "Strength", "Protein", "Water 2L", "Supplements", "Daily log filled", "Walk / steps", "No alcohol"]
HABIT_REWARD = [0, 1, 2, 3, 4, 6, None, None]   # row -> index in REWARDS (folder and crown are earned on the profile page)


def months(d):
    for m in range(1, 13):
        mm = f"{m:02d}"; prv = f"h{m - 1:02d}" if m > 1 else "cy_symptoms"
        # -- daily log
        c = d.page(f"m{mm}", "Daily log" if m == 1 else None, 0, active="LOG", seq=(prv, f"h{mm}"))
        txt(c, f"Month {mm}", ML, 84, "Disp", 40, INK); txt(c, "DAILY LOG  ·  ONE ROW A NIGHT", ML + 2, 108, "SansB", 8.4, TANG, tr=1.8)
        txt(c, "MONTH", ML + 290, 84, "SansB", 7.2, TAUPE, tr=1.2); dotted(c, ML + 334, ML + 470, 86)
        txt(c, "YEAR", ML + 290, 108, "SansB", 7.2, TAUPE, tr=1.2); dotted(c, ML + 334, ML + 470, 110)
        stk(c, ["m_fan", "m_icewater", "m_window", "m_thermostat", "m_fog", "m_lifting", "m_sleepmask", "m_nightsweat", "m_rage", "m_tears", "m_shrug", "m_crown"][m - 1], CR - 60, 84, 96, 0, maxw=130)
        cols = [("Day", 28), ("Period", 30), ("Hot flashes", 76), ("Night sweat", 44), ("Sleep h", 42), ("Mood", 76), ("Fog", 30), ("Energy", 76), ("Notes", 0)]
        fixed = sum(w for _, w in cols); cols[-1] = ("Notes", CW - fixed)
        top = 134; rh = 28; hh = 30
        rr(c, ML, top, CW, hh + 31 * rh, 12, fill=CARD, stroke=RULE, lw=0.7)
        c.saveState(); p = c.beginPath(); p.roundRect(ML, Y(top) - hh, CW, hh, 12); c.clipPath(p, stroke=0, fill=0); c.setFillColor(TANG_L); c.rect(ML, Y(top) - hh, CW, hh, stroke=0, fill=1); c.restoreState()
        x = ML; xs = []
        for lab, w in cols:
            xs.append(x)
            txt(c, lab.upper(), x + w / 2, top + 13, "SansB", 6.3, MOCHA, "c", 0.5)
            if lab in ("Hot flashes", "Mood", "Energy"):
                for k in range(5):
                    txt(c, str(k + 1), x + 8 + k * 13 + 4.5, top + 25, "Sans", 6, MUTED, "c")
            x += w
            if w and x < CR - 1:
                vline(c, x, top + 4, top + hh + 31 * rh - 4, RULE2, 0.5)
        for i in range(31):
            yy = top + hh + i * rh
            if i % 2:
                rr(c, ML + 2, yy, CW - 4, rh, 0, fill=HexColor("#FBF7EE"))
            hline(c, ML + 6, CR - 6, yy + rh, RULE2, 0.5)
            txt(c, str(i + 1), xs[0] + 14, yy + rh / 2 + 4, "Num", 12, MOCHA, "c")
            circ(c, xs[1] + 15, yy + rh / 2, 6.5, stroke=PINK, lw=0.8)
            scale5(c, xs[2] + 8, yy + rh / 2 - 4.5, 9, 4, TANG)
            box(c, xs[3] + 16, yy + rh / 2 - 5, 10, MOCHA)
            dotted(c, xs[4] + 6, xs[4] + 36, yy + rh / 2 + 4)
            for k in range(5):
                circ(c, xs[5] + 8 + k * 13 + 4.5, yy + rh / 2, 4.5, stroke=MOCHA, lw=0.7)
            box(c, xs[6] + 10, yy + rh / 2 - 5, 10, MOCHA)
            scale5(c, xs[7] + 8, yy + rh / 2 - 4.5, 9, 4, PINK)
            dotted(c, xs[8] + 6, CR - 10, yy + rh / 2 + 4)
        txt(c, "period: fill the circle for flow (empty = none, half = spotting, full = heavy)  ·  hot flashes: tick the worst level that day", W / 2, top + hh + 31 * rh + 16, "SansI", 8.2, MUTED, "c")
        month_strip(c, m); d.end()

        # -- habits
        nxt = f"m{m + 1:02d}" if m < 12 else "b_strength"
        c = d.page(f"h{mm}", "Habit grids" if m == 1 else None, 0, active="LOG", seq=(f"m{mm}", nxt))
        txt(c, f"Month {mm}", ML, 84, "Disp", 40, INK); txt(c, "HABITS  ·  COLOUR A SQUARE, EARN A REWARD", ML + 2, 108, "SansB", 8.4, TANG, tr=1.8)
        stk(c, REWARDS[(m - 1) % 8][0], CR - 60, 84, 80, 0, maxw=110)
        top = 150; lw_ = 118; sw_ = 44; gx = ML + lw_; cwid = (CW - lw_ - sw_) / 31; rh = 40
        rr(c, ML, top, CW, 30 + 8 * rh, 12, fill=CARD, stroke=RULE, lw=0.7)
        for dday in range(31):
            txt(c, str(dday + 1), gx + dday * cwid + cwid / 2, top + 20, "SansB", 6.2, MUTED, "c")
        txt(c, "STREAK", CR - sw_ / 2, top + 20, "SansB", 6.2, MUTED, "c", 0.6)
        for hi, hname in enumerate(HABITS):
            yy = top + 30 + hi * rh
            hline(c, ML + 6, CR - 6, yy, RULE2, 0.5)
            txt(c, hname, ML + 14, yy + rh / 2 + 3.5, "SansM", 9.4, INK)
            txt(c, f"→ {REWARDS[HABIT_REWARD[hi]][1].lower()}" if HABIT_REWARD[hi] is not None else "bonus, no reward", ML + 14, yy + rh / 2 + 14, "SansI", 7, TANG if HABIT_REWARD[hi] is not None else MUTED)
            for dday in range(31):
                rr(c, gx + dday * cwid + 1.5, yy + 6, cwid - 3, rh - 12, 3, fill=WHITE, stroke=RULE2, lw=0.5)
            rr(c, CR - sw_ + 6, yy + 8, sw_ - 14, rh - 16, 6, stroke=TANG, lw=0.8, dash=(2, 3))
        t = top + 30 + 8 * rh + 18
        card(c, ML, t, CW / 2 - 7, 284, "What helped", TANG); lines(c, ML + 16, t + 24, CW / 2 - 39, 8, 30)
        card(c, ML + CW / 2 + 7, t, CW / 2 - 7, 284, "What made it worse", PINK); lines(c, ML + CW / 2 + 23, t + 24, CW / 2 - 39, 8, 30)
        t += 284 + 14
        card(c, ML, t, CW, 1052 - t, "Unlocked this month", PINK)
        for i, (stn, title, _, _) in enumerate(REWARDS):
            cx = ML + 52 + i * ((CW - 104) / 7)
            rr(c, cx - 30, t + 36, 60, 60, 12, stroke=RULE, lw=0.8, dash=(3, 4), fill=WHITE)
            stk(c, stn, cx, t + 66, 40, maxw=44)
            txt(c, title, cx, t + 112, "Sans", 7.6, MUTED, "c")
        txt(c, "MONTH IN THREE WORDS", ML + 20, t + 150, "SansB", 7.2, TAUPE, tr=1.2); dotted(c, ML + 170, CR - 20, t + 151)
        month_strip(c, m); d.end()


# ---------------------------------------------------------------- body
def body(d):
    c = d.page("b_strength", "Body", 0, active="BODY", seq=("h12", "b_measure"))
    head(c, "Strength", "muscle and bone are the long game — 2 to 3 sessions a week", TANG, "m_lifting", 104)
    table(c, ML, 150, CW, [("Week", 1), ("Session 1", 3), ("Session 2", 3), ("Session 3", 3), ("Felt", 1.6)], 12, 44, TANG, 26, TANG_L, [f"W{i}" for i in range(1, 13)])
    t = 150 + 26 + 12 * 44 + 18
    card(c, ML, t, CW / 2 - 7, 1052 - t, "My lifts and numbers", MOCHA)
    table(c, ML + 14, t + 30, CW / 2 - 35, [("Move", 2.5), ("Start", 1), ("Now", 1)], 6, 32, MOCHA, 22, MOCHA_L, ["Squat", "Hinge", "Push", "Pull", "Carry", ""], 8.8)
    card(c, ML + CW / 2 + 7, t, CW / 2 - 7, 1052 - t, "Walks, steps, stretches", TANG); lines(c, ML + CW / 2 + 23, t + 24, CW / 2 - 39, 7, 30)
    d.end()

    c = d.page("b_measure", None, 0, active="BODY", seq=("b_strength", "b_triggers"))
    head(c, "Numbers", "only the ones that help — skip any you like", MOCHA, "a_bottle", 96)
    table(c, ML, 150, CW, [("Month", 1.2), ("Weight", 1.4), ("Waist", 1.3), ("Blood pressure", 2), ("Resting HR", 1.6), ("Notes", 3.5)], 12, 42, MOCHA, 26, MOCHA_L, [f"{i:02d}" for i in range(1, 13)])
    t = 150 + 26 + 12 * 42 + 18
    card(c, ML, t, CW, 1052 - t, "Protein & water goals", TANG)
    for i, lab in enumerate(("Protein goal (g / day)", "Water goal (L / day)", "Steps goal", "Bedtime")):
        x = ML + 20 + (i % 2) * (CW / 2); yy = t + 50 + (i // 2) * 48
        txt(c, lab.upper(), x, yy, "SansB", 7.4, TAUPE, tr=1.2); dotted(c, x, x + CW / 2 - 40, yy + 24)
    txt(c, "a rule of thumb many clinicians use: 1.2–1.6 g protein per kg of body weight. Check yours with your doctor.", ML + 20, t + 166, "SansI", 8.8, MUTED)
    d.end()

    c = d.page("b_triggers", None, 0, active="BODY", seq=("b_measure", "c_meds"))
    head(c, "Triggers", "what set it off, what it set off", PINK, "m_nowine", 100)
    table(c, ML, 150, CW, [("Date", 1.3), ("Trigger", 3), ("What happened", 3.4), ("How bad", 1.3), ("Again?", 1.1)], 16, 38, PINK, 26, PINK_L)
    t = 150 + 26 + 16 * 38 + 18
    card(c, ML, t, CW, 1052 - t, "Usual suspects", PINK)
    sus = ["Coffee", "Alcohol", "Spicy food", "Sugar", "Hot rooms", "Stress", "Tight clothes", "Late screens", "Skipped meals", "Hot showers", "Dehydration", "Arguments"]
    for i, s in enumerate(sus):
        x = ML + 20 + (i % 4) * ((CW - 40) / 4); yy = t + 54 + (i // 4) * 34
        box(c, x, yy - 9, 11, PINK); txt(c, s, x + 18, yy, "Sans", 9.2, INK)
    d.end()


# ---------------------------------------------------------------- care
def care(d):
    c = d.page("c_meds", "Doctor & care", 0, active="CARE", seq=("b_triggers", "c_supps"))
    head(c, "Meds & HRT", "what, how much, since when, how it went", PINK, "m_pills", 100)
    table(c, ML, 150, CW, [("Name", 2.6), ("Dose", 1.4), ("Started", 1.4), ("Stopped", 1.4), ("Effect / side effects", 3.6)], 10, 40, PINK, 26, PINK_L)
    t = 150 + 26 + 10 * 40 + 18
    card(c, ML, t, CW, 1052 - t, "Questions I have about treatment", MOCHA)
    checks(c, ML + 16, t + 22, CW - 32, ["Am I a candidate for HRT? Which type and form?", "What are my personal risks and benefits?", "Non-hormonal options for hot flashes and sleep?", "Local estrogen for dryness or bladder symptoms?", "How long before we review?"], 30, MOCHA, size=9.2, extra_lines=3)
    d.end()

    c = d.page("c_supps", None, 0, active="CARE", seq=("c_meds", "c_summary"))
    head(c, "Supplements", "the potion shelf — 14 days on time unlocks the potion", TANG, "a_potion", 96)
    table(c, ML, 150, CW, [("Supplement", 2.4), ("Dose & time", 1.8), ("Why", 2.4), ("Started", 1.2), ("Noticed", 2.4)], 9, 40, TANG, 26, TANG_L, ["Magnesium", "Vitamin D", "Omega-3", "Creatine", "Iron", "", "", "", ""])
    t = 150 + 26 + 9 * 40 + 18
    card(c, ML, t, CW, 236, "14-day on-time streak", TANG)
    for r_ in range(3):
        for i in range(14):
            cx = ML + 40 + i * ((CW - 80) / 13); yy = t + 60 + r_ * 58
            circ(c, cx, yy, 14, stroke=TANG, lw=0.9, fill=TANG_XL); txt(c, str(i + 1), cx, yy + 3.5, "Sans", 8, TANG, "c")
    txt(c, "always check supplements against your meds with a pharmacist", W / 2, t + 222, "SansI", 8.8, MUTED, "c")
    t += 236 + 14
    card(c, ML, t, CW / 2 - 7, 1052 - t, "What I noticed", MOCHA); lines(c, ML + 16, t + 24, CW / 2 - 39, int((1052 - t - 44) / 30), 30)
    card(c, ML + CW / 2 + 7, t, CW / 2 - 7, 1052 - t, "To ask the pharmacist", PINK); lines(c, ML + CW / 2 + 23, t + 24, CW / 2 - 39, int((1052 - t - 44) / 30), 30)
    d.end()

    c = d.page("c_summary", None, 0, active="CARE", seq=("c_supps", "c_questions"))
    head(c, "For the doctor", "the one-page summary — show it exactly like this", PINK, "m_doctor", 104)
    for i, lab in enumerate(("Date of visit", "Doctor", "Last period", "Usual cycle length")):
        x = ML + (i % 2) * (CW / 2); yy = 162 + (i // 2) * 34; txt(c, lab.upper(), x, yy, "SansB", 7.4, TAUPE, tr=1.2); dotted(c, x + 120, x + CW / 2 - 24, yy + 1)
    table(c, ML, 240, CW, [("Symptom", 2.6), ("How often", 1.6), ("How bad 1–5", 1.4), ("Since", 1.3), ("Worst time", 1.6), ("Tried", 2)], 12, 36, PINK, 26, PINK_L,
          ["Hot flashes", "Night sweats", "Sleep", "Mood / anxiety", "Brain fog", "Cycle changes", "Joints / aches", "Headaches", "Libido / dryness", "Bladder", "", ""], 9)
    t = 240 + 26 + 12 * 36 + 16
    card(c, ML, t, CW / 2 - 7, 1052 - t, "Family history", MOCHA)
    checks(c, ML + 16, t + 22, CW / 2 - 39, ["Breast cancer", "Blood clots / stroke", "Heart disease", "Osteoporosis", "Early menopause"], 28, MOCHA, size=9, extra_lines=1)
    card(c, ML + CW / 2 + 7, t, CW / 2 - 7, 1052 - t, "What I want from this visit", PINK); lines(c, ML + CW / 2 + 23, t + 24, CW / 2 - 39, 6, 28)
    d.end()

    c = d.page("c_questions", None, 0, active="CARE", seq=("c_summary", "c_labs"))
    head(c, "Questions", "write them before, tick them during, note the answers", MOCHA, "q_askdoctor", 96)
    for i in range(7):
        t = 150 + i * 126
        rr(c, ML, t, CW, 114, 12, fill=CARD, stroke=RULE, lw=0.7)
        circ(c, ML + 24, t + 24, 9, stroke=MOCHA, lw=0.9); txt(c, str(i + 1), ML + 24, t + 27.5, "SansB", 8.6, MOCHA, "c")
        txt(c, "Q", ML + 44, t + 28, "SansB", 7.4, TAUPE, tr=1.2); dotted(c, ML + 60, CR - 40, t + 29)
        box(c, CR - 30, t + 18, 12, MOCHA, 3)
        txt(c, "A", ML + 44, t + 60, "SansB", 7.4, TAUPE, tr=1.2); dotted(c, ML + 60, CR - 20, t + 61); dotted(c, ML + 60, CR - 20, t + 89)
    d.end()

    c = d.page("c_labs", None, 0, active="CARE", seq=("c_questions", "c_annual"))
    head(c, "Labs", "FSH alone does not diagnose perimenopause — track the set", PINK, "l_labs", 60)
    table(c, ML, 150, CW, [("Test", 2.6), ("Date", 1.4), ("Result", 1.6), ("Range", 1.6), ("Notes", 3)], 18, 36, PINK, 26, PINK_L,
          ["FSH", "Estradiol", "LH", "AMH", "TSH / thyroid", "Vitamin D", "Ferritin / iron", "Full blood count", "Lipids / cholesterol", "HbA1c / glucose", "B12", "Liver function", "", "", "", "", "", ""], 9)
    t = 150 + 26 + 18 * 36 + 16
    txt(c, "hormone levels swing day to day in perimenopause: one normal result does not cancel your symptoms.", ML, t + 12, "SansI", 9, MUTED)
    t += 30
    card(c, ML, t, CW / 2 - 7, 1052 - t, "Tests to ask about next time", PINK); lines(c, ML + 16, t + 24, CW / 2 - 39, int((1052 - t - 44) / 30), 30)
    card(c, ML + CW / 2 + 7, t, CW / 2 - 7, 1052 - t, "What the results changed", MOCHA); lines(c, ML + CW / 2 + 23, t + 24, CW / 2 - 39, int((1052 - t - 44) / 30), 30)
    d.end()

    c = d.page("c_annual", None, 0, active="CARE", seq=("c_labs", "mi_journal1"))
    head(c, "Checks & visits", "the yearly admin of being a grown woman", MOCHA, "a_folder", 90)
    card(c, ML, 150, CW, 360, "Screening checklist", MOCHA)
    left = ["Mammogram", "Cervical screening", "Bone density (DEXA)", "Blood pressure", "Cholesterol", "Blood sugar"]
    right = ["Dental", "Eyes", "Skin check", "Colon screening", "Pelvic exam", "Vaccines"]
    txt(c, "DONE", ML + 16, 184, "SansB", 6.6, TAUPE, tr=1); txt(c, "DATE / NEXT DUE", ML + CW / 2 - 140, 184, "SansB", 6.6, TAUPE, tr=1)
    checks(c, ML + 16, 184, CW / 2 - 39, left, 44, MOCHA, size=9.4)
    checks(c, ML + CW / 2 + 16, 184, CW / 2 - 39, right, 44, MOCHA, size=9.4)
    txt(c, "intervals depend on age, country and history: ask what applies to you", ML + 16, 496, "SansI", 8.6, MUTED)
    table(c, ML, 530, CW, [("Date", 1.4), ("Who", 2.4), ("Why", 3), ("Outcome / next step", 3.2)], 12, 40, PINK, 26, PINK_L)
    txt(c, "appointments", ML + 2, 524, "SansB", 7.4, PINK, tr=1.4)
    d.end()


# ---------------------------------------------------------------- mind
PROMPTS = [["What my body is asking for this week, if I actually listen.", "A thing I put up with at 25 that I am done with now.", "Who gets my energy, and who has been getting it for free."],
           ["The version of me at 60 looks back at this year and says...", "Three things that felt good in my body today, however small.", "What I am grieving, and what I am quietly gaining."]]


def mind(d):
    for pi, prompts in enumerate(PROMPTS):
        pid = f"mi_journal{pi + 1}"; prv = "c_annual" if pi == 0 else "mi_journal1"; nxt = "mi_journal2" if pi == 0 else "mi_rage"
        c = d.page(pid, "Mind" if pi == 0 else None, 0, active="MIND", seq=(prv, nxt))
        head(c, "Journal", "three prompts, no right answers", MOCHA, ("m_reading", "m_bath")[pi], 104)
        for i, s in enumerate(prompts):
            t = 150 + i * 300
            card(c, ML, t, CW, 286, f"Prompt {i + 1}", (MOCHA, TANG, PINK)[i])
            para(c, s, ML + 20, t + 50, CW - 40, "DispI", 14, INK)
            lines(c, ML + 20, t + 62, CW - 40, 7, 30)
        d.end()

    c = d.page("mi_rage", None, 0, active="MIND", seq=("mi_journal2", "mi_wins"))
    head(c, "Rage page", "scribble. nobody is reading this.", PINK, "m_rage", 104)
    rr(c, ML, 150, CW, 640, 18, fill=CARD, stroke=PINK, lw=1, dash=(4, 5))
    flame(c, ML + 40, 190, 22); flame(c, CR - 40, 190, 22, PINK, TANG); flame(c, ML + 40, 760, 22, PINK, TANG); flame(c, CR - 40, 760, 22)
    txt(c, "scream here", W / 2, 475, "Script", 44, PINK_L, "c")
    card(c, ML, 806, CW / 2 - 7, 1052 - 806, "What actually set it off", MOCHA); lines(c, ML + 16, 830, CW / 2 - 39, 6, 32)
    card(c, ML + CW / 2 + 7, 806, CW / 2 - 7, 1052 - 806, "What I need right now", TANG); lines(c, ML + CW / 2 + 23, 830, CW / 2 - 39, 6, 32)
    d.end()

    c = d.page("mi_wins", None, 0, active="MIND", seq=("mi_rage", "mi_done"))
    head(c, "Wins", "the boring ones count double", TANG, "m_crown", 100)
    table(c, ML, 150, CW, [("Date", 1.3), ("The win", 5), ("How it felt", 3)], 22, 38, TANG, 26, TANG_L)
    txt(c, "slept through · said no · lifted heavier · asked the question · wore the thing", W / 2, 1040, "SansI", 9, MUTED, "c")
    d.end()

    c = d.page("mi_done", None, 0, active="MIND", seq=("mi_wins", "mi_energy"))
    head(c, "Done with · into now", "the edit of a lifetime", MOCHA, "m_dance", 104)
    card(c, ML, 150, CW / 2 - 7, 880, "Done with", PINK); checks(c, ML + 16, 172, CW / 2 - 39, ["Apologising for taking up space", "Hot rooms", ""], 40, PINK, size=9.4, extra_lines=17)
    card(c, ML + CW / 2 + 7, 150, CW / 2 - 7, 880, "Into now", TANG); checks(c, ML + CW / 2 + 23, 172, CW / 2 - 39, ["Early nights", "Heavy weights", ""], 40, TANG, size=9.4, extra_lines=17)
    d.end()

    c = d.page("mi_energy", None, 0, active="MIND", seq=("mi_done", "n_lined1"))
    head(c, "Energy audit", "what drains, what fills, what I will protect", TANG, "m_hug", 104)
    card(c, ML, 150, CW / 2 - 7, 540, "Drains me", MOCHA); lines(c, ML + 16, 174, CW / 2 - 39, 15, 32)
    card(c, ML + CW / 2 + 7, 150, CW / 2 - 7, 540, "Fills me", TANG); lines(c, ML + CW / 2 + 23, 174, CW / 2 - 39, 15, 32)
    card(c, ML, 708, CW, 1052 - 708, "This week I will protect", PINK)
    for i in range(3):
        circ(c, ML + 28, 758 + i * 40, 9, stroke=PINK, lw=0.9); txt(c, str(i + 1), ML + 28, 761 + i * 40, "SansB", 8.4, PINK, "c"); dotted(c, ML + 48, CR - 20, 762 + i * 40)
    txt(c, "one non-negotiable: ", ML + 20, 912, "SansB", 7.4, TAUPE, tr=1.2); dotted(c, ML + 140, CR - 20, 913)
    d.end()


def notes(d):
    kinds = [("lined", "Lined", 3), ("dot", "Dotted", 2), ("grid", "Grid", 2)]
    order = [(k, label, n) for k, label, cnt in kinds for n in range(1, cnt + 1)]
    for idx, (kind, label, n) in enumerate(order):
        pid = f"n_{kind}{n}"
        prv = f"n_{order[idx - 1][0]}{order[idx - 1][2]}" if idx else "mi_energy"
        nxt = f"n_{order[idx + 1][0]}{order[idx + 1][2]}" if idx < len(order) - 1 else "s1"
        c = d.page(pid, "Notes" if idx == 0 else None, 0, active="NOTES", dots=(kind == "dot"), seq=(prv, nxt))
        txt(c, label, ML, 78, "Disp", 32, INK); txt(c, f"NOTES  ·  {n}", ML + 2, 98, "SansB", 7.8, TAUPE, tr=1.7)
        txt(c, "DATE", CR - 200, 78, "SansB", 7.2, TAUPE, tr=1.2); dotted(c, CR - 170, CR, 80)
        arcs(c, ML + 170, 96, 14, (TANG, PINK), PAPER)
        if kind == "lined":
            for y in range(130, 1060, 30):
                hline(c, ML, CR, y, RULE, 0.6)
        elif kind == "grid":
            c.saveState(); c.setStrokeColor(RULE2); c.setLineWidth(0.5)
            for y in range(130, 1062, 26):
                c.line(ML, Y(y), CR, Y(y))
            for x in range(ML, CR + 1, 26):
                c.line(x, Y(130), x, Y(130 + ((1060 - 130) // 26) * 26))
            c.restoreState()
        d.end()


# ---------------------------------------------------------------- sticker book
BOOK = [
    ("Margo moods", "tap, lasso, paste anywhere", TANG, ["m_fan", "m_icewater", "m_window", "m_thermostat", "m_fog", "m_lifting", "m_sleepmask", "m_nightsweat", "m_rage", "m_tears", "m_shrug", "m_crown",
                                                       "m_doctor", "m_nocoffee", "m_nowine", "m_protein", "m_pills", "m_walk", "m_bath", "m_reading", "m_scroll3am", "m_dance", "m_hug", "m_coffee_ok"]),
    ("Symptom labels", "name it to tame it", PINK, ["l_hotflash", "l_nightsweat", "l_sleep", "l_mood", "l_brainfog", "l_headache", "l_joints", "l_bloating", "l_palpitations", "l_energy",
                                                  "l_libido", "l_period", "l_spotting", "l_skipped", "l_heavy", "l_cramps", "l_anxiety", "l_irritable", "l_tears", "l_dry"]),
    ("Care & body labels", "for the doctor pages and the grids", MOCHA, ["l_doctor", "l_labs", "l_meds", "l_hrt", "l_supplements", "l_water", "l_protein", "l_workout", "l_steps", "l_win"]),
    ("Scales & cycle", "thermometers, moons, drops", TANG, ["f1", "f2", "f3", "f4", "f5", "moon_new", "moon_wax", "moon_full", "moon_wane", "drop1", "drop2", "drop3", "x_ice", "x_thermostat", "x_window"]),
    ("Build your Hot Girl", "Margo and the 8 rewards", PINK, ["base_margo", "a_sleepmask", "a_dumbbell", "a_shaker", "a_bottle", "a_potion", "a_folder", "a_fan", "a_crown"]),
    ("Little quotes", "for the days you need them", MOCHA, ["q_nottoday", "q_estrogen", "q_maincharacter", "q_openwindow", "q_hotgirlera", "q_unbothered", "q_imfine", "q_fogmode", "q_plottwist", "q_stillhot", "q_rest", "q_askdoctor"]),
    ("Washi & decor", "the pretty stuff", TANG, ["washi_tang", "washi_pink", "washi_check", "d_frame", "d_banner", "d_arrow", "d_heart", "d_lipstick", "d_sunglasses", "d_icedcoffee", "d_cat", "d_flame"]),
]


def sticker_pages(d, chrome=True):
    pages = []
    for ti, sub, col, names in BOOK:
        for k in range(0, len(names), 15):
            pages.append((ti, sub, col, names[k:k + 15], k // 15, len(names) > 15))
    cw, ch = CW / 3, 168
    for pi, (ti, sub, col, names, part, multi) in enumerate(pages):
        pid = f"s{pi + 1}"
        prv = f"s{pi}" if pi else "n_grid2"
        nxt = f"s{pi + 2}" if pi < len(pages) - 1 else None
        c = d.page(pid, "Sticker book" if pi == 0 else None, 0, active="STICKERS", seq=(prv, nxt)) if chrome else d.page(pid, ti if part == 0 else None, 0, chrome=False)
        head(c, ti + (f" · {part + 1}" if multi else ""), sub, col, None, size=36)
        stk(c, names[0], CR - 60, 84, 84, 4, maxw=120)
        for i, n in enumerate(names):
            cx = ML + (i % 3) * cw + cw / 2; cy = 160 + (i // 3) * (ch + 10) + ch / 2
            rr(c, ML + (i % 3) * cw + 4, cy - ch / 2, cw - 8, ch, 12, fill=CARD, stroke=RULE2, lw=0.6)
            stk(c, n, cx, cy, ch - 24, 0, maxw=cw - 36, ghost=True)
        if not chrome:
            txt(c, f"{NAME} · perimenopause sticker pack", W / 2, 1076, "SansI", 9, MUTED, "c")
        d.end()
    return len(pages)


def main():
    path = os.path.join(OUT, "Hot_Girl_Era_Perimenopause_Planner.pdf")
    d = Doc(path)
    cover(d); home(d); profile(d); howto(d)
    cycle(d); months(d); body(d); care(d); mind(d); notes(d); sticker_pages(d)
    d.c.save(); lighten(path)
    print(path, d.n, "pages", round(os.path.getsize(path) / 1e6, 1), "MB")
    pack_path = os.path.join(OUT, "Hot_Girl_Era_Sticker_Pack.pdf")
    pk = Doc(pack_path); pk.c.setTitle(f"{NAME} Sticker Pack"); pk.c.setSubject("102 digital perimenopause planner stickers for GoodNotes")
    sticker_pages(pk, chrome=False); pk.c.save(); lighten(pack_path)
    print(pack_path, pk.n, "pages", round(os.path.getsize(pack_path) / 1e6, 1), "MB")
    if MISSING:
        print(f"{len(MISSING)} stickers not on disk yet (skipped):", " ".join(sorted(MISSING)))


if __name__ == "__main__":
    main()
