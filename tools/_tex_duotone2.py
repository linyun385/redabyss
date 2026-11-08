# -*- coding: utf-8 -*-
"""双色调染色 v2：压暗、加重墨、旧纸色更旧。输出到 tex_tint2，和 v1 并排对比。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
SRC = GAME / 'data' / 'tex_final'
OUT = GAME / 'data' / 'tex_tint2'
SHEET = GAME / 'data' / 'tex_sheets2'
OUT.mkdir(parents=True, exist_ok=True)

ECO_COLORS = {
    'surface': (0x99, 0x8b, 0x53), 'cold': (0x59, 0xb4, 0xb6),
    'arid': (0xc9, 0x83, 0x50), 'sea': (0x68, 0xb2, 0x91),
    'vent': (0xd0, 0x6b, 0x6b), 'rad': (0x85, 0xa5, 0x67),
    'core': (0xc4, 0x69, 0x94), 'nexus': (0x84, 0xb2, 0xe4),
}
PAPER = (0xcb, 0xbf, 0xa2)   # 更旧的纸
DARK_K = 0.16                # 更深的墨
MID = 0.62                   # 主色占更大面积，整体压暗
ECOS = list(ECO_COLORS)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def duotone(im, base):
    gray = im.convert('L')
    dark = tuple(round(c * DARK_K) for c in base)
    # 整体压暗 15%，避免高光区域太跳
    gray = gray.point(lambda x: int(x * 0.86))
    lr, lg, lb = [], [], []
    for g in range(256):
        t = g / 255.0
        if t < MID:
            c = lerp(dark, base, t / MID)
        else:
            c = lerp(base, PAPER, (t - MID) / (1 - MID))
        lr.append(c[0]); lg.append(c[1]); lb.append(c[2])
    return Image.merge('RGB', [gray.point(lr), gray.point(lg), gray.point(lb)])


CELL = 268
GAP, PAD = 6, 26
sheet = Image.new('RGB', (PAD * 2 + CELL * 5 + GAP * 4, PAD * 2 + (CELL + GAP) * 8 + 10), (14, 12, 11))
d = ImageDraw.Draw(sheet)
for r, eco in enumerate(ECOS):
    for v in range(1, 6):
        p = SRC / ('%s_v%d.png' % (eco, v))
        if not p.exists():
            continue
        im = duotone(Image.open(p), ECO_COLORS[eco])
        im.save(OUT / ('%s_v%d.png' % (eco, v)), 'PNG')
        sheet.paste(im.resize((CELL, CELL), Image.LANCZOS), (PAD + (v - 1) * (CELL + GAP), PAD + r * (CELL + GAP)))
    d.text((8, PAD + r * (CELL + GAP) + CELL // 2 - 4), eco[:3], fill=(210, 190, 160))
sheet.save(SHEET / 'dark_overview.png', 'PNG')
print('dark_overview', sheet.size)

# 亮版 vs 暗版 同生态 v1 并排，看哪个更贴卡牌
C = 300
cmp = Image.new('RGB', (C * 2 + 30, C * 8 + 9 * 8 + 10), (14, 12, 11))
cd = ImageDraw.Draw(cmp)
for i, eco in enumerate(ECOS):
    a = GAME / 'data' / 'tex_tint' / ('%s_v1.png' % eco)
    b = OUT / ('%s_v1.png' % eco)
    y = 8 + i * (C + 9)
    if a.exists():
        cmp.paste(Image.open(a).resize((C, C), Image.LANCZOS), (8, y))
    if b.exists():
        cmp.paste(Image.open(b).resize((C, C), Image.LANCZOS), (C + 22, y))
    cd.text((8, y + 6), eco, fill=(240, 230, 210))
cmp.save(SHEET / 'light_vs_dark.png', 'PNG')
print('light_vs_dark', cmp.size)
print('暗版 →', OUT)
