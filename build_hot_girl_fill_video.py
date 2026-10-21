#!/usr/bin/env python3
"""Screen-recording style video of a woman filling in the Hot Girl Era perimenopause tracker with an Apple Pencil.

Six scenes (profile + first reward on Margo, daily log rows, the Hot Map, a habit grid with a reward, the doctor summary, cover)
and the same engine as build_wedding_fill_video.py: handwriting (Caveat) revealed left to right with a pencil at the tip,
ticks drawn stroke by stroke, fills and stickers pop in, a virtual camera pans and zooms, scenes crossfade.

Run:  .venv-planner/bin/python build_hot_girl_fill_video.py
Output: images/hot_girl/video/video_fill_{vertical,square}.mp4
"""
import math
import os
import random
import subprocess

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__)); WD = os.path.join(ROOT, "images", "hot_girl")
PDF = os.path.join(WD, "Hot_Girl_Era_Perimenopause_Planner.pdf"); OUT = os.path.join(WD, "video"); os.makedirs(OUT, exist_ok=True)
SC = 3; FPS = 30
INK = (62, 44, 38, 255); TANG = (232, 112, 58, 255); PINK = (229, 69, 122, 255); PEACH = (248, 217, 195, 255); MOCHA = (107, 74, 58, 255)
random.seed(11)
HAND = ImageFont.truetype(os.path.join(ROOT, "fonts", "Caveat-SemiBold.ttf"), 17 * SC)
PAGES = dict(profile=3, m01=8, cy_hotmap=6, h01=9, c_summary=37, cover=1)


def render_page(key):
    f = os.path.join(WD, "pages_png", f"fill_{key}")
    subprocess.run(["pdftoppm", "-f", str(PAGES[key]), "-l", str(PAGES[key]), "-r", str(72 * SC), "-png", "-singlefile", PDF, f], check=True)
    return Image.open(f + ".png").convert("RGBA")


def ease(t):
    t = min(max(t, 0), 1); return 0.5 - 0.5 * math.cos(math.pi * t)


class Ev:
    def __init__(self, kind, dur, layer, pos, cam, tip=None):
        self.kind, self.dur, self.layer, self.pos, self.cam, self.tip = kind, dur, layer, pos, cam, tip   # pos: top-left px in page; cam: (cx, cy, width) in pt


def text_layer(s, col=INK, size=None):
    font = HAND if size is None else ImageFont.truetype(os.path.join(ROOT, "fonts", "Caveat-SemiBold.ttf"), int(size * SC))
    w = int(font.getlength(s)) + 30; h = int(font.size * 1.5); im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 8
    for ch in s:
        dy = random.uniform(-2.0, 2.0); d.text((x, int(font.size * .15) + dy), ch, font=font, fill=col); x += font.getlength(ch) + random.uniform(-.8, .8)
    return im, int(x) + 4


def write(x_pt, base_pt, s, cam, col=INK, size=15, speed=0.028):
    """handwritten line whose baseline sits at base_pt (page pt, top-based)."""
    im, wpx = text_layer(s, col, size); font_size = im.height / 1.5
    return Ev("wipe", max(.3, len(s) * speed), im, (int(x_pt * SC) - 8, int(base_pt * SC - font_size * 1.0)), cam, wpx)


def tick(cx_pt, cy_pt, cam, col=INK):
    r = 7 * SC; im = Image.new("RGBA", (r * 3, r * 3), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(r * .5, r * 1.5), (r * 1.1, r * 2.2), (r * 2.4, r * .5)]; d.line(pts, fill=col, width=int(1.8 * SC), joint="curve")
    return Ev("stroke", .45, im, (int(cx_pt * SC - r * 1.5 + 2 * SC), int(cy_pt * SC - r * 1.7)), cam, pts)


def sticker_ev(name, cx_pt, cy_pt, h_pt, cam, rot=0):
    s = Image.open(os.path.join(WD, "cut_2x", name + ".png")).convert("RGBA"); h = int(h_pt * SC); s = s.resize((int(s.width * h / s.height), h), Image.LANCZOS)
    if rot:
        s = s.rotate(rot, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", (s.width + 80, s.height + 80), (0, 0, 0, 0)); a = Image.new("L", sh.size, 0); a.paste(s.getchannel("A"), (40, 50)); a = a.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * .35))
    sh.putalpha(a); sh.alpha_composite(s, (40, 40))
    return Ev("pop", .6, sh, (int(cx_pt * SC - sh.width / 2), int(cy_pt * SC - sh.height / 2)), cam)


# ---------------------------------------------------------------- fills
def fill(cx_pt, cy_pt, w_pt, h_pt, cam, col=TANG, shape="rect", dur=.25):
    """A coloured square or disk popping into a grid cell (the "colour a square" gesture)."""
    w, h = max(2, int(w_pt * SC)), max(2, int(h_pt * SC)); im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    (d.ellipse if shape == "disk" else d.rounded_rectangle)((0, 0, w - 1, h - 1), **({} if shape == "disk" else {"radius": int(2 * SC)}), fill=col)
    return Ev("pop", dur, im, (int(cx_pt * SC - w / 2), int(cy_pt * SC - h / 2)), cam)


def small_tick(cx_pt, cy_pt, cam, col=INK):
    r = 4.2 * SC; im = Image.new("RGBA", (int(r * 3), int(r * 3)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(r * .5, r * 1.5), (r * 1.1, r * 2.2), (r * 2.4, r * .5)]; d.line(pts, fill=col, width=int(1.6 * SC), joint="curve")
    return Ev("stroke", .3, im, (int(cx_pt * SC - r * 1.45), int(cy_pt * SC - r * 1.5)), cam, pts)


# ---------------------------------------------------------------- scenes (page coordinates in pt, 834 x 1112, top-based)
FULL = (417, 556, 834)


def scene_profile():
    A = (345, 210, 620); B = (300, 560, 620); C = (417, 900, 700)
    ev = [("pause", .6, FULL)]
    ev += [write(108, 193, "Vera", A), write(346, 193, "47", A), write(660, 193, "October", A, size=14)]
    ev += [write(134, 233, "Dr. Lima", A), write(428, 233, "to stop guessing and start showing", A, size=14)]
    ev.append(("pause", .3, B))
    ev.append(sticker_ev("a_fan", 262, 520, 70, B))
    ev.append(tick(760, 280 + 56.5 / 2 + 6 * 64.5 - 2, (560, 660, 620)))
    ev.append(fill(104, 926, 30, 30, C, TANG, "disk", .35))
    ev.append(write(150, 931, "fan unlocked!", C, PINK, 15))
    ev.append(("pause", .8, FULL))
    return ev


def scene_log():
    A = (300, 260, 620)
    ev = [("pause", .6, FULL)]
    rows = [(1.0, 3, True, "5.5", 2, True, 2, "woke at 3 am, again"), (0.5, 2, False, "6", 3, False, 3, "fan on the desk"), (0, 4, True, "5", 2, True, 2, "window open all night"),
            (0, 1, False, "7", 4, False, 4, "walk + magnesium"), (0, 1, False, "7.5", 4, False, 4, "slept. finally.")]
    for i, (flow, hf, ns, sleep, mood, fog, en, note) in enumerate(rows):
        yy = 164 + i * 28; cy = yy + 14; cam = (300, 220 + 24 * i, 620)
        if flow:
            ev.append(fill(87, cy, 11 * flow + 2, 11 * flow + 2, cam, PINK, "disk"))
        ev.append(small_tick(110 + (hf - 1) * 13 + 4.5, cy, cam, TANG))
        if ns:
            ev.append(small_tick(199, cy, cam, MOCHA))
        ev.append(write(229, cy + 5, sleep, cam, INK, 13, .04))
        ev.append(fill(272 + (mood - 1) * 13 + 4.5, cy, 7, 7, cam, MOCHA, "disk", .2))
        if fog:
            ev.append(small_tick(355, cy, cam, MOCHA))
        ev.append(small_tick(378 + (en - 1) * 13 + 4.5, cy, cam, PINK))
        ev.append(write(454, cy + 5, note, (520, 220 + 24 * i, 620), INK, 13, .03))
    ev.append(sticker_ev("m_fan", 640, 164 + 7 * 28 + 10, 72, (560, 340, 620), -4))
    ev.append(sticker_ev("q_openwindow", 520, 164 + 10 * 28 + 4, 46, (560, 340, 620), 3))
    ev.append(("pause", .8, FULL))
    return ev


def scene_hotmap():
    gx, cw, rh = 98, (738 - 70) / 31, 28
    A = (330, 300, 620)
    ev = [("pause", .6, FULL)]
    month0 = [(1, PEACH), (2, PEACH), (4, TANG), (7, PEACH), (8, TANG), (9, PINK), (13, PEACH), (14, PEACH), (19, TANG), (20, TANG), (21, PINK), (26, PEACH)]
    for d, col in month0:
        ev.append(fill(gx + d * cw + cw / 2, 206 + rh / 2, cw - 2, rh - 4, A, col, "rect", .18))
    month1 = [(0, PEACH), (3, TANG), (4, TANG), (5, PINK), (10, PEACH), (16, TANG), (17, PEACH), (23, PEACH), (24, TANG), (29, PEACH)]
    for d, col in month1:
        ev.append(fill(gx + d * cw + cw / 2, 206 + rh + rh / 2, cw - 2, rh - 4, A, col, "rect", .18))
    ev.append(("pause", .3, A))
    ev.append(write(470, 569, "the week before my period", (417, 420, 834), PINK, 14))
    ev.append(sticker_ev("f4", 720, 566, 30, (417, 420, 834), -3))
    ev.append(("pause", .8, FULL))
    return ev


def scene_habits():
    gx, cw, rh = 162, (738 - 118 - 44) / 31, 40
    A = (330, 330, 620); B = (417, 900, 700)
    ev = [("pause", .6, FULL)]
    for hi, days, col in ((0, range(7), TANG), (1, (0, 2, 4, 6), PINK), (2, range(5), TANG), (3, (0, 1, 2, 3, 4, 5, 6), PEACH), (5, range(7), TANG)):
        yy = 180 + hi * rh
        for d in days:
            ev.append(fill(gx + d * cw + cw / 2, yy + rh / 2, cw - 3, rh - 12, (330, 260 + 24 * hi, 620), col, "rect", .15))
    ev.append(write(752, 180 + 25, "7", (600, 300, 620), PINK, 16))
    ev.append(sticker_ev("a_sleepmask", 96, 882, 44, B))
    ev.append(write(224, 966, "cooler. calmer. mine.", B, INK, 15))
    ev.append(("pause", .8, FULL))
    return ev


def scene_doctor():
    A = (345, 300, 620); B = (417, 820, 620)
    ev = [("pause", .6, FULL)]
    ev += [write(170, 163, "14 November", A, size=14), write(540, 163, "Dr. Lima", A, size=14), write(170, 197, "3 October", A, size=14), write(540, 197, "24 to 40 days", A, size=14)]
    rows = [("daily", "4", "March", "evenings", "fan, no coffee"), ("4x a week", "3", "March", "3 am", "window open"), ("5-6 h", "3", "spring", "", "magnesium"), ("", "2", "", "all day", "")]
    xs = [233, 345, 444, 535, 648]
    for r, vals in enumerate(rows):
        base = 240 + 26 + r * 36 + 23
        for x, s in zip(xs, vals):
            if s:
                ev.append(write(x, base, s, (345, 300 + 20 * r, 620), INK, 13, .03))
    t = 240 + 26 + 12 * 36 + 16
    ev.append(tick(67, t + 22 + 28 * 4 - 5, B)); ev.append(tick(67, t + 22 + 28 * 5 - 5, B))
    ev.append(write(ML_ + 20, t + 56, "HRT: yes or no, and why", B, INK, 14)); ev.append(write(ML_ + 20, t + 84, "sleep first, then the rest", B, INK, 14))
    ev.append(sticker_ev("q_askdoctor", 300, t + 170, 54, B, -4))
    ev.append(("pause", .8, FULL))
    return ev


ML_ = 44 + 369 + 7
SCENES = [("profile", scene_profile, "1 · Meet Margo, earn your first reward"), ("m01", scene_log, "2 · One row a night, thirty seconds"), ("cy_hotmap", scene_hotmap, "3 · Colour the Hot Map"),
          ("h01", scene_habits, "4 · Colour a square, earn a reward"), ("c_summary", scene_doctor, "5 · Show it to your doctor as it is"), ("cover", lambda: [("pause", 2.2, FULL)], "Hot Girl Era · perimenopause tracker")]


def caption(fr, text, W, H):
    d = ImageDraw.Draw(fr, "RGBA"); f = ImageFont.truetype(os.path.join(ROOT, "fonts", "DMSans-SemiBold.ttf"), int(W * 0.034))
    tw = d.textlength(text.upper(), font=f); pw, ph = tw + W * 0.08, W * 0.085; x0 = (W - pw) / 2; y0 = H - ph - H * 0.045
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), ph / 2, fill=(255, 252, 246, 238), outline=(232, 112, 58, 255), width=3)
    d.text((W / 2, y0 + ph / 2), text.upper(), font=f, fill=(107, 74, 58), anchor="mm")


def scene_frames(page, evs, W, H, cap):
    PW, PH = page.size; t = 0.0; tl = []; camk = []
    for e in evs:
        if isinstance(e, tuple):
            _, d, cam = e; camk.append((t, cam)); t += d; continue
        camk.append((t, e.cam)); tl.append((t, e)); t += e.dur + (0.12 if e.kind == "wipe" else 0.08)
    total = t + .2

    def cam_at(time):
        cur = camk[0][1]; prev = cur; ts = 0.0
        for kt, kc in camk:
            if kt > time:
                break
            if kc != cur:
                prev, cur, ts = cur, kc, kt
        a = ease((time - ts) / 0.9) if ts else 1.0
        return tuple(prev[i] + (cur[i] - prev[i]) * a for i in range(3))
    state = page.copy(); done = set()
    for fi in range(int(total * FPS)):
        time = fi / FPS
        for st, e in tl:
            if id(e) not in done and time >= st + e.dur:
                state.alpha_composite(e.layer, e.pos) if e.pos[0] >= 0 and e.pos[1] >= 0 and e.pos[0] + e.layer.width <= PW and e.pos[1] + e.layer.height <= PH else state.paste(e.layer, e.pos, e.layer)
                done.add(id(e))
        cx, cy, cw = cam_at(time); bw = cw * SC; bh = bw * H / W
        x0 = min(max(0, cx * SC - bw / 2), PW - bw) if bw <= PW else (PW - bw) / 2
        y0 = min(max(0, cy * SC - bh / 2), PH - bh) if bh <= PH else (PH - bh) / 2         # taller than the page: centre it on a cream band
        box = (int(x0), int(y0), int(x0 + bw), int(y0 + bh)); crop = state.crop(box); tip_px = None
        if bh > PH or bw > PW:
            bgc = Image.new("RGBA", crop.size, (248, 241, 227, 255)); bgc.alpha_composite(crop); crop = bgc
        for st, e in tl:
            if id(e) in done or time < st:
                continue
            p = (time - st) / e.dur; lay = e.layer; pos = (e.pos[0] - box[0], e.pos[1] - box[1])
            if e.kind == "wipe":
                wpx = max(1, int(e.tip * p)); mk = Image.new("L", lay.size, 0); ImageDraw.Draw(mk).rectangle((0, 0, wpx, lay.height), fill=255)
                crop.paste(lay, pos, ImageChops.multiply(lay.getchannel("A"), mk)); tip_px = (pos[0] + wpx, pos[1] + lay.height * .6)
            elif e.kind == "stroke":
                mk = Image.new("L", lay.size, 0); md = ImageDraw.Draw(mk); pts = e.tip; seg = p * (len(pts) - 1); full = int(seg); last = pts[0]
                for i in range(full):
                    md.line([pts[i], pts[i + 1]], fill=255, width=int(2.4 * SC)); last = pts[i + 1]
                if full < len(pts) - 1:
                    f = seg - full; a_, b_ = pts[full], pts[full + 1]; last = (a_[0] + (b_[0] - a_[0]) * f, a_[1] + (b_[1] - a_[1]) * f); md.line([a_, last], fill=255, width=int(2.4 * SC))
                crop.paste(lay, pos, ImageChops.multiply(lay.getchannel("A"), mk)); tip_px = (pos[0] + last[0], pos[1] + last[1])
            elif e.kind == "pop":
                sc = 0.2 + 0.8 * ease(p / .6) + (0.12 * math.sin(math.pi * min(1, p)) if p < 1 else 0); w2, h2 = max(2, int(lay.width * sc)), max(2, int(lay.height * sc))
                l2 = lay.resize((w2, h2), Image.BICUBIC); crop.paste(l2, (pos[0] + (lay.width - w2) // 2, pos[1] + (lay.height - h2) // 2), l2)
        fr = crop.resize((W, H), Image.LANCZOS).convert("RGB")
        if tip_px:
            s_ = W / bw; d = ImageDraw.Draw(fr); tx, ty = tip_px[0] * s_, tip_px[1] * s_ + math.sin(time * 40) * 1.2
            d.polygon([(tx, ty), (tx + 12, ty - 6), (tx + 190, ty - 150), (tx + 170, ty - 168), (tx + 6, ty - 14)], fill=(247, 247, 249), outline=(170, 170, 178))
            d.polygon([(tx, ty), (tx + 12, ty - 6), (tx + 6, ty - 14)], fill=(60, 60, 66))
        caption(fr, cap, W, H)
        yield fr


def main():
    pages = {k: render_page(k) for k in PAGES}
    for name, (W, H) in (("vertical", (1080, 1920)), ("square", (1080, 1080))):
        wr = imageio.get_writer(os.path.join(OUT, f"video_fill_{name}.mp4"), fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p", macro_block_size=1)
        prev = None; n = 0
        for key, build, cap in SCENES:
            for i, fr in enumerate(scene_frames(pages[key], build(), W, H, cap)):
                if prev is not None and i < 12:                       # 0.4 s crossfade from the previous scene's last frame
                    fr = Image.blend(prev, fr, ease((i + 1) / 12))
                wr.append_data(np.asarray(fr)); last = fr; n += 1
            prev = last
        wr.close(); print(name, round(n / FPS, 1), "s")


if __name__ == "__main__":
    main()
