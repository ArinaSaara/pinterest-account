#!/usr/bin/env python3
"""15 s silent listing video for Code & Cozy (1080x1080 + 1080x1350 vertical).

Storyboard: hero mockup -> iPad "screen recording" that taps through home, month, day, work hub, sprint board
(tap ripples at the real link positions) -> sticker wall -> title card.

Run:  .venv-planner/bin/python build_it_video.py
Output: images/it_girl/video/video_listing_{square,vertical}.mp4
"""
import math
import os

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw

import build_it_mockups as bm
from build_mockups import ipad, place

ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, "images", "it_girl", "video"); os.makedirs(OUT, exist_ok=True)
FPS = 30; S = 1080; SW = 640


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * min(max(t, 0), 1))


def kb(img, t, z0, z1, cx=.5, cy=.5):
    z = z0 + (z1 - z0) * t; w, h = img.size; side = min(w, h) / z
    x0 = min(max(0, cx * w - side / 2), w - side); y0 = min(max(0, cy * h - side / 2), h - side)
    return img.crop((int(x0), int(y0), int(x0 + side), int(y0 + side))).resize((S, S), Image.BILINEAR)


def ripple(img, x, y, t):
    """tap ripple at canvas (x, y), t 0..1"""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); r = 18 + 50 * t; a = int(200 * (1 - t))
    d.ellipse((x - r, y - r, x + r, y + r), outline=(192, 105, 74, a), width=5); d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(192, 105, 74, int(a * .8)))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def main():
    bg = bm.backdrop((S, S)); sw = SW; bez = int(sw * .045)
    tw = sw + 2 * bez; ix, iy = (S - tw) // 2, 60 + 0
    def screen(key):
        c = bg.copy(); tab = ipad(bm.page(key), sw); place(c, tab, ix, iy); return c.convert("RGB")
    def P(x, y):
        return bm.pt(None, bez, sw, x, y, ix, iy)

    hero = Image.open(os.path.join(bm.OUT, "01_hero_square.png")).convert("RGB")
    title = Image.open(os.path.join(bm.OUT, "07_all_stickers.png")).convert("RGB").resize((S, S), Image.LANCZOS)
    # (page key, seconds, tap point on that page (pt) or None)
    seq = [("home", 1.5, (99, 231)), ("jan", 1.5, (326, 503)), ("day_wed", 2.0, (821, 616)), ("work", 1.4, (606, 314)), ("sprint", 2.0, None)]
    scr = {k: screen(k) for k, _, _ in seq}
    frames = []
    n = int(2.0 * FPS)
    for i in range(n):
        frames.append(kb(hero, ease(i / n), 1.0, 1.1, .5, .5))
    for k, sec, tap in seq:
        m = int(sec * FPS); base = scr[k]
        for i in range(m):
            t = i / FPS; f = base
            if tap and t > sec - 0.65:
                f = ripple(base, *P(*tap), (t - (sec - 0.65)) / 0.65)
            frames.append(kb(f, ease(i / m), 1.0, 1.07, .5, .5))
    n = int(2.0 * FPS)
    for i in range(n):
        frames.append(kb(title, ease(i / n), 1.0, 1.02))
    # title card
    card = bm.backdrop((S, S)); d = ImageDraw.Draw(card)
    d.text((S // 2, 300), "Code & Cozy", font=bm.F("PlayfairDisplay-Regular", 130), fill=bm.INK, anchor="mm")
    d.text((S // 2, 400), "2027 DAILY PLANNER FOR GOODNOTES", font=bm.F("DMSans-SemiBold", 32), fill=bm.SAGE_D, anchor="mm")
    for j, line in enumerate(("508 hyperlinked pages", "work hub  ·  health  ·  life", "80 cozy stickers included")):
        d.text((S // 2, 520 + j * 60), line, font=bm.F("DMSans-Regular", 38), fill=bm.INK, anchor="mm")
    for nme, x, y, h, r in (("work_3", 220, 810, 300, -5), ("dev_3", 560, 830, 280, 4), ("fit_2", 880, 800, 330, -3)):
        s_ = bm.stk(nme, h, r); card.alpha_composite(s_, (x - s_.width // 2, y - s_.height // 2))
    d.text((S // 2, 1020), "instant download  ·  iPad  ·  Monday & Sunday start", font=bm.F("DMSans-Regular", 28), fill=bm.MUTED, anchor="mm")
    card = card.convert("RGB")
    for i in range(int(2.5 * FPS)):
        frames.append(card)
    # crossfades
    cuts = []; acc = 0
    for sec in [2.0] + [x[1] for x in seq] + [2.0]:
        acc += int(sec * FPS); cuts.append(acc)
    h = 6
    for c in cuts:
        a_, b_ = frames[c - h - 1], frames[c + h]
        for j in range(2 * h):
            frames[c - h + j] = Image.blend(a_, b_, (j + 1) / (2 * h + 1))
    for name, vert in (("video_listing_square.mp4", False), ("video_listing_vertical.mp4", True)):
        p = os.path.join(OUT, name); w = imageio.get_writer(p, fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p", macro_block_size=1)
        for f in frames:
            if vert:
                cv = Image.new("RGB", (1080, 1350), (246, 241, 229)); cv.paste(f, (0, 135)); f = cv
            w.append_data(np.asarray(f))
        w.close(); print(p, round(os.path.getsize(p) / 1e6, 1), "MB", len(frames) / FPS, "s")


if __name__ == "__main__":
    main()
