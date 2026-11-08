# -*- coding: utf-8 -*-
"""通用牌 × 职业专属牌 查重对照表。

用途：用户要「先铺一批通用卡 → 再拿它们对照，砍掉重复/没意义的职业专属牌」。
现在把「哪些职业牌和某张通用牌撞了」机械列出来，人只做判断，不靠记忆。

两种撞法：
  A. 完全撞：effect 一模一样（含 target/hits/数值）
  B. 近似撞：主效果相同、数值差 ≤ 2、target 相同（6 伤害 vs 7 伤害这种）

用法：python tools/dup_check.py
输出：docs/design/DUP_VS_SHARED.md
"""
import json, glob, io
from pathlib import Path
from collections import defaultdict

GAME = Path(__file__).resolve().parents[1]
CARDS = GAME / 'cards'
OUT = GAME / 'docs' / 'design' / 'DUP_VS_SHARED.md'
CN = {'diver': '下潜者', 'tremor': '震语者', 'anmin': '维护者', 'cangmin': '疯先知', 'shared': '通用'}


def load():
    out = {}
    for f in sorted(CARDS.glob('*.json')):
        if f.name.startswith('_'):
            continue
        try:
            out[f.stem] = json.loads(f.read_text(encoding='utf-8'))
        except Exception as e:
            print('skip', f.name, e)
    return out


def fp(card):
    """完全指纹：effect 的规范化 JSON"""
    return json.dumps(card.get('effect') or {}, sort_keys=True, ensure_ascii=False)


def main_shape(card):
    """主效果签名：(effect 的键集合, 种类, 数值, target, hits)。
       ★ 键集合必须一致才算同类 —— 否则「5 伤害 + 回血 2」会和「3 伤害」被判成撞车（第一版就是这么错的）。"""
    e = card.get('effect') or {}
    target = e.get('target') or ''
    hits = e.get('hits') or 1
    keys = tuple(sorted(k for k in e if k not in ('target', 'hits')))
    for k in ('damage', 'block', 'draw', 'heal', 'resonance_gain'):
        if e.get(k):
            return (keys, k, int(e[k]), target, hits)
    sp = e.get('special') or []
    if sp:
        s0 = sp[0] if isinstance(sp[0], dict) else {'code': sp[0]}
        v = s0.get('value', s0.get('v', 0))
        return (keys, 'special:' + str(s0.get('code')), int(v or 0), target, hits)
    return (keys, None, 0, target, hits)


data = load()
shared = data.get('shared', [])
others = []
for cls, arr in data.items():
    if cls == 'shared':
        continue
    for c in arr:
        others.append((cls, c))

fp_index = defaultdict(list)
shape_index = defaultdict(list)
for cls, c in others:
    fp_index[fp(c)].append((cls, c))
    shape_index[main_shape(c)].append((cls, c))

buf = io.StringIO()
buf.write('# 通用牌 × 职业专属牌 查重对照\n\n')
buf.write('> 由 `tools/dup_check.py` 机械生成。**只列事实，不替你决定删哪张**。\n')
buf.write('> 通用牌 %d 张；职业牌 %d 张（%s）。\n\n' % (
    len(shared), len(others),
    '、'.join('%s %d' % (CN.get(k, k), len(v)) for k, v in data.items() if k != 'shared')))
buf.write('两种撞法：\n')
buf.write('- **完全撞**：effect 一模一样\n')
buf.write('- **近似撞**：主效果同、数值差 ≤2、目标相同（6 伤害 vs 7 伤害）\n\n')

exact_total = 0
near_total = 0
free = []

for s in shared:
    f = fp(s)
    shp = main_shape(s)
    exact = fp_index.get(f, [])
    # 近似：同 shape，数值差 <= 2，且不完全相同
    near = []
    if shp[1]:
        for dv in (-1, 1, -2, 2):
            probe = (shp[0], shp[1], shp[2] + dv, shp[3], shp[4])
            near.extend([x for x in shape_index.get(probe, []) if fp(x[1]) != f])
    # 去重（同一张卡可能同时命中 +1 和 +2）
    seen = set()
    near_u = []
    for cls, c in near:
        if c['id'] in seen:
            continue
        seen.add(c['id'])
        near_u.append((cls, c))

    buf.write('---\n\n## `%s` %s（通用）\n\n' % (s['id'], s['name']))
    e = s.get('effect') or {}
    buf.write('效果：`%s`\n\n' % json.dumps(e, ensure_ascii=False))
    if not exact and not near_u:
        buf.write('**没有任何职业牌与它相撞** —— 这张填补的是空白。\n\n')
        free.append(s)
        continue
    if exact:
        exact_total += len(exact)
        buf.write('### 完全撞（%d 张）\n\n' % len(exact))
        for cls, c in exact:
            buf.write('- `%s` %s（%s）\n' % (c['id'], c['name'], CN.get(cls, cls)))
        buf.write('\n')
    if near_u:
        near_total += len(near_u)
        buf.write('### 近似撞（%d 张）\n\n' % len(near_u))
        for cls, c in near_u:
            buf.write('- `%s` %s（%s）— `%s`\n' % (
                c['id'], c['name'], CN.get(cls, cls),
                json.dumps(c.get('effect') or {}, ensure_ascii=False)))
        buf.write('\n')

buf.write('---\n\n## 汇总\n\n')
buf.write('- 通用牌里**完全撞**掉的职业牌：%d 次\n' % exact_total)
buf.write('- 通用牌里**近似撞**上的职业牌：%d 次\n' % near_total)
buf.write('- **没撞任何职业牌**的通用牌：%d 张 —— %s\n' % (
    len(free), '、'.join('%s %s' % (s['id'], s['name']) for s in free) or '无'))
buf.write('\n> 注意：一个职业牌可能同时被两张通用牌撞上，统计是「次数」不是「张数」。\n')

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT.name)
print('完全撞 %d 次 / 近似撞 %d 次 / 通用牌无撞 %d 张' % (exact_total, near_total, len(free)))
