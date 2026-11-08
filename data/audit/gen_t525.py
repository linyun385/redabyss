# -*- coding: utf-8 -*-
"""T525 遗物强度分级 → docs/design/relic_tier.md

分级模型（量纲=分/场，血=1）：
  每条 effect_code 按触发频率折算每场收益：
    combat_start ×5 场景值 / turn_start ×8 / run_start ×30（整局按 30 场战斗）/ on_kill ×3
  动作价值：draw 3/张, block 0.6/点, heal 0.6/点, maxhp 2/点, resonance 0.5/点,
            gaze正值 = −1/点（债）, gaze负值 = +1/点, 其他动作 0
  副作用：负值动作按对应价值扣；总评 = Σ(动作价值×折算次数)
  分级：S ≥ 30 / A ≥ 15 / B ≥ 5 / C < 5（C = 拿了几乎没感觉）
  「C 档没人要」重点列出。on_kill 频率低自带惩罚。
复算：python data/audit/gen_t525.py

用法：python data/audit/gen_t525.py
"""
import io, sys, json
from pathlib import Path
from collections import defaultdict, Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME

OUT = GAME / 'docs' / 'design' / 'relic_tier.md'
RAW = json.load(open(GAME / 'data' / 'audit' / 'raw_all.json', encoding='utf-8'))
POOLS = [('relics', '通用'), ('anminRelics', '维护者'), ('cngRelics', '疯先知')]
TRIG_W = {'combat_start': 5, 'turn_start': 8, 'run_start': 30, 'on_kill': 3}
ACT_W = {'draw': 3.0, 'block': 0.6, 'heal': 0.6, 'maxhp': 2.0, 'resonance': 0.5}

def relic_score(r):
    total = 0.0
    detail = []
    for ec in r.get('effect_code') or []:
        trig, act, v = ec.get('trigger'), ec.get('action'), ec.get('value')
        if not isinstance(v, (int, float)):
            continue
        w = ACT_W.get(act)
        if act == 'gaze':
            w = -1.0 if v > 0 else 1.0
            v = abs(v)
        if w is None:
            continue
        s = w * v * TRIG_W.get(trig, 1)
        total += s
        detail.append('%s %s%+d → %.1f' % (trig, act, v, s))
    return total, detail

def tier(s):
    return 'S' if s >= 30 else ('A' if s >= 15 else ('B' if s >= 5 else 'C'))

rows = []
for pk, pn in POOLS:
    for r in RAW[pk]:
        s, detail = relic_score(r)
        rows.append((r, pn, s, tier(s), detail))

buf = io.StringIO()
buf.write('# T525 · 遗物强度分级（S/A/B/C）\n\n')
buf.write('> 模型：每条 effect_code 按「触发次数折算」（开战×5 / 每回合×8 / 整局×30 / 击杀×3）×动作价值')
buf.write('（抽 3/张、挡 0.6/点、回血 0.6/点、上限 2/点、共振 0.5/点、凝视 +1=−1 凝视 −1=+1）求和。\n')
buf.write('> S≥30 / A≥15 / B≥5 / C<5。常数为口径设定，用于排序。复算：`python data/audit/gen_t525.py`。\n\n')

tc = Counter(t[3] for t in rows)
buf.write('## 分布\n\n| 档 | 件数 |\n|---|---|\n')
for k in ['S', 'A', 'B', 'C']:
    buf.write('| %s | %d |\n' % (k, tc[k]))

buf.write('\n## S 档（拿到就变一大截）\n\n')
for r, pn, s, t, d in sorted([x for x in rows if x[3] == 'S'], key=lambda x: -x[2]):
    buf.write('- **`%s` %s（%s，%.0f 分）**：%s\n  - 明细：%s\n' % (
        r['id'], r['name'], pn, s, r.get('effect_text'), '；'.join(d)))

buf.write('\n## C 档（没人要的重点区，%d 件）\n\n' % tc['C'])
buf.write('| id | 名字 | 池 | 分 | 效果 | 为什么没人要 |\n|---|---|---|---|---|---|\n')
for r, pn, s, t, d in sorted([x for x in rows if x[3] == 'C'], key=lambda x: x[2]):
    why = '收益折算后 <5 分/场——体感≈无'
    if any(ec.get('action') == 'gaze' and (ec.get('value') or 0) > 0 for ec in r.get('effect_code') or []):
        why = '凝视是净负债：收益被凝视代价吃掉'
    buf.write('| %s | %s | %s | %.1f | %s | %s |\n' % (r['id'], r['name'], pn, s, r.get('effect_text'), why))

buf.write('\n## 全表\n\n')
buf.write('| 档 | id | 名字 | 池 | 分 | 效果 |\n|---|---|---|---|---|---|\n')
for r, pn, s, t, d in sorted(rows, key=lambda x: -x[2]):
    buf.write('| %s | %s | %s | %s | %.1f | %s |\n' % (t, r['id'], r['name'], pn, s, r.get('effect_text')))

buf.write('\n### 模型说明\n\n- 折算次数按「一场战斗平均 8 回合 / 一局 30 场」口径；on_kill 乘 3（精英战也就杀 1~3 只）。\n')
buf.write('- 效果含未知动作（非 ACT_W 表内）按 0 计——这类遗物会被低估，全表可查明细。\n')
buf.write('- 模型不含「与卡组配合」的乘数（如共振遗物对共振流的实际价值）——分级是裸强度。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, dict(tc))
