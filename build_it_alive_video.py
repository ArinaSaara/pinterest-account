#!/usr/bin/env python3
"""Gentle 'living sticker' loops: breathing, hair/head sway, lamp glow, twinkles and falling confetti / snow, drawn
over the finished sticker with a mesh warp. Not character animation: the artwork is a still image, so motion is limited.

Run:  .venv-planner/bin/python build_it_alive_video.py
Output: images/it_girl/video/alive_<name>.mp4 (4 s loops, 1080x1080) and alive_reel.mp4 (all, crossfaded)
"""
import math
import os

import imageio.v2 as imageio
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.abspath(__file__)); IT = os.path.join(ROOT, "images", "it_girl"); OUT = os.path.join(IT, "video")
S, FPS, SEC = 1080, 30, 4
CREAM = np.array([250, 246, 234], np.float32)
CLIPS = [("dev_3", "confetti"), ("work_1", "dust"), ("seasons_8", "twinkle"), ("seasons_7", "snow"), ("cozy_1", "dust"), ("fit_2", "dust")]


def prep(name):
    im = Image.open(os.path.join(IT, "cut", name + ".png")).convert("RGBA"); sc = min(860 / im.width, 860 / im.height)
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS); a = np.asarray(im).astype(np.float32)
    pad = 40; a = np.pad(a, ((pad, pad), (pad, pad), (0, 0))); return a, pad


def frame_warp(a, t, rng_phase):
    h, w = a.shape[:2]; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); u = yy / h; ph = 2 * math.pi * t
    top = np.clip(1 - u / .62, 0, 1) ** 1.6; mid = np.exp(-((u - .55) / .22) ** 2)
    dx = 5.0 * top * np.sin(ph + 2.2 * u + rng_phase) + 1.6 * mid * math.sin(2 * ph)
    dy = -4.0 * mid * math.sin(ph + .6) - 1.5 * top * math.sin(2 * ph + 1)
    src = [yy - dy, xx - dx]; out = np.stack([ndi.map_coordinates(a[..., c], src, order=1, mode="constant") for c in range(4)], -1)
    return out


def glow(a_rgba, t):
    rgb = a_rgba[..., :3]; r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    warm = ((r > 215) & (g > 170) & (b < 170) & (r - b > 70)).astype(np.float32); warm = ndi.gaussian_filter(warm, 3)
    k = .10 + .08 * math.sin(2 * math.pi * t * 2)
    out = a_rgba.copy(); out[..., :3] = np.clip(rgb + warm[..., None] * np.array([60, 40, 8]) * (k * 3), 0, 255); return out, warm


def main():
    os.makedirs(OUT, exist_ok=True); allf = []
    for name, fx in CLIPS:
        a, pad = prep(name); h, w = a.shape[:2]; ox, oy = (S - w) // 2, (S - h) // 2 + 10; rng = np.random.default_rng(abs(hash(name)) % 1000)
        _, warm = glow(a, 0); ys, xs = np.where(warm > .5)
        n_p = 60 if fx in ("confetti", "snow") else 26
        px = rng.random(n_p) * S; py = rng.random(n_p) * S; sp = .5 + rng.random(n_p); col = rng.integers(0, 4, n_p); ph0 = rng.random(n_p)
        tw = [(xs[i], ys[i], rng.random()) for i in rng.integers(0, max(1, len(xs)), 18)] if len(xs) else []
        p = os.path.join(OUT, f"alive_{name}.mp4"); wr = imageio.get_writer(p, fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p", macro_block_size=1); frames = []
        for fi in range(SEC * FPS):
            t = fi / (SEC * FPS)
            st = frame_warp(a, t, 0.0); st, _ = glow(st, t)
            bg = np.ones((S, S, 3), np.float32) * CREAM
            for y in range(0, S, 54):
                bg[y, :] *= .985
            for x in range(0, S, 54):
                bg[:, x] *= .985
            reg = bg[oy:oy + h, ox:ox + w]; al = st[..., 3:4] / 255
            sh = ndi.gaussian_filter(ndi.shift(a[..., 3], (16, 0), order=1), 12)[..., None] * .28 / 255 * 255 / 255
            reg[:] = reg * (1 - sh * (1 - al)) ; reg[:] = reg * (1 - al) + st[..., :3] * al
            img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA"); ov = np.zeros((S, S, 4), np.float32)
            cols = [(214, 170, 60), (192, 105, 74), (107, 127, 88), (84, 140, 190)]
            for i in range(n_p):
                if fx == "confetti":
                    y = (py[i] + t * S * sp[i]) % S; x = px[i] + 20 * math.sin(2 * math.pi * (t * sp[i] * 1 + ph0[i])); r = 6; c = cols[col[i]] + (235,)
                    yi, xi = int(y), int(x) % S; ov[max(0, yi - r):yi + r, max(0, xi - r // 2):xi + r // 2] = c
                elif fx == "snow":
                    y = (py[i] + t * S * (.6 + sp[i] * .4)) % S; x = px[i] + 14 * math.sin(2 * math.pi * (t + ph0[i])); yi, xi = int(y), int(x) % S; r = 3 + int(sp[i] * 3)
                    ov[max(0, yi - r):yi + r, max(0, xi - r):xi + r] = (255, 255, 255, 235)
                else:
                    y = (py[i] - t * S * .25 * sp[i]) % S; x = px[i] + 10 * math.sin(2 * math.pi * (t + ph0[i])); yi, xi = int(y), int(x) % S
                    ov[max(0, yi - 3):yi + 3, max(0, xi - 3):xi + 3] = (214, 170, 60, int(160 * (.5 + .5 * math.sin(2 * math.pi * (t * 2 + ph0[i])))))
            if fx == "twinkle":
                for (x0, y0, f) in tw:
                    k = max(0, math.sin(2 * math.pi * (t * 2 + f))) ** 6; r = int(3 + 9 * k); xi, yi = x0 + ox, y0 + oy
                    ov[max(0, yi - r):yi + r, max(0, xi - 1):xi + 1] = (255, 244, 190, int(255 * k)); ov[max(0, yi - 1):yi + 1, max(0, xi - r):xi + r] = (255, 244, 190, int(255 * k))
            ovi = Image.fromarray(ov.astype(np.uint8)).filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(1.2))
            f = np.asarray(Image.alpha_composite(img, ovi).convert("RGB")); wr.append_data(f); frames.append(f)
        wr.close(); allf.append(frames); print(p)
    reel = os.path.join(OUT, "alive_reel.mp4"); wr = imageio.get_writer(reel, fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p", macro_block_size=1)
    for fr in allf:
        for f in fr[: 3 * FPS] if False else fr:
            wr.append_data(f)
    wr.close(); print(reel)


if __name__ == "__main__":
    main()
