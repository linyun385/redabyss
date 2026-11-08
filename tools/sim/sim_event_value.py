# -*- coding: utf-8 -*-
"""H06 事件期望收益 → docs/design/sim_event_value.md
用 T441 事件 result 数据算每选项价值分（与 event_rr.md 同模型：血=1 分基准）。
事件结果是确定值——本任务无随机性，脚本化是为了可复算与批量找负期望。
可复算：python tools/sim/sim_event_value.py
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simlib import GAME

OUT = GAME / 'docs' / 'design' / 'sim_event_value.md'
GAIN = {'common': 15, 'uncommon': 30, 'rare': 45, 'special': 15}
def value(r):
    r = r or {}
    gain = (r.get('gold', 0)*0.5 + r.get('parts', 0)*0.5 + r.get('heal', 0)*0.5
            + GAIN.get(r.get('card_reward'), 0) + (40 if r.get('relic') else 0)
            + (20 if r.get('upgrade') else 0) + max(0, r.get('resonance', 0))*0.5
            + max(0, -r.get('gaze', 0)))
    loss = (r.get('damage', 0) + min(0, r.get('maxhp', 0))*-2
            + max(0, r.get('gaze', 0)) + max(0, -r.get('resonance', 0))*0.5)
    return gain, loss, gain - loss

raw = json.loads((GAME / 'data/audit/raw_all.json').read_text(encoding='utf-8'))
rows = []
for pool in ['events', 'anminEvents', 'cngEvents']:
    for ev in raw[pool]:
        for i, o in enumerate(ev.get('options') or [], 1):
            g, l, net = value(o.get('result') or {})
            rows.append((net, ev['id'], ev['title'], i, o.get('text', ''), g, l))
rows.sort()

buf = []
buf.append('# H06 · 事件期望收益（价值分模型）')
buf.append('')
buf.append('> **假设**：价值分口径与 event_rr.md 完全一致（血=1 分：金/零件/回血 ×0.5，给牌 普15/精30/稀45，遗物 40，升级 20，共振 ×0.5，洗凝视 1；损失=伤害+上限×2+凝视获取+共振付出×0.5）。')
buf.append('> **局限与说明**：事件 result 是**确定值**——本任务没有随机性，「期望」即字段值本身；本脚本化只为了可复算与全量扫描。价值分是横向排序口径，不是绝对定价。')
buf.append('')
neg = [r for r in rows if r[0] < 0]
buf.append('## 负期望选项（%d / %d）' % (len(neg), len(rows)))
buf.append('')
buf.append('| 事件 | 选项 | 文本 | 收益 | 损失 | 净值 |')
buf.append('|---|---|---|---|---|---|')
for net, eid, title, i, t, g, l in neg:
    buf.append('| %s %s | #%d | %s | %.1f | %.1f | **%.1f** |' % (eid, title, i, t, g, l, net))
buf.append('')
buf.append('## 净值分布')
buf.append('')
buf.append('| 区间 | 选项数 |')
buf.append('|---|---|')
import collections
dist = collections.Counter()
for net, *_ in rows:
    dist['≤−8' if net <= -8 else '−8~0' if net <= 0 else '0~25' if net < 25 else '≥25'] += 1
for k in ['≤−8', '−8~0', '0~25', '≥25']:
    buf.append('| %s | %d |' % (k, dist[k]))
buf.append('')
buf.append('## 与 event_rr.md 的一致性')
buf.append('')
buf.append('两份产出同一模型同一数据——数字应完全一致（负期望 1 个、必选 20 个的对账在 event_rr.md）。本篇的价值=把该模型转成 tools/sim/ 的可重跑脚本。')
buf.append('')
buf.append('## 复算')
buf.append('')
buf.append('`python tools/sim/sim_event_value.py`（GAIN 表在顶部，改常数即改口径）。')
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
import io as _io; sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
print('options', len(rows), 'negative', len(neg), 'dist', dict(dist))
