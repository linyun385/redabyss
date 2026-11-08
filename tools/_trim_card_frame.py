# -*- coding: utf-8 -*-
"""检测并裁掉卡面四周的纸边框（米黄/纸白），保留黑底画面。

判据：逐边扫描，若最外 N 像素的平均亮度显著高于画面中心且接近纸色，判为纸边框。
只处理指定 id；裁前把原 webp 备份到 art/_review/v1/。
"""
import shutil
import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
ART = GAME / 'web' / 'assets' / 'art'
BAK = GAME / 'art' / '_review' / 'v1'
IDS = ['anm_0051', 'anm_0052', 'anm_0053', 'anm_0054', 'anm_0055', 'anm_0056', 'anm_0057']

# 纸边框判定：外侧条带亮度 > 110 且饱和度低（偏米黄/白），内圈明显更暗
PROBE = 0.09      # 探测最外 9%
PAPER_MIN = 110   # 纸色亮度下限（0-255）


def strip_luma(im, side, frac=PROBE):
    w, h = im.size
    n = max(1, int(min(w, h) * frac))
    if side == 'top':
        box = (0, 0, w, n)
    elif side == 'bottom':
        box = (0, h - n, w, h)
    elif side == 'left':
        box = (0, 0, n, h)
    else:
        box = (w - n, 0, w, h)
    return sum(im.crop(box).convert('L').resize((8, 8)).getdata()) / 64


def find_frame(im):
    """返回 (left, top, right, bottom) 要各裁掉多少像素；没框返回全 0"""
    w, h = im.size
    n = max(1, int(min(w, h) * PROBE))
    lums = {s: strip_luma(im, s) for s in ('top', 'bottom', 'left', 'right')}
    center = sum(im.crop((w // 3, h // 3, 2 * w // 3, 2 * h // 3)).convert('L').resize((8, 8)).getdata()) / 64
    cuts = {}
    for s, v in lums.items():
        # 外侧比中心亮出 60 以上 → 判为纸框
        cuts[s] = n if (v > PAPER_MIN and v - center > 60) else 0
    return cuts, lums, center


BAK.mkdir(parents=True, exist_ok=True)
for cid in IDS:
    f = ART / (cid + '.webp')
    if not f.exists():
        print(f'{cid}: 无文件，跳过')
        continue
    im = Image.open(f).convert('RGB')
    cuts, lums, center = find_frame(im)
    tag = ' '.join(f'{k}={v}' for k, v in cuts.items())
    if not any(cuts.values()):
        print(f'{cid}: 无纸框（实测亮度 ' + ' '.join(f'{k}:{v:.0f}' for k, v in lums.items()) + f' 中心 {center:.0f}）')
        continue
    bak = BAK / (cid + '_withframe.webp')
    if not bak.exists():
        shutil.copy2(f, bak)
    l, t, r, b = cuts['left'], cuts['top'], cuts['right'], cuts['bottom']
    box = (l, t, im.width - r, im.height - b)
    out = im.crop(box)
    out.save(f, 'WEBP', quality=88, method=6)
    print(f'{cid}: 裁 {tag} → {out.size}  ({f.stat().st_size // 1024}KB)')
print('完成')
