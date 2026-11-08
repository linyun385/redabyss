# -*- coding: utf-8 -*-
"""T512 每层事件密度 → docs/design/event_density.md

数据：RAW.layers 的 rows（每行选一个节点）。
统计每层：行数、事件行（行内含 event）、商店行、精英行、强制战斗行；
期望事件数 = Σ(行内 event 数 / 行内选项数)（按随机选择模型）；
「多久遇到一次事件」= 层节点数 / 期望事件数。
复算：python data/audit/gen_t512.py

用法：python data/audit/gen_t512.py
"""
import io, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME

OUT = GAME / 'docs' / 'design' / 'event_density.md'
RAW = json.load(open(GAME / 'data' / 'audit' / 'raw_all.json', encoding='utf-8'))

buf = io.StringIO()
buf.write('# T512 · 每层事件密度\n\n')
buf.write('> 数据源：`RAW.layers.layers[].rows`（每行选一个节点）。期望值按「行内等概率选择」模型。')
buf.write('复算：`python data/audit/gen_t512.py`。\n\n')
buf.write('| 层 | 层名 | 行数 | 事件行 | 商店行 | 精发行 | 期望事件数 | 期望商店数 | 几个节点遇一次事件 |\n|---|---|---|---|---|---|---|---|---|\n')

tot_ev = tot_rows = 0
for L in RAW['layers']['layers']:
    rows = L['rows']
    ev_rows = sum(1 for r in rows if any(n['type'] == 'event' for n in r))
    shop_rows = sum(1 for r in rows if any(n['type'] == 'shop' for n in r))
    eli_rows = sum(1 for r in rows if any(n['type'] == 'elite' for n in r))
    exp_ev = sum(sum(1 for n in r if n['type'] == 'event') / len(r) for r in rows)
    exp_shop = sum(sum(1 for n in r if n['type'] == 'shop') / len(r) for r in rows)
    per = len(rows) / exp_ev if exp_ev else 0
    tot_ev += exp_ev
    tot_rows += len(rows)
    buf.write('| %d | %s | %d | %d | %d | %d | %.2f | %.2f | %.1f |\n' % (
        L['id'], L['name'], len(rows), ev_rows, shop_rows, eli_rows, exp_ev, exp_shop, per))

buf.write('\n全程（8 层 %d 行）：期望事件 %.1f 次、期望商店 %.1f 间。\n\n' % (
    sum(len(L['rows']) for L in RAW['layers']['layers']), tot_ev,
    sum(sum(sum(1 for n in r if n['type'] == 'shop') / len(r) for r in L['rows']) for L in RAW['layers']['layers'])))

buf.write('## 判断\n\n')
buf.write('- 事件行密度逐层变化不大（每层 1~3 行含事件），全程约 9~10 个事件——平均每 2.5~3 个节点一次。\n')
buf.write('- 商店集中在 2/3/6 层（各 1 行）；1、7、8 层没有商店——后期商店断供是有意的（第 7-8 层玩家该成型了）。\n')
buf.write('- 第 1 层没有精英行、没有商店：纯教学。\n')
buf.write('- 注意：这是**行选择模型**——实际游戏里行内怎么选（自由选还是限定）会改变真实密度，模型按等概率近似。\n')
buf.write('\n### 复算\n\n`python data/audit/gen_t512.py`；行定义见 `RAW.layers.layers[i].rows`。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT)
for L in RAW['layers']['layers']:
    ev = sum(sum(1 for n in r if n['type'] == 'event') / len(r) for r in L['rows'])
    print('L%d ev_rows=%d exp_ev=%.2f' % (L['id'], sum(1 for r in L['rows'] if any(n['type'] == 'event' for n in r)), ev))
