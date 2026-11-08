# -*- coding: utf-8 -*-
"""T402 重复效果标记 → 重新生成 docs/design/vein_audit_matrix.md：
1. 「与谁重复」列填入（完全撞 / 近似撞，判据与 tools/dup_check.py 完全相同，范围扩到全部 219 张）
2. 文末追加「重复清单」节

完全撞：effect 规范化 JSON 一模一样（dup_check.py 的 fp）
近似撞：同 (键集, 主种类, target, hits) 桶内主数值差 ±1/±2，且 effect 不完全相同（dup_check.py 的 probe）
结构同（数值大改）：键集/结构相同但主数值差 >2 —— 补充视图，dup_check 不报，这里标出来以免漏看

用法：python data/audit/gen_t402.py
"""
import io, sys, json
from pathlib import Path
from collections import defaultdict, Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import (GAME, CN_CLASS, CN_TYPE, CN_RARITY, load_cards,
                          all_cards, vein_key, effect_fp, main_shape, one_line)

OUT = GAME / 'docs' / 'design' / 'vein_audit_matrix.md'

pairs = all_cards(load_cards())
by_id = {c['id']: (cls, c) for cls, c in pairs}

# ── 完全撞组 ──
fp_map = defaultdict(list)
for cls, c in pairs:
    fp_map[effect_fp(c)].append(c['id'])
exact_groups = {fp: ids for fp, ids in fp_map.items() if len(ids) >= 2}
exact_of = {}
for fp, ids in exact_groups.items():
    for i in ids:
        exact_of[i] = ids

# ── 结构同组（键集+target+hits 相同；含特殊码序列） ──
def struct_key(c):
    e = c.get('effect') or {}
    sp = tuple(json.dumps(s, sort_keys=True) for s in (e.get('special') or []))
    return (tuple(sorted(k for k in e)), e.get('target'), e.get('hits'), sp)

struct_map = defaultdict(list)
for cls, c in pairs:
    struct_map[struct_key(c)].append(c['id'])
struct_groups = {k: ids for k, ids in struct_map.items() if len(ids) >= 2}

# ── 近似撞：同 (键集,主种类,target,hits) 桶，主值 ±1/±2，fp 不同 ──
bucket = defaultdict(list)
for cls, c in pairs:
    shp = main_shape(c)
    bucket[(shp[0], shp[1], shp[3], shp[4])].append(c)
near_pairs = set()
for key, members in bucket.items():
    for i, a in enumerate(members):
        for b in members[i + 1:]:
            if effect_fp(a) == effect_fp(b):
                continue
            va, vb = main_shape(a)[2], main_shape(b)[2]
            if abs(va - vb) in (1, 2):
                near_pairs.add(tuple(sorted((a['id'], b['id']))))
near_adj = defaultdict(set)
for a, b in near_pairs:
    near_adj[a].add(b)
    near_adj[b].add(a)

def fmt_ids(ids, cap=4):
    ids = [i for i in ids if i]
    if len(ids) <= cap:
        return '、'.join(ids)
    return '、'.join(ids[:cap]) + ' …+%d' % (len(ids) - cap)

# ── 收尾润版：泛化行（逐字重复≥3）追加意图标签（T500） ──
import re as _re
_intent = {}
for _ln in (GAME / 'docs' / 'design' / 'card_intent_reverse.md').read_text(encoding='utf-8').splitlines():
    _m = _re.match(r'- `(\S+)` .+?（(.+?)）：', _ln)
    if _m:
        _intent[_m.group(1)] = _m.group(2)
_cnt = Counter()
for _cls, _c in pairs:
    _cnt[one_line(_c).replace(' ', '')] += 1
_generic = {k for k, v in _cnt.items() if v >= 3}

def polished(cid, line):
    if line.replace(' ', '') in _generic and cid in _intent:
        return '%s〔意图：%s〕' % (line, _intent[cid])
    return line

def dup_cell(cid):
    parts = []
    ex = [i for i in exact_of.get(cid, []) if i != cid]
    if ex:
        parts.append('完全:' + fmt_ids(sorted(ex)))
    nr = sorted(near_adj.get(cid, set()))
    if nr:
        parts.append('近似:' + fmt_ids(nr))
    sg = struct_groups.get(struct_key(by_id[cid][1]), [])
    sg = [i for i in sg if i != cid and i not in ex and i not in nr]
    if sg:
        parts.append('结构同:' + fmt_ids(sorted(sg)))
    return '<br>'.join(parts) if parts else ''

# ── 差异点描述 ──
def diff_desc(ida, idb):
    a, b = by_id[ida][1], by_id[idb][1]
    ea, eb = a.get('effect') or {}, b.get('effect') or {}
    ds = []
    for k in sorted(set(ea) | set(eb)):
        va, vb = ea.get(k), eb.get(k)
        if json.dumps(va, sort_keys=True) != json.dumps(vb, sort_keys=True):
            ds.append('%s %s→%s' % (k, va, vb))
    return '；'.join(ds) or '（无差异？）'

# ── 重建表格（T401 内容不变 + 填列） ──
buf = io.StringIO()
buf.write('# T401 · 全卡脉象矩阵\n\n')
buf.write('> 生成：`python data/audit/gen_t401.py`（矩阵）+ `python data/audit/gen_t402.py`（重复列与本节）。\n')
buf.write('> 数据源：`cards/*.json`（权威，219 张）。效果一句话由 `tools/card_desc.py` 的')
buf.write('`describe_card()` 生成，与 `docs/design/CARD_EFFECTS_AUTO.md` 同源。\n')
buf.write('> 「与谁重复」列判据与 `tools/dup_check.py` 相同、范围扩到全部 219 张（T402）。\n\n')
buf.write('| id | 职业 | 名字 | 脉 | 类型 | 费 | 稀有度 | 效果一句话 | 与谁重复 |\n')
buf.write('|---|---|---|---|---|---|---|---|---|\n')
n = 0
for cls, c in pairs:
    n += 1
    buf.write('| %s | %s | %s | %s | %s | %s | %s | %s | %s |\n' % (
        c['id'], CN_CLASS[cls], c['name'], vein_key(c), CN_TYPE.get(c.get('type'), ''),
        c.get('energy', 0), CN_RARITY.get(c.get('rarity'), ''), polished(c['id'], one_line(c)), dup_cell(c['id'])))
buf.write('\n总行数：%d\n\n' % n)

buf.write('## 数据源比对（cards/*.json vs web/index.html RAW）\n\n')
buf.write('用 node 从 `web/index.html` 行 6401 `const RAW =` 抽出字面量逐字段比对，结果：')
buf.write('**零不一致**（5 个文件全部字段与 RAW 一致），以 json 为准无需取舍。\n\n')

# ── 重复清单 ──
buf.write('## 重复清单（T402）\n\n')
buf.write('**数字来源说明**：`tools/dup_check.py` 只对比「通用 × 职业」，本夜实跑报 '
          '**完全撞 4 次 / 近似撞 21 次 / 通用无撞 7 张**（与任务书里记录的旧数字一致）。\n')
buf.write('本节用**同一套判据**扩到全部 219 张两两对比（含职业×职业），数字与 4/21 不可比——范围不同。\n')
buf.write('判据复述：完全撞 = effect 规范化 JSON 一模一样；近似撞 = 同(键集,主种类,target,hits)且主数值差 ∈ {1,2} 且 effect 不全同。\n\n')

buf.write('### 完全撞（%d 组）\n\n' % len(exact_groups))
for fp, ids in sorted(exact_groups.items(), key=lambda kv: kv[1][0]):
    names = ['`%s` %s（%s）' % (i, by_id[i][1]['name'], CN_CLASS[by_id[i][0]]) for i in ids]
    buf.write('- %s\n  - effect：`%s`\n' % (' = '.join(names), fp[:120]))

# 近似撞连通分量
seen_comp = set()
near_comps = []
for start in sorted(near_adj):
    if start in seen_comp:
        continue
    comp, stack = set(), [start]
    while stack:
        x = stack.pop()
        if x in comp:
            continue
        comp.add(x)
        stack.extend(near_adj[x] - comp)
    seen_comp |= comp
    near_comps.append(sorted(comp))
buf.write('\n### 近似撞（%d 组，连通分量归并）\n\n' % len(near_comps))
buf.write('说明：±1/±2 探测产生的对按连通分量归并；同一分量内首尾差可能 >2（链式），差异看每对标注。\n\n')
for comp in near_comps:
    names = ['`%s` %s（%s）' % (i, by_id[i][1]['name'], CN_CLASS[by_id[i][0]]) for i in comp]
    buf.write('- %s\n' % ' / '.join(names))
    for i in range(len(comp) - 1):
        buf.write('  - `%s` vs `%s`：%s\n' % (comp[i], comp[i + 1], diff_desc(comp[i], comp[i + 1])))

buf.write('\n### 结构同但数值大改（主数值差 >2，补充视图，%d 组）\n\n' % len(struct_groups))
sg_count = 0
for k, ids in sorted(struct_groups.items(), key=lambda kv: kv[1][0]):
    vals = [main_shape(by_id[i][1])[2] for i in ids]
    if vals and (max(vals) - min(vals) > 2) and len(set(ids)) >= 2:
        sg_count += 1
        names = ['`%s` %s（%s，主值 %s）' % (i, by_id[i][1]['name'], CN_CLASS[by_id[i][0]],
                 main_shape(by_id[i][1])[2]) for i in ids]
        buf.write('- %s\n' % ' / '.join(names))
if sg_count == 0:
    buf.write('（无：结构相同的组主数值差都 ≤2，已并入上面两档）\n')

buf.write('\n### 汇总\n\n')
marked = sum(1 for cls, c in pairs if dup_cell(c['id']))
buf.write('- 219 张中，「与谁重复」列非空的：%d 张\n' % marked)
buf.write('- 完全撞组：%d 组（%d 张卡）；近似撞分量：%d 组\n' % (
    len(exact_groups), sum(len(v) for v in exact_groups.values()), len(near_comps)))
buf.write('- 复算：`python data/audit/gen_t402.py` 重跑后核对上面数字。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, '| marked:', marked, '| exact groups:', len(exact_groups),
      '| near comps:', len(near_comps))
