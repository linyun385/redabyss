# -*- coding: utf-8 -*-
"""生态纹理后处理：裁纸边 → 输出 final → 拼 8×5 总览 → 小尺寸平铺测试。

为什么裁边：万相会把「泛黄旧纸」画成四周一圈淡色边框，不裁掉平铺会出现格子线。
为什么做小尺寸测试：地图上生态区实际可能只有几十像素，远看时的区分度比大图更重要。
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
ART = GAME / 'web' / 'assets' / 'art'
OUT = GAME / 'data' / 'tex_final'
SHEET = GAME / 'data' / 'tex_sheets2'
OUT.mkdir(parents=True, exist_ok=True)
SHEET.mkdir(parents=True, exist_ok=True)

ECOS = ['surface', 'cold', 'arid', 'sea', 'vent', 'rad', 'core', 'nexus']
CROP = 0.055          # 每边裁掉 5.5%
CELL = 268
SMALL = 64            # 地图上生态区的大致像素尺寸


def load(eco, v):
    p = ART / ('tex2_%s_v%d.webp' % (eco, v))
    if not p.exists():
        return None
    im = Image.open(p).convert('RGB')
    w, h = im.size
    c = int(min(w, h) * CROP)
    return im.crop((c, c, w - c, h - c))


def cell(im, n):
    s = im.resize((n, n), Image.LANCZOS)
    return s


manifest = []
for eco in ECOS:
    for v in range(1, 6):
        im = load(eco, v)
        if im is None:
            print('MISS', eco, v)
            continue
        out = OUT / ('%s_v%d.png' % (eco, v))
        im.save(out, 'PNG')
        manifest.append((eco, v, out))

# ---- 1) 8×5 总览（每行一个生态，左起 v1..v5）
GAP, PAD = 6, 26
W = PAD * 2 + CELL * 5 + GAP * 4
H = PAD * 2 + (CELL + GAP) * 8 + 10
sheet = Image.new('RGB', (W, H), (14, 12, 11))
d = ImageDraw.Draw(sheet)
for r, eco in enumerate(ECOS):
    for v in range(1, 6):
        c = load(eco, v)
        if c is None:
            continue
        x = PAD + (v - 1) * (CELL + GAP)
        y = PAD + r * (CELL + GAP)
        sheet.paste(cell(c, CELL), (x, y))
    d.text((6, PAD + r * (CELL + GAP) + CELL // 2 - 4), eco[:3], fill=(210, 190, 160))
sheet.save(SHEET / 'overview.png', 'PNG')
print('overview', sheet.size)

# ---- 2) 小尺寸平铺测试：每生态 v1 缩到 64px 后 6×6 平铺在 384 方块里
TILE_N = 6
BLOCK = SMALL * TILE_N
cols = 4
rows = 2
B = Image.new('RGB', (cols * (BLOCK + GAP) + GAP, rows * (BLOCK + 30 + GAP) + GAP), (12, 11, 10))
bd = ImageDraw.Draw(B)
for i, eco in enumerate(ECOS):
    c = load(eco, 1)
    if c is None:
        continue
    t = c.resize((SMALL, SMALL), Image.LANCZOS)
    cx = GAP + (i % cols) * (BLOCK + GAP)
    cy = GAP + (i // cols) * (BLOCK + 30 + GAP)
    for ty in range(TILE_N):
        for tx in range(TILE_N):
            B.paste(t, (cx + tx * SMALL, cy + ty * SMALL))
    bd.text((cx + 4, cy + BLOCK + 6), eco, fill=(220, 200, 170))
B.save(SHEET / 'tiling.png', 'PNG')
print('tiling', B.size)

# ---- 3) 背景预览：拿每个生态的纹理放大+模糊+压暗，模拟「进入该生态时的背景」
BW, BH = 640, 360
bg = Image.new('RGB', (cols * BW // 2 + GAP, rows * BH // 2 + GAP), (12, 11, 10))
for i, eco in enumerate(ECOS):
    c = load(eco, 2) or load(eco, 1)
    if c is None:
        continue
    big = c.resize((BW, BH), Image.LANCZOS).filter(ImageFilter.GaussianBlur(6))
    big = Image.eval(big, lambda x: int(x * 0.62))
    small = big.resize((BW // 2, BH // 2), Image.LANCZOS)
    x = GAP + (i % cols) * (BW // 2 + GAP)
    y = GAP + (i // cols) * (BH // 2 + GAP)
    bg.paste(small, (x, y))
bg.save(SHEET / 'backgrounds.png', 'PNG')
print('backgrounds', bg.size)
print('final 图 %d 张 → %s' % (len(manifest), OUT))
