# -*- coding: utf-8 -*-
import json, io

p = 'tools/mapgen_spec.json'
spec = json.load(open(p, encoding='utf-8'))
spec['quota']['bands'] = {
    '1': { 'combat': 6, 'elite': 0, 'random': 3, 'shop': 1, 'event': 3 },
    '2': { 'combat': 7, 'elite': 2, 'random': 3, 'shop': 1, 'event': 3 },
    '3': { 'combat': 7, 'elite': 2, 'random': 3, 'shop': 1, 'event': 3 },
    '4': { 'combat': 8, 'elite': 2, 'random': 3, 'shop': 2, 'event': 4 },
    '5': { 'combat': 8, 'elite': 3, 'random': 3, 'shop': 1, 'event': 4 },
    '6': { 'combat': 8, 'elite': 3, 'random': 3, 'shop': 1, 'event': 4 },
    '7': { 'combat': 9, 'elite': 3, 'random': 3, 'shop': 1, 'event': 4 },
    '8': { 'combat': 9, 'elite': 3, 'random': 3, 'shop': 1, 'event': 4, 'finalBoss': 1 }
}
json.dump(spec, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
tot = {b: sum(v for k, v in d.items()) for b, d in spec['quota']['bands'].items()}
print('配额合计:', tot, '| 全图:', sum(tot.values()))

# 同步 mapgen.js DEFAULTS
p2 = 'tools/mapgen.js'
s = io.open(p2, encoding='utf-8').read()
import re
m = re.search(r'(quota: \{ // [^\n]+\n)((?:[^}]+\n)+?)    \},', s)
if m:
    new_q = m.group(1) + """1: { combat: 6, elite: 0, random: 3, shop: 1, event: 3 },
      2: { combat: 7, elite: 2, random: 3, shop: 1, event: 3 },
      3: { combat: 7, elite: 2, random: 3, shop: 1, event: 3 },
      4: { combat: 8, elite: 2, random: 3, shop: 2, event: 4 },
      5: { combat: 8, elite: 3, random: 3, shop: 1, event: 4 },
      6: { combat: 8, elite: 3, random: 3, shop: 1, event: 4 },
      7: { combat: 9, elite: 3, random: 3, shop: 1, event: 4 },
      8: { combat: 9, elite: 3, random: 3, shop: 1, event: 4, finalBoss: 1 }
    },"""
    s = s[:m.start()] + new_q + s[m.end():]
    io.open(p2, 'w', encoding='utf-8').write(s)
    print('DEFAULTS quota synced')
else:
    print('quota regex miss')
