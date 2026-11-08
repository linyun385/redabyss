# -*- coding: utf-8 -*-
"""把 eco_textures 的 8×5 张拼成 8 张联络表，供人一眼对比选图。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
ART = GAME / 'web' / 'assets' / 'art'
OUT = GAME / 'data' / 'tex_sheets'
OUT.mkdir(parents=True, exist_ok=True)

ECOS = ['surface', 'cold', 'arid', 'sea', 'vent', 'rad', 'core', 'nexus']
CELL = 340
GAP = 8
PAD = 10


def fit(im, size):
    im = im.convert('RGB')
    w, h = im.size
    s = min(size / w, size / h)
    im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    canvas = Image.new('RGB', (size, size), (18, 16, 14))
    canvas.paste(im, ((size - im.size[0]) // 2, (size - im.size[1]) // 2))
    return canvas


for eco in ECOS:
    cells = []
    for v in range(1, 6):
        p = ART / ('tex_%s_v%d.webp' % (eco, v))
        if p.exists():
            cells.append(fit(Image.open(p), CELL))
        else:
            blank = Image.new('RGB', (CELL, CELL), (60, 20, 20))
            cells.append(blank)
    W = PAD * 2 + CELL * 5 + GAP * 4
    H = PAD * 2 + CELL + 34
    sheet = Image.new('RGB', (W, H), (12, 11, 10))
    d = ImageDraw.Draw(sheet)
    for i, c in enumerate(cells):
        x = PAD + i * (CELL + GAP)
        sheet.paste(c, (x, PAD))
        d.text((x + 6, PAD + CELL + 8), 'v%d' % (i + 1), fill=(220, 200, 170))
    out = OUT / ('eco_%s.png' % eco)
    sheet.save(out, 'PNG')
    print(out, sheet.size)
