#!/usr/bin/env python3
"""Animate stickers with a hosted image-to-video model on fal.ai (Kling v3 Pro by default).

Needs FAL_KEY in .env and `pip install fal-client`. Every call costs money: start with ONE sticker.

Run:  .venv-planner/bin/python build_it_fal_video.py work_1            # one sticker, 5 s
      .venv-planner/bin/python build_it_fal_video.py work_1 dev_3 ...  # several
Output: images/it_girl/video/fal_<sticker>.mp4 (+ the cream-background input in images/it_girl/fal_in/)
"""
import os
import sys
import urllib.request

import fal_client
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__)); IT = os.path.join(ROOT, "images", "it_girl")
MODEL = os.environ.get("FAL_MODEL", "fal-ai/kling-video/v3/pro/image-to-video"); DURATION = os.environ.get("DURATION", "5"); VERTICAL = bool(os.environ.get("VERTICAL"))   # VERTICAL=1 -> 2:3 input for Pinterest
STYLE = " Keep the hand-painted watercolor illustration style, the characters' faces and outfits unchanged. Locked static camera, the whole illustration stays in frame without zooming or panning, smooth gentle motion, no text."
PROMPTS = {
    "work_1": "The girl slowly lifts the mug, takes a small sip, blinks softly and smiles; steam rises from the mug; the small dog breathes calmly; the warm candle glow flickers.",
    "dev_3": "The girl cheers with both arms up, laughing; golden confetti falls; the small dog wags and bounces; the lamp glows.",
    "seasons_7": "The girl glides on the ice with a graceful skating motion, scarf flowing, soft snow falling, string lights twinkling.",
    "seasons_8": "The girl hangs a golden ornament on the Christmas tree and smiles; the tree lights twinkle; the small dog wags its tail.",
    "seasons_5": "The girl gathers a bunch of maple leaves, smiles and tosses a few into the air; golden leaves drift down; the small dog in the sweater wags its tail and sniffs the leaves; warm autumn light and the lamp glow.",
    "seasons_6": "The girl carves the pumpkin with a small tool, smiles; the lantern flickers warmly; steam rises from the bowl.",
    "cozy_1": "The girl turns a page of her book, blinks softly and smiles; the lamp glow flickers; the dog sleeps and breathes calmly.",
    "fit_2": "The girl does smooth dumbbell curls with a happy expression; her curls bounce slightly; leaves sway.",
    "work_3": "The girl types on the laptop, glances at the screen and smiles; the dog breathes calmly; the lamp glow flickers.",
}


def load_key():
    for l in open(os.path.join(ROOT, ".env")):
        if l.startswith("FAL_KEY="):
            os.environ["FAL_KEY"] = l.rstrip("\n").partition("=")[2]


def make_input(name):
    os.makedirs(os.path.join(IT, "fal_in"), exist_ok=True); p = os.path.join(IT, "fal_in", name + ("_v" if VERTICAL else "") + ".jpg")
    st = Image.open(os.path.join(IT, "cut", name + ".png")).convert("RGBA"); sc = min(900 / st.width, (1000 if VERTICAL else 760) / st.height); st = st.resize((int(st.width * sc), int(st.height * sc)), Image.LANCZOS)
    W, H = (1080, 1620) if VERTICAL else (1080, 1080)
    bg = Image.new("RGB", (W, H), (250, 246, 234)); bg.paste(st, ((W - st.width) // 2, (H - st.height) // 2), st); bg.save(p, quality=95); return p


def main():
    load_key(); names = sys.argv[1:] or ["work_1"]
    for name in names:
        url = fal_client.upload_file(make_input(name)); print(name, "uploaded; generating with", MODEL, "...")
        res = fal_client.subscribe(MODEL, arguments=dict(start_image_url=url, prompt=PROMPTS.get(name, "The girl moves gently and naturally, blinks and smiles.") + STYLE, duration=DURATION, generate_audio=False),
                                   with_logs=False)
        out = os.path.join(IT, "video", f"fal_{name}{'_vertical' if VERTICAL else ''}.mp4"); urllib.request.urlretrieve(res["video"]["url"], out); print(out, round(os.path.getsize(out) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
