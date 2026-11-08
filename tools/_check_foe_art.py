# -*- coding: utf-8 -*-
"""按像素统计给敌人图做客观体检：
  red%  偏红像素占比（R 明显大于 G/B）
  lum   平均亮度
筛出三类可疑：不红 / 太亮（洗白） / 太暗（黑成一片），只为缩小复核范围。
"""
import json
import sys
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
ART = GAME / 'web' / 'assets' / 'art'
CAT = json.loads((GAME / 'data' / 'art_catalog.json').read_text(encoding='utf-8'))
NAMES = {r['id']: r['name'] for r in CAT}


def stats(p):
    im = Image.open(p).convert('RGB')
    im.thumbnail((160, 160))
    px = list(im.getdata())
    n = len(px)
    red = sum(1 for r, g, b in px if r > g * 1.25 and r > b * 1.25 and r > 60)
    lum = sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b in px) / n
    return red / n * 100, lum


def main():
    ids = [i for i in NAMES if i.startswith('enemy_')]
    rows = []
    for i in ids:
        p = ART / (i + '.webp')
        if not p.exists():
            continue
        r, l = stats(p)
        rows.append((i, NAMES[i], r, l))
    bad = [x for x in rows if x[2] < 15 or x[3] > 165 or x[3] < 22]
    rows.sort(key=lambda x: x[2])
    print('体检 %d 张；可疑 %d 张' % (len(rows), len(bad)))
    print('\n最不红的 8 张：')
    for i, nm, r, l in rows[:8]:
        print('  %-14s %-12s 红占比 %5.1f%%  亮度 %5.1f' % (i, nm, r, l))
    print('\n最亮的 5 张：')
    for i, nm, r, l in sorted(rows, key=lambda x: -x[3])[:5]:
        print('  %-14s %-12s 红占比 %5.1f%%  亮度 %5.1f' % (i, nm, r, l))
    out = GAME / 'data' / 'foe_check.json'
    out.write_text(json.dumps([{'id': i, 'name': nm, 'red': round(r, 1), 'lum': round(l, 1)}
                               for i, nm, r, l in rows], ensure_ascii=False, indent=1), encoding='utf-8')
    print('\n明细 → %s' % out.name)
    return 0


if __name__ == '__main__':
    sys.exit(main())
