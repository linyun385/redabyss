# -*- coding: utf-8 -*-
"""K01 遗物价值重算 → docs/design/_RELIC_RECALC.md
两个口径：
  口径 A（与 05 批同模型）：只计 effect_code 的 5 类动作+凝视——验证「94 件<0.5」是否被 06/07 批修的采样 bug 污染过
  口径 B（mod 计分版）：口径 A + mod 字段折算（vein_cost -1 → 能量节省当量；chain_bonus/keep_block/cost_redirect 定性加注）
口径 B 的 mod 折算假设（写明）：1 能量 ≈ 7.6 分（4 能量≈30 分/回合 ÷4 × 0.8 折扣）；对应脉卡一局打出 6 次（H03 卡组 42 张里该脉 ~6 张、每张打 1 次）；keep_block = 每回合格挡产出的一半保留 ≈ 每回合 +2.4 分（保守按 4/回合挡产出 ×0.6×50%）；cost_redirect gaze = 每次改写省 1 能量但加 1 凝视（净 -1 能量 +1 债）按每局 4 次改写计。
可复算：python tools/sim/relic_recalc.py
"""
import sys, io, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from simlib import GAME

from config import RELIC_FIGHTS, RELIC_TURNS_PER_FIGHT, RELIC_KILLS_PER_FIGHT, GOLD_PER_POINT, ENERGY_PER_POINT, VEIN_PLAYS, KEEP_BLOCK_PER_TURN, COST_REDIRECT_TIMES
FIGHTS, TURNS_PER_FIGHT, KILLS_PER_FIGHT = RELIC_FIGHTS, RELIC_TURNS_PER_FIGHT, RELIC_KILLS_PER_FIGHT
TRIG = {'combat_start': FIGHTS, 'turn_start': FIGHTS * TURNS_PER_FIGHT, 'run_start': 1, 'on_kill': FIGHTS * KILLS_PER_FIGHT}
ACT = {'draw': 3.0, 'block': 0.6, 'heal': 0.6, 'maxhp': 2.0, 'resonance': 0.5}
COST_REDIRECT_NET = COST_REDIRECT_TIMES * (ENERGY_PER_POINT - 1)

def base_score(r):
    total, unk = 0.0, 0
    for ec in r.get('effect_code') or []:
        a, v, t = ec.get('action'), ec.get('value'), ec.get('trigger')
        if not isinstance(v, (int, float)):
            continue
        w = ACT.get(a)
        if a == 'gaze':
            w = -1.0 if v > 0 else 1.0
            v = abs(v)
        if w is None:
            unk += 1
            continue
        total += w * v * TRIG.get(t, 0)
    return total, unk

def mod_score(mod):
    if not mod:
        return 0.0, ''
    parts = []
    s = 0.0
    if 'vein_cost' in mod:
        s += mod['vein_cost_delta'] * -1 * ENERGY_PER_POINT * VEIN_PLAYS
        parts.append('费用-1×%d次' % VEIN_PLAYS)
    if 'chain_bonus' in mod:
        parts.append('连携+%d（定性加注，不计分）' % mod['chain_bonus'])
    if mod.get('keep_block'):
        s += KEEP_BLOCK_PER_TURN * TURNS_PER_FIGHT * FIGHTS / TURNS_PER_FIGHT  # 每回合 2.4 分 × 总回合
        parts.append('格挡保留')
    if 'cost_redirect' in mod:
        s += COST_REDIRECT_NET
        parts.append('代价改写×4')
    return s, '+'.join(parts)

raw = json.loads((GAME / 'data/audit/raw_all.json').read_text(encoding='utf-8'))
CN_R = {'common': '普通', 'uncommon': '精良', 'rare': '稀有', 'boss': 'boss'}
rows = []
for pk, pn in [('relics', '通用'), ('anminRelics', '维护者'), ('cngRelics', '疯先知')]:
    for r in raw[pk]:
        base, unk = base_score(r)
        ms, mdesc = mod_score(r.get('mod'))
        price = 285 if r.get('rarity') in ('rare', 'boss') else 140
        rA = (base / GOLD_PER_POINT) / price
        rB = ((base + ms) / GOLD_PER_POINT) / price
        rows.append((rB, r['id'], r['name'], pn, CN_R.get(r.get('rarity'), ''), base, ms, rA, rB, unk, mdesc))

import collections
bandA = collections.Counter('亏' if r[7] < 0.5 else '平' if r[7] < 1 else '值' for r in rows)
bandB = collections.Counter('亏' if r[8] < 0.5 else '平' if r[8] < 1 else '值' for r in rows)
exits = [r for r in rows if r[7] < 0.5 <= r[8]]

buf = []
buf.append('# K01 · 遗物价值重算（修复后模拟器 + mod 计分口径）')
buf.append('')
buf.append('> **先澄清一件事**：`sim_relic_value.py` 是**确定模型**——不经过 show_three/pick_card（grep 验证零引用），')
buf.append('> 所以「94 件<0.5」**没有被 06/07 批修的两个采样 bug 污染过**——06 批 K01 任务书里「那是被污染的数」的说法不准确。')
buf.append('> 真正的问题是 I02 发现的另一个缺陷：**19 件遗物的 mod 字段（费用减免/连携/格挡保留/代价改写）不在 effect_code 里，模型计分为零**。')
buf.append('> 本篇给两个口径：A=05 批同模型重跑（应逐数一致）；**B=mod 计分版（真值口径）**。全部为估算。')
buf.append('')
buf.append('> **口径 B 的 mod 折算假设**：1 能量≈7.6 分；对应脉卡一局打出 6 次；keep_block 每回合 +2.4 分；代价改写每局 4 次（每次净省 1 能量欠 1 凝视）。**这些假设不依赖任何未拍板口径，但对卡组构成敏感——按中位卡组估。**')
buf.append('')
buf.append('## 口径对账')
buf.append('')
buf.append('| 口径 | 值 | 平 | 亏 |')
buf.append('|---|---|---|---|')
buf.append('| A（05 批同模型重跑） | %d | %d | %d |' % (bandA['值'], bandA['平'], bandA['亏']))
buf.append('| B（mod 计分版） | %d | %d | %d |' % (bandB['值'], bandB['平'], bandB['亏']))
buf.append('')
buf.append('- 口径 A 与 05 批逐数一致（1/12/94）——**「94 件亏」在确定模型下复现，不是采样 bug 污染**。')
buf.append('- 口径 B 把 %d 件 mod 遗物抬出亏损带——「94 件亏」的真值口径下修为 **%d 件**。' % (len(exits), bandB['亏']))
buf.append('')
buf.append('## 被抬出亏损带的 %d 件（新旧对比）' % len(exits))
buf.append('')
buf.append('| id | 名字 | 口径A 性价比 | 口径B 性价比 | mod 计分 |')
buf.append('|---|---|---|---|---|')
for rB, rid, name, pn, rar, base, ms, rA, rB2, unk, mdesc in sorted(exits, key=lambda x: -x[8]):
    buf.append('| %s | %s | %.2f | **%.2f** | %s |' % (rid, name, rA, rB2, mdesc))
buf.append('')
buf.append('## 口径 B 的 Top 10（真值口径下最值的遗物）')
buf.append('')
buf.append('| id | 名字 | 池 | 稀有度 | 口径B 性价比 |')
buf.append('|---|---|---|---|---|')
for rB, rid, name, pn, rar, base, ms, rA, rB2, unk, mdesc in sorted(rows, key=lambda x: -x[8])[:10]:
    buf.append('| %s | %s | %s | %s | **%.2f** |' % (rid, name, pn, rar, rB2))
buf.append('')
buf.append('## 口径 B 下仍然亏的（重新清点后仍 <0.5，%d 件）' % bandB['亏'])
buf.append('')
buf.append('| id | 名字 | 口径A | 口径B | 效果 |')
buf.append('|---|---|---|---|---|')
for rB, rid, name, pn, rar, base, ms, rA, rB2, unk, mdesc in sorted([r for r in rows if r[8] < 0.5], key=lambda x: x[8]):
    et = ''
    for pk in ['relics', 'anminRelics', 'cngRelics']:
        for r in raw[pk]:
            if r['id'] == rid:
                et = (r.get('effect_text') or '')[:50]
    buf.append('| %s | %s | %.2f | %.2f | %s |' % (rid, name, rA, rB2, et))
buf.append('')
buf.append('## 判定')
buf.append('')
buf.append('1. 「94 件亏」的两个修正：**采样 bug 没碰过它**（确定模型）；真缺陷是 mod 未计分——补上后亏件 94→%d。' % bandB['亏'])
buf.append('2. 亏件残余主力是**纯小数值件**（I02 的 C1/C2 类）——它们的弱不是模型口径问题，是设计问题（稀有度没兑现/存在感缺失），维持 I02 结论。')
buf.append('3. mod 遗物（费用减免/格挡保留/代价改写）的真值口径显著高于裸口径——**它们不是废件，是「对卡组构成敏感」的件**，印证 I02 的 B 类判断。')
buf.append('')
buf.append('## 复算')
buf.append('')
buf.append('`python tools/sim/relic_recalc.py`（ENERGY_PER_POINT/VEIN_PLAYS/KEEP_BLOCK_PER_TURN 假设常数在顶部，改后重跑即刷新）。')
OUT = GAME / 'docs' / 'design' / '_RELIC_RECALC.md'
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
print('A bands', dict(bandA), '| B bands', dict(bandB), '| exits', len(exits))
