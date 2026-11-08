# -*- coding: utf-8 -*-
"""T524 事件风险收益比表 → docs/design/event_rr.md

评分模型（常数全部写明，量纲=「分」，血=1 分基准）：
  损失 = damage×1 + maxhp负值×2（永久代价加倍） + gaze正值×1（凝视是债） + resonance负值×0.5
  收益 = gold×0.5 + parts×0.5 + heal×0.5 + card_reward(common 15/uncommon 30/rare 45/special 15)
         + relic 40 + upgrade 20 + resonance正值×0.5 + gaze负值×1（洗凝视）
  净值 = 收益 − 损失
标记：
  「玩家不会选」= 净值 ≤ −8（亏损明显）
  「必选」= 净值 ≥ 25 且 损失 = 0
复算：python data/audit/gen_t524.py

用法：python data/audit/gen_t524.py
"""
import io, sys, json
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME

OUT = GAME / 'docs' / 'design' / 'event_rr.md'
RAW = json.load(open(GAME / 'data' / 'audit' / 'raw_all.json', encoding='utf-8'))
POOLS = [('events', '通用'), ('anminEvents', '维护者'), ('cngEvents', '疯先知')]
CR_VAL = {'common': 15, 'uncommon': 30, 'rare': 45, 'special': 15}

def score(r):
    if not r:
        return 0, 0, 0
    loss = (r.get('damage', 0) + min(0, r.get('maxhp', 0)) * -2
            + max(0, r.get('gaze', 0)) + max(0, -r.get('resonance', 0)) * 0.5)
    gain = (r.get('gold', 0) * 0.5 + r.get('parts', 0) * 0.5 + r.get('heal', 0) * 0.5
            + CR_VAL.get(r.get('card_reward'), 0) + (40 if r.get('relic') else 0)
            + (20 if r.get('upgrade') else 0)
            + max(0, r.get('resonance', 0)) * 0.5 + max(0, -r.get('gaze', 0)))
    return gain, loss, gain - loss

rows = []
for pk, pn in POOLS:
    for ev in RAW[pk]:
        for i, opt in enumerate(ev.get('options') or []):
            g, l, net = score(opt.get('result') or {})
            rows.append((ev, pn, i + 1, opt.get('text', ''), g, l, net))

buf = io.StringIO()
buf.write('# T524 · 事件风险收益比表\n\n')
buf.write('> 模型（量纲=分，血=1）：损失 = damage + maxhp损失×2 + 凝视获取×1 + 共振付出×0.5；')
buf.write('收益 = 金×0.5 + 零件×0.5 + 回血×0.5 + 给牌(普15/精30/稀45) + 遗物40 + 升级20 + 共振×0.5 + 洗凝视×1。')
buf.write('净值 = 收益−损失。事件结果是确定值（result 字段无随机），期望值即字段值本身。\n')
buf.write('> 标记：「玩家不会选」= 净值 ≤ −8；「必选」= 净值 ≥ 25 且零损失。复算：`python data/audit/gen_t524.py`。\n\n')

buf.write('## 「玩家不会选」选项（净值 ≤ −8）\n\n')
buf.write('| 事件 | 池 | 选项 | 原文 | 收益 | 损失 | 净值 |\n|---|---|---|---|---|---|---|\n')
bad = [r for r in rows if r[6] <= -8]
for ev, pn, i, t, g, l, net in sorted(bad, key=lambda r: r[6]):
    buf.write('| %s %s | %s | %d | %s | %.1f | %.1f | %.1f |\n' % (ev['id'], ev['title'], pn, i, t, g, l, net))

buf.write('\n## 「必选」选项（净值 ≥ 25 且零损失）\n\n')
buf.write('| 事件 | 池 | 选项 | 原文 | 收益 | 净值 |\n|---|---|---|---|---|---|\n')
must = [r for r in rows if r[6] >= 25 and r[5] == 0]
for ev, pn, i, t, g, l, net in sorted(must, key=lambda r: -r[6]):
    buf.write('| %s %s | %s | %d | %s | %.1f | %.1f |\n' % (ev['id'], ev['title'], pn, i, t, g, net))

buf.write('\n## 全部选项表\n\n')
buf.write('| 事件 | 池 | # | 选项原文 | 收益 | 损失 | 净值 |\n|---|---|---|---|---|---|---|\n')
for ev, pn, i, t, g, l, net in rows:
    buf.write('| %s %s | %s | %d | %s | %.1f | %.1f | %.1f |\n' % (ev['id'], ev['title'], pn, i, t, g, l, net))

buf.write('\n## 统计\n\n')
buf.write('- 选项总数 %d；「玩家不会选」%d 个；「必选」%d 个；其余 %d 个。\n' % (
    len(rows), len(bad), len(must), len(rows) - len(bad) - len(must)))
buf.write('- 净值分布：≤−8：%d；−8~0：%d；0~25：%d；≥25：%d。\n' % (
    sum(1 for r in rows if r[6] <= -8), sum(1 for r in rows if -8 < r[6] <= 0),
    sum(1 for r in rows if 0 < r[6] < 25), sum(1 for r in rows if r[6] >= 25)))
buf.write('\n### 模型说明\n\n常数为口径设定（非实测），用于横向排序而非绝对定价；「必选」的零损失门槛让「给牌但扣血」不进必选——扣血的收益永远打折。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, '| bad', len(bad), '| must', len(must), '| total', len(rows))
