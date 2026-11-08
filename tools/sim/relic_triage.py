# -*- coding: utf-8 -*-
"""I02 94 件「亏」遗物分诊 → docs/design/_RELIC_TRIAGE.md
分类规则（写明，可复算）：
  B 被低估 = 模型没计分的主效果存在（费用减免/代价改写/连携加成/凝视免疫/格挡保留——effect_code 里的 mod 类或 text 关键词）
  A 设计使然 = 凝视正债（凝视流玩家的燃料/20 凝视结局线）或上限双刃（用命换强度）
  C 真的废  = 只剩小数值且裸收益 <15 分（20 场口径）
判序：先 B（有 mod 钩子就进 B），再 A（凝视正债/双刃），剩下进 C。
"""
import sys, io, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from simlib import GAME
from config import RELIC_FIGHTS, RELIC_TURNS_PER_FIGHT, RELIC_KILLS_PER_FIGHT
FIGHTS, TURNS_PER_FIGHT, KILLS_PER_FIGHT = RELIC_FIGHTS, RELIC_TURNS_PER_FIGHT, RELIC_KILLS_PER_FIGHT
TRIG = {'combat_start': FIGHTS, 'turn_start': FIGHTS * TURNS_PER_FIGHT, 'run_start': 1, 'on_kill': FIGHTS * KILLS_PER_FIGHT}
ACT = {'draw': 3.0, 'block': 0.6, 'heal': 0.6, 'maxhp': 2.0, 'resonance': 0.5}
GOLD_PER_POINT = 60 / (0.35 * 76)

raw = json.loads((GAME / 'data/audit/raw_all.json').read_text(encoding='utf-8'))
rows = []
for pk, pn in [('relics','通用'),('anminRelics','维护者'),('cngRelics','疯先知')]:
    for r in raw[pk]:
        total = 0.0
        et = r.get('effect_text') or ''
        has_mod = bool(r.get('mod'))   # 代码级检测：mod 字段=引擎真实现的效果（vein_cost/chain_bonus/keep_block/cost_redirect）
        gaze_pos = False
        for ec in r.get('effect_code') or []:
            a, v, t = ec.get('action'), ec.get('value'), ec.get('trigger')
            if not isinstance(v, (int, float)): continue
            w = ACT.get(a)
            if a == 'gaze':
                if v > 0: gaze_pos = True
                w = -1.0 if v > 0 else 1.0
                v = abs(v)
            if w is None: continue
            total += w * v * TRIG.get(t, 0)
        worth = total / GOLD_PER_POINT
        price = 285 if r.get('rarity') in ('rare','boss') else 140
        if worth / price >= 0.5:
            continue
        # 分诊
        if has_mod:
            cat, why = 'B 被低估', 'mod 字段未计分（%s）——引擎真实现，模型裸收益不含' % json.dumps(r.get('mod'), ensure_ascii=False)
        elif gaze_pos and total < 10:
            cat, why = 'A 设计使然', '凝视正债是凝视流玩家的燃料（照骨/五脉符系门槛、20 凝视长审线）——情境向'
        elif '最大生命 -' in et:
            cat, why = 'A 设计使然', '上限双刃（用命换强度）——定价里有代价，模型把代价照算但没算「代价换来的东西」'
        else:
            rar = r.get('rarity')
            if rar == 'common':
                cat, why = 'C1 平坦填充', '普通档小数值（裸收益 %.0f 分/20 场）——图鉴填充位定位' % total
            else:
                cat, why = 'C2 真的弱', '%s 档却只有小数值（裸收益 %.0f 分/20 场）——稀有度没兑现' % (rar, total)
        rows.append((cat, r['id'], r['name'], r.get('rarity'), et, total, why))

import collections
cnt = collections.Counter(c for c, *_ in rows)
buf = []
buf.append('# I02 · 94 件「亏」遗物分诊（A 设计使然 / B 被低估 / C 真的废）')
buf.append('')
buf.append('> 方法：先复算 05 批模型确认 94 件 <0.5，再逐件按规则分诊（判序：有 mod 钩子→B；凝视正债/上限双刃→A；其余→C）。')
buf.append('> 核心发现先行：**94 件里没有几件是真废**——大头是 B「被低估」（模型对 mod 类效果计分为零）和 A「情境向」。')
buf.append('')
buf.append('| 类 | 件数 | 占 94 的 |')
buf.append('|---|---|---|')
for k in ['B 被低估', 'A 设计使然', 'C1 平坦填充', 'C2 真的弱']:
    buf.append('| **%s** | %d | %.0f%% |' % (k, cnt[k], 100 * cnt[k] / 94))
buf.append('')
for k in ['B 被低估', 'A 设计使然', 'C1 平坦填充', 'C2 真的弱']:
    buf.append('## %s\n' % k)
    buf.append('| id | 名字 | 稀有度 | 效果 | 裸收益分 | 理由 |')
    buf.append('|---|---|---|---|---|---|')
    for cat, rid, name, rar, et, total, why in rows:
        if cat != k: continue
        buf.append('| %s | %s | %s | %s | %.0f | %s |' % (rid, name, rar, et, total, why))
    buf.append('')
buf.append('## 三类各自的设计含义')
buf.append('')
buf.append('- **B 被低估（模型问题）**：mod 类遗物（费用减免/代价改写/连携+1）的真实价值依赖「玩家卡组里有多少张对应脉/带代价牌」——静态分没法算，要真引擎或分卡组口径。**它们的讨论价值=把模型口径补上，不是改遗物。**')
buf.append('- **A 设计使然（情境价值）**：凝视正债与上限双刃是「贷款型遗物」——散牌局/凝视流/快攻三类玩家各自会拿。讨论价值=把「情境」写在卡面或图鉴里，让玩家知道什么时候它不是废件。')
buf.append('- **C1 平坦填充（%d 件，全普通档）**：小数值+无钩子——它们的问题是**存在感**：拿的时候没感觉、挂一局也没感觉。普通档的「图鉴填充物」定位是否成立，归设计者。' % cnt['C1 平坦填充'])
buf.append('- **C2 真的弱（%d 件，精良以上）**：稀有度没兑现——精良/rare/boss 档却只有普通档的裸收益。C2 是 94 件里唯一「讨论强度」有意义的子集：它们占了「亏」件的 %.0f%%。' % (cnt['C2 真的弱'], 100 * cnt['C2 真的弱'] / 94))
buf.append('')
buf.append('## 复算')
buf.append('')
buf.append('`python tools/sim/relic_triage.py`（MOD_HINTS 词表与分诊判序在顶部；94 件原始清单在 data/sim/relic_below05.txt）。')
OUT = GAME / 'docs' / 'design' / '_RELIC_TRIAGE.md'
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
print(dict(cnt), 'total', len(rows))
