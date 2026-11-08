# -*- coding: utf-8 -*-
"""给核心卡卡面套统一的金属金色边框（程序生成，不经模型）。

版式（768×768）：
    0–4    深黑垫边
    4–9    暗金内凹线
    9–45   金色主带（斜向渐变 + 每 3px 一道拉丝暗线）
    45–50  暗金分层线
    50–53  亮金细线
    53–54  黑线（与画面分隔）
    54–714 画面（660 见方）
四角叠一块更厚的金色角片，角片上压一个凹点。
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
RAW = GAME / 'art' / '_wanx'
ART = GAME / 'web' / 'assets' / 'art'

SIZE = 768
PIC = 660
OFF = (SIZE - PIC) // 2      # 54
W = OFF                      # 框宽

DARK = (10, 6, 4)
GOLD_HI = (246, 226, 158)
GOLD_MID = (201, 162, 74)
GOLD_LO = (138, 100, 32)
GOLD_DEEP = (72, 50, 16)
BLACK = (6, 4, 3)


def gold_grad(t):
    """t: 0→1，返回该位置的金色（暗金 → 亮金 → 暗金，模拟金属高光在中线）"""
    if t < 0.35:
        k = t / 0.35
        a, b = GOLD_LO, GOLD_HI
    else:
        k = (t - 0.35) / 0.65
        a, b = GOLD_HI, GOLD_DEEP
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def make_frame():
    """返回一张 SIZE×SIZE 的 RGBA 框（中间透空）"""
    fr = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(fr)

    # 四条边按「沿框宽方向的渐变」逐像素画，形成斜向高光
    for i in range(W):
        col = gold_grad(i / max(1, W - 1))
        d.rectangle([i, 0, i, SIZE], fill=col + (255,))
        d.rectangle([0, i, SIZE, i], fill=col + (255,))
        d.rectangle([SIZE - 1 - i, 0, SIZE - 1 - i, SIZE], fill=col + (255,))
        d.rectangle([0, SIZE - 1 - i, SIZE, SIZE - 1 - i], fill=col + (255,))

    # 拉丝：每 3px 一道极暗的细线（只画在主带区域）
    for i in range(9, 45, 3):
        d.rectangle([i, 0, i, SIZE], outline=None, fill=(90, 64, 20, 70))
        d.rectangle([0, i, SIZE, i], fill=(90, 64, 20, 70))
        d.rectangle([SIZE - 1 - i, 0, SIZE - 1 - i, SIZE], fill=(90, 64, 20, 70))
        d.rectangle([0, SIZE - 1 - i, SIZE, SIZE - 1 - i], fill=(90, 64, 20, 70))

    # 关键分层线（外→内）
    def line(pos, color, width=1):
        d.rectangle([pos, pos, SIZE - 1 - pos, SIZE - 1 - pos], outline=color, width=width)

    line(0, BLACK + (255,), 4)          # 外垫边
    line(4, GOLD_DEEP + (255,), 5)      # 内凹线
    line(45, GOLD_DEEP + (255,), 5)     # 内分层
    line(50, GOLD_HI + (255,), 3)       # 亮金细线
    line(53, BLACK + (255,), 1)         # 与画面分隔

    # 四角角片
    corner = 96
    for (cx, cy, dx, dy) in [
        (0, 0, 1, 1), (SIZE - corner, 0, 1, 1),
        (0, SIZE - corner, 1, 1), (SIZE - corner, SIZE - corner, 1, 1),
    ]:
        d.rectangle([cx, cy, cx + corner, cy + corner],
                    fill=GOLD_MID + (255,))
        d.rectangle([cx, cy, cx + corner, cy + corner],
                    outline=GOLD_DEEP + (255,), width=3)
        d.rectangle([cx + 6, cy + 6, cx + corner - 6, cy + corner - 6],
                    outline=GOLD_HI + (255,), width=2)
        # 角片中央的凹点
        m = corner // 2
        r = 7
        d.ellipse([cx + m - r, cy + m - r, cx + m + r, cy + m + r],
                  fill=GOLD_DEEP + (255,))
        d.ellipse([cx + m - r + 2, cy + m - r + 2, cx + m + r - 2, cy + m + r - 2],
                  fill=GOLD_HI + (255,))

    # 把中间透开（保留 53px 处的黑分隔线）
    inner = OFF
    d.rectangle([inner, inner, SIZE - 1 - inner, SIZE - 1 - inner], fill=(0, 0, 0, 0))
    return fr


def apply(cid, save_preview=False):
    src = RAW / (cid + '.png')
    if not src.exists():
        src = ART / (cid + '.webp')
    im = Image.open(src).convert('RGB').resize((PIC, PIC), Image.LANCZOS)
    canvas = Image.new('RGB', (SIZE, SIZE), DARK)
    canvas.paste(im, (OFF, OFF))
    canvas = Image.alpha_composite(canvas.convert('RGBA'), make_frame()).convert('RGB')
    out = ART / (cid + '.webp')
    canvas.save(out, 'WEBP', quality=90, method=6)
    if save_preview:
        canvas.save(GAME / 'art' / '_review' / (cid + '_gold.png'))
    return out


if __name__ == '__main__':
    ids = sys.argv[1:] or ['anm_0051', 'anm_0052', 'anm_0053',
                           'anm_0054', 'anm_0055', 'anm_0056', 'anm_0057']
    for cid in ids:
        p = apply(cid, save_preview=True)
        print(f'{cid}: {p.stat().st_size // 1024}KB')
