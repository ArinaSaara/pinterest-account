#!/usr/bin/env python3
"""Simulated "drawing process" time-lapse of one finished sticker: pencil sketch -> flat colours -> full painting
-> die-cut border and shadow. It is built from the final artwork (edge map, posterised layer, full colour), not recorded.

Run:  .venv-planner/bin/python build_it_draw_video.py [sticker]      # default work_3
Output: images/it_girl/video/video_drawing_<sticker>.mp4 (1080x1350)
"""
import math
import os
import sys

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.abspath(__file__)); IT = os.path.join(ROOT, "images", "it_girl")
NAME = sys.argv[1] if len(sys.argv) > 1 else "work_3"
W, H, FPS = 1080, 1350, 30
PAPER = np.array([250, 246, 234], np.float32)
rng = np.random.default_rng(5)


def smooth(x):
    x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)


def build():
    im = Image.open(os.path.join(IT, "cut", NAME + ".png")).convert("RGBA")
    a = np.asarray(im.getchannel("A")) > 128
    # inner artwork only: shrink the white die-cut border so the border can "grow" at the end
    inner = ndi.binary_erosion(a, iterations=14)
    ys, xs = np.where(inner); im = im.crop((xs.min() - 20, ys.min() - 20, xs.max() + 20, ys.max() + 20))
    sc = min(900 / im.width, 900 / im.height); im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    rgba = np.asarray(im).astype(np.float32); alpha = rgba[..., 3] / 255
    art = rgba[..., :3]; core = ndi.binary_erosion(alpha > .5, iterations=int(14 * sc) + 2)
    gray = art.mean(axis=2); g = ndi.gaussian_filter(gray, 2.4); mag = np.hypot(ndi.sobel(g, 0), ndi.sobel(g, 1))
    line = (np.clip((mag - 38) / 70, 0, 1) ** 1.3) * core * 0.75
    pim = Image.fromarray(art.astype(np.uint8)).quantize(14, method=Image.MEDIANCUT).convert("RGB").filter(ImageFilter.MedianFilter(7))
    flat = np.asarray(pim).astype(np.float32); flat = flat * 0.6 + ndi.gaussian_filter(art, (4, 4, 0)) * 0.4
    return art, alpha, line, flat, core, im.size


def field(shape, ymix=.45, seed=0):
    r = np.random.default_rng(seed).random(shape); f = ndi.gaussian_filter(r, 22); f = (f - f.min()) / (f.max() - f.min())
    yy = np.linspace(0, 1, shape[0])[:, None] * np.ones(shape); xx = np.linspace(0, 1, shape[1])[None, :] * np.ones(shape)
    f = (1 - ymix) * f + ymix * (0.8 * yy + 0.2 * xx); return (f - f.min()) / (f.max() - f.min())


def main():
    art, alpha, line, flat, core, (w, h) = build()
    ox, oy = (W - w) // 2, (H - h) // 2 - 20
    F1, F2, F3 = field((h, w), .5, 1), field((h, w), .3, 2), field((h, w), .15, 3)
    border = ndi.binary_dilation(alpha > .5, iterations=int(16 * w / 900) + 6) & ~(alpha > .5)
    sil = ndi.binary_dilation(alpha > .5, iterations=int(16 * w / 900) + 6)
    shadow = ndi.gaussian_filter(ndi.shift(sil.astype(np.float32), (18, 0), order=0), 14) * .30
    bg = np.ones((H, W, 3), np.float32) * PAPER
    # faint grid paper
    for y in range(0, H, 54):
        bg[y, :] *= .985
    for x in range(0, W, 54):
        bg[:, x] *= .985
    T = [("sketch", 7.0), ("flat", 5.0), ("paint", 6.0), ("border", 2.5), ("hold", 2.5)]; total = sum(d for _, d in T)
    path = os.path.join(IT, "video"); os.makedirs(path, exist_ok=True); out = os.path.join(path, f"video_drawing_{NAME}.mp4")
    wr = imageio.get_writer(out, fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p", macro_block_size=1)
    cur = None; prev_tip = None
    for fi in range(int(total * FPS)):
        t = fi / FPS; ph = None; acc = 0
        for n, d in T:
            if t < acc + d:
                ph, p = n, (t - acc) / d; break
            acc += d
        canvas = bg.copy(); reg = canvas[oy:oy + h, ox:ox + w]; tip = None
        ink = np.array([110, 92, 84], np.float32)
        def lay(base, top, m):
            return base * (1 - m[..., None]) + top * m[..., None]
        if ph == "sketch":
            m = smooth((p * 1.12 - F1) * 14) * line; reg[:] = lay(reg, ink, m * .9); Fr = F1; tt = p * 1.12
        else:
            reg[:] = lay(reg, ink, line * .9 * (1 if ph == "flat" else max(0, 1 - (p if ph == "paint" else 1) * .75)))
            tt = None
        if ph in ("flat", "paint", "border", "hold"):
            if ph == "flat":
                m = smooth((p * 1.1 - F2) * 10) * core; reg[:] = lay(reg, flat, m); Fr = F2; tt = p * 1.1
            else:
                reg[:] = lay(reg, flat, core.astype(np.float32))
                if ph == "paint":
                    m = smooth((p * 1.1 - F3) * 10) * alpha; reg[:] = lay(reg, art, m); Fr = F3; tt = p * 1.1
                else:
                    reg[:] = lay(reg, art, alpha)
        if ph in ("border", "hold"):
            k = 1.0 if ph == "hold" else smooth(p)
            sh = shadow * k; canvas[oy:oy + h, ox:ox + w] = reg
            canvas[oy:oy + h, ox:ox + w] = canvas[oy:oy + h, ox:ox + w] * (1 - sh[..., None] * (1 - alpha[..., None])) + 0 * sh[..., None]
            reg = canvas[oy:oy + h, ox:ox + w]
            reg[:] = lay(reg, np.array([255, 255, 255], np.float32), (border * k).astype(np.float32)); reg[:] = lay(reg, art, alpha)
        # pencil/brush cursor on the frontier
        if tt is not None and ph in ("sketch", "flat", "paint"):
            band = (np.abs(Fr - tt) < .012) & (line > .1 if ph == "sketch" else core)
            ys, xs = np.where(band)
            if len(ys):
                i = int(rng.integers(len(ys))); tip = (xs[i] + ox, ys[i] + oy)
                if prev_tip: tip = (prev_tip[0] * .6 + tip[0] * .4, prev_tip[1] * .6 + tip[1] * .4)
                prev_tip = tip
        img = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
        if tip:
            tx, ty = tip; d.polygon([(tx, ty), (tx + 12, ty - 6), (tx + 190, ty - 150), (tx + 170, ty - 168), (tx + 6, ty - 14)], fill=(247, 247, 249), outline=(170, 170, 178)); d.polygon([(tx, ty), (tx + 12, ty - 6), (tx + 6, ty - 14)], fill=(60, 60, 66))
        label = {"sketch": "1  sketch", "flat": "2  base colours", "paint": "3  painting", "border": "4  die-cut", "hold": "Code & Cozy"}[ph]
        from PIL import ImageFont
        f = ImageFont.truetype(os.path.join(ROOT, "fonts", "PlayfairDisplay-Regular.ttf"), 54); f2 = ImageFont.truetype(os.path.join(ROOT, "fonts", "DMSans-SemiBold.ttf"), 26)
        d.text((W // 2, 1230), label, font=f, fill=(56, 54, 46), anchor="mm")
        if ph == "hold":
            d.text((W // 2, 1290), "DIGITAL STICKERS FOR GOODNOTES", font=f2, fill=(76, 94, 64), anchor="mm")
        else:
            d.rounded_rectangle((300, 1290, 780, 1298), 4, fill=(225, 218, 200)); d.rounded_rectangle((300, 1290, 300 + 480 * min(1, t / (total - T[-1][1])), 1298), 4, fill=(107, 127, 88))
        wr.append_data(np.asarray(img))
    wr.close(); print(out, round(os.path.getsize(out) / 1e6, 1), "MB", total, "s")


if __name__ == "__main__":
    main()
