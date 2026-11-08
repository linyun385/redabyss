# -*- coding: utf-8 -*-
"""查每个职业的脉分布 —— 脉象系统能不能落地，取决于这个。"""
import json, glob
from pathlib import Path
from collections import Counter, defaultdict

GAME = Path(__file__).resolve().parents[1]
CARDS = GAME / 'cards'
CN = {'diver': '下潜者', 'tremor': '震语者', 'anmin': '维护者', 'cangmin': '疯先知', 'shared': '通用'}
VEIN = {'light': '光', 'water': '水', 'heat': '热', 'tremor': '震', 'mineral': '矿'}

rows = {}
for f in sorted(CARDS.glob('*.json')):
    if f.name.startswith('_'):
        continue
    cls = f.stem
    arr = json.loads(f.read_text(encoding='utf-8'))
    c = Counter()
    multi = 0
    noVein = 0
    for card in arr:
        vs = [v for v in (card.get('veins') or []) if v in VEIN]
        if not vs:
            noVein += 1
            continue
        if len(vs) > 1:
            multi += 1
        for v in vs:
            c[v] += 1
    rows[cls] = (len(arr), c, multi, noVein)

print('%-8s %4s %5s %5s %5s %5s %5s   %s' % ('职业', '总', '光', '水', '热', '震', '矿', '无脉/多脉'))
for cls, (total, c, multi, noVein) in rows.items():
    print('%-8s %4d %5d %5d %5d %5d %5d   %d/%d' % (
        CN.get(cls, cls), total,
        c['light'], c['water'], c['heat'], c['tremor'], c['mineral'], noVein, multi))

print()
print('各脉全池总数：')
total = Counter()
for cls, (_, c, _, _) in rows.items():
    if cls == 'shared':
        continue
    for k, v in c.items():
        total[k] += v
for k, v in total.most_common():
    print('  %s %d' % (VEIN[k], v))

print()
print('按职业算「专注单脉」能不能撑起来（最短的脉 / 该职业总牌）：')
for cls, (t, c, _, _) in rows.items():
    if cls == 'shared':
        continue
    lo = min((c[k], k) for k in VEIN)
    hi = max((c[k], k) for k in VEIN)
    print('  %-4s 最厚 %s %d 张（%.0f%%）　最薄 %s %d 张（%.0f%%）' % (
        CN[cls], VEIN[hi[1]], hi[0], hi[0] * 100.0 / t,
        VEIN[lo[1]], lo[0], lo[0] * 100.0 / t))
