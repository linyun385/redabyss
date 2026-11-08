# -*- coding: utf-8 -*-
"""T403 效果类型分布 → 追加到 docs/design/vein_audit_matrix.md 表尾。

判型规则（任务书原文）：damage/hits→伤害；block→格挡；draw/energy/discard→资源；
special code ∈ {burn,poison,weak,frail}→减益；∈ {strength,dexterity,regenerate,thorns}→增益。
一张卡可归多类。多脉卡在它带的每条脉下各计一次（文末注明）。

用法：python data/audit/gen_t403.py
"""
import io, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import (GAME, CN_CLASS, load_cards, all_cards, card_veins,
                          effect_types)

OUT = GAME / 'docs' / 'design' / 'vein_audit_matrix.md'
VEINS = ['光', '水', '热', '震', '矿', '无']
CLS_ORDER = ['diver', 'tremor', 'anmin', 'cangmin', 'shared']

cell = defaultdict(Counter)   # (vein, cls) -> Counter of types
for cls, c in all_cards(load_cards()):
    for v in card_veins(c):
        cell[(v, cls)].update(effect_types(c))

buf = io.StringIO()
buf.write('\n## 效果类型分布（T403）\n\n')
buf.write('判型规则（按 effect 键，一张卡可归多类）：`damage`/`hits`→伤害；`block`→格挡；')
buf.write('`draw`/`energy`/`discard`→资源；special code ∈ {burn,poison,weak,frail}→减益；')
buf.write('∈ {strength,dexterity,regenerate,thorns}→增益。多脉卡在每条带到的脉下各计一次。\n\n')
buf.write('| 脉 | ' + ' | '.join(CN_CLASS[c] for c in CLS_ORDER) + ' | 合计 |\n')
buf.write('|---|' + '---|' * (len(CLS_ORDER) + 1) + '\n')

def fmt(ctr):
    if not ctr:
        return '—'
    keys = ['伤害', '格挡', '资源', '减益', '增益']
    return ' / '.join('%s%d' % (k, ctr[k]) for k in keys if ctr[k]) or '—'

vein_totals = Counter()
for v in VEINS:
    row = []
    for cls in CLS_ORDER:
        row.append(fmt(cell[(v, cls)]))
        vein_totals[v] += sum(cell[(v, cls)].values())
    total_cards = sum(1 for _, c in all_cards(load_cards()) if v in card_veins(c))
    buf.write('| **%s** | %s | %d 张 |\n' % (v, ' | '.join(row), total_cards))

buf.write('\n### 每脉四角色总量（按「类型出现次数」）\n\n')
buf.write('| 脉 | 伤害 | 格挡 | 资源 | 减益 | 增益 |\n|---|---|---|---|---|---|\n')
for v in VEINS:
    agg = Counter()
    for cls in CLS_ORDER:
        agg.update(cell[(v, cls)])
    buf.write('| %s | %d | %d | %d | %d | %d |\n' % (
        v, agg['伤害'], agg['格挡'], agg['资源'], agg['减益'], agg['增益']))

buf.write('\n### 一眼看出谁缺什么\n\n')
# 每脉每角色「张数」
from collections import defaultdict as _dd
cardn = _dd(int)
for cls, c in all_cards(load_cards()):
    for v in card_veins(c):
        cardn[(v, cls)] += 1
for v in VEINS[:5]:
    lacking = [CN_CLASS[cls] for cls in ['diver', 'tremor', 'anmin', 'cangmin'] if cardn[(v, cls)] <= 3]
    if lacking:
        buf.write('- **%s**：%s 的卡 ≤3 张（%s）\n' % (v, '、'.join(lacking),
            '、'.join('%s%d' % (CN_CLASS[cls], cardn[(v, cls)]) for cls in ['diver', 'tremor', 'anmin', 'cangmin', 'shared'])))
buf.write('- 「无脉」11 张全部在通用池。\n')
buf.write('\n复算：`python data/audit/gen_t403.py`（追加运行，不重复写入本节则先还原矩阵：`python data/audit/gen_t402.py`）。\n')

with open(OUT, 'a', encoding='utf-8') as f:
    f.write(buf.getvalue())
print('appended T403 section to', OUT)
