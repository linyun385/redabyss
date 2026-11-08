# -*- coding: utf-8 -*-
"""量化 8 个生态的主色，检查区分度。输出平均色 / 色相 / 明度，并拼一张主色条。"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
FINAL = GAME / 'data' / 'tex_final'
OUT = GAME / 'data' / 'tex_sheets2'
ECOS = ['surface', 'cold', 'arid', 'sea', 'vent', 'rad', 'core', 'nexus']


def stats(im):
    im = im.resize((64, 64), Image.LANCZOS).convert('RGB')
    px = list(im.getdata())
    n = len(px)
    r = sum(p[0] for p in px) / n
    g = sum(p[1] for p in px) / n
    b = sum(p[2] for p in px) / n
    hsv = im.convert('HSV').resize((1, 1), Image.LANCZOS).getpixel((0, 0))
    return (round(r), round(g), round(b)), hsv, max(px, key=sum)


rows = []
for eco in ECOS:
    cols = []
    for v in range(1, 6):
        p = FINAL / ('%s_v%d.png' % (eco, v))
        if not p.exists():
            continue
        rgb, hsv, bright = stats(Image.open(p))
        cols.append((v, rgb, hsv))
    if not cols:
        continue
    ar = tuple(sum(c[1][i] for c in cols) // len(cols) for i in range(3))
    ah = sum(c[2][0] for c in cols) // len(cols)
    print('%-8s 平均RGB=%s  平均色相=%3d  明度=%3d' % (eco, ar, ah, sum(c[2][2] for c in cols) // len(cols)))
    rows.append((eco, ar, ah))

# 主色条：每生态一行，5 个变体的平均色
W = 8 * 110
bar = Image.new('RGB', (W, 60), (10, 9, 8))
d = ImageDraw.Draw(bar)
for i, (eco, rgb, h) in enumerate(rows):
    d.rectangle([i * 110, 0, i * 110 + 105, 45], fill=rgb)
    d.text((i * 110 + 4, 48), '%s h%d' % (eco[:3], h), fill=(230, 220, 200))
bar.save(OUT / 'main_colors.png', 'PNG')

# 色相距离：找出撞色的两两对
print('\n色相距离（<12 视为撞色）：')
for i in range(len(rows)):
    for j in range(i + 1, len(rows)):
        d1 = abs(rows[i][2] - rows[j][2])
        d1 = min(d1, 255 - d1)
        if d1 < 12:
            print('  !! %s vs %s : 色相差 %d  RGB %s / %s' % (rows[i][0], rows[j][0], d1, rows[i][1], rows[j][1]))
print('main_colors ->', OUT / 'main_colors.png')
