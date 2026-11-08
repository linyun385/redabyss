# -*- coding: utf-8 -*-
"""把选中的 8 张生态纹理导出成游戏用资产（web/assets/tex/）。

为什么压暗+降对比：地图格子只有 24px，纹理是底色不是主角——
对比度高会让格子里的图标/连线读不出来。这一步让纹理退到背景。
"""
import sys
from pathlib import Path
from PIL import Image, ImageEnhance

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
SRC = GAME / 'data' / 'tex_tint2'
OUT = GAME / 'web' / 'assets' / 'tex'
OUT.mkdir(parents=True, exist_ok=True)

# 选定版本（用户 2026-11-05 拍板「用你推荐的那套」）
PICK = {
    'surface': 1, 'cold': 1, 'arid': 1, 'sea': 2,
    'vent': 2, 'rad': 1, 'core': 1, 'nexus': 1,
}
SIZE = 128            # 显示 48px，2.7× 缩放余量
# 2026-11-05 第一版 0.78/0.86 在实机上看「淡到几乎看不出材质」，提到 0.94/1.16 重出。
BRIGHT = 0.94         # 轻微压暗，避免抢节点图标的对比
CONTRAST = 1.16       # 纹理要看得出来

for eco, v in PICK.items():
    p = SRC / ('%s_v%d.png' % (eco, v))
    im = Image.open(p).convert('RGB')
    im = ImageEnhance.Brightness(im).enhance(BRIGHT)
    im = ImageEnhance.Contrast(im).enhance(CONTRAST)
    im = im.resize((SIZE, SIZE), Image.LANCZOS)
    out = OUT / ('eco_%s.webp' % eco)
    im.save(out, 'WEBP', quality=90, method=6)
    print('%-8s v%d -> %s (%d B)' % (eco, v, out.name, out.stat().st_size))
print('导出目录', OUT)
