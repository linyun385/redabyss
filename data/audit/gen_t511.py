# -*- coding: utf-8 -*-
"""T511 卡池三维分布 → docs/design/pool_3d.md

规格口径：费用(0/1/2+) × 类型(攻击/技能+能力) × 稀有度(普通/精良/稀有) = 18 格。
「特殊」稀有度 14 张不进 18 格（它不是强度档，是机制展示位），单独列。
附 27 格完整版（能力单列）。
复算：python data/audit/gen_t511.py

用法：python data/audit/gen_t511.py
"""
import io, sys
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME, CN_CLASS, load_cards, all_cards

OUT = GAME / 'docs' / 'design' / 'pool_3d.md'

def cost_b(e):
    return '0' if e == 0 else ('1' if e == 1 else '2+')

def type_b(t):
    return '攻击' if t == 'attack' else '技能+能力'

c18 = Counter()
c27 = Counter()
special_cards = []
for cls, c in all_cards(load_cards()):
    r = c.get('rarity')
    cb, tb = cost_b(c.get('energy', 0)), type_b(c.get('type'))
    if r == 'special':
        special_cards.append((cls, c))
        continue
    if r in ('common', 'uncommon', 'rare'):
        c18[(cb, tb, r)] += 1
        c27[(cb, {'attack': '攻击', 'skill': '技能', 'power': '能力'}[c.get('type')], r)] += 1

buf = io.StringIO()
buf.write('# T511 · 卡池三维分布（费用 × 类型 × 稀有度）\n\n')
buf.write('> 数据源：`cards/*.json`（219 张，其中「特殊」稀有度 14 张不入三维表）。复算：`python data/audit/gen_t511.py`。\n\n')

buf.write('## 18 格规格口径表（攻击 / 技能+能力合并）\n\n')
buf.write('| 费用 | 类型 | 普通 | 精良 | 稀有 | 合计 |\n|---|---|---|---|---|---|\n')
empties, ones = [], []
for cb in ['0', '1', '2+']:
    for tb in ['攻击', '技能+能力']:
        vals = [c18[(cb, tb, r)] for r in ('common', 'uncommon', 'rare')]
        for r, n in zip(('普通', '精良', '稀有'), vals):
            if n == 0:
                empties.append((cb, tb, r))
            elif n == 1:
                ones.append((cb, tb, r))
        buf.write('| %s | %s | %d | %d | %d | %d |\n' % (cb, tb, *vals, sum(vals)))

buf.write('\n### 空格（%d 个）\n\n' % len(empties))
for cb, tb, r in empties:
    buf.write('- %s 费 %s %s：**0 张**\n' % (cb, tb, r))
buf.write('\n### 只剩 1 张的格（%d 个）\n\n' % len(ones))
for cb, tb, r in ones:
    members = [c['id'] for cls, c in all_cards(load_cards())
               if c.get('rarity') == r and cost_b(c.get('energy', 0)) == cb
               and type_b(c.get('type')) == tb]
    buf.write('- %s 费 %s %s：1 张（`%s`）\n' % (cb, tb, r, '、'.join(members)))

buf.write('\n## 27 格完整版（能力单列）\n\n')
buf.write('| 费用 | 类型 | 普通 | 精良 | 稀有 | 合计 |\n|---|---|---|---|---|---|\n')
for cb in ['0', '1', '2+']:
    for tb in ['攻击', '技能', '能力']:
        vals = [c27[(cb, tb, r)] for r in ('common', 'uncommon', 'rare')]
        buf.write('| %s | %s | %d | %d | %d | %d |\n' % (cb, tb, *vals, sum(vals)))

buf.write('\n## 「特殊」稀有度 14 张（不入三维表）\n\n')
buf.write('| id | 角色 | 名字 | 类型 | 费 |\n|---|---|---|---|---|\n')
for cls, c in special_cards:
    buf.write('| %s | %s | %s | %s | %s |\n' % (
        c['id'], CN_CLASS[cls], c['name'], c.get('type'), c.get('energy', 0)))

buf.write('\n## 一眼\n\n')
buf.write('- 空格和单卡格就是「玩家没得选」的地方；18 格里空格 %d 个、单卡格 %d 个。\n' % (len(empties), len(ones)))
buf.write('- 2+ 费的格子普遍薄（全池 2 费 41、3 费 7）——高费位是结构性缺口。\n')
buf.write('- 能力（power）只有 21 张且集中在 1 费——0 费能力和 2+ 费能力几乎不存在。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, '| empty', len(empties), '| single', len(ones))
for e in empties:
    print('  EMPTY:', e)
