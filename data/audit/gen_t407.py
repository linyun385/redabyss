# -*- coding: utf-8 -*-
"""T407 每条脉的费用曲线 → docs/design/vein_cost_curve.md

统计每条脉（光/水/热/震/矿/无脉/多脉）在 0/1/2/3+ 费各多少张 + 平均费。
多脉卡单列；「无脉」= veins 为空。复算：python data/audit/gen_t407.py

用法：python data/audit/gen_t407.py
"""
import io, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME, CN_CLASS, load_cards, all_cards

OUT = GAME / 'docs' / 'design' / 'vein_cost_curve.md'

buckets = defaultdict(Counter)
totals = Counter()
avg = defaultdict(list)
cls_vein_cost = defaultdict(Counter)
for cls, c in all_cards(load_cards()):
    vs = c.get('veins') or []
    k = '+'.join(sorted(vs)) if vs else '无脉'
    e = c.get('energy', 0)
    b = '0' if e == 0 else ('1' if e == 1 else ('2' if e == 2 else '3+'))
    buckets[k][b] += 1
    totals[k] += 1
    avg[k].append(e)
    if len(vs) == 1:
        cls_vein_cost[(vs[0], cls)][b] += 1

ORDER = ['light', 'water', 'heat', 'tremor', 'mineral', '无脉']
CN = {'light': '光', 'water': '水', 'heat': '热', 'tremor': '震', 'mineral': '矿'}
multi_keys = [k for k in buckets if '+' in k]

buf = io.StringIO()
buf.write('# T407 · 每条脉的费用曲线\n\n')
buf.write('> 数据源：`cards/*.json`（219 张）。复算：`python data/audit/gen_t407.py`。\n\n')
buf.write('| 脉 | 0 费 | 1 费 | 2 费 | 3+ 费 | 合计 | 平均费 |\n|---|---|---|---|---|---|---|\n')
for v in ORDER:
    b = buckets[v]
    a = sum(avg[v]) / len(avg[v]) if avg[v] else 0
    buf.write('| %s | %d | %d | %d | %d | %d | %.2f |\n' % (
        CN.get(v, v), b['0'], b['1'], b['2'], b['3+'], totals[v], a))
for k in multi_keys:
    b = buckets[k]
    a = sum(avg[k]) / len(avg[k])
    cn = '+'.join(CN[x] for x in k.split('+'))
    buf.write('| 多脉(%s) | %d | %d | %d | %d | %d | %.2f |\n' % (
        cn, b['0'], b['1'], b['2'], b['3+'], totals[k], a))

buf.write('\n### 全池对照\n\n')
b = Counter()
for cls, c in all_cards(load_cards()):
    e = c.get('energy', 0)
    b['0' if e == 0 else ('1' if e == 1 else ('2' if e == 2 else '3+'))] += 1
buf.write('全池：0 费 %d / 1 费 %d / 2 费 %d / 3+ 费 %d（合计 219）。\n\n' % (b['0'], b['1'], b['2'], b['3+']))

buf.write('### 脉内费用形状（一眼）\n\n')
buf.write('- **光**：0/1 费占大头，2 费以上是小额爆发位——符合「单回合内」的短时间轴。\n')
buf.write('- **矿**：0/1 费为主——「每张都值」的堆叠位，贵牌少。\n')
buf.write('- **热**：0/1 费铺火，2 费重灼烧——铺+烧两段。\n')
buf.write('- **震**：2/3 费占比最高（拿到就能用的大动作）——注意 3+ 费全池仅 7 张，震占了几张。\n')
buf.write('- **水**：几乎全部 ≤1 费——流动本来就不该贵。\n')
buf.write('- **无脉**：0-1 费为主，通用池全是润滑位。\n')
buf.write('- 3+ 费全池 7 张：%s。\n' % '、'.join(
    '`%s`' % c['id'] for cls, c in all_cards(load_cards()) if c.get('energy', 0) >= 3))

buf.write('\n### 每脉每角色费用分布（补充）\n\n')
buf.write('| 脉 | 角色 | 0 | 1 | 2 | 3+ |\n|---|---|---|---|---|---|\n')
for v in ORDER[:5]:
    for cls in ['diver', 'tremor', 'anmin', 'cangmin']:
        cc = cls_vein_cost[(v, cls)]
        buf.write('| %s | %s | %d | %d | %d | %d |\n' % (
            CN[v], CN_CLASS[cls], cc['0'], cc['1'], cc['2'], cc['3+']))

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, dict(b))
