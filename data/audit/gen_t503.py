# -*- coding: utf-8 -*-
"""T503 三种特殊机制使用分布 → docs/design/special_mech_dist.md

三族定义：
  lock 族   = cost_type == 'lock'（本层只能用一次）
  凝视族    = cost_type == 'mark'（打出凝视+1）+ effect 键 gaze_cost / gaze_gain + special code gaze_reduce
  共振族    = effect 键 resonance_gain / resonance_cost / resonance_drain + special code resonance_lock
另扫 special 全部 code，列出只被 1 张卡用到的码（死机制候选，只报告）。

用法：python data/audit/gen_t503.py
"""
import io, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME, CN_CLASS, load_cards

OUT = GAME / 'docs' / 'design' / 'special_mech_dist.md'
CLASSES = ['diver', 'tremor', 'anmin', 'cangmin', 'shared']
cards = load_cards()
ALL = [(cls, c) for cls in CLASSES for c in cards[cls]]

lock_cards, gaze_cards, reso_cards = [], [], []
for cls, c in ALL:
    e = c.get('effect') or {}
    if c.get('cost_type') == 'lock':
        lock_cards.append((cls, c, 'cost_type=lock'))
    if c.get('cost_type') == 'mark':
        gaze_cards.append((cls, c, 'cost_type=mark(打出凝视+1)'))
    for k in ('gaze_cost', 'gaze_gain'):
        if e.get(k):
            gaze_cards.append((cls, c, '%s=%s' % (k, e[k])))
    for s in e.get('special') or []:
        if isinstance(s, dict) and s.get('code') == 'gaze_reduce':
            gaze_cards.append((cls, c, 'gaze_reduce=%s' % s.get('value')))
    for k in ('resonance_gain', 'resonance_cost', 'resonance_drain'):
        if e.get(k):
            reso_cards.append((cls, c, '%s=%s' % (k, e[k])))
    for s in e.get('special') or []:
        if isinstance(s, dict) and s.get('code') == 'resonance_lock':
            reso_cards.append((cls, c, 'resonance_lock'))

def fam_table(name, entries, note):
    ids = {c['id'] for _, c, _ in entries}
    per_cls = Counter(CN_CLASS[cls] for cls, _, _ in entries)
    vals = []
    for _, c, tag in entries:
        try:
            vals.append(float(tag.split('=')[-1].rstrip(')')))
        except ValueError:
            pass
    avg = sum(vals) / len(vals) if vals else 0
    b = ['- **%s**：%d 张卡用到（去重 id 数 %d）；按角色：%s' % (
        name, len(entries), len(ids),
        '、'.join('%s %d' % kv for kv in sorted(per_cls.items())))]
    b.append('  - 数值证据：%s' % (', '.join('`%s` %s(%s)' % (c['id'], c['name'], tag) for cls, c, tag in entries[:14])
             + (' … 等 %d 条' % (len(entries) - 14) if len(entries) > 14 else '')))
    b.append('  - 平均数值：%s（仅统计带数字的用法，n=%d）' % (('%.2f' % avg) if vals else '—', len(vals)))
    b.append('  - %s\n' % note)
    return '\n'.join(b)

# 特殊码分布
code_cards = defaultdict(list)
for cls, c in ALL:
    for s in (c.get('effect') or {}).get('special') or []:
        if isinstance(s, dict):
            code_cards[s.get('code')].append((cls, c, s.get('value')))

buf = io.StringIO()
buf.write('# T503 · lock / 凝视 / 共振 三种特殊机制的使用分布\n\n')
buf.write('> 数据源：`cards/*.json`（219 张）。定义见文末。复算：`python data/audit/gen_t503.py`。\n\n')
buf.write(fam_table('lock（本层一次）', lock_cards,
                     '定位：给大数值动作定价——「这层只给你一次机会」。'))
buf.write(fam_table('凝视（mark 代价 + 效果键）', gaze_cards,
                     '定位：凝视既是代价（cost_type=mark）又是门槛（gaze_cost）又能被管理（gaze_reduce）。'))
buf.write(fam_table('共振（gain / cost / drain / lock）', reso_cards,
                     '定位：资源循环——攒（gain）、花（cost）、泄（drain）、锁（resonance_lock）。'))

buf.write('## 附：special 全部 code 分布（找只被 1 张卡用的机制）\n\n')
buf.write('| code | 用卡数 | 卡 | 只此一张？ |\n|---|---|---|---|\n')
for code, lst in sorted(code_cards.items(), key=lambda kv: len(kv[1])):
    ids = '、'.join('`%s` %s' % (c['id'], c['name']) for _, c, _ in lst)
    buf.write('| %s | %d | %s | %s |\n' % (code, len(lst), ids, '**是 ← 死机制候选**' if len(lst) == 1 else ''))

buf.write('\n## 结论\n\n')
singles = [(code, lst) for code, lst in code_cards.items() if len(lst) == 1]
buf.write('- 只被 1 张卡用到的 special code：%s —— 共 %d 个。' % (
    '、'.join('`%s`' % c for c, _ in singles), len(singles)))
buf.write('它们大概率是「为一张卡单独写的机制」，引擎里可能各只有一处分支（只报告，不改）。\n')
buf.write('- 三族里最重的是共振（%d 次用法 / %d 张卡），凝视次之（%d 次 / %d 张），lock 最轻（%d 次 / %d 张）。' % (
    len(reso_cards), len({c['id'] for _, c, _ in reso_cards}),
    len(gaze_cards), len({c['id'] for _, c, _ in gaze_cards}),
    len(lock_cards), len({c['id'] for _, c, _ in lock_cards})))
buf.write('与 T400 §2.2 的机制归属一致：共振/凝视是跨角色经济，lock 是低频大招的定价器。\n')
buf.write('\n定义：lock 族 = `cost_type=="lock"`；凝视族 = `cost_type=="mark"` ∪ `gaze_cost` ∪ `gaze_gain` ∪ special`gaze_reduce`；')
buf.write('共振族 = `resonance_gain` ∪ `resonance_cost` ∪ `resonance_drain` ∪ special`resonance_lock`。一张卡可同入多族（按用法计次）。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, '| lock', len(lock_cards), '| gaze', len(gaze_cards),
      '| reso', len(reso_cards), '| single codes', [c for c, _ in singles])
