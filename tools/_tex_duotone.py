# -*- coding: utf-8 -*-
"""把纹理染成地图生态色板的双色调版画。

为什么这么做：
  · 提示词里的「赭黄+烟灰+朱砂」风格段会压过颜色描述，生成出来八个生态全挤在橙红。
  · 地图上本来就有权威色板（web/index.html:8357 ECO_COLORS），颜色不该由我发明。
  · 石版画本身就是两三色套印——把纹理灰度化再按「深墨→主色→纸色」三段映射，
    质感保持不变，颜色严格等于地图色板。

映射：暗部 = 主色×0.30，中间 = 主色，亮部 = 纸色 #e9dfc6
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
SRC = GAME / 'data' / 'tex_final'
OUT = GAME / 'data' / 'tex_tint'
SHEET = GAME / 'data' / 'tex_sheets2'
OUT.mkdir(parents=True, exist_ok=True)

# 权威色板：web/index.html:8357
ECO_COLORS = {
    'surface': (0x99, 0x8b, 0x53),
    'cold':    (0x59, 0xb4, 0xb6),
    'arid':    (0xc9, 0x83, 0x50),
    'sea':     (0x68, 0xb2, 0x91),
    'vent':    (0xd0, 0x6b, 0x6b),
    'rad':     (0x85, 0xa5, 0x67),
    'core':    (0xc4, 0x69, 0x94),
    'nexus':   (0x84, 0xb2, 0xe4),
}
PAPER = (0xe9, 0xdf, 0xc6)
ECOS = list(ECO_COLORS)
DARK_K = 0.30          # 暗部 = 主色 × 0.30


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def duotone(im, base):
    gray = im.convert('L')
    dark = tuple(round(c * DARK_K) for c in base)
    lut_r, lut_g, lut_b = [], [], []
    for g in range(256):
        t = g / 255.0
        if t < 0.5:
            c = lerp(dark, base, t / 0.5)
        else:
            c = lerp(base, PAPER, (t - 0.5) / 0.5)
        lut_r.append(c[0]); lut_g.append(c[1]); lut_b.append(c[2])
    out = Image.merge('RGB', [gray.point(lut_r), gray.point(lut_g), gray.point(lut_b)])
    return out


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
        cell = im.resize((CELL, CELL), Image.LANCZOS)
        x = PAD + (v - 1) * (CELL + GAP)
        y = PAD + r * (CELL + GAP)
        sheet.paste(cell, (x, y))
    d.text((8, PAD + r * (CELL + GAP) + CELL // 2 - 4), eco[:3], fill=(210, 190, 160))
sheet.save(SHEET / 'tinted_overview.png', 'PNG')
print('tinted_overview', sheet.size)

# 主色条：色板本身 + 转换后的平均色，验证颜色是不是真的等于地图色
bar = Image.new('RGB', (8 * 110, 96), (10, 9, 8))
bd = ImageDraw.Draw(bar)
for i, eco in enumerate(ECOS):
    bd.rectangle([i * 110, 0, i * 110 + 105, 44], fill=ECO_COLORS[eco])
    p = OUT / ('%s_v1.png' % eco)
    if p.exists():
        m = Image.open(p).resize((48, 48), Image.LANCZOS)
        px = list(m.getdata())
        n = len(px)
        avg = tuple(sum(q[k] for q in px) // n for k in range(3))
        bd.rectangle([i * 110, 52, i * 110 + 105, 74], fill=avg)
    bd.text((i * 110 + 4, 78), eco[:5], fill=(230, 220, 200))
bar.save(SHEET / 'tint_check.png', 'PNG')
print('tint_check', bar.size)
print('染色完成 →', OUT)
