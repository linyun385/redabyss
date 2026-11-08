# -*- coding: utf-8 -*-
"""A · 卡池结构画像 → docs/design/ui/07_card_pool_shape.md
可复算：python tools/sim/card_pool_shape.py
"""
import sys, io, json, collections
from pathlib import Path

GAME = Path(__file__).resolve().parents[2]
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

FEES = ['0', '1', '2', '3']
RARS = ['common', 'uncommon', 'rare', 'special']
TYPES = ['attack', 'skill', 'power']
CLASSES = ['diver', 'tremor', 'anmin', 'cangmin', 'shared']
CN = {'diver': '下潜者', 'tremor': '震语者', 'anmin': '维护者', 'cangmin': '疯先知', 'shared': '通用',
      'attack': '攻击', 'skill': '技能', 'power': '能力',
      'common': '普通', 'uncommon': '精良', 'rare': '稀有', 'special': '特殊'}

cards_by_cls = {}
total = 0
for f in CLASSES:
    arr = json.loads((GAME / 'cards' / (f + '.json')).read_text(encoding='utf-8'))
    cards_by_cls[f] = arr
    total += len(arr)

all_cards = {}
for cl in CLASSES:
    for c in cards_by_cls[cl]:
        all_cards[c['id']] = c

grid = collections.defaultdict(list)
for cls in CLASSES:
    for c in cards_by_cls[cls]:
        fee = str(min(c.get('energy', 0), 3))
        rar = c.get('rarity', 'common')
        typ = c.get('type', 'skill')
        grid[(fee, rar, typ, cls)].append(c['id'])

grid_all = collections.defaultdict(int)
for (fee, rar, typ, cls), ids in grid.items():
    grid_all[(fee, rar, typ)] += len(ids)

effect_counter = collections.Counter()
effect_values = collections.defaultdict(list)
effect_holders = collections.defaultdict(set)
for cls in CLASSES:
    for c in cards_by_cls[cls]:
        e = c.get('effect') or {}
        for k, v in e.items():
            if k in ('target', 'special'):
                continue
            effect_counter[k] += 1
            effect_holders[k].add(c['id'])
            if isinstance(v, (int, float)):
                effect_values[k].append(v)
        for sp in e.get('special') or []:
            if isinstance(sp, dict) and sp.get('code'):
                code = 'special:' + sp['code']
                effect_counter[code] += 1
                effect_holders[code].add(c['id'])

buf = []
buf.append('# A · 卡池结构画像（%d 张）' % total)
buf.append('')
buf.append('> 任务书按 209 张；实际 **%d 张**。以实际数据为准。全部为代码级统计。' % total)
buf.append('> 复算：`python tools/sim/card_pool_shape.py`')
buf.append('')

buf.append('## A1 · 四维交叉表')
buf.append('')
for cls in CLASSES:
    buf.append('### %s（%d 张）' % (CN[cls], len(cards_by_cls[cls])))
    buf.append('')
    buf.append('| 费 | 类型 | 普通 | 精良 | 稀有 | 特殊 | 合计 |')
    buf.append('|---|---|---|---|---|---|---|')
    for fee in FEES:
        for typ in TYPES:
            vals = []
            row_total = 0
            for rar in RARS:
                n = len(grid.get((fee, rar, typ, cls), []))
                vals.append(str(n) if n else '\u00b7')
                row_total += n
            if row_total == 0:
                continue
            buf.append('| %s | %s | %s | %d |' % (fee, CN[typ], ' | '.join(vals), row_total))
    buf.append('')

buf.append('### 跨职业汇总（含 shared）')
buf.append('')
buf.append('| 费 | 类型 | 普通 | 精良 | 稀有 | 特殊 | 合计 |')
buf.append('|---|---|---|---|---|---|---|')
for fee in FEES:
    for typ in TYPES:
        vals = []
        row_total = 0
        for rar in RARS:
            n = grid_all.get((fee, rar, typ), 0)
            vals.append(str(n) if n else '\u00b7')
            row_total += n
        if row_total == 0:
            continue
        buf.append('| %s | %s | %s | %d |' % (fee, CN[typ], ' | '.join(vals), row_total))
buf.append('')

buf.append('## A2 · 薄位（<=1 张）与过密位（>=8 张）')
buf.append('')
buf.append('### 薄位')
buf.append('')
buf.append('| 费 | 稀有度 | 类型 | 职业 | 张数 | 例 |')
buf.append('|---|---|---|---|---|---|')
for (fee, rar, typ, cls), ids in sorted(grid.items()):
    if len(ids) <= 1:
        names = ', '.join(all_cards[i]['name'] for i in ids[:2] if i in all_cards)
        buf.append('| %s | %s | %s | %s | %d | %s |' % (fee, CN[rar], CN[typ], CN[cls], len(ids), names))
buf.append('')
buf.append('### 过密位（>=8 张）')
buf.append('')
buf.append('| 费 | 稀有度 | 类型 | 职业 | 张数 | 例 |')
buf.append('|---|---|---|---|---|---|')
for (fee, rar, typ, cls), ids in sorted(grid.items(), key=lambda x: -len(x[1])):
    if len(ids) >= 8:
        names = ', '.join(all_cards[i]['name'] for i in ids[:2] if i in all_cards)
        buf.append('| %s | %s | %s | %s | %d | %s |' % (fee, CN[rar], CN[typ], CN[cls], len(ids), names))
buf.append('')

buf.append('## A3 · 效果键分布')
buf.append('')
buf.append('| 键 | 次数 | 卡数 | 平均值 | 仅一次？ |')
buf.append('|---|---|---|---|---|')
for k, n in effect_counter.most_common():
    vals = effect_values.get(k, [])
    avg = '%.1f' % (sum(vals) / len(vals)) if vals else '-'
    once = '**<- 仅一次**' if n == 1 else ''
    buf.append('| %s | %d | %d | %s | %s |' % (k, n, len(effect_holders[k]), avg, once))
buf.append('')
once_keys = [k for k, n in effect_counter.items() if n == 1]
buf.append('### 仅用一次的键')
buf.append('')
for k in sorted(once_keys):
    buf.append('- `%s`: %s' % (k, ', '.join(sorted(effect_holders[k]))))
buf.append('')

buf.append('## A4 结论')
buf.append('')
buf.append('### 1. 最空的三个生态位')
buf.append('')
gap_list = []
for fee in FEES:
    for typ in TYPES:
        n = sum(grid_all.get((fee, r, typ), 0) for r in RARS)
        gap_list.append((n, fee, typ))
gap_list.sort()
for n, fee, typ in gap_list[:5]:
    buf.append('- **%s费 %s**: 全池仅 %d 张' % (fee, CN[typ], n))
buf.append('')

buf.append('### 2. 核心卡该占哪个生态位')
buf.append('')
buf.append('核心卡 = 高费(2-3) + 独特机制 + 每职业 1-2 张。')
buf.append('')
for fee in ['2', '3']:
    for typ in TYPES:
        rn = grid_all.get((fee, 'rare', typ), 0)
        if rn <= 3:
            buf.append('- **%s费 %s 稀有档**: 全池仅 %d 张 -> 核心卡落这里最不撞车' % (fee, CN[typ], rn))
n3 = sum(grid_all.get(('3', r, t), 0) for r in RARS for t in TYPES)
buf.append('- 3费全池 %d 张（T407）；3费稀有档更少——**3费稀有档是最大空位**。' % n3)
n2r = grid_all.get(('2', 'rare', 'attack'), 0)
buf.append('- 2费稀有攻击 %d 张——如果做一张「改变玩法」的2费攻击核心，也不太撞。' % n2r)
buf.append('')

buf.append('### 3. 「改变玩法」的实现路径')
buf.append('')
existing = sorted(k for k in effect_counter if not k.startswith('special:'))
buf.append('现有 effect 键（%d 个非 special）: %s' % (len(existing), ', '.join(existing)))
sp_codes = sorted(k.replace('special:', '') for k in effect_counter if k.startswith('special:'))
buf.append('')
buf.append('现有 special code（%d 个）: %s' % (len(sp_codes), ', '.join(sp_codes)))
buf.append('')
buf.append('**现有键不能覆盖、需要加新键的候选**：')
buf.append('- 每回合首张牌翻倍 -> 需 per_turn_first 标记')
buf.append('- 手牌上限增减 -> 需 hand_size_mod')
buf.append('- 敌人意图可见+1拍 -> 需 intent_preview')
buf.append('- 战斗开始时从牌库检索 -> 需 tutor 机制')
buf.append('- 引擎 applySpecial 已有 15 个 case；新增 case = 引擎改动（不在 UI 范畴）')
buf.append('')
buf.append('---')
buf.append('')
buf.append('> 我没开浏览器，所有结论是代码级的。读到的是 cards/*.json 当前版本。')

OUT = GAME / 'docs' / 'design' / 'ui' / '07_card_pool_shape.md'
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
print('written', OUT, '| total', total, '| thin', sum(1 for v in grid.values() if len(v) <= 1), '| dense', sum(1 for v in grid.values() if len(v) >= 8), '| once_keys', once_keys)
