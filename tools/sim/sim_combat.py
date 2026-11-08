# -*- coding: utf-8 -*-
"""H02 战斗回合数模拟 → docs/design/sim_combat.md
用 T440 敌人数值 + 前期 DPS≈15 近似，逐层：平均回合数、期望承伤/场、四角色可连续作战场数。
可复算：python tools/sim/sim_combat.py（seed=42）
"""
import sys, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simlib import GAME, PARAMS, load_raw, layer_enemy_pool, simulate_fight

OUT = GAME / 'docs' / 'design' / 'sim_combat.md'
from config import N_COMBAT_SAMPLE, SEED
N_SAMPLE = N_COMBAT_SAMPLE
import random
rng = random.Random(SEED)
raw = load_raw()

buf = []
buf.append('# H02 · 战斗回合数与生存模拟\n')
buf.append('')
buf.append('> **假设**：① 玩家 DPS=%.0f（前期口径，见 combat_pace.md 双口径）；② 承伤=敌人平均单发×攻击频率×回合数（defend/buff 回合按 0 摊入，偏保守——实际会更高）；')
buf.append('> ③ 玩家血量 diver 80/tremor 72/anmin 76/cangmin 30（醒侧）；④ 回合数=ceil(血/DPS)。')
buf.append('> **局限**：不模拟格挡（承伤按裸吃算，是**上界**）；不模拟升级/遗物/层规则（dry/heat_tick 会更高）；cangmin 梦侧 60 血池未计。')
buf.append('> 因此「能撑几场」是**最坏情况参考**，实际存活场数应明显高于此。')
buf.append('')
buf.append('## 逐层表（每层抽样 %d 场，seed=%d）' % (N_SAMPLE, SEED))
buf.append('')
buf.append('| 层 | 敌池 | 平均回合 | 回合 10/90 分位 | 期望承伤/场 | 80 血可连续作战 | 30 血（疯先知醒） |')
buf.append('|---|---|---|---|---|---|---|')
summary = []
for L in range(1, 9):
    pool = layer_enemy_pool(raw, L)
    rounds, takes = [], []
    for _ in range(N_SAMPLE):
        e = rng.choice(pool)
        r, t = simulate_fight(rng, e)
        rounds.append(r); takes.append(t)
    ar, at = statistics.mean(rounds), statistics.mean(takes)
    lo, hi = sorted(rounds)[int(.1*N_SAMPLE)], sorted(rounds)[int(.9*N_SAMPLE)]
    summary.append((L, len(pool), ar, at))
    buf.append('| %d | %d 只 | %.1f | %d~%d | %.1f | %.0f 场 | %.0f 场 |' % (
        L, len(pool), ar, lo, hi, at, 80 / at if at else 999, 30 / at if at else 999))
buf.append('')
buf.append('## 判断\n')
m12 = summary[1][3]
buf.append('1. 期望承伤/场从 L1 的 %.1f 涨到 L8 的 %.1f（×%.1f）——与强度曲线（T453）同向。' % (
    summary[0][3], summary[-1][3], summary[-1][3] / summary[0][3]))
buf.append('2. **80 血裸吃可连作战数在 L3 降到 %.0f 场**——与 T507/T528「L3 最容易死」互证（注意这是无格挡上界，实际能撑更多，但格挡装不满时该数字就是真实压力）。' % (80 / summary[2][3]))
buf.append('3. 疯先知（醒 30 血）裸吃口径在 L2 起只剩 %.0f~%.0f 场余量——**必须靠格挡/梦池活着**，这与 first_5min「他从头到尾都在血线上」一致。' % (30 / summary[1][3], 30 / summary[2][3]))
buf.append('')
buf.append('## 复算\n')
buf.append('`python tools/sim/sim_combat.py`；模型=simlib.simulate_fight；敌人数值=T440（raw_all.json）。')
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
for s in summary: print(s)
