#!/usr/bin/env python3
"""Instantiate static TTFs (reportlab can't use variable fonts) from the OFL variable fonts in fonts/src.

Fonts (all SIL Open Font License, from github.com/google/fonts): Playfair Display, DM Sans, Jost, Pinyon Script.
Run:  .venv-planner/bin/python build_it_fonts.py
"""
import os
import shutil

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "fonts", "src"); OUT = os.path.join(ROOT, "fonts")

JOBS = [
    ("PlayfairDisplay[wght].ttf", "PlayfairDisplay-Regular.ttf", {"wght": 400}),
    ("PlayfairDisplay[wght].ttf", "PlayfairDisplay-Bold.ttf", {"wght": 700}),
    ("PlayfairDisplay-Italic[wght].ttf", "PlayfairDisplay-Italic.ttf", {"wght": 400}),
    ("DMSans[opsz,wght].ttf", "DMSans-Regular.ttf", {"wght": 400, "opsz": 14}),
    ("DMSans[opsz,wght].ttf", "DMSans-Medium.ttf", {"wght": 500, "opsz": 14}),
    ("DMSans[opsz,wght].ttf", "DMSans-SemiBold.ttf", {"wght": 600, "opsz": 14}),
    ("DMSans-Italic[opsz,wght].ttf", "DMSans-Italic.ttf", {"wght": 400, "opsz": 14}),
    ("Jost[wght].ttf", "Jost-ExtraLight.ttf", {"wght": 200}),
]
for src, dst, axes in JOBS:
    f = TTFont(os.path.join(SRC, src)); instantiateVariableFont(f, axes, inplace=True); f.save(os.path.join(OUT, dst))
shutil.copy(os.path.join(SRC, "PinyonScript-Regular.ttf"), os.path.join(OUT, "PinyonScript-Regular.ttf"))
print(sorted(os.listdir(OUT)))
