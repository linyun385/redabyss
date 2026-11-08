# -*- coding: utf-8 -*-
"""基础牌符号图：程序化生成，血红底 + 极简剪影。

为什么不用 AI 生图：
  1. ComfyUI 没配 COMFYUI_DIR，起不来
  2. 卡面图在界面上只有几十像素高，AI 的细节全被缩没
  3. 「背景必须是血红」这条用代码能 100% 保证，AI 保证不了

产出 3 张，覆盖 9 个内联卡 id：
  sym_atk      一击 / 苍民白班·攻击 / 苍民夜班·攻击
  sym_def      缩起 / 苍民白班·防御 / 苍民夜班·防御
  sym_sign     三个职业的签名牌
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw, ImageFilter

GAME = Path(__file__).resolve().parents[1]
OUT = GAME / 'web' / 'assets' / 'art'
S = 512

# 血红：上暗下亮，符合「红光从下往上」
BG_TOP = (58, 0, 0)
BG_BOT = (176, 16, 16)
INK = (226, 216, 196)      # 旧纸白
EDGE = (10, 4, 4)          # 近黑描边


def base():
    """竖向渐变的血红底。"""
    im = Image.new('RGB', (S, S))
    d = ImageDraw.Draw(im)
    for y in range(S):
        t = y / (S - 1)
        t = t ** 0.85
        c = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3))
        d.line([(0, y), (S, y)], fill=c)
    return im


def hatch(im, step=9, alpha=26):
    """斜向排线，让画面有石版画的线感。"""
    lay = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for x in range(-S, S * 2, step):
        d.line([(x, 0), (x - S, S)], fill=(0, 0, 0, alpha), width=1)
    im.paste(Image.alpha_composite(im.convert('RGBA'), lay).convert('RGB'), (0, 0))


def vignette(im):
    """四角压暗。"""
    lay = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(lay)
    for r in range(S // 2, 0, -4):
        a = int(150 * (1 - r / (S / 2)) ** 1.6)
        d.ellipse([S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r], fill=a)
    lay = lay.filter(ImageFilter.GaussianBlur(28))
    dark = Image.new('RGB', (S, S), (8, 0, 0))
    im.paste(dark, (0, 0), lay)


def save(im, name):
    im.save(OUT / (name + '.webp'), 'WEBP', quality=88, method=6)
    print('  %s.webp' % name)


def draw_atk():
    """砸下的锤：粗柄 + 梯形锤头，带凿痕。"""
    im = base()
    d = ImageDraw.Draw(im)
    cx, cy = S // 2, S // 2

    # 柄（斜置）
    d.polygon([(cx - 20, cy + 150), (cx - 2, cy + 150),
               (cx + 62, cy - 96), (cx + 44, cy - 104)], fill=INK, outline=EDGE, width=5)
    # 锤头
    d.polygon([(cx - 96, cy - 158), (cx + 96, cy - 196),
               (cx + 116, cy - 96), (cx - 76, cy - 58)], fill=INK, outline=EDGE, width=7)
    # 锤面带凿痕
    for k in range(4):
        y0 = cy - 150 + k * 22
        d.line([(cx - 86, y0), (cx + 100, y0 - 16)], fill=EDGE, width=3)
    # 砸击的裂纹
    d.line([(cx - 150, cy + 40), (cx - 60, cy + 10)], fill=EDGE, width=4)
    d.line([(cx + 90, cy + 30), (cx + 170, cy - 6)], fill=EDGE, width=4)
    hatch(im)
    vignette(im)
    save(im, 'sym_atk')


def draw_def():
    """缩起：拱形轮廓 + 内里的蜷缩人形。"""
    im = base()
    d = ImageDraw.Draw(im)
    cx, cy = S // 2, S // 2

    # 外盾（下半圆弧 + 上平）
    d.pieslice([cx - 150, cy - 130, cx + 150, cy + 190], 0, 180, fill=INK, outline=EDGE, width=7)
    d.rectangle([cx - 150, cy - 138, cx + 150, cy + 26], fill=INK, outline=EDGE, width=7)
    # 内里的蜷缩轮廓（深色挖空）
    d.ellipse([cx - 96, cy - 96, cx + 96, cy + 66], fill=(120, 10, 10))
    # 蜷起的人：头 + 背脊弧
    d.ellipse([cx - 26, cy - 74, cx + 14, cy - 34], fill=INK)
    d.arc([cx - 74, cy - 60, cx + 56, cy + 52], 300, 140, fill=INK, width=17)
    # 盾上的铆点
    for pt in [(cx - 128, cy - 108), (cx + 128, cy - 108), (cx - 128, cy - 6), (cx + 128, cy - 6)]:
        d.ellipse([pt[0] - 8, pt[1] - 8, pt[0] + 8, pt[1] + 8], fill=EDGE)
    hatch(im)
    vignette(im)
    save(im, 'sym_def')


def draw_sign():
    """签名牌：一张斜放的纸，上有横线与折角。"""
    im = base()
    d = ImageDraw.Draw(im)
    cx, cy = S // 2, S // 2

    # 纸（四边形，略斜）
    paper = [(cx - 108, cy - 148), (cx + 116, cy - 128),
             (cx + 104, cy + 150), (cx - 120, cy + 130)]
    d.polygon(paper, fill=INK, outline=EDGE, width=7)
    # 折角
    d.polygon([(cx + 116, cy - 128), (cx + 60, cy - 118), (cx + 110, cy - 62)],
              fill=(150, 20, 20), outline=EDGE, width=5)
    # 文字线
    for k in range(6):
        y = cy - 88 + k * 34
        w = 150 if k % 2 == 0 else 108
        d.line([(cx - 84, y), (cx - 84 + w, y - 8)], fill=EDGE, width=5)
    # 一枚印章
    d.ellipse([cx - 24, cy + 68, cx + 40, cy + 122], outline=(150, 20, 20), width=9)
    d.ellipse([cx - 10, cy + 82, cx + 26, cy + 108], outline=(150, 20, 20), width=5)
    hatch(im)
    vignette(im)
    save(im, 'sym_sign')


def wire():
    """把这 3 张接进 ART 表，并把 9 个内联 id 指过去。"""
    HTML = GAME / 'web' / 'index.html'
    s = HTML.read_text(encoding='utf-8')
    k = 'window.ART = '
    i = s.find(k)
    j = s.find(';', i)
    art = json.loads(s[i + len(k):j])

    art['sym_atk'] = 'assets/art/sym_atk.webp'
    art['sym_def'] = 'assets/art/sym_def.webp'
    art['sym_sign'] = 'assets/art/sym_sign.webp'

    # 9 个内联 id → 3 张符号图
    MAP = {
        'basic_atk': 'sym_atk', 'cng_w_atk': 'sym_atk', 'cng_d_atk': 'sym_atk',
        'basic_def': 'sym_def', 'cng_w_def': 'sym_def', 'cng_d_def': 'sym_def',
        'diver_sign': 'sym_sign', 'anmin_sign': 'sym_sign', 'tremor_sign': 'sym_sign',
    }
    for cid, sym in MAP.items():
        art[cid] = art[sym]

    new = k + json.dumps(art, ensure_ascii=False, separators=(',', ':')) + ';'
    if new != s[i:j + 1]:
        s = s[:i] + new + s[j + 1:]
        HTML.write_text(s, encoding='utf-8')
        print('ART 表已更新（%d 条），9 个内联 id 已指向 3 张符号图' % len(art))
    else:
        print('ART 表无变化')
    return MAP


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    print('生成符号图：')
    draw_atk()
    draw_def()
    draw_sign()
    print()
    m = wire()
    print()
    for cid, sym in m.items():
        print('  %-14s → %s' % (cid, sym))
