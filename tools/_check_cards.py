# -*- coding: utf-8 -*-
"""卡牌批量出图后的机械体检（只为缩圈，不代替人眼）。

判据来源：红渊的既定视觉约束
  · 光必须是血红（R 明显压过 G/B）
  · 背景大片纯黑，主体亮、边缘暗
  · 不许跑出冷色（蓝/绿）——之前有张凝胶卡整瓶发蓝
  · 不许过曝成一片平均亮度的糊图

输出：data/card_check.json + 控制台分组清单

用法：python tools/_check_cards.py
"""
import json
import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
ART = GAME / 'web' / 'assets' / 'art'
OUT = GAME / 'data' / 'card_check.json'


def stat(im):
    im = im.convert('RGB')
    im.thumbnail((128, 128))
    px = list(im.getdata())
    n = len(px)
    red = blue = green = 0
    lum = 0
    for r, g, b in px:
        lum += (r * 299 + g * 587 + b * 114) // 1000
        if r > 55 and r > g * 1.45 and r > b * 1.45:
            red += 1
        elif b > 70 and b > r * 1.15 and b > g * 1.05:
            blue += 1
        elif g > 70 and g > r * 1.1 and g > b * 1.1:
            green += 1
    return {'red': round(red / n, 3), 'blue': round(blue / n, 3),
            'green': round(green / n, 3), 'lum': round(lum / n, 1)}


def main():
    ids = [r['id'] for r in json.loads(
        (GAME / 'data' / 'art_catalog.json').read_text(encoding='utf-8'))
        if not r['id'].startswith(('enemy_', 'event_'))]
    rows, bad = [], {'暗': [], '冷色': [], '红太少': [], '过亮': []}
    miss = []
    for rid in ids:
        p = ART / (rid + '.webp')
        if not p.exists():
            miss.append(rid)
            continue
        s = stat(Image.open(p))
        s['id'] = rid
        rows.append(s)
        if s['lum'] < 22:
            bad['暗'].append((rid, s['lum']))
        if s['blue'] > 0.05 or s['green'] > 0.08:
            bad['冷色'].append((rid, s['blue'], s['green']))
        if s['red'] < 0.12:
            bad['红太少'].append((rid, s['red']))
        if s['lum'] > 130:
            bad['过亮'].append((rid, s['lum']))
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
    print('卡牌 %d 张，缺图 %d 张' % (len(rows), len(miss)))
    for k, v in bad.items():
        print('  %s: %d 张' % (k, len(v)))
    for k in ('冷色', '红太少', '暗', '过亮'):
        if bad[k]:
            print('\n-- %s --' % k)
            print('  ' + ', '.join(str(x[0]) for x in bad[k]))
    flag = sorted({x[0] for v in bad.values() for x in v})
    print('\n需要人眼看的合计 %d 张（去重后）' % len(flag))
    (GAME / 'data' / 'card_flag.txt').write_text('\n'.join(flag), encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
