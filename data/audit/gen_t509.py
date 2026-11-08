# -*- coding: utf-8 -*-
"""T509 遗物里的「必拿」→ docs/design/relic_mustpick.md

判定算法（可复算）：
  副作用 = effect_code 里存在 (action=gaze 且 value>0)（凝视是债）或任何 value<0 或 maxhp 负值。
  必拿候选 = 无副作用 且 trigger ∈ {combat_start, turn_start, run_start}（无条件/自动触发）且 value>0。
  on_kill 触发需要击杀（条件性），不算必拿。
  收益差 = 该遗物主动作数值 vs 同稀有度、同 trigger+action 的全部遗物数值中位数。

用法：python data/audit/gen_t509.py
"""
import io, sys, json, statistics
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME

OUT = GAME / 'docs' / 'design' / 'relic_mustpick.md'
RAW = json.load(open(GAME / 'data' / 'audit' / 'raw_all.json', encoding='utf-8'))
POOL = [('relics', '通用池'), ('anminRelics', '维护者池'), ('cngRelics', '疯先知池')]
CN_R = {'common': '普通', 'uncommon': '精良', 'rare': '稀有', 'boss': 'boss'}
ACT_CN = {'draw': '抽牌', 'heal': '回血', 'block': '格挡', 'maxhp': '生命上限',
          'resonance': '共振', 'gaze': '凝视'}

relics = []
for pk, pn in POOL:
    for r in RAW[pk]:
        r['_pool'] = pn
        relics.append(r)

def has_downside(r):
    for ec in r.get('effect_code') or []:
        a, v = ec.get('action'), ec.get('value')
        if a == 'gaze' and isinstance(v, (int, float)) and v > 0:
            return '凝视 +%s' % v
        if isinstance(v, (int, float)) and v < 0:
            return '%s %s' % (ACT_CN.get(a, a), v)
    return None

def main_effect(r):
    """主动作：取第一个正数值动作（凝视正数视为副作用不算）。"""
    for ec in r.get('effect_code') or []:
        a, v = ec.get('action'), ec.get('value')
        if isinstance(v, (int, float)) and v > 0 and a != 'gaze':
            return a, v
    return None, None

# 必拿候选
cands = []
for r in relics:
    if has_downside(r):
        continue
    trigs = [ec.get('trigger') for ec in r.get('effect_code') or []]
    if not any(t in ('combat_start', 'turn_start', 'run_start') for t in trigs):
        continue
    a, v = main_effect(r)
    if a is None:
        continue
    cands.append((r, a, v))

# 同稀有度同动作中位数（含带副作用的，作为「市场价」）
market = defaultdict(list)
for r in relics:
    a, v = main_effect(r)
    if a:
        market[(r.get('rarity'), a)].append(v)

def cand_diff(r, a, v):
    mk = market.get((r.get('rarity'), a))
    if not mk:
        return None, 0
    return statistics.median(mk), v - statistics.median(mk)

strong = [(r, a, v, med, d) for r, a, v in cands
          for med, d in [cand_diff(r, a, v)]
          if med is None or d >= 1 or len(market.get((r.get('rarity'), a), [])) <= 2]
rest = [(r, a, v, med, d) for r, a, v in cands
        for med, d in [cand_diff(r, a, v)]
        if (r, a, v, med, d) not in strong]

buf = io.StringIO()
buf.write('# T509 · 遗物里的「必拿」\n\n')
buf.write('> 数据源：RAW.relics(77) + anminRelics(15) + cngRelics(15) = **107 件**。\n')
buf.write('> 判定算法与收益对照见文末。复算：`python data/audit/gen_t509.py`。只报告，不改。\n\n')

buf.write('## 必拿（明显强，%d 件）\n\n' % len(strong))
buf.write('入选线：无副作用 ∧ 自动触发 ∧ 主收益比同稀有度同动作中位数 **高 ≥1**（或该动作在同稀有度里 ≤2 件，属稀缺位）。\n\n')
buf.write('| id | 名字 | 池 | 稀有度 | 触发 | 效果 | 主收益 | 同稀有度同动作中位数 | 差 |\n|---|---|---|---|---|---|---|---|---|\n')
for r, a, v, med, d in sorted(strong, key=lambda x: (x[0].get('rarity'), -(x[4] if x[4] is not None else 0))):
    trig = '/'.join(sorted({ec.get('trigger') for ec in r.get('effect_code') or []}))
    diff = ('%+.1f' % d) if d is not None else '（该档独一份）'
    buf.write('| %s | %s | %s | %s | %s | %s | %s %s | %s | %s |\n' % (
        r['id'], r['name'], r['_pool'], CN_R.get(r.get('rarity'), ''), trig,
        r.get('effect_text'), ACT_CN.get(a, a), v, med, diff))

buf.write('\n## 其余无副作用的白赚件（%d 件，稳定但不突出）\n\n' % len(rest))
buf.write('无副作用、自动触发，但收益不高于同档中位——「不亏」，不是「必拿」。\n\n')
buf.write('| id | 名字 | 池 | 稀有度 | 效果 | 主收益 vs 中位 |\n|---|---|---|---|---|---|\n')
for r, a, v, med, d in sorted(rest, key=lambda x: (x[0].get('rarity'), -x[2])):
    buf.write('| %s | %s | %s | %s | %s | %s%s vs %s |\n' % (
        r['id'], r['name'], r['_pool'], CN_R.get(r.get('rarity'), ''),
        r.get('effect_text'), ACT_CN.get(a, a), v, med))

n_down = sum(1 for r in relics if has_downside(r))
buf.write('\n## 反面清单：带副作用的遗物（%d 件，不会是必拿）\n\n' % n_down)
buf.write('其中凝视正数（凝视是债）%d 件；负数值（掉血/减益）若干。完整列表随逐件数据可查，'
          '典型：凝视+2 换收益的遗物在凝视经济里是「贷款」，不是白给。\n\n' %
          sum(1 for r in relics if any(ec.get('action') == 'gaze' and isinstance(ec.get('value'), (int, float)) and ec.get('value') > 0 for ec in r.get('effect_code') or [])))

buf.write('## 判定算法（复算用）\n\n')
buf.write('1. 副作用 = `effect_code` 中存在 `gaze` 正值（凝视是债）或任何负数值。\n')
buf.write('2. 必拿候选 = 无副作用 ∧ trigger ∈ {combat_start, turn_start, run_start} ∧ 存在正数值非凝视动作。\n')
buf.write('3. `on_kill` 需要击杀（条件性），一律不算必拿。\n')
buf.write('4. 收益差 = 主动作数值 − 同(稀有度,动作)全部遗物数值中位数（含带副作用者，作市场价）。\n')
buf.write('5. 「必拿」的最后一步是体感判断：上表全部满足「拿到就白赚、不改变卡组方向」，其中收益差为正的更甚。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, '| candidates', len(cands), '| with downside', n_down)
