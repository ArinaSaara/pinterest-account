#!/usr/bin/env python3
"""Composite planner pages onto photoreal iPad scenes (blank white screens).

Scenes: images/year_of_dragons/scenes/*.jpg  (generated with a blank white iPad screen)
Pages:  images/year_of_dragons/pages/*.png
Output: images/year_of_dragons/mockups_photo/*.jpg

The screen is found as the largest near-white blob; its four extreme corners
give a quad, and the page is perspective-mapped onto it. A faint copy of the
original photo is blended back on top so the screen keeps its lighting.

Run:  python3 build_photo_mockups.py
"""
import glob
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
YD = os.path.join(ROOT, "images", "year_of_dragons")
SCENES = os.path.join(YD, "scenes"); PAGES = os.path.join(YD, "pages"); OUT = os.path.join(YD, "mockups_photo")
os.makedirs(OUT, exist_ok=True)
AV = "/System/Library/Fonts/Avenir Next.ttc"


def white_mask(img, thr=236):
    g = img.convert("RGB"); w, h = g.size
    px = g.load(); m = Image.new("L", (w, h), 0); mp = m.load()
    for y in range(h):
        for x in range(w):
            r, gg, b = px[x, y]
            if r > thr and gg > thr and b > thr and abs(r - b) < 14 and abs(r - gg) < 14:
                mp[x, y] = 255
    return m


def largest_blob(mask):
    """Flood fill from the mask centre region to keep only the screen blob."""
    w, h = mask.size; mp = mask.load()
    # seed: the white pixel closest to the centre
    cx, cy = w // 2, h // 2; seed = None
    for r in range(0, max(w, h)):
        for dx, dy in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r), (r, r), (-r, -r), (r, -r), (-r, r)):
            x, y = cx + dx, cy + dy
            if 0 <= x < w and 0 <= y < h and mp[x, y] == 255:
                seed = (x, y); break
        if seed:
            break
    out = Image.new("L", (w, h), 0); op = out.load()
    stack = [seed]; op[seed] = 255
    while stack:
        x, y = stack.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and mp[nx, ny] == 255 and op[nx, ny] == 0:
                op[nx, ny] = 255; stack.append((nx, ny))
    return out


def quad_of(mask):
    w, h = mask.size; mp = mask.load()
    pts = [(x, y) for y in range(0, h, 2) for x in range(0, w, 2) if mp[x, y]]
    tl = min(pts, key=lambda p: p[0] + p[1]); br = max(pts, key=lambda p: p[0] + p[1])
    tr = max(pts, key=lambda p: p[0] - p[1]); bl = min(pts, key=lambda p: p[0] - p[1])
    return tl, tr, br, bl


def persp_coeffs(src, dst):
    """Coefficients for Image.transform(PERSPECTIVE) mapping dst quad -> src rect (PIL wants the inverse)."""
    A = []; B = []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    n = 8
    M = [row[:] + [B[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c])); M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                for k in range(c, n + 1):
                    M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def composite(scene_path, page_path, out_name, shrink=0.0, lighting=0.10, label=None):
    scene = Image.open(scene_path).convert("RGB")
    small = scene.resize((scene.width // 4, scene.height // 4), Image.BILINEAR)
    blob = largest_blob(white_mask(small)).resize(scene.size, Image.NEAREST).filter(ImageFilter.MaxFilter(3))
    tl, tr, br, bl = quad_of(blob)
    if shrink:
        cx = (tl[0] + tr[0] + br[0] + bl[0]) / 4; cy = (tl[1] + tr[1] + br[1] + bl[1]) / 4
        tl, tr, br, bl = [(cx + (x - cx) * (1 - shrink), cy + (y - cy) * (1 - shrink)) for x, y in (tl, tr, br, bl)]
    page = Image.open(page_path).convert("RGB")
    pw, ph = page.size
    coeffs = persp_coeffs([(0, 0), (pw, 0), (pw, ph), (0, ph)], [tl, tr, br, bl])
    warped = page.transform(scene.size, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    # mask = warped quad
    qm = Image.new("L", scene.size, 0); ImageDraw.Draw(qm).polygon([tl, tr, br, bl], fill=255)
    qm = qm.filter(ImageFilter.GaussianBlur(1.2))
    out = scene.copy(); out.paste(warped, (0, 0), qm)
    # keep a hint of the photo's screen lighting / reflections
    lit = Image.blend(out, scene, lighting); out.paste(lit, (0, 0), qm)
    if label:
        d = ImageDraw.Draw(out); S = out.width
        F1 = ImageFont.truetype(AV, int(S * 0.036), index=2); F2 = ImageFont.truetype(AV, int(S * 0.017))
        pad = int(S * 0.02); t1, t2 = label
        w1 = d.textlength(t1, font=F1); w2 = d.textlength(t2, font=F2); bw = max(w1, w2) + 2 * pad; bh = int(S * 0.036 + S * 0.017 + 3 * pad)
        x0, y0 = int(S * 0.04), int(S * 0.04)
        tag = Image.new("RGBA", (int(bw), bh), (255, 255, 255, 215)); out.paste(tag, (x0, y0), tag)
        d.text((x0 + pad, y0 + pad), t1, font=F1, fill=(60, 56, 54)); d.text((x0 + pad, y0 + pad + int(S * 0.036) + pad // 2), t2, font=F2, fill=(120, 110, 100))
    out.save(os.path.join(OUT, out_name), quality=92)
    print(out_name, "quad:", [tuple(int(v) for v in p) for p in (tl, tr, br, bl)])


def growth_demo_page():
    """September page with the first four stages pasted in and some ticks, saved to pages/_demo_sep.png."""
    pg = Image.open(os.path.join(PAGES, "fire_09_sep.png")).convert("RGBA")
    M, W = 110, 1536; slot = (W - 2 * M) / 8; ry = 320; a = (226, 112, 52)
    for i in range(4):
        f = sorted(glob.glob(os.path.join(ROOT, "images", "fire", "transparent", f"0{i + 1}*.png")))[0]
        s = Image.open(f).convert("RGBA"); b = s.getchannel("A").getbbox(); s = s.crop(b)
        s = s.resize((int(s.width * 170 / s.height), 170), Image.LANCZOS)
        cx = M + slot * i + slot / 2; pg.alpha_composite(s, (int(cx - s.width / 2), int(ry + 100 - s.height / 2)))
    d = ImageDraw.Draw(pg)
    for i in range(4):
        cx = M + slot * i + slot / 2; d.ellipse((cx - 13, ry + 250, cx + 13, ry + 276), fill=a)
    d.line((M + slot / 2, ry + 263, M + slot * 3.5, ry + 263), fill=a, width=5)
    gx = M + 300; cell = (W - M - gx) / 30; gy = ry + 340 + 20 + 50
    for r in range(5):
        yy = gy + 30 + r * 78
        for day in range(14 - r * 2):
            x = gx + day * cell + cell / 2; d.ellipse((x - 11, yy + 17, x + 11, yy + 39), fill=(252, 226, 206), outline=a, width=2)
    p = os.path.join(PAGES, "_demo_sep.png"); pg.convert("RGB").save(p); return p


if __name__ == "__main__":
    demo = growth_demo_page()
    composite(os.path.join(SCENES, "desk_square.jpg"), os.path.join(PAGES, "00_cover.png"), "01_desk_cover.jpg",
              label=("Year of Dragons", "digital planner for GoodNotes · 33 pages · 32 dragon stickers"))
    composite(os.path.join(SCENES, "desk_square.jpg"), demo, "02_desk_growth.jpg",
              label=("Watch it grow", "paste the next dragon stage every time you hit a streak milestone"))
    composite(os.path.join(SCENES, "hands_square.jpg"), os.path.join(PAGES, "01_contents.png"), "03_hands_contents.jpg",
              label=("Hyperlinked contents", "tap a season, a month or a tracker and jump straight there"))
    composite(os.path.join(SCENES, "hands_square.jpg"), os.path.join(PAGES, "03_hall_of_dragons.png"), "04_hands_hall.jpg")
    composite(os.path.join(SCENES, "linen_pin.jpg"), os.path.join(PAGES, "00_cover.png"), "05_pin_cover.jpg")
    composite(os.path.join(SCENES, "linen_pin.jpg"), os.path.join(PAGES, "ice_01_sheet.png"), "06_pin_ice_sheet.jpg")
    composite(os.path.join(SCENES, "desk_square.jpg"), os.path.join(PAGES, "lightning_90_savings.png"), "07_desk_hoard.jpg")
    files = sorted(glob.glob(os.path.join(OUT, "*.jpg"))); h = 600
    ims = [Image.open(f).convert("RGB") for f in files if "preview" not in f]; ims = [i.resize((int(i.width * h / i.height), h), Image.LANCZOS) for i in ims]
    sheet = Image.new("RGB", (sum(i.width for i in ims) + 10 * (len(ims) + 1), h + 20), (200, 196, 190)); x = 10
    for i in ims:
        sheet.paste(i, (x, 10)); x += i.width + 10
    sheet.save(os.path.join(OUT, "preview_photo_mockups.jpg"), quality=85)
