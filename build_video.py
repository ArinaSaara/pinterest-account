#!/usr/bin/env python3
"""15-second silent listing video for Etsy / Pinterest from the planner mockups.

Storyboard (30 fps, 1080x1080):
  0-3 s   cover on the desk, slow zoom in
  3-9 s   September page on the desk, dragon stages 1-4 pop into the growth bar
  9-12 s  contents page in hands
  12-15 s all four adults + title card, fade out

Needs imageio + imageio-ffmpeg (a venv is fine):
  <venv>/bin/python build_video.py
Output: images/year_of_dragons/etsy_upload/video_listing.mp4 (and a 1080x1350 vertical cut)
"""
import glob
import math
import os

import imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import build_photo_mockups as bpm

ROOT = os.path.dirname(os.path.abspath(__file__))
YD = os.path.join(ROOT, "images", "year_of_dragons")
SCENES = os.path.join(YD, "scenes"); PAGES = os.path.join(YD, "pages"); MP = os.path.join(YD, "mockups_photo")
OUT = os.path.join(YD, "etsy_upload")
FPS = 30; SIZE = 1080
AV = "/System/Library/Fonts/Avenir Next.ttc"


def demo_page(k, pop=1.0):
    """September page with k stages pasted; the k-th one scaled by `pop` (for the bounce)."""
    pg = Image.open(os.path.join(PAGES, "fire_09_sep.png")).convert("RGBA")
    M, W = 110, 1536; slot = (W - 2 * M) / 8; ry = 320; a = (226, 112, 52)
    d = ImageDraw.Draw(pg)
    for i in range(k):
        f = sorted(glob.glob(os.path.join(ROOT, "images", "fire", "transparent", f"0{i + 1}*.png")))[0]
        s = Image.open(f).convert("RGBA"); s = s.crop(s.getchannel("A").getbbox())
        h = 170 * (pop if i == k - 1 else 1.0); s = s.resize((max(1, int(s.width * h / s.height)), max(1, int(h))), Image.LANCZOS)
        cx = M + slot * i + slot / 2; pg.alpha_composite(s, (int(cx - s.width / 2), int(ry + 100 - s.height / 2)))
        d.ellipse((cx - 13, ry + 250, cx + 13, ry + 276), fill=a)
    if k > 1:
        d.line((M + slot / 2, ry + 263, M + slot * (k - 0.5), ry + 263), fill=a, width=5)
    gx = M + 300; cell = (W - M - gx) / 30; gy = ry + 340 + 20 + 50
    days = [3, 7, 10, 14][k - 1] if k else 0
    for r in range(5):
        yy = gy + 30 + r * 78
        for day in range(max(0, days - r)):
            x = gx + day * cell + cell / 2; d.ellipse((x - 11, yy + 17, x + 11, yy + 39), fill=(252, 226, 206), outline=a, width=2)
    return pg.convert("RGB")


class Scene:
    """Caches the screen quad of a photo so many pages can be composited quickly."""
    def __init__(self, path):
        self.scene = Image.open(path).convert("RGB")
        small = self.scene.resize((self.scene.width // 4, self.scene.height // 4), Image.BILINEAR)
        blob = bpm.largest_blob(bpm.white_mask(small)).resize(self.scene.size, Image.NEAREST).filter(ImageFilter.MaxFilter(3))
        self.quad = bpm.quad_of(blob)
        qm = Image.new("L", self.scene.size, 0); ImageDraw.Draw(qm).polygon(list(self.quad), fill=255); self.mask = qm.filter(ImageFilter.GaussianBlur(1.2))

    def show(self, page):
        pw, ph = page.size
        co = bpm.persp_coeffs([(0, 0), (pw, 0), (pw, ph), (0, ph)], list(self.quad))
        warped = page.transform(self.scene.size, Image.PERSPECTIVE, co, Image.BICUBIC)
        out = self.scene.copy(); out.paste(warped, (0, 0), self.mask)
        lit = Image.blend(out, self.scene, 0.10); out.paste(lit, (0, 0), self.mask); return out


def ken_burns(img, t, z0=1.0, z1=1.12, cx=0.5, cy=0.5):
    """Crop with zoom from z0 to z1 (t in 0..1) around (cx, cy), returned at SIZE x SIZE."""
    z = z0 + (z1 - z0) * t; w, h = img.size; side = min(w, h) / z
    x0 = cx * w - side / 2; y0 = cy * h - side / 2
    x0 = min(max(0, x0), w - side); y0 = min(max(0, y0), h - side)
    return img.crop((int(x0), int(y0), int(x0 + side), int(y0 + side))).resize((SIZE, SIZE), Image.BILINEAR)


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * min(max(t, 0), 1))


def title_card(t):
    bg = Image.new("RGB", (SIZE, SIZE), (250, 246, 238)); gd = ImageDraw.Draw(bg)
    for c, (cx, cy) in zip(((252, 226, 206), (222, 236, 248), (210, 240, 242), (232, 224, 248)), ((200, 300), (880, 300), (200, 820), (880, 820))):
        gd.ellipse((cx - 360, cy - 360, cx + 360, cy + 360), fill=c)
    bg = bg.filter(ImageFilter.GaussianBlur(140)).convert("RGBA")
    d = ImageDraw.Draw(bg); F1 = ImageFont.truetype(AV, 92, index=2); F2 = ImageFont.truetype(AV, 34); F3 = ImageFont.truetype(AV, 30, index=2)
    d.text((SIZE // 2, 150), "Year of Dragons", font=F1, fill=(60, 56, 54), anchor="mm")
    d.text((SIZE // 2, 230), "hyperlinked GoodNotes planner  ·  32 growing stickers", font=F2, fill=(110, 100, 95), anchor="mm")
    for i, (key, label, col) in enumerate((("fire", "AUTUMN", (226, 112, 52)), ("ice", "WINTER", (86, 140, 196)), ("water", "SPRING", (36, 148, 166)), ("lightning", "SUMMER", (122, 92, 190)))):
        f = sorted(glob.glob(os.path.join(ROOT, "images", key, "transparent", "08*.png")))[0]
        s = Image.open(f).convert("RGBA"); s = s.crop(s.getchannel("A").getbbox()); s = s.resize((int(s.width * 560 / s.height), 560), Image.LANCZOS)
        cx = 135 + i * 270; bg.alpha_composite(s, (int(cx - s.width / 2), 300))
        d = ImageDraw.Draw(bg); d.text((cx, 900), label, font=F3, fill=col, anchor="mm")
    d.text((SIZE // 2, 990), "instant download  ·  undated  ·  for iPad", font=F2, fill=(140, 134, 128), anchor="mm")
    return bg.convert("RGB")


def frames():
    desk = Scene(os.path.join(SCENES, "desk_square.jpg")); hands = Scene(os.path.join(SCENES, "hands_square.jpg"))
    cover = desk.show(Image.open(os.path.join(PAGES, "00_cover.png")).convert("RGB"))
    contents = hands.show(Image.open(os.path.join(PAGES, "01_contents.png")).convert("RGB"))
    n1 = 3 * FPS
    for i in range(n1):
        yield ken_burns(cover, ease(i / n1), 1.0, 1.25, 0.5, 0.49)
    # growth: 6 s as a crisp "screen recording" of the page itself, zoomed on the growth bar
    n2 = 6 * FPS; pops = [0.6, 1.9, 3.2, 4.5]; cache = {}
    for i in range(n2):
        t = i / FPS; k = sum(1 for p in pops if t >= p); pop = 1.0
        if k:
            dt = t - pops[k - 1]
            if dt < 0.5:
                pop = 0.2 + 0.8 * ease(dt / 0.25) + (0.18 * math.sin(math.pi * dt / 0.5) if dt > 0.25 else 0)
        key = (k, round(pop, 2))
        if key not in cache:
            cache[key] = demo_page(k, pop)
        pg = cache[key]
        # square crop: tight on the bar (side 1100 around y=470) then pull out to show the habit grid (side 1416)
        side = 1416
        cy = 560 if t < 5.0 else 560 + 250 * ease((t - 5.0) / 1.0)
        x0 = 768 - side / 2; y0 = max(0, cy - side / 2)
        fr = pg.crop((int(x0), int(y0), int(x0 + side), int(y0 + side))).resize((SIZE, SIZE), Image.LANCZOS)
        # thin device bezel to read as a screen
        d = ImageDraw.Draw(fr); d.rectangle((0, 0, SIZE - 1, SIZE - 1), outline=(34, 34, 38), width=14)
        yield fr
    n3 = 3 * FPS
    for i in range(n3):
        yield ken_burns(contents, ease(i / n3), 1.15, 1.0, 0.5, 0.5)
    n4 = 3 * FPS; card = title_card(0)
    for i in range(n4):
        f = card
        if i > n4 - 20:
            a = (n4 - i) / 20; f = Image.blend(Image.new("RGB", (SIZE, SIZE), (250, 246, 238)), card, a)
        yield f


def crossfade(seq, cuts=(3 * FPS, 9 * FPS, 12 * FPS), n=12):
    """Blend n frames around each cut for softer transitions."""
    buf = list(seq)
    for c in cuts:
        for j in range(n):
            a = (j + 1) / (n + 1); buf[c - n // 2 + j] = Image.blend(buf[c - n // 2 - 1], buf[c + n // 2], a)
    return buf


if __name__ == "__main__":
    fr = crossfade(frames())
    out = os.path.join(OUT, "video_listing_square.mp4")
    w = imageio.get_writer(out, fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p", macro_block_size=1)
    for f in fr:
        w.append_data(__import__("numpy").asarray(f))
    w.close()
    # vertical 1080x1350 cut for Pinterest / Etsy mobile: pad with cream bars
    out2 = os.path.join(OUT, "video_listing_vertical.mp4")
    w = imageio.get_writer(out2, fps=FPS, codec="libx264", quality=8, pixelformat="yuv420p", macro_block_size=1)
    for f in fr:
        c = Image.new("RGB", (1080, 1350), (250, 246, 238)); c.paste(f, (0, 135)); w.append_data(__import__("numpy").asarray(c))
    w.close()
    print(out, round(os.path.getsize(out) / 1e6, 1), "MB,", len(fr) / FPS, "s"); print(out2, round(os.path.getsize(out2) / 1e6, 1), "MB")
