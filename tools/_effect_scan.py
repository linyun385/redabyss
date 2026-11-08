# -*- coding: utf-8 -*-
"""摸清 effect 里到底有哪些键、哪些 special code，各出现多少次、值长什么样。"""
import json, glob, collections, io, sys

keys = collections.Counter()
sample = {}
special = collections.Counter()
ssample = {}
utop = collections.Counter()

for f in glob.glob('cards/*.json'):
    arr = json.load(open(f, encoding='utf-8'))
    for c in arr:
        e = c.get('effect') or {}
        for k, v in e.items():
            keys[k] += 1
            if k not in sample:
                sample[k] = v
        for s in (e.get('special') or []):
            code = s.get('code')
            special[code] += 1
            if code not in ssample:
                ssample[code] = s
        u = c.get('upgrade') or {}
        for k, v in u.items():
            utop[k] += 1

out = io.StringIO()
out.write('=== effect 顶层键 ===\n')
for k, n in keys.most_common():
    out.write('%-20s %4d   样例: %s\n' % (k, n, json.dumps(sample[k], ensure_ascii=False)[:90]))
out.write('\n=== special code ===\n')
for k, n in special.most_common():
    out.write('%-22s %4d   样例: %s\n' % (k, n, json.dumps(ssample[k], ensure_ascii=False)[:110]))
out.write('\n=== upgrade 顶层键 ===\n')
for k, n in utop.most_common():
    out.write('%-16s %4d\n' % (k, n))

open('tools/_effect_keys.txt', 'w', encoding='utf-8').write(out.getvalue())
print('written')
