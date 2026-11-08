# -*- coding: utf-8 -*-
"""T441 事件全表 → docs/design/event_table.md

每事件一行组：id/层/池/标题/选项数/每选项(veins 标签 + 结果摘要 + 结果文本存在性)。
结果摘要 = result 字段的人话（gold/damage/card_reward/relic/parts/gaze/resonance/heal/maxhp/upgrade…）。
末尾统计：每层事件数、veins 标签分布（哪条脉事件最多/最少）、结果类型分布。
复算：python data/audit/gen_t441.py

用法：python data/audit/gen_t441.py
"""
import io, sys, json
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME, CN_VEIN

OUT = GAME / 'docs' / 'design' / 'event_table.md'
RAW = json.load(open(GAME / 'data' / 'audit' / 'raw_all.json', encoding='utf-8'))
POOLS = [('events', '通用'), ('anminEvents', '维护者'), ('cngEvents', '疯先知')]

KEY_CN = [('gold', '金'), ('parts', '零件'), ('damage', '扣血'), ('heal', '回血'),
          ('maxhp', '生命上限'), ('card_reward', '给牌'), ('relic', '给遗物'),
          ('upgrade', '升级'), ('gaze', '凝视'), ('resonance', '共振'),
          ('delete_card', '删牌'), ('upgrade_random', '随机升级')]

def result_cn(r):
    if not r:
        return '无事发生'
    parts = []
    for k, cn in KEY_CN:
        if k in r:
            parts.append('%s %s' % (cn, r[k]))
    for k in r:
        if k not in dict(KEY_CN):
            parts.append('%s %s' % (k, r[k]))
    return '、'.join(parts) or json.dumps(r, ensure_ascii=False)

buf = io.StringIO()
buf.write('# T441 · 事件全表\n\n')
buf.write('> 数据源：`data/audit/raw_all.json` 的 events/anminEvents/cngEvents = **102 个事件**。\n')
buf.write('> 「结果」= 选项 result 字段逐键翻译；选项原文与结果文本过长不入表，可在 RAW 里按 id 查。')
buf.write('复算：`python data/audit/gen_t441.py`。\n\n')

vein_counter = Counter()
result_counter = Counter()
per_layer = defaultdict(lambda: [0, 0])
rows_by_pool = {p: [] for p, _ in POOLS}
for pk, pn in POOLS:
    for ev in RAW[pk]:
        rows_by_pool[pk].append(ev)
        per_layer[(pn, ev['layer'])][0] += 1
        for opt in ev.get('options') or []:
            r = opt.get('result') or {}
            for v in opt.get('veins') or []:
                vein_counter[CN_VEIN.get(v, v)] += 1
            if not r:
                result_counter['无结果'] += 1
            else:
                result_counter['有结果'] += 1

for pk, pn in POOLS:
    buf.write('## %s（%d 个）\n\n' % (pn, len(rows_by_pool[pk])))
    buf.write('| id | 层 | 标题 | 选项数 | 选项明细（veins 标签 → 结果） |\n|---|---|---|---|---|\n')
    for ev in rows_by_pool[pk]:
        opts = ev.get('options') or []
        detail = '<br>'.join(
            '「%s」[%s] → %s' % (o.get('text', ''), '+'.join(CN_VEIN.get(v, v) for v in (o.get('veins') or [])) or '无脉',
                                 result_cn(o.get('result') or {}))
            for o in opts)
        buf.write('| %s | %d | %s | %d | %s |\n' % (ev['id'], ev['layer'], ev['title'], len(opts), detail))
    buf.write('\n')

buf.write('## 统计\n\n')
buf.write('### 脉标签分布（哪条脉的事件最多/最少）\n\n')
buf.write('| 脉 | 挂该脉的选项数 |\n|---|---|\n')
for v, n in vein_counter.most_common():
    buf.write('| %s | %d |\n' % (v, n))
buf.write('| 无脉 | %d |\n' % sum(1 for pk, _ in POOLS for ev in RAW[pk] for o in ev.get('options') or [] if not o.get('veins')))
total_opts = sum(len(ev.get('options') or []) for pk, _ in POOLS for ev in RAW[pk])
buf.write('\n总选项 %d 个。\n\n' % total_opts)

buf.write('### 每层事件数\n\n| 层 | 通用 | 维护者 | 疯先知 |\n|---|---|---|---|\n')
for L in range(1, 9):
    buf.write('| %d | %d | %d | %d |\n' % (
        L,
        sum(1 for ev in RAW['events'] if ev['layer'] == L),
        sum(1 for ev in RAW['anminEvents'] if ev['layer'] == L),
        sum(1 for ev in RAW['cngEvents'] if ev['layer'] == L)))

buf.write('\n### 结果类型分布\n\n| 类型 | 选项数 |\n|---|---|\n')
for k, n in result_counter.most_common():
    buf.write('| %s | %d |\n' % (k, n))

buf.write('\n### 复算\n\n`python data/audit/gen_t441.py`。脉标签按选项 `veins` 数组逐个计入（多脉选项各计一次）；「无结果」= result 为空。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, '| events', sum(len(v) for v in rows_by_pool.values()), '| veins', dict(vein_counter))
