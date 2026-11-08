# -*- coding: utf-8 -*-
"""统计费用分布：全体 + 按脉 + 按职业"""
import json, glob, os, collections, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

D = r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\cards'
files = [f for f in glob.glob(os.path.join(D, '*.json')) if not os.path.basename(f).startswith('_')]
print('files:', [os.path.basename(f) for f in files])

cards = []
for f in files:
    try:
        data = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        print('skip', os.path.basename(f), e); continue
    items = data if isinstance(data, list) else (data.get('cards') if isinstance(data, dict) else None)
    if isinstance(items, list):
        for c in items:
            if isinstance(c, dict) and 'energy' in c:
                c['_file'] = os.path.basename(f)
                cards.append(c)

print('total cards:', len(cards))
print()

def hist(keyfn, title):
    h = collections.Counter()
    for c in cards:
        h[keyfn(c)] += 1
    print('==', title)
    for k in sorted(h, key=lambda x: (str(type(x)), x)):
        print(f'   {k}: {h[k]}')
    print()

hist(lambda c: c.get('energy'), '费用分布（全体）')

# 按文件（职业）
for f in files:
    sub = [c for c in cards if c['_file'] == os.path.basename(f)]
    if not sub: continue
    h = collections.Counter(c.get('energy') for c in sub)
    tot = len(sub)
    avg = sum((c.get('energy') or 0) for c in sub) / tot if tot else 0
    print(f'== {os.path.basename(f)}  n={tot}  平均费={avg:.2f}  ' + ' '.join(f'{k}费:{h[k]}' for k in sorted(h)))
print()

# 按脉
def veins(c):
    v = c.get('veins') or []
    return '+'.join(v) if v else '无脉'
h = collections.Counter(veins(c) for c in cards)
print('== 脉分布')
for k, v in h.most_common():
    print(f'   {k}: {v}')
print()

# 脉 × 费
print('== 各脉费用分布')
byvn = collections.defaultdict(list)
for c in cards:
    byvn[veins(c)].append(c.get('energy') or 0)
for k in sorted(byvn, key=lambda x: -len(byvn[x])):
    arr = byvn[k]
    hh = collections.Counter(arr)
    print(f'   {k:12s} n={len(arr):3d} avg={sum(arr)/len(arr):.2f}  ' + ' '.join(f'{x}费:{hh[x]}' for x in sorted(hh)))
