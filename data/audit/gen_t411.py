# -*- coding: utf-8 -*-
"""T411 特殊机制卡清单（lock / gaze / resonance）→ docs/design/vein_special_mech_cards.md

机制定义（覆盖 cost_type、effect 键、special code 三个入口）：
  lock        = cost_type 'lock'（本层只能用一次）｜special 无 lock 码
  resonance_lock = special code 'resonance_lock'（共振锁定）
  gaze_cost   = effect 键 gaze_cost（凝视门槛）
  gaze_gain   = effect 键 gaze_gain（打牌加凝视）
  gaze_reduce = special code 'gaze_reduce'（降凝视）
  mark 代价   = cost_type 'mark'（打出凝视 +1）
  resonance_gain  = effect 键
  resonance_cost  = effect 键
  resonance_drain = effect 键
一张卡可用多个机制 → 每机制一行。表列：id/名字/角色/机制/数值。
复算：python data/audit/gen_t411.py

用法：python data/audit/gen_t411.py
"""
import io, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME, CN_CLASS, load_cards

OUT = GAME / 'docs' / 'design' / 'vein_special_mech_cards.md'
CLASSES = ['diver', 'tremor', 'anmin', 'cangmin', 'shared']
rows = defaultdict(list)
for cls in CLASSES:
    for c in load_cards()[cls]:
        e = c.get('effect') or {}
        if c.get('cost_type') == 'lock':
            rows['lock（本层一次）'].append((cls, c, 'cost_type=lock'))
        if c.get('cost_type') == 'mark':
            rows['mark 代价（打出凝视+1）'].append((cls, c, '凝视 +1'))
        for k, label in [('gaze_cost', 'gaze_cost（凝视门槛）'),
                         ('gaze_gain', 'gaze_gain（加凝视）'),
                         ('resonance_gain', 'resonance_gain（攒共振）'),
                         ('resonance_cost', 'resonance_cost（花共振）'),
                         ('resonance_drain', 'resonance_drain（泄共振）')]:
            if e.get(k):
                rows[label].append((cls, c, '%s=%s' % (k, e[k])))
        for s in e.get('special') or []:
            if isinstance(s, dict) and s.get('code') == 'resonance_lock':
                rows['resonance_lock（共振锁定）'].append((cls, c, '锁定'))
            if isinstance(s, dict) and s.get('code') == 'gaze_reduce':
                rows['gaze_reduce（降凝视）'].append((cls, c, 'gaze_reduce=%s' % s.get('value')))

buf = io.StringIO()
buf.write('# T411 · 特殊机制卡清单（lock / gaze / resonance）\n\n')
buf.write('> 数据源：`cards/*.json`（219 张）。机制入口覆盖 cost_type / effect 键 / special code 三个层面（定义见文末）。\n')
buf.write('> 一张卡可用多个机制，在每个机制下各出现一行。复算：`python data/audit/gen_t411.py`。\n\n')

total_rows = 0
for mech in ['lock（本层一次）', 'mark 代价（打出凝视+1）', 'gaze_cost（凝视门槛）',
             'gaze_gain（加凝视）', 'gaze_reduce（降凝视）', 'resonance_gain（攒共振）',
             'resonance_cost（花共振）', 'resonance_drain（泄共振）', 'resonance_lock（共振锁定）']:
    lst = rows.get(mech, [])
    ids = {c['id'] for _, c, _ in lst}
    buf.write('## %s（%d 张卡）\n\n' % (mech, len(ids)))
    buf.write('| id | 名字 | 角色 | 数值 |\n|---|---|---|---|\n')
    for cls, c, val in lst:
        buf.write('| %s | %s | %s | %s |\n' % (c['id'], c['name'], CN_CLASS[cls], val))
        total_rows += 1
    buf.write('\n')

buf.write('## 定义（复算口径）\n\n')
buf.write('- lock：`cost_type=="lock"`（引擎：本层只能用一次）\n')
buf.write('- mark：`cost_type=="mark"`（打出时凝视 +1）\n')
buf.write('- gaze_cost / gaze_gain：同名 effect 键；gaze_reduce：special code\n')
buf.write('- resonance_gain / resonance_cost / resonance_drain：同名 effect 键；resonance_lock：special code\n')
buf.write('- 合计 %d 行（含一卡多机制重复计入）；涉及去重卡数 %d。\n' % (
    total_rows, len({c['id'] for lst in rows.values() for _, c, _ in lst})))

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, '| rows', total_rows, '| cards', len({c['id'] for lst in rows.values() for _, c, _ in lst}))
