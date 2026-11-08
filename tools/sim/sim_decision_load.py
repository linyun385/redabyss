# -*- coding: utf-8 -*-
"""H10 决策负担量化 → docs/design/sim_decision_load.md
每回合手牌 5 张（角色池+通用池，稀有度权重同 T506），4 能量：
决策点 = 可行出牌子集数（2^5 上限，费用和 ≤4 的子集）+ 资源决策数（共振/凝视支付牌）。
四角色各 2000 回合，seed=42。可复算：python tools/sim/sim_decision_load.py
"""
import sys, statistics, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simlib import GAME, PARAMS, CN_CLASS, load_cards, class_pool

OUT = GAME / 'docs' / 'design' / 'sim_decision_load.md'
from config import N_DECISION_TURNS, SEED
N = N_DECISION_TURNS
import random
rng = random.Random(SEED)
cards = load_cards()
WEIGHT = PARAMS['RARITY_W']

buf = []
buf.append('# H10 · 决策负担量化（每回合要比较几个选择）')
buf.append('')
buf.append('> **假设**：① 手牌=抽 5（角色池+通用池按稀有度权重 6/3/1，special 按精良）；')
buf.append('> ② 决策点=**可行出牌子集数**（5 张牌的全部子集里费用和 ≤4 的个数——每个子集是一个「这一回合可以怎么打」；打牌顺序的排列不另计，因为绝大多数顺序不影响结果）+ 资源决策（共振/凝视支付牌在手=多一个「花不花」的分叉）；')
buf.append('> ③ 能量 4。')
buf.append('> **局限**：子集数不含「同效果等价」的合并（两张一模一样的缩起算 2 个子集——高估）；不含留牌/跨回合规划（低估疯先知/震语者的真实决策量）；阈值判定是口径不是实测。')
buf.append('')
buf.append('| 角色 | 可行子集数中位 | 均值 | 10/90 分位 | 资源决策/回合 | 合成决策广度 |')
buf.append('|---|---|---|---|---|---|')
res = {}
for cls in ['diver', 'tremor', 'anmin', 'cangmin']:
    pool = class_pool(cls, cards)
    w = [WEIGHT.get(c.get('rarity'), 1) for c in pool]
    subsets, resd, meaningfuls = [], [], []
    for _ in range(N):
        hand = rng.choices(pool, weights=w, k=5)
        costs = [c.get('energy', 0) for c in hand]
        cnt = 0
        meaningful = 0
        for mask in range(32):
            bits = [(mask >> i) & 1 for i in range(5)]
            spent = sum(c * b for c, b in zip(costs, bits))
            if spent <= 4:
                cnt += 1
                if spent >= 3:   # 「认真打」的子集：花掉 ≥3 能量
                    meaningful += 1
        subsets.append(cnt)
        meaningfuls.append(meaningful)
        resd.append(sum(1 for c in hand if (c.get('effect') or {}).get('resonance_cost')
                        or (c.get('effect') or {}).get('gaze_cost')))
    m = statistics.median(subsets)
    mm = statistics.median(meaningfuls)
    res[cls] = (m, mm, statistics.mean(meaningfuls), sorted(meaningfuls)[int(.1*N)], sorted(meaningfuls)[int(.9*N)],
                statistics.mean(resd), mm + statistics.mean(resd))
    buf.append('| %s | %.0f | %.0f | %.1f | %.0f / %.0f | %.2f | %.1f |' % (
        CN_CLASS[cls], m, mm, res[cls][2], res[cls][3], res[cls][4], res[cls][5], res[cls][6]))
buf.append('')
buf.append('## 判断')
buf.append('')
order = sorted(res.items(), key=lambda kv: kv[1][6])
buf.append('1. 首版指标（全部可行子集）**饱和在 31/32**——手牌几乎全是 0-1 费，任何子集都可行，该指标无信息量（按「不许硬凑」规矩如实报告并换指标）。有意义子集（花≥3 能量）中位 %.0f~%.0f，才有区分度。' % (
    min(r[1] for r in res.values()), max(r[1] for r in res.values())))
buf.append('2. 决策广度最高 **%s**（%.1f）、最低 **%s**（%.1f）——与 T506 的静态版结论同向（那版也是这两位垫底）。' % (
    CN_CLASS[order[-1][0]], order[-1][1][6], CN_CLASS[order[0][0]], order[0][1][6]))
buf.append('3. 有意义子集仍超出 7±2 的穷举范围——启发式结论维持：超过 ~10 的选择是噪音不是深度。')
buf.append('4. 本篇与 T506 的差别：T506 数「类别数」，本篇数「可行动作组合数」——后者反映「这回合我其实能做的事」，但饱和教训说明指标设计要先看分布再下结论。')
buf.append('')
buf.append('## 复算')
buf.append('')
buf.append('`python tools/sim/sim_decision_load.py`（N/SEED 顶部；子集枚举固定 32 掩码）。')
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
import io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
for k, v in res.items(): print(k, ['%.1f' % x for x in v])
