# -*- coding: utf-8 -*-
"""T446 数值离群扫描 → docs/design/numeric_outliers.md

桶 = (类型, 稀有度, 费用)，桶内 ≥4 张才判。主数值 = main_shape 主种类数值。
判定：主值 < 同桶同主种类中位数 ×0.5 或 > ×1.5（且中位数 >0）→ 离群。
每处列 id/数值/中位数/偏离%。只报告。复算：python data/audit/gen_t446.py

用法：python data/audit/gen_t446.py
"""
import io, sys, statistics
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME, CN_CLASS, CN_TYPE, load_cards, all_cards, main_shape, CN_RARITY

OUT = GAME / 'docs' / 'design' / 'numeric_outliers.md'

bucket = defaultdict(list)
for cls, c in all_cards(load_cards()):
    bucket[(c.get('type'), c.get('rarity'), c.get('energy'))].append((cls, c))

buf = io.StringIO()
buf.write('# T446 · 数值离群扫描\n\n')
buf.write('> 桶 = (类型 × 稀有度 × 费用)，桶内 ≥4 张才判；主数值 = `audit_common.main_shape` 主种类数值；')
buf.write('中位数按**同桶同主种类**取（block 8 与 draw 2 不互比）。')
buf.write('离群线：主值 < 中位数 ×0.5 或 > ×1.5（中位数 >0）。复算：`python data/audit/gen_t446.py`。只报告。\n\n')

outliers = []
for key, members in sorted(bucket.items(), key=lambda kv: -len(kv[1])):
    if len(members) < 4:
        continue
    kind_vals = defaultdict(list)
    for cls, c in members:
        k, v = main_shape(c)[1], main_shape(c)[2]
        if k and v > 0:
            kind_vals[k].append((v, cls, c))
    for k, lst in kind_vals.items():
        if len(lst) < 3:
            continue
        med = statistics.median([v for v, _, _ in lst])
        if med <= 0:
            continue
        for v, cls, c in lst:
            if v < med * 0.5 or v > med * 1.5:
                outliers.append((key, k, med, v, cls, c))

buf.write('## 离群清单（%d 处）\n\n' % len(outliers))
buf.write('| id | 名字 | 角色 | 桶（类型/稀有度/费） | 主种类 | 数值 | 同类中位数 | 偏离 |\n|---|---|---|---|---|---|---|---|\n')
for key, k, med, v, cls, c in sorted(outliers, key=lambda x: abs(x[3] / x[2] - 1), reverse=True):
    dev = '%+.0f%%' % ((v / med - 1) * 100)
    buf.write('| %s | %s | %s | %s/%s/%s | %s | %s | %s | %s |\n' % (
        c['id'], c['name'], CN_CLASS[cls], CN_TYPE.get(key[0], key[0]),
        CN_RARITY.get(key[1], key[1]), key[2], k, v, med, dev))

if not outliers:
    buf.write('（无离群）\n')

buf.write('\n## 桶覆盖\n\n')
buf.write('- 参与判定的桶（≥4 张）：%d 个；离群 %d 处。\n' % (
    sum(1 for m in bucket.values() if len(m) >= 4), len(outliers)))
buf.write('\n### 说明\n\n')
buf.write('- 离群 ≠ 错：高离群可能是「稀有度没给够」（对照 T504 低稀强清单），低离群可能是「有额外机制补偿」（共振支付/门槛/代价）。逐处判断是设计师的活。\n')
buf.write('- 主种类相同的卡才互比——同桶内跨种类的数值不可比。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, '| outliers', len(outliers))
for o in outliers[:15]:
    print('  ', o[5]['id'], o[1], o[3], 'vs med', o[2])
