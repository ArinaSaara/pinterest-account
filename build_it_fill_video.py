#!/usr/bin/env python3
"""Screen-recording style video of someone filling in a Code & Cozy daily page with an Apple Pencil.

Handwriting (Caveat) is revealed left to right with a pencil cursor at the tip, ticks are drawn stroke by stroke,
highlighter bars wipe in, focus tomatoes / water drops pop, a sticker is pasted at the end. A virtual camera pans
and zooms between the areas being filled.

Run:  .venv-planner/bin/python build_it_fill_video.py
Output: images/it_girl/video/video_fill_{vertical,square}.mp4
"""
import math
import os
import random
import subprocess

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__)); IT = os.path.join(ROOT, "images", "it_girl")
PDF = os.path.join(IT, "Code_and_Cozy_Planner_2027_Mon.pdf"); OUT = os.path.join(IT, "video"); os.makedirs(OUT, exist_ok=True)
SC = 3; FPS = 30; PAGE_NO = 100            # Wed 13 Jan 2027
INK = (38, 52, 92, 255); TERRA = (192, 105, 74); SAGE = (107, 127, 88); GOLD = (214, 170, 60)
random.seed(7)
HAND = ImageFont.truetype(os.path.join(ROOT, "fonts", "Caveat-SemiBold.ttf"), 17 * SC)


def render_page():
    f = os.path.join(IT, "pages_png", "fill_base")
    subprocess.run(["pdftoppm", "-f", str(PAGE_NO), "-l", str(PAGE_NO), "-r", str(72 * SC), "-png", "-singlefile", PDF, f], check=True)
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


def write(x_pt, base_pt, s, cam, col=INK, size=None, speed=0.045):
    """handwritten line whose baseline sits at base_pt (page pt, top-based)."""
    im, wpx = text_layer(s, col, size); font_size = im.height / 1.5
    pos = (int(x_pt * SC) - 8, int(base_pt * SC - font_size * 1.0))
    return Ev("wipe", max(.4, len(s) * speed), im, pos, cam, wpx)


def tick(cx_pt, cy_pt, cam, col=INK):
    r = 7 * SC; im = Image.new("RGBA", (r * 3, r * 3), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(r * .5, r * 1.5), (r * 1.1, r * 2.2), (r * 2.4, r * .5)]; d.line(pts, fill=col, width=int(1.8 * SC), joint="curve")
    return Ev("stroke", .45, im, (int(cx_pt * SC - r * 1.5 + 2 * SC), int(cy_pt * SC - r * 1.7)), cam, pts)


def bar(x1, x2, y1, y2, col, cam):
    w, h = int((x2 - x1) * SC), int((y2 - y1) * SC); im = Image.new("RGBA", (w, h), col + (92,))
    return Ev("wipe", .7, im, (int(x1 * SC), int(y1 * SC)), cam, w)


def pop(cx_pt, cy_pt, r_pt, col, cam, ring=False):
    r = int(r_pt * SC); im = Image.new("RGBA", (r * 2 + 4, r * 2 + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((2, 2, 2 * r + 2, 2 * r + 2), fill=None if ring else col + (235,), outline=col + (255,), width=int(1.4 * SC))
    return Ev("pop", .32, im, (int(cx_pt * SC - r - 2), int(cy_pt * SC - r - 2)), cam)


def sticker_ev(name, cx_pt, cy_pt, h_pt, cam):
    s = Image.open(os.path.join(IT, "cut", name + ".png")).convert("RGBA"); h = int(h_pt * SC); s = s.resize((int(s.width * h / s.height), h), Image.LANCZOS)
    sh = Image.new("RGBA", (s.width + 80, s.height + 80), (0, 0, 0, 0)); a = Image.new("L", sh.size, 0); a.paste(s.getchannel("A"), (40, 50)); a = a.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * .35))
    sh.putalpha(a); sh.alpha_composite(s, (40, 40))
    return Ev("pop", .6, sh, (int(cx_pt * SC - sh.width / 2), int(cy_pt * SC - sh.height / 2)), cam)


def events():
    A = (250, 250, 470); B = (250, 520, 470); Cm = (640, 360, 330); D = (250, 840, 470); E = (440, 960, 560); F = (417, 556, 834)
    ev = []
    ev.append(("pause", 1.0, F))
    for i, t in enumerate(("Ship the checkout PR", "Fix flaky login test", "Walk with Pixel at lunch")):
        ev.append(write(78, 202 + 30 * (i + 1) - 3, t, A))
    todo = ["Review Maya's PR", "Reply to design thread", "Update sprint board", "Write migration notes", "Book dentist"]
    for i, t in enumerate(todo):
        ev.append(write(74, 328 + 28 * (i + 1) - 3, t, B))
    for i in (0, 2):
        ev.append(tick(59, 328 + 28 * (i + 1) - 4, B))
    ev.append(("pause", .3, B))
    # schedule
    gt = 218; rh = (862 - 10 - 218) / 15; row = lambda h: gt + (h - 7) * rh
    ev.append(bar(528, 776, row(9) + 2, row(9) + rh - 2, SAGE, Cm)); ev.append(write(534, row(9) + rh - 12, "Standup", Cm, size=15))
    ev.append(bar(528, 776, row(10) + 2, row(12) + rh - 2, TERRA, Cm)); ev.append(write(534, row(10) + rh - 12, "Deep work: auth bug", Cm, size=15))
    ev.append(bar(528, 776, row(14) + 2, row(14) + rh - 2, GOLD, Cm)); ev.append(write(534, row(14) + rh - 12, "1:1 with Maya", Cm, size=15))
    ev.append(bar(528, 776, row(16) + 2, row(17) + rh - 2, SAGE, Cm)); ev.append(write(534, row(16) + rh - 12, "Sprint planning", Cm, size=15))
    # notes
    for i, t in enumerate(("standup: API freeze moved to Fri", "- ask Dan about staging env", "- demo on Thursday!")):
        ev.append(write(56, 598 + 28 * (i + 1) - 4, t, (250, 700, 470)))
    # focus tomatoes
    for k in range(3):
        ev.append(pop(62 + 27 * k, 833, 6.8, TERRA, D))
    for k in range(3):
        ev.append(("pause", 0, D))
    # life
    ev.append(pop(64 + 35 * 3, 934, 13, GOLD, E, ring=True))
    for k in range(5):
        ev.append(pop(560 + 27.5 * k, 936, 7.5, (84, 140, 190), E))
    ev.append(write(76, 974 + 38 - 4, "oat porridge + coffee", E, size=15)); ev.append(write(76, 974 + 60 - 4, "pasta with Maya", E, size=15))
    ev.append(write(570, 974 + 20 + 26 - 4, "shipped it!! + sunny walk", E, size=15))
    ev.append(sticker_ev("dev_3", 330, 720, 96, (330, 640, 520)))
    ev.append(("pause", 1.6, F))
    return ev


def main():
    page = render_page(); PW, PH = page.size; evs = events()
    # timeline
    t = 0.0; tl = []; cam_prev = (417, 556, 834); camk = []   # camera keyframes (time, cam)
    for e in evs:
        if isinstance(e, tuple):
            _, d, cam = e; camk.append((t, cam)); t += d; continue
        camk.append((t, e.cam)); tl.append((t, e)); t += e.dur + (0.12 if e.kind == "wipe" else 0.08)
    total = t + .2
    def cam_at(time):
        # hold each keyframe's camera; blend over 0.9 s after a change
        cur = camk[0][1]; prev = cur; ts = 0.0
        for kt, kc in camk:
            if kt > time:
                break
            if kc != cur:
                prev, cur, ts = cur, kc, kt
        a = ease((time - ts) / 0.9) if ts else 1.0
        return tuple(prev[i] + (cur[i] - prev[i]) * a for i in range(3))
    state = page.copy(); done = set()
    for name, (W, H) in (("vertical", (1080, 1350)), ("square", (1080, 1080))):
        state = page.copy(); done = set()
        wr = imageio.get_writer(os.path.join(OUT, f"video_fill_{name}.mp4"), fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p", macro_block_size=1)
        for fi in range(int(total * FPS)):
            time = fi / FPS
            for st, e in tl:
                if id(e) not in done and time >= st + e.dur:
                    layer = e.layer
                    state.alpha_composite(layer, e.pos) if e.pos[0] >= 0 and e.pos[1] >= 0 and e.pos[0] + layer.width <= PW and e.pos[1] + layer.height <= PH else state.paste(layer, e.pos, layer)
                    done.add(id(e))
            cx, cy, cw = cam_at(time); bw = cw * SC; bh = bw * H / W
            x0 = min(max(0, cx * SC - bw / 2), PW - bw); y0 = min(max(0, cy * SC - bh / 2), PH - bh)
            box = (int(x0), int(y0), int(x0 + bw), int(y0 + bh)); crop = state.crop(box); tip_px = None
            for st, e in tl:
                if id(e) in done or time < st:
                    continue
                p = (time - st) / e.dur; lay = e.layer; pos = (e.pos[0] - box[0], e.pos[1] - box[1])
                if e.kind == "wipe":
                    wpx = max(1, int(e.tip * ease(p) if False else e.tip * p)); m = lay.getchannel("A").copy(); mk = Image.new("L", lay.size, 0); ImageDraw.Draw(mk).rectangle((0, 0, wpx, lay.height), fill=255)
                    from PIL import ImageChops
                    m = ImageChops.multiply(m, mk); crop.paste(lay, pos, m); tip_px = (pos[0] + wpx, pos[1] + lay.height * .6)
                elif e.kind == "stroke":
                    n = max(2, int(len(e.tip) * 0)); mk = Image.new("L", lay.size, 0); md = ImageDraw.Draw(mk)
                    pts = e.tip; seg = p * (len(pts) - 1); full = int(seg); last = None
                    for i in range(full):
                        md.line([pts[i], pts[i + 1]], fill=255, width=int(2.4 * SC)); last = pts[i + 1]
                    if full < len(pts) - 1:
                        f = seg - full; a_, b_ = pts[full], pts[full + 1]; last = (a_[0] + (b_[0] - a_[0]) * f, a_[1] + (b_[1] - a_[1]) * f); md.line([a_, last], fill=255, width=int(2.4 * SC))
                    from PIL import ImageChops
                    crop.paste(lay, pos, ImageChops.multiply(lay.getchannel("A"), mk)); tip_px = (pos[0] + last[0], pos[1] + last[1])
                elif e.kind == "pop":
                    sc = 0.2 + 0.8 * ease(p / .6) + (0.12 * math.sin(math.pi * min(1, p)) if p < 1 else 0); w2, h2 = max(2, int(lay.width * sc)), max(2, int(lay.height * sc))
                    l2 = lay.resize((w2, h2), Image.BICUBIC); crop.paste(l2, (pos[0] + (lay.width - w2) // 2, pos[1] + (lay.height - h2) // 2), l2)
            fr = crop.resize((W, H), Image.LANCZOS).convert("RGB")
            if tip_px:
                s_ = W / bw; d = ImageDraw.Draw(fr); tx, ty = tip_px[0] * s_, tip_px[1] * s_ + math.sin(time * 40) * 1.2
                d.polygon([(tx, ty), (tx + 12, ty - 6), (tx + 190, ty - 150), (tx + 170, ty - 168), (tx + 6, ty - 14)], fill=(247, 247, 249), outline=(170, 170, 178))
                d.polygon([(tx, ty), (tx + 12, ty - 6), (tx + 6, ty - 14)], fill=(60, 60, 66))
            wr.append_data(np.asarray(fr))
        wr.close(); print(name, round(total, 1), "s")


if __name__ == "__main__":
    main()
