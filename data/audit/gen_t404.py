# -*- coding: utf-8 -*-
"""T404 跨角色同脉同效果清单 → 追加到 docs/design/vein_audit_matrix.md。

条件（任务书原文，全部满足才算一组）：
  1. 脉相同（多脉卡要求 vein 集合完全一致）
  2. effect 键集合相同
  3. 主要数值接近（差 ≤2）
  4. 属于不同角色
每组输出：脉 / 全部 id / 差异点；组尾给一句「同一种解法 or 恰好撞」的判断 + 依据。

用法：python data/audit/gen_t404.py
"""
import io, sys, json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import (GAME, CN_CLASS, CN_TYPE, CN_VEIN, load_cards,
                          all_cards, card_veins, main_shape)

OUT = GAME / 'docs' / 'design' / 'vein_audit_matrix.md'

cards = load_cards()
PAIRS = [(cls, c) for cls, c in all_cards(cards)]

def key_of(c):
    e = c.get('effect') or {}
    return tuple(sorted(k for k in e))

def veinset(c):
    vs = c.get('veins') or []
    return frozenset(vs) if vs else frozenset(['无'])

bucket = defaultdict(list)
for cls, c in PAIRS:
    bucket[(veinset(c), key_of(c))].append((cls, c))

# 桶内按主值做 ≤2 连通聚类
groups = []
for k, members in bucket.items():
    classes = {cls for cls, _ in members}
    if len(classes) < 2:
        continue
    members = sorted(members, key=lambda m: main_shape(m[1])[2])
    # 连通：主值差 ≤2
    comp, comps = [members[0]], []
    for m in members[1:]:
        if main_shape(m[1])[2] - main_shape(comp[-1][1])[2] <= 2:
            comp.append(m)
        else:
            comps.append(comp); comp = [m]
    comps.append(comp)
    for comp in comps:
        if len({cls for cls, _ in comp}) >= 2:
            groups.append((k, comp))

buf = io.StringIO()
buf.write('\n## 跨角色同脉同效果（T404）\n\n')
buf.write('条件：脉集合相同 + effect 键集合相同 + 主数值差 ≤2 + 分属不同角色。共 %d 组。\n\n' % len(groups))

def classify_group(comp):
    """一句判断：基准线解法 or 疑似恰好撞。
    依据：effect 只有一个数值键且键是 damage/block/heal/draw → 各角色池的基准线位；
    键更多（复合效果）→ 更可能是恰好撞（同样的配方想到一起去了）。"""
    e = comp[0][1].get('effect') or {}
    core_keys = [k for k in e if k not in ('target', 'hits')]
    if len(core_keys) == 1 and core_keys[0] in ('damage', 'block', 'heal', 'draw'):
        return '同一种解法（%s基准线）' % {'damage': '直伤', 'block': '格挡', 'heal': '治疗', 'draw': '过牌'}[core_keys[0]]
    return '疑似恰好撞（复合效果同配方）'

for (vs, keys), comp in sorted(groups, key=lambda g: g[0][0]):
    vein = '+'.join(sorted(CN_VEIN.get(v, v) for v in vs)) if '无' not in vs else '无脉'
    ids = ['`%s` %s（%s，主值 %s）' % (c['id'], c['name'], CN_CLASS[cls], main_shape(c)[2]) for cls, c in comp]
    diffs = []
    if len(comp) >= 2:
        base = comp[0][1].get('effect') or {}
        for cls, c in comp[1:]:
            e = c.get('effect') or {}
            for k in sorted(set(base) | set(e)):
                if json.dumps(base.get(k), sort_keys=True) != json.dumps(e.get(k), sort_keys=True):
                    diffs.append('%s %s vs %s' % (k, base.get(k), e.get(k)))
    buf.write('- 脉 **%s**：%s\n' % (vein, ' / '.join(ids)))
    buf.write('  - 差异点：%s\n' % ('；'.join(diffs) or '零差异（完全同效果）'))
    buf.write('  - 判断：%s —— %s\n' % (
        classify_group(comp),
        '各角色池都需要这个基础位，数值恰好落在同档，属结构性重复' if '基准线' in classify_group(comp)
        else '效果不是单键基准，两边的角色不约而同用了同一配方'))

buf.write('\n### 一句总判断\n\n')
n_base = sum(1 for _, comp in groups if '基准线' in classify_group(comp))
buf.write('%d 组里 %d 组是「不同角色的同一种解法」——单键基准牌（纯格挡/纯直伤/纯治疗/纯抽牌）在各角色池里各写了一遍；'
          '其余 %d 组是复合效果撞配方。依据：单键基准牌是每个角色池的结构需求（防御锚点/输出锚点），'
          '数值档位接近是必然；复合效果撞配方才是真正的「想法撞车」，重构时优先看后者。\n' % (
    len(groups), n_base, len(groups) - n_base))
buf.write('\n复算：`python data/audit/gen_t404.py`（追加运行；还原矩阵用 `python data/audit/gen_t402.py` 后依次补 T403/T404）。\n')

with open(OUT, 'a', encoding='utf-8') as f:
    f.write(buf.getvalue())
print('appended T404:', len(groups), 'groups')
